"""
NOVARYX - State Persistence & Resume
Saves generation state for crash recovery and resume capability.

Every phase auto-saves. If interrupted, resume from last checkpoint.
Zero work lost. Production-grade reliability.
"""

from .generation_state import GenerationState, PhaseStatus, StateManager
from .checkpoint_manager import CheckpointManager
from .resume_handler import ResumeHandler

__all__ = [
    "GenerationState",
    "PhaseStatus",
    "StateManager",
    "CheckpointManager",
    "ResumeHandler",
]