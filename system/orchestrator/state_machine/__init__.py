"""
NOVARYX - State Machine Engine
Controls all state transitions, resume capability, and fault tolerance.

Ensures:
  - Valid state transitions only
  - Resume after crash
  - Timeout detection
  - Rollback on failure
  - Full event logging
"""

from .state_machine import NovaryxStateMachine, SystemState, StateTransition
from .state_definitions import (
    GenerationState,
    VALID_TRANSITIONS,
    TERMINAL_STATES,
    RECOVERABLE_STATES,
    STATE_METADATA
)
from .state_persistence import StatePersistence, StateSnapshot
from .state_monitor import StateMonitor

__all__ = [
    "NovaryxStateMachine",
    "SystemState",
    "StateTransition",
    "GenerationState",
    "VALID_TRANSITIONS",
    "TERMINAL_STATES",
    "RECOVERABLE_STATES",
    "STATE_METADATA",
    "StatePersistence",
    "StateSnapshot",
    "StateMonitor"
]