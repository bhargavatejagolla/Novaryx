"""
NOVARYX - Resume Handler
Detects interrupted generations and resumes from last checkpoint.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Callable

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .generation_state import GenerationState, StateManager, PhaseStatus
from .checkpoint_manager import CheckpointManager

logger = logging.getLogger("novaryx.resume")


class ResumeHandler:
    """
    Handles generation interruption and resume.
    
    Flow:
      1. Check for saved state
      2. If found, ask user if they want to resume
      3. Load state and continue from last phase
      4. Skip already completed phases
    """
    
    def __init__(self):
        self.state_manager = StateManager()
        self.checkpoint_manager = CheckpointManager()
        self.on_resume_callbacks = []
    
    def check_for_interrupted(self) -> Optional[GenerationState]:
        """Check if there's an interrupted generation to resume"""
        
        # Load active state
        state = self.state_manager.load()
        
        if state is None:
            logger.info("No saved state found")
            return None
        
        # Check if generation was interrupted
        next_phase = state.get_next_pending_phase()
        
        if next_phase is None and state.get_progress() >= 100:
            logger.info("Previous generation completed")
            return None
        
        # Check if it's recent (within last 24 hours)
        from datetime import datetime, timezone
        if state.last_saved:
            try:
                last_saved = datetime.fromisoformat(state.last_saved)
                hours_ago = (datetime.now() - last_saved).total_seconds() / 3600
                if hours_ago > 24:
                    logger.info(f"State too old ({hours_ago:.0f} hours), starting fresh")
                    return None
            except Exception:
                pass
        
        logger.info(f"Found interrupted generation: {state.generation_id}")
        return state
    
    def resume_generation(
        self,
        state: GenerationState,
        phase_handlers: Dict[str, Callable]
    ) -> GenerationState:
        """
        Resume generation from saved state.
        
        Args:
            state: Loaded generation state
            phase_handlers: Dict of phase_name → handler function
        
        Returns:
            Completed generation state
        """
        
        print("\n" + "=" * 70)
        print("🔄 RESUMING GENERATION")
        print("=" * 70)
        print(f"   Project: {state.project_name}")
        print(f"   Progress: {state.get_progress():.0f}%")
        print(f"   Resuming from: {state.current_phase or 'beginning'}")
        print("=" * 70)
        
        state.resumed = True
        state.resume_count += 1
        
        # Find next pending phase
        next_phase = state.get_next_pending_phase()
        
        if next_phase is None:
            print("   All phases complete!")
            return state
        
        # Execute remaining phases
        phases_to_run = []
        found_next = False
        for name in state.phases:
            if name == next_phase:
                found_next = True
            if found_next and state.phases[name].status in [PhaseStatus.PENDING, PhaseStatus.FAILED]:
                phases_to_run.append(name)
        
        print(f"   Remaining phases: {len(phases_to_run)}")
        
        for phase_name in phases_to_run:
            handler = phase_handlers.get(phase_name)
            
            if handler is None:
                logger.warning(f"No handler for phase: {phase_name}")
                state.fail_phase(phase_name, f"No handler registered")
                continue
            
            print(f"\n   ▶️  Running: {phase_name}")
            
            try:
                state.start_phase(phase_name)
                self.state_manager.save()
                
                # Execute phase handler
                result = handler(state)
                
                if result is not None:
                    state.complete_phase(phase_name, result)
                else:
                    state.complete_phase(phase_name)
                
                self.state_manager.save()
                
                # Create checkpoint after each phase
                if hasattr(state, 'generated_files') and state.generated_files:
                    self.checkpoint_manager.create_checkpoint(
                        generation_id=state.generation_id,
                        name=phase_name,
                        files=state.generated_files
                    )
                
                print(f"   ✅ {phase_name} completed")
                
            except Exception as e:
                logger.error(f"Phase {phase_name} failed: {e}")
                state.fail_phase(phase_name, str(e))
                self.state_manager.save()
                
                print(f"   ❌ {phase_name} failed: {e}")
                
                # Stop on critical failures
                if "critical" in str(e).lower():
                    break
        
        state.display()
        
        return state
    
    def register_phase_handler(self, phase_name: str, handler: Callable):
        """Register a handler for a specific phase"""
        self.on_resume_callbacks.append((phase_name, handler))
    
    def get_resume_summary(self, state: GenerationState) -> str:
        """Get a human-readable resume summary"""
        completed = sum(1 for p in state.phases.values() if p.status == PhaseStatus.COMPLETED)
        failed = sum(1 for p in state.phases.values() if p.status == PhaseStatus.FAILED)
        pending = sum(1 for p in state.phases.values() if p.status == PhaseStatus.PENDING)
        
        lines = [
            f"Generation: {state.generation_id}",
            f"Project: {state.project_name}",
            f"Progress: {completed}/{state.total_phases} phases",
            f"Failed: {failed}",
            f"Remaining: {pending}",
            f"Resume count: {state.resume_count}",
        ]
        
        if state.get_failed_phases():
            lines.append(f"Failed phases: {', '.join(state.get_failed_phases())}")
        
        return "\n".join(lines)


# ---- Test ----

def test_state_persistence():
    """Test state persistence and resume"""
    
    print("\n" + "=" * 60)
    print("🧪 STATE PERSISTENCE TEST")
    print("=" * 60)
    
    # Create state
    manager = StateManager()
    state = manager.create_state(
        prompt="Build a dark purple SaaS dashboard",
        project_name="TestDashboard"
    )
    
    # Simulate completing phases
    state.start_phase("intent_parsing")
    state.complete_phase("intent_parsing", {"type": "saas_dashboard"})
    manager.save()
    
    state.start_phase("design_system")
    state.design_system_data = {"primary": "#7c3aed"}
    state.complete_phase("design_system")
    manager.save()
    
    # Simulate crash
    print(f"\n   Simulated progress: {state.get_progress():.0f}%")
    print(f"   State saved at: {state.last_saved}")
    
    # Load state (simulating restart)
    loaded = manager.load(state.generation_id)
    
    if loaded:
        print(f"\n   ✅ State restored!")
        print(f"   Progress: {loaded.get_progress():.0f}%")
        print(f"   Resume count: {loaded.resume_count}")
        print(f"   Next phase: {loaded.get_next_pending_phase()}")
        
        loaded.display()
    
    # Test checkpoint
    checkpoint_mgr = CheckpointManager()
    checkpoint_mgr.create_checkpoint(
        generation_id=state.generation_id,
        name="after_design",
        files={"test.tsx": "// test"},
        metadata={"phase": "design"}
    )
    
    checkpoints = checkpoint_mgr.list_checkpoints(state.generation_id)
    print(f"\n   Checkpoints: {len(checkpoints)}")
    for cp in checkpoints:
        print(f"      - {cp['name']}: {cp['files']} files")
    
    # Test resume handler
    resume_handler = ResumeHandler()
    interrupted = resume_handler.check_for_interrupted()
    
    if interrupted:
        summary = resume_handler.get_resume_summary(interrupted)
        print(f"\n   Resume summary:\n{summary}")
    
    # List saved states
    saved = manager.list_saved_states()
    print(f"\n   Saved states: {len(saved)}")
    for s in saved:
        print(f"      - {s['project']}: {s['progress']}")
    
    print("\n✅ State Persistence test complete")
    
    return manager


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_state_persistence()