"""
Tests for phase 2 of the moral realism ABM system.

This module tests the enhanced functionality including:
- Extended ActionType enum
- Complex constraint validation
- Small state behaviors
"""

import pytest

from src.models.agent import AgentType
from src.models.leadership_type import LeadershipType, get_leadership_profile


class TestPhase2Enhancements:
    """Tests for Phase 2 enhancements."""

    def test_action_type_count(self):
        """Verify action types have been extended."""
        from src.prompts.leadership_prompts import ActionType

        action_types = list(ActionType)
        assert len(action_types) >= 30, f"Expected at least 30 action types, got {len(action_types)}"

    def test_security_actions_exist(self):
        """Verify security action types exist."""
        from src.prompts.leadership_prompts import ActionType

        security_actions = [
            ActionType.SECURITY_MILITARY,
            ActionType.SECURITY_ALLIANCE,
            ActionType.SECURITY_MEDIATION,
        ]
        for action in security_actions:
            assert hasattr(ActionType, action.name)

    def test_economic_actions_exist(self):
        """Verify economic action types exist."""
        from src.prompts.leadership_prompts import ActionType

        economic_actions = [
            ActionType.ECONOMIC_TRADE,
            ActionType.ECONOMIC_SANCTION,
            ActionType.ECONOMIC_AID,
        ]
        for action in economic_actions:
            assert hasattr(ActionType, action.name)

    def test_norm_actions_exist(self):
        """Verify norm action types exist."""
        from src.prompts.leadership_prompts import ActionType

        norm_actions = [
            ActionType.NORM_PROPOSAL,
            ActionType.NORM_REFORM,
            ActionType.ORG_REFORM,
        ]
        for action in norm_actions:
            assert hasattr(ActionType, action.name)

    def test_diplomatic_actions_exist(self):
        """Verify diplomatic action types exist."""
        from src.prompts.leadership_prompts import ActionType

        diplomatic_actions = [
            ActionType.DIPLOMATIC_VISIT,
            ActionType.DIPLOMATIC_ALLIANCE,
        ]
        for action in diplomatic_actions:
            assert hasattr(ActionType, action.name)

    def test_leadership_profiles(self):
        """Verify leadership profiles are accessible."""
        profiles = [
            get_leadership_profile(LeadershipType.WANGDAO),
            get_leadership_profile(LeadershipType.HEGEMON),
            get_leadership_profile(LeadershipType.QIANGQUAN),
            get_leadership_profile(LeadershipType.HUNYONG),
        ]

        for profile in profiles:
            assert profile is not None
            assert profile.moral_standard >= 0 and profile.moral_standard <= 1
