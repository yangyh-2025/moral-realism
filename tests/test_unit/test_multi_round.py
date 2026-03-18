"""
Unit tests for Multi-round workflow module

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
from typing import Dict, List

try:
    from application.workflows.multi_round import (
        MultiRoundWorkflow,
        WorkflowState,
        RoundResult,
        WorkflowPhase
    )
    WORKFLOWS_AVAILABLE = True
except ImportError:
    WORKFLOWS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not WORKFLOWS_AVAILABLE,
    reason="Workflows module not available"
)


@pytest.mark.unit
class TestWorkflowPhase:
    """Test WorkflowPhase enum"""

    def test_phase_values(self):
        """Test that all phases have values"""
        if WORKFLOWS_AVAILABLE:
            phases = [
                WorkflowPhase.INITIALIZATION,
                WorkflowPhase.SITUATION_ASSESSMENT,
                WorkflowPhase.LEADER_DECISION,
                WorkflowPhase.STATE_FOLLOWUP,
                WorkflowPhase.EXECUTION,
                WorkflowPhase.EVALUATION,
                WorkflowPhase.FINALIZATION
            ]

            for phase in phases:
                assert isinstance(phase.value, str)
                assert len(phase.value) > 0


@pytest.mark.unit
class TestWorkflowState:
    """Test WorkflowState dataclass"""

    def test_workflow_state_creation(self):
        """Test creating workflow state"""
        if WORKFLOWS_AVAILABLE:
            state = WorkflowState(
                current_round=0,
                max_rounds=10,
                current_phase=WorkflowPhase.INITIALIZATION,
                agents=[],
                environment_state={},
                is_complete=False
            )

            assert state.current_round == 0
            assert state.max_rounds == 10
            assert state.current_phase == WorkflowPhase.INITIALIZATION
            assert state.is_complete is False

    def test_workflow_state_defaults(self):
        """Test workflow state with defaults"""
        if WORKFLOWS_AVAILABLE:
            state = WorkflowState(
                current_round=0,
                max_rounds=10,
                current_phase=WorkflowPhase.INITIALIZATION
            )

            assert state.agents == []
            assert state.environment_state == {}
            assert state.is_complete is False


@pytest.mark.unit
class TestRoundResult:
    """Test RoundResult dataclass"""

    def test_round_result_creation(self):
        """Test creating round result"""
        if WORKFLOWS_AVAILABLE:
            result = RoundResult(
                round_number=1,
                success=True,
                decisions=[],
                interactions=[],
                events=[],
                metrics={},
                error_message=None
            )

            assert result.round_number == 1
            assert result.success is True
            assert result.decisions == []
            assert result.error_message is None

    def test_round_result_with_error(self):
        """Test round result with error"""
        if WORKFLOWS_AVAILABLE:
            result = RoundResult(
                round_number=1,
                success=False,
                decisions=[],
                interactions=[],
                events=[],
                metrics={},
                error_message="Test error"
            )

            assert result.success is False
            assert result.error_message == "Test error"


@pytest.mark.unit
class TestMultiRoundWorkflow:
    """Test MultiRoundWorkflow class"""

    @pytest.fixture
    def workflow(self):
        """Create workflow"""
        if WORKFLOWS_AVAILABLE:
            return MultiRoundWorkflow(
                max_rounds=5,
                agents=[],
                environment_state={}
            )

    def test_workflow_initialization(self, workflow):
        """Test workflow initialization"""
        if WORKFLOWS_AVAILABLE:
            assert workflow.max_rounds == 5
            assert workflow.current_round == 0
            assert workflow.is_complete is False

    def test_advance_round(self, workflow):
        """Test advancing round"""
        if WORKFLOWS_AVAILABLE:
            initial_round = workflow.current_round
            workflow.advance_round()

            assert workflow.current_round == initial_round + 1

    def test_check_complete(self, workflow):
        """Test checking workflow completion"""
        if WORKFLOWS_AVAILABLE:
            # Should not be complete initially
            assert workflow.check_complete() is False

            # Set to max round
            workflow.current_round = workflow.max_rounds
            assert workflow.check_complete() is True

    def test_get_current_phase(self, workflow):
        """Test getting current phase"""
        if WORKFLOWS_AVAILABLE:
            phase = workflow.get_current_phase()
            assert isinstance(phase, WorkflowPhase)

    def test_execute_round(self, workflow):
        """Test executing a round"""
        if WORKFLOWS_AVAILABLE:
            result = workflow.execute_round()

            assert isinstance(result, RoundResult)
            assert result.round_number == 1

    def test_execute_workflow(self, workflow):
        """Test executing complete workflow"""
        if WORKFLOWS_AVAILABLE:
            results = workflow.execute()

            assert isinstance(results, list)
            assert len(results) == workflow.max_rounds
            assert workflow.is_complete is True

    def test_get_workflow_summary(self, workflow):
        """Test getting workflow summary"""
        if WORKFLOWS_AVAILABLE:
            summary = workflow.get_summary()

            assert isinstance(summary, dict)
            assert "total_rounds" in summary
            assert "completed_rounds" in summary
            assert "success_rate" in summary

    def test_get_state(self, workflow):
        """Test getting workflow state"""
        if WORKFLOWS_AVAILABLE:
            state = workflow.get_state()

            assert isinstance(state, WorkflowState)
            assert state.current_round == workflow.current_round
            assert state.max_rounds == workflow.max_rounds
