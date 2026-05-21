"""
NOVARYX - State Machine
Controls all state transitions with validation, logging, and recovery.
"""

import logging
import time
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
from dataclasses import dataclass, field

from .state_definitions import (
    GenerationState,
    is_valid_transition,
    get_allowed_transitions,
    get_state_metadata,
    TERMINAL_STATES,
    RECOVERABLE_STATES
)

logger = logging.getLogger("novaryx.state_machine")


@dataclass
class StateTransition:
    """Record of a state transition"""
    from_state: GenerationState
    to_state: GenerationState
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


class SystemState:
    """Current state of the NOVARYX system with full history"""
    
    def __init__(self):
        self.current_state: GenerationState = GenerationState.IDLE
        self.previous_state: Optional[GenerationState] = None
        self.state_entered_at: datetime = datetime.now()
        self.transition_history: List[StateTransition] = []
        self.state_data: Dict[str, Any] = {}
        self.error_count: int = 0
        self.max_errors: int = 10
    
    def record_transition(self, transition: StateTransition):
        """Record a state transition in history"""
        self.transition_history.append(transition)
        self.previous_state = transition.from_state
        self.current_state = transition.to_state
        self.state_entered_at = transition.timestamp
        
        # Track errors
        if not transition.success:
            self.error_count += 1
    
    def get_time_in_current_state(self) -> float:
        """Get seconds spent in current state"""
        return (datetime.now() - self.state_entered_at).total_seconds()
    
    def has_exceeded_error_limit(self) -> bool:
        """Check if too many errors have occurred"""
        return self.error_count >= self.max_errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "state_entered_at": self.state_entered_at.isoformat(),
            "error_count": self.error_count,
            "transition_count": len(self.transition_history),
            "last_transitions": [
                {
                    "from": t.from_state.value,
                    "to": t.to_state.value,
                    "timestamp": t.timestamp.isoformat(),
                    "reason": t.reason
                }
                for t in self.transition_history[-5:]  # Last 5
            ]
        }


class NovaryxStateMachine:
    """
    Central state machine for NOVARYX.
    
    Ensures:
    - Only valid state transitions occur
    - All transitions are logged
    - Timeouts are detected
    - Recovery is possible from failures
    - State can be saved and restored
    """
    
    def __init__(self):
        self.state = SystemState()
        self.transition_hooks: Dict[GenerationState, List[Callable]] = {}
        self.on_error_hook: Optional[Callable] = None
        self.on_complete_hook: Optional[Callable] = None
        self._running = False
        
        logger.info("StateMachine initialized")
    
    # ---- Core Transition Logic ----
    
    def transition(
        self,
        to_state: GenerationState,
        reason: str = "",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Attempt to transition to a new state.
        
        Args:
            to_state: Target state
            reason: Why we're transitioning
            metadata: Additional data about the transition
        
        Returns:
            True if transition succeeded, False otherwise
        """
        from_state = self.state.current_state
        
        # Check if valid transition
        if not is_valid_transition(from_state, to_state):
            logger.error(
                f"Invalid transition: {from_state.value} → {to_state.value}"
            )
            logger.info(
                f"Allowed transitions from {from_state.value}: "
                f"{[s.value for s in get_allowed_transitions(from_state)]}"
            )
            return False
        
        # Check if terminal
        if from_state in TERMINAL_STATES and from_state != GenerationState.FAILED:
            logger.warning(
                f"Cannot transition from terminal state: {from_state.value}"
            )
            return False
        
        # Create transition record
        transition_record = StateTransition(
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.now(),
            reason=reason,
            metadata=metadata or {},
            success=True
        )
        
        # Log transition
        state_meta = get_state_metadata(to_state)
        logger.info(
            f"State Transition: {from_state.value} → {to_state.value} "
            f"({reason}) [{state_meta.get('phase', 'unknown')}]"
        )
        
        # Record in history
        self.state.record_transition(transition_record)
        
        # Run transition hooks
        self._run_hooks(to_state, metadata or {})
        
        # Check if terminal state reached
        if to_state in TERMINAL_STATES:
            if to_state == GenerationState.COMPLETED and self.on_complete_hook:
                self.on_complete_hook(self.state)
            elif to_state == GenerationState.FAILED and self.on_error_hook:
                self.on_error_hook(self.state)
        
        return True
    
    def force_transition(
        self,
        to_state: GenerationState,
        reason: str = "forced"
    ) -> bool:
        """Force a transition even if not normally allowed (use carefully)"""
        from_state = self.state.current_state
        
        logger.warning(
            f"Forced transition: {from_state.value} → {to_state.value} ({reason})"
        )
        
        transition_record = StateTransition(
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.now(),
            reason=f"FORCED: {reason}",
            success=True
        )
        
        self.state.record_transition(transition_record)
        return True
    
    # ---- State Checking ----
    
    def is_in_state(self, state: GenerationState) -> bool:
        """Check if currently in a specific state"""
        return self.state.current_state == state
    
    def is_in_phase(self, phase: str) -> bool:
        """Check if currently in a specific phase"""
        meta = get_state_metadata(self.state.current_state)
        return meta.get("phase") == phase
    
    def is_terminal(self) -> bool:
        """Check if in a terminal state"""
        return self.state.current_state in TERMINAL_STATES
    
    def is_recoverable(self) -> bool:
        """Check if current state allows recovery"""
        return self.state.current_state in RECOVERABLE_STATES
    
    def can_proceed(self) -> bool:
        """Check if system can proceed with generation"""
        return not self.is_terminal() and not self.is_in_state(GenerationState.PAUSED)
    
    # ---- Hooks ----
    
    def add_hook(
        self,
        state: GenerationState,
        callback: Callable[[SystemState, Dict[str, Any]], None]
    ):
        """Add a hook that runs when entering a specific state"""
        if state not in self.transition_hooks:
            self.transition_hooks[state] = []
        self.transition_hooks[state].append(callback)
    
    def set_error_hook(self, callback: Callable[[SystemState], None]):
        """Set callback for when system enters FAILED state"""
        self.on_error_hook = callback
    
    def set_complete_hook(self, callback: Callable[[SystemState], None]):
        """Set callback for when system enters COMPLETED state"""
        self.on_complete_hook = callback
    
    def _run_hooks(self, state: GenerationState, metadata: Dict[str, Any]):
        """Run all hooks for a state"""
        if state in self.transition_hooks:
            for hook in self.transition_hooks[state]:
                try:
                    hook(self.state, metadata)
                except Exception as e:
                    logger.error(f"Hook failed for state {state.value}: {e}")
    
    # ---- Recovery ----
    
    def recover(self) -> bool:
        """Attempt to recover from a failure state"""
        if not self.is_recoverable():
            logger.warning(f"Cannot recover from {self.state.current_state.value}")
            return False
        
        logger.info(f"Attempting recovery from {self.state.current_state.value}")
        return self.transition(
            GenerationState.RECOVERING,
            reason="Attempting recovery"
        )
    
    def rollback(self) -> bool:
        """Rollback to a safe state"""
        logger.warning("Initiating rollback")
        return self.force_transition(
            GenerationState.ROLLING_BACK,
            reason="Rollback initiated"
        )
    
    def reset(self):
        """Complete reset to IDLE state"""
        logger.warning("Resetting state machine to IDLE")
        self.state = SystemState()
    
    # ---- Timeout Detection ----
    
    def check_timeout(self) -> bool:
        """Check if current state has timed out"""
        meta = get_state_metadata(self.state.current_state)
        timeout = meta.get("timeout_seconds")
        
        if timeout is None:
            return False
        
        elapsed = self.state.get_time_in_current_state()
        
        if elapsed > timeout:
            logger.warning(
                f"State {self.state.current_state.value} timed out "
                f"({elapsed:.0f}s > {timeout}s)"
            )
            self.force_transition(
                GenerationState.TIMED_OUT,
                reason=f"Timeout after {elapsed:.0f}s (limit: {timeout}s)"
            )
            return True
        
        return False
    
    # ---- Status ----
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        meta = get_state_metadata(self.state.current_state)
        
        return {
            "current_state": self.state.current_state.value,
            "phase": meta.get("phase", "unknown"),
            "description": meta.get("description", ""),
            "is_terminal": self.is_terminal(),
            "is_recoverable": self.is_recoverable(),
            "time_in_state_seconds": self.state.get_time_in_current_state(),
            "error_count": self.state.error_count,
            "transition_count": len(self.state.transition_history),
            "allowed_transitions": [
                s.value for s in get_allowed_transitions(self.state.current_state)
            ]
        }
    
    def display_status(self):
        """Display current state machine status"""
        status = self.get_status()
        
        print("\n" + "=" * 50)
        print("🔧 STATE MACHINE STATUS")
        print("=" * 50)
        print(f"   State: {status['current_state'].upper()}")
        print(f"   Phase: {status['phase']}")
        print(f"   Description: {status['description']}")
        print(f"   Time in state: {status['time_in_state_seconds']:.0f}s")
        print(f"   Terminal: {'Yes' if status['is_terminal'] else 'No'}")
        print(f"   Errors: {status['error_count']}")
        print(f"   Allowed next states: {', '.join(status['allowed_transitions'])}")
        print("=" * 50 + "\n")
    
    def get_transition_log(self, count: int = 10) -> str:
        """Get recent transition history as formatted string"""
        log_lines = ["State Transition History:"]
        log_lines.append("-" * 50)
        
        for t in self.state.transition_history[-count:]:
            arrow = "→"
            log_lines.append(
                f"  {t.from_state.value} {arrow} {t.to_state.value} "
                f"({t.reason}) [{t.timestamp.strftime('%H:%M:%S')}]"
            )
        
        return "\n".join(log_lines)


# ---- Test Function ----

def test_state_machine():
    """Test the state machine with a sample flow"""
    
    print("\n" + "=" * 60)
    print("🧪 STATE MACHINE TEST")
    print("=" * 60)
    
    sm = NovaryxStateMachine()
    
    # Sample generation flow
    test_flow = [
        (GenerationState.INITIALIZING, "System startup"),
        (GenerationState.READY, "All systems ready"),
        (GenerationState.PARSING_PROMPT, "Received user prompt"),
        (GenerationState.CLASSIFYING_PROJECT, "Project type: saas"),
        (GenerationState.PLANNING_ARCHITECTURE, "Designing system"),
        (GenerationState.RETRIEVING_TEMPLATES, "Finding templates"),
        (GenerationState.GENERATING_PAGES, "Generating 6 pages"),
        (GenerationState.ASSEMBLING_PROJECT, "Assembling files"),
        (GenerationState.VERIFYING_SYNTAX, "Checking syntax"),
        (GenerationState.VERIFYING_IMPORTS, "Validating imports"),
    ]
    
    print("\n📋 Running sample generation flow:\n")
    
    for state, reason in test_flow:
        success = sm.transition(state, reason)
        status = "✅" if success else "❌"
        print(f"  {status} {state.value} ({reason})")
        
        if not success:
            print(f"     Allowed: {[s.value for s in get_allowed_transitions(sm.state.current_state)]}")
            break
    
    # Test invalid transition
    print("\n🔒 Testing invalid transition:")
    sm.transition(GenerationState.PARSING_PROMPT, "Should fail")
    
    # Force complete
    sm.force_transition(GenerationState.COMPLETED, "Test complete")
    
    sm.display_status()
    print(sm.get_transition_log())
    
    # Test recovery
    sm.force_transition(GenerationState.FAILED, "Simulated failure")
    print(f"\n🔄 Recoverable: {sm.is_recoverable()}")
    sm.recover()
    sm.display_status()
    
    print("✅ State machine test complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_state_machine()