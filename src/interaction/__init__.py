"""
Interaction mechanisms for the moral realism ABM system.

This module provides components for managing agent interactions,
including InteractionManager, BehaviorSelector, ResponseGenerator,
and InteractionRules.
"""

from .interaction_manager import (
    InteractionManager,
    InteractionResult,
    InteractionStep,
)
from .behavior_selector import (
    BehaviorSelector,
    Behavior,
    BehaviorConstraint,
    ValidationResult,
)
from .response_generator import (
    ResponseGenerator,
    ResponseType,
    ResponseTemplate,
    MessageType,
)
from .interaction_rules import (
    InteractionRules,
    InteractionConstraint,
    InteractionCategory,
    MoralImpact,
)

__all__ = [
    # Interaction Manager
    "InteractionManager",
    "InteractionResult",
    "InteractionStep",
    # Behavior Selector
    "BehaviorSelector",
    "Behavior",
    "BehaviorConstraint",
    "ValidationResult",
    # Response Generator
    "ResponseGenerator",
    "ResponseType",
    "ResponseTemplate",
    "MessageType",
    # Interaction Rules
    "InteractionRules",
    "InteractionConstraint",
    "InteractionCategory",
    "MoralImpact",
]
