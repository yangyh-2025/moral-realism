"""
Unit tests for Base Agent module

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
import json
import time
from unittest.mock import Mock

try:
    from entities.base_agent import (
        DecisionCache,
        AgentLearning,
        ConsistencyReport,
        DecisionPriority,
        AccessLevel
    )
    from entities.power_system import PowerMetrics, PowerTier
    ENTITIES_AVAILABLE = True
except ImportError:
    ENTITIES_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not ENTITIES_AVAILABLE,
    reason="Entities module not available"
)


@pytest.mark.unit
def test_access_level_values():
    """Test access level values"""
    assert AccessLevel.PUBLIC.value == "public"
    assert AccessLevel.RESTATER.value == "restricted"
    assert AccessLevel.PRIVATE.value == "private"
    assert AccessLevel.CLASSIFIED.value == "classified"


@pytest.mark.unit
def test_decision_priority_values():
    """Test priority values"""
    assert DecisionPriority.EMERGENCY.value == 5
    assert DecisionPriority.HIGH.value == 4
    assert DecisionPriority.MEDIUM.value == 3
    assert DecisionPriority.LOW.value == 2
    assert DecisionPriority.ROUTINE.value == 1


@pytest.mark.unit
class TestDecisionCache:
    """Test DecisionCache class"""

    @pytest.fixture
    def cache(self):
        return DecisionCache(max_size=100, ttl=3600)

    def test_cache_initialization(self, cache):
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["max_size"] == 100

    def test_cache_decision(self, cache):
        context = {"agent_id": "test_agent", "round": 1}
        decision = {"action": "test", "target": "target"}
        cache.cache_decision(context, decision, "test_agent")
        stats = cache.get_stats()
        assert stats["size"] == 1

    def test_get_cached_decision(self, cache):
        context = {"agent_id": "test_agent", "round": 1}
        decision = {"action": "test", "target": "target"}
        cache.cache_decision(context, decision, "test_agent")
        retrieved = cache.get_cached_decision(context)
        assert retrieved is not None
        assert retrieved["action"] == "test"

    def test_get_nonexistent_cached_decision(self, cache):
        context = {"agent_id": "nonexistent", "round": 1}
        result = cache.get_cached_decision(context)
        assert result is None

    def test_cache_lru_eviction(self, cache):
        cache = DecisionCache(max_size=3, ttl=3600)
        for i in range(4):
            context = {"round": i}
            decision = {"action": f"action_{i}"}
            cache.cache_decision(context, decision, "test")
        stats = cache.get_stats()
        assert stats["size"] == 3

    def test_clear_all(self, cache):
        cache.cache_decision({"round": 1}, {"action": "test"}, "test")
        assert cache.get_stats()["size"] == 1
        cache.clear_all()
        assert cache.get_stats()["size"] == 0


@pytest.mark.unit
class TestAgentLearning:
    """Test AgentLearning class"""

    @pytest.fixture
    def learning(self):
        return AgentLearning(agent_id="test_agent", max_outcomes=1000)

    def test_learning_initialization(self, learning):
        assert learning.agent_id == "test_agent"
        assert len(learning._outcomes) == 0

    def test_record_outcome(self, learning):
        decision = {"type": "test_action", "target": "target"}
        outcome = {"success": True}
        learning.record_outcome(decision, outcome)
        assert len(learning._outcomes) == 1

    def test_get_success_rate(self, learning):
        for _ in range(8):
            decision = {"type": "test_action"}
            outcome = {"success": True}
            learning.record_outcome(decision, outcome)
        for _ in range(2):
            decision = {"type": "test_action"}
            outcome = {"success": False}
            learning.record_outcome(decision, outcome)
        rate = learning.get_success_rate()
        assert rate == 0.8

    def test_get_success_rate_empty(self, learning):
        rate = learning.get_success_rate()
        assert rate == 0.0


@pytest.mark.unit
class TestConsistencyReport:
    """Test ConsistencyReport class"""

    def test_report_initialization(self):
        report = ConsistencyReport(
            is_consistent=True,
            issues=[],
            confidence_score=1.0
        )
        assert report.is_consistent is True
        assert report.confidence_score == 1.0

    def test_add_issue(self):
        report = ConsistencyReport(is_consistent=True)
        report.add_issue("Test issue")
        assert report.is_consistent is False
        assert len(report.issues) == 1

    def test_to_dict(self):
        report = ConsistencyReport(
            is_consistent=False,
            issues=["issue1"],
            confidence_score=0.5
        )
        result = report.to_dict()
        assert result["is_consistent"] is False
        assert result["confidence_score"] == 0.5
