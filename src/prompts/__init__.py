"""Prompt templates and management for moral realism ABM system."""

from src.prompts.leadership_prompts import GreatPowerPromptBuilder, ActionType, ACTION_DESCRIPTIONS
from src.prompts.base_prompt import BasePromptBuilder, PromptContext, PromptBuilderRegistry, create_default_context
from src.prompts.behavior_prompts import BehaviorPromptBuilder, BehaviorCategory, BEHAVIOR_DESCRIPTIONS
from src.prompts.response_prompts import ResponsePromptBuilder, MessageType, ResponseTone

__all__ = [
    # From leadership_prompts
    "GreatPowerPromptBuilder",
    "ActionType",
    "ACTION_DESCRIPTIONS",
    # From base_prompt
    "BasePromptBuilder",
    "PromptContext",
    "PromptBuilderRegistry",
    "create_default_context",
    # From behavior_prompts
    "BehaviorPromptBuilder",
    "BehaviorCategory",
    "BEHAVIOR_DESCRIPTIONS",
    # From response_prompts
    "ResponsePromptBuilder",
    "MessageType",
    "ResponseTone",
]
