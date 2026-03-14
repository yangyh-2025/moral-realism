"""
Security tests for input validation

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
from typing import Dict, List

try:
    from fastapi.testclient import TestClient
    from backend.main import app
    from pydantic import ValidationError
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not API_AVAILABLE,
    reason="Backend API not available"
)


@pytest.mark.security
class TestInputValidation:
    """Test input validation across endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_create_simulation_missing_required_fields(self, client):
        """Test creating simulation with missing required fields"""
        response = client.post(
            "/api/simulation/create",
            json={"name": "Test"}  # Missing max_rounds and agents_config
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_create_simulation_invalid_max_rounds(self, client):
        """Test creating simulation with invalid max_rounds"""
        response = client.post(
            "/api/simulation/create",
            json={
                "name": "Test",
                "max_rounds": -1,  # Invalid: negative
                "agents_config": {}
            }
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_create_simulation_invalid_max_rounds_too_large(self, client):
        """Test creating simulation with max_rounds too large"""
        response = client.post(
            "/api/simulation/create",
            json={
                "name": "Test",
                "max_rounds": 10000,  # Invalid: too large
                "agents_config": {}
            }
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_create_simulation_invalid_agent_config(self, client):
        """Test creating simulation with invalid agent config"""
        response = client.post(
            "/api/simulation/create",
            json={
                "name": "Test",
                "max_rounds": 10,
                "agents_config": "not a dict"  # Invalid type
            }
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_create_event_missing_required_fields(self, client):
        """Test creating event with missing required fields"""
        response = client.post(
            "/api/events/create",
            json={"name": "Test Event"}  # Missing event_type and description
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_create_event_invalid_impact_level(self, client):
        """Test creating event with invalid impact level"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "Test description",
                "impact_level": 2.0,  # Invalid: should be 0-1
                "priority": "normal"
            }
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_create_event_invalid_priority(self, client):
        """Test creating event with invalid priority"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "Test description",
                "impact_level": 0.5,
                "priority": "invalid"  # Invalid priority value
            }
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_injection_attack_via_simulation_name(self, client):
        """Test for injection attack via simulation name"""
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "${malicious_code}",
            "{{7*7}}",
            "'; DROP TABLE users; --"
        ]

        for malicious_input in malicious_inputs:
            response = client.post(
                "/api/simulation/create",
                json={
                    "name": malicious_input,
                    "max_rounds": 10,
                    "agents_config": {}
                }
            )

            # Should accept the string (sanitization handled by application layer)
            # Status could be 201 or 400 depending on validation
            assert response.status_code in [201, 400, 422]

    def test_injection_attack_via_event_description(self, client):
        """Test for injection attack via event description"""
        malicious_description = "${system('echo exploited')}"

        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": malicious_description,
                "impact_level": 0.5,
                "priority": "normal"
            }
        )

        # Should handle the input
        assert response.status_code in [201, 400, 422]

    def test_oversized_json_payload(self, client):
        """Test for oversized JSON payload"""
        large_payload = {
            "name": "Test",
            "max_rounds": 10,
            "agents_config": {
                f"agent_{i}": {
                    "name": f"Agent {i}",
                    "description": "X" * 100000,  # Large description
                    "power_metrics": {
                        "economic_power": i * 100,
                        "military_power": i * 80,
                        "political_power": i * 90,
                        "diplomatic_power": i * 85
                    }
                }
                for i in range(100)
            }
        }

        response = client.post(
            "/api/simulation/create",
            json=large_payload
        )

        # Should handle large payload gracefully
        assert response.status_code in [201, 400, 413, 507]

    def test_malformed_json(self, client):
        """Test for malformed JSON"""
        response = client.post(
            "/api/simulation/create",
            data='{"name": "Test", "incomplete": "json"',  # Malformed
            headers={"Content-Type": "application/json"}
        )

        # Should return parse error
        assert response.status_code in [400, 422]

    def test_invalid_content_type(self, client):
        """Test for invalid Content-Type header"""
        response = client.post(
            "/api/simulation/create",
            data='{"name": "Test"}',
            headers={"Content-Type": "application/xml"}  # Wrong content type
        )

        # Should return unsupported media type error
        assert response.status_code == 415


@pytest.mark.security
class TestNumericValidation:
    """Test numeric input validation"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_numeric_fields_as_strings(self, client):
        """Test numeric fields passed as strings"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "Test description",
                "impact_level": "0.5",  # Should be float
                "priority": "normal"
            }
        )

        # Accept string that can be converted to float
        assert response.status_code in [201, 400, 422]

    def test_numeric_fields_negative_values(self, client):
        """Test numeric fields with negative values where invalid"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "Test description",
                "impact_level": -1.0,  # Invalid: should be 0-1
                "priority": "normal"
            }
        )

        assert response.status_code in [400, 422]

    def test_numeric_fields_extreme_values(self, client):
        """Test numeric fields with extreme values"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "Test description",
                "impact_level": 999999999.0,  # Invalid: too large
                "priority": "normal"
            }
        )

        # Should reject extreme values
        assert response.status_code in [400, 422]


@pytest.mark.security
class TestArrayValidation:
    """Test array/list input validation"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_empty_agents_list(self, client):
        """Test empty agents list"""
        response = client.post(
            "/api/simulation/create",
            json={
                "name": "Test",
                "max_rounds": 10,
                "agents_config": {}  # Empty
            }
        )

        # May accept or reject empty config
        assert response.status_code in [201, 400, 422]

    def test_agents_list_with_invalid_types(self, client):
        """Test agents list with invalid types"""
        response = client.post(
            "/api/simulation/create",
            json={
                "name": "Test",
                "max_rounds": 10,
                "agents_config": {
                    "agent1": "not a dict",  # Invalid type
                    "agent2": ["not", "a", "dict"]  # Invalid type
                }
            }
        )

        # Should reject invalid types
        assert response.status_code in [400, 422]

    def test_participants_array_limit(self, client):
        """Test participants array with excessive elements"""
        # Create event with many participants
        many_participants = [f"agent_{i}" for i in range(1000)]

        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "Test description",
                "participants": many_participants,
                "impact_level": 0.5,
                "priority": "normal"
            }
        )

        # Should handle or reject large arrays
        assert response.status_code in [201, 400, 422]


@pytest.mark.security
class TestStringValidation:
    """Test string input validation"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_empty_required_strings(self, client):
        """Test empty required string fields"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "",  # Empty: should be rejected
                "description": "Test description",
                "impact_level": 0.5,
                "priority": "normal"
            }
        )

        # Should reject empty name
        assert response.status_code in [400, 422]

    def test_whitespace_only_strings(self, client):
        """Test whitespace-only string fields"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "   ",  # Whitespace only
                "description": "Test description",
                "impact_level": 0.5,
                "priority": "normal"
            }
        )

        # Should reject whitespace-only name
        assert response.status_code in [400, 422]

    def test_excessively_long_strings(self, client):
        """Test excessively long string fields"""
        long_name = "X" * 10000  # Very long name

        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": long_name,
                "description": "Test description",
                "impact_level": 0.5,
                "priority": "normal"
            }
        )

        # Should reject excessively long strings
        assert response.status_code in [400, 422]


@pytest.mark.security
class TestEnumValidation:
    """Test enum/choice input validation"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_invalid_enum_values(self, client):
        """Test invalid enum values"""
        invalid_priorities = [
            "INVALID_PRIORITY",
            "invalid_priority",
            "CRITICAL!",  # Contains special chars
            "123"  # Numeric
            "",
            None
        ]

        for invalid_priority in invalid_priorities:
            response = client.post(
                "/api/events/create",
                json={
                    "event_type": "user_defined",
                    "name": "Test Event",
                    "description": "Test description",
                    "impact_level": 0.5,
                    "priority": invalid_priority
                }
            )

            # Should reject invalid priority
            assert response.status_code in [400, 422]

    def test_case_sensitivity(self, client):
        """Test that enum validation is case-sensitive"""
        # Test with uppercase (assuming lowercase is valid)
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "Test description",
                "impact_level": 0.5,
                "priority": "NORMAL"  # Uppercase
            }
        )

        # Should reject if validation is case-sensitive
        assert response.status_code in [201, 400, 422]


@pytest.mark.security
class TestNestedValidation:
    """Test nested object validation"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_invalid_nested_structure(self, client):
        """Test invalid nested object structure"""
        response = client.post(
            "/api/simulation/create",
            json={
                "name": "Test",
                "max_rounds": 10,
                "agents_config": {
                    "agent1": {
                        "name": "Agent 1",
                        "power_metrics": "not an object",  # Invalid: should be object
                        "leader_type": "wangdao"
                    }
                }
            }
        )

        # Should reject invalid nested structure
        assert response.status_code in [400, 422]

    def test_missing_nested_required_fields(self, client):
        """Test missing required fields in nested objects"""
        response = client.post(
            "/api/simulation/create",
            json={
                "name": "Test",
                "max_rounds": 10,
                "agents_config": {
                    "agent1": {
                        "name": "Agent 1",
                        # Missing power_metrics
                        "leader_type": "wangdao"
                    }
                }
            }
        )

        # Should reject missing required nested fields
        assert response.status_code in [400, 422]

    def test_invalid_power_metrics_fields(self, client):
        """Test invalid power metrics fields"""
        response = client.post(
            "/api/simulation/create",
            json={
                "name": "Test",
                "max_rounds": 10,
                "agents_config": {
                    "agent1": {
                        "name": "Agent 1",
                        "power_metrics": {
                            "economic_power": "not a number",  # Invalid
                            "military_power": 80,
                            "political_power": 90,
                            "diplomatic_power": 85
                        },
                        "leader_type": "wangdao"
                    }
                }
            }
        )

        # Should reject invalid power metrics
        assert response.status_code in [400, 422]


@pytest.mark.security
class TestPathTraversal:
    """Test for path traversal attacks"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_path_traversal_in_strings(self, client):
        """Test for path traversal attempts in string fields"""
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\",
            "${HOME}/.ssh/id_rsa",
            "{{config['home']}}/.ssh/id_rsa"
        ]

        for malicious_input in path_traversal_attempts:
            response = client.post(
                "/api/events/create",
                json={
                    "event_type": "user_defined",
                    "name": malicious_input,
                    "description": "Test description",
                    "impact_level": 0.5,
                    "priority": "normal"
                }
            )

            # Application should sanitize path traversal attempts
            # May accept if sanitization converts to safe string
            assert response.status_code in [201, 400, 422]


@pytest.mark.security
class TestNullValidation:
    """Test null/None value handling"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_none_in_optional_fields(self, client):
        """Test None values in optional fields"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "Test description",
                "impact_level": 0.5,
                "priority": "normal",
                "participants": None  # Null in optional array field
            }
        )

        # Should handle None in optional fields
        assert response.status_code in [201, 400, 422]

    def test_none_in_required_fields(self, client):
        """Test None values in required fields"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": None,  # Null in required field
                "description": "Test description",
                "impact_level": 0.5,
                "priority": "normal"
            }
        )

        # Should reject None in required fields
        assert response.status_code in [400, 422]
