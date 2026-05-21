"""
NOVARYX - State Persistence
Save and restore system state for crash recovery.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from .state_definitions import GenerationState
from .state_machine import NovaryxStateMachine, SystemState

logger = logging.getLogger("novaryx.state_persistence")


@dataclass
class StateSnapshot:
    """A complete snapshot of system state at a point in time"""
    snapshot_id: str
    timestamp: str
    current_state: str
    previous_state: str
    error_count: int
    transition_count: int
    state_data: Dict[str, Any]
    metadata: Dict[str, Any]


class StatePersistence:
    """
    Handles saving and loading state machine state.
    
    Enables:
    - Crash recovery
    - State inspection
    - Debugging
    - Generation resumption
    """
    
    def __init__(self, state_dir: str = None):
        if state_dir is None:
            novaryx_root = Path.home() / "novaryx"
            state_dir = str(novaryx_root / "system" / "state_snapshots")
        
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_snapshot_file = self.state_dir / "current_state.json"
        self.snapshots_dir = self.state_dir / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)
        
        logger.info(f"State persistence initialized at: {self.state_dir}")
    
    def save_state(self, state_machine: NovaryxStateMachine) -> bool:
        """Save current state to disk"""
        try:
            state = state_machine.state
            
            snapshot = StateSnapshot(
                snapshot_id=f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now().isoformat(),
                current_state=state.current_state.value,
                previous_state=state.previous_state.value if state.previous_state else "",
                error_count=state.error_count,
                transition_count=len(state.transition_history),
                state_data=state.state_data,
                metadata={
                    "version": "1.0.0",
                    "saved_by": "state_persistence"
                }
            )
            
            # Save current state
            snapshot_dict = asdict(snapshot)
            with open(self.current_snapshot_file, "w") as f:
                json.dump(snapshot_dict, f, indent=2)
            
            # Also save timestamped snapshot
            timestamped_file = self.snapshots_dir / f"{snapshot.snapshot_id}.json"
            with open(timestamped_file, "w") as f:
                json.dump(snapshot_dict, f, indent=2)
            
            logger.debug(f"State saved: {snapshot.current_state}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    def load_state(self, state_machine: NovaryxStateMachine) -> bool:
        """
        Load state from disk and restore state machine.
        
        Returns True if state was restored successfully.
        """
        if not self.current_snapshot_file.exists():
            logger.info("No saved state found, starting fresh")
            return False
        
        try:
            with open(self.current_snapshot_file, "r") as f:
                data = json.load(f)
            
            # Restore state machine
            state = state_machine.state
            state.current_state = GenerationState(data["current_state"])
            
            if data.get("previous_state"):
                state.previous_state = GenerationState(data["previous_state"])
            
            state.error_count = data.get("error_count", 0)
            state.state_data = data.get("state_data", {})
            
            logger.info(
                f"State restored: {state.current_state.value} "
                f"(saved at {data.get('timestamp', 'unknown')})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return False
    
    def get_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get the latest state snapshot data"""
        if not self.current_snapshot_file.exists():
            return None
        
        try:
            with open(self.current_snapshot_file, "r") as f:
                return json.load(f)
        except Exception:
            return None
    
    def list_snapshots(self) -> list:
        """List all saved snapshots"""
        snapshots = []
        if self.snapshots_dir.exists():
            for file in sorted(self.snapshots_dir.glob("snap_*.json"), reverse=True):
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                    snapshots.append({
                        "file": file.name,
                        "timestamp": data.get("timestamp", ""),
                        "state": data.get("current_state", "unknown")
                    })
                except Exception:
                    continue
        return snapshots
    
    def clear_state(self):
        """Clear all saved state"""
        try:
            if self.current_snapshot_file.exists():
                self.current_snapshot_file.unlink()
            
            for snap in self.snapshots_dir.glob("snap_*.json"):
                snap.unlink()
            
            logger.info("All saved states cleared")
        except Exception as e:
            logger.error(f"Failed to clear states: {e}")
    
    def save_task_progress(self, task_id: str, progress_data: Dict[str, Any]):
        """Save task-specific progress"""
        task_file = self.state_dir / "tasks" / f"{task_id}.json"
        task_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(task_file, "w") as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save task progress: {e}")
    
    def load_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load task-specific progress"""
        task_file = self.state_dir / "tasks" / f"{task_id}.json"
        
        if not task_file.exists():
            return None
        
        try:
            with open(task_file, "r") as f:
                return json.load(f)
        except Exception:
            return None