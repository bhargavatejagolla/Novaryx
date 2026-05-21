"""
NOVARYX - Generation State
Tracks every phase of generation with full serialization.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger("novaryx.state")


class PhaseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PhaseState:
    """State of a single generation phase"""
    phase_name: str
    status: PhaseStatus = PhaseStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    
    def start(self):
        self.status = PhaseStatus.IN_PROGRESS
        self.started_at = datetime.now().isoformat()
    
    def complete(self, data: Dict = None):
        self.status = PhaseStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        if data:
            self.data.update(data)
        if self.started_at:
            start = datetime.fromisoformat(self.started_at)
            self.duration_seconds = (datetime.now() - start).total_seconds()
    
    def fail(self, error: str):
        self.status = PhaseStatus.FAILED
        self.errors.append(error)
        self.completed_at = datetime.now().isoformat()
    
    def warn(self, warning: str):
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict:
        return {
            "phase": self.phase_name,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "data_keys": list(self.data.keys()),
            "errors": self.errors,
            "warnings": self.warnings,
            "duration": f"{self.duration_seconds:.1f}s"
        }


@dataclass
class GenerationState:
    """Complete generation state across all phases"""
    
    # Identity
    generation_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    project_name: str = ""
    prompt: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Phase tracking
    phases: Dict[str, PhaseState] = field(default_factory=dict)
    current_phase: str = ""
    total_phases: int = 0
    completed_phases: int = 0
    
    # Data storage
    design_system_data: Optional[Dict] = None
    layout_data: Optional[Dict] = None
    component_selections: Optional[Dict] = None
    generated_files: Optional[Dict[str, str]] = None
    backend_schema: Optional[Dict] = None
    
    # Metadata
    version: str = "2.6.0"
    resumed: bool = False
    resume_count: int = 0
    last_saved: str = ""
    
    def init_phases(self, phase_names: List[str]):
        """Initialize all phases as pending"""
        self.total_phases = len(phase_names)
        for name in phase_names:
            self.phases[name] = PhaseState(phase_name=name)
    
    def start_phase(self, phase_name: str):
        """Mark a phase as in progress"""
        if phase_name in self.phases:
            self.phases[phase_name].start()
        else:
            self.phases[phase_name] = PhaseState(phase_name=phase_name)
            self.phases[phase_name].start()
        self.current_phase = phase_name
    
    def complete_phase(self, phase_name: str, data: Dict = None):
        """Mark a phase as completed"""
        if phase_name in self.phases:
            self.phases[phase_name].complete(data)
            self.completed_phases += 1
    
    def fail_phase(self, phase_name: str, error: str):
        """Mark a phase as failed"""
        if phase_name in self.phases:
            self.phases[phase_name].fail(error)
    
    def get_progress(self) -> float:
        """Get overall progress percentage"""
        if self.total_phases == 0:
            return 0.0
        return (self.completed_phases / self.total_phases) * 100
    
    def get_next_pending_phase(self) -> Optional[str]:
        """Get the next phase that hasn't been completed"""
        for name, phase in self.phases.items():
            if phase.status in [PhaseStatus.PENDING, PhaseStatus.FAILED]:
                return name
        return None
    
    def get_failed_phases(self) -> List[str]:
        """Get list of failed phases"""
        return [name for name, p in self.phases.items() if p.status == PhaseStatus.FAILED]
    
    def to_dict(self) -> Dict:
        return {
            "generation_id": self.generation_id,
            "project_name": self.project_name,
            "prompt": self.prompt[:100],
            "version": self.version,
            "resumed": self.resumed,
            "resume_count": self.resume_count,
            "progress": f"{self.get_progress():.0f}%",
            "current_phase": self.current_phase,
            "phases": {name: p.to_dict() for name, p in self.phases.items()},
            "has_design": self.design_system_data is not None,
            "has_layout": self.layout_data is not None,
            "has_components": self.component_selections is not None,
            "has_files": self.generated_files is not None,
            "has_backend": self.backend_schema is not None,
            "last_saved": self.last_saved,
        }
    
    def display(self):
        """Display current state"""
        print("\n" + "=" * 60)
        print(f"📊 GENERATION STATE: {self.generation_id}")
        print("=" * 60)
        print(f"   Project: {self.project_name or 'Unnamed'}")
        print(f"   Progress: {self.get_progress():.0f}%")
        print(f"   Current: {self.current_phase or 'Not started'}")
        print(f"   Resumed: {'Yes' if self.resumed else 'No'}")
        
        for name, phase in self.phases.items():
            icons = {
                PhaseStatus.COMPLETED: "✅",
                PhaseStatus.IN_PROGRESS: "🔄",
                PhaseStatus.FAILED: "❌",
                PhaseStatus.PENDING: "⏳",
                PhaseStatus.SKIPPED: "⏭️",
            }
            icon = icons.get(phase.status, "❓")
            dur = f" ({phase.duration_seconds:.1f}s)" if phase.duration_seconds > 0 else ""
            print(f"   {icon} {name}: {phase.status.value}{dur}")
        
        print("=" * 60)


class StateManager:
    """Manages saving and loading generation state"""
    
    def __init__(self, state_dir: str = None):
        if state_dir is None:
            state_dir = str(Path.home() / "novaryx" / "state")
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.current_state: Optional[GenerationState] = None
    
    def create_state(self, prompt: str, project_name: str = "") -> GenerationState:
        """Create a new generation state"""
        state = GenerationState(
            prompt=prompt,
            project_name=project_name
        )
        
        state.init_phases([
            "intent_parsing",
            "design_system",
            "layout_selection",
            "component_selection",
            "3d_selection",
            "animation_config",
            "page_generation",
            "backend_generation",
            "theme_adaptation",
            "verification",
            "repair",
            "packaging",
        ])
        
        self.current_state = state
        self.save()
        
        logger.info(f"Created state: {state.generation_id}")
        return state
    
    def save(self) -> bool:
        """Save current state to disk"""
        if not self.current_state:
            return False
        
        try:
            self.current_state.last_saved = datetime.now().isoformat()
            
            state_file = self.state_dir / f"{self.current_state.generation_id}.json"
            
            # Build serializable data
            data = {
                "meta": {
                    "generation_id": self.current_state.generation_id,
                    "project_name": self.current_state.project_name,
                    "prompt": self.current_state.prompt,
                    "created_at": self.current_state.created_at,
                    "version": self.current_state.version,
                    "resumed": self.current_state.resumed,
                    "resume_count": self.current_state.resume_count,
                    "current_phase": self.current_state.current_phase,
                    "total_phases": self.current_state.total_phases,
                    "completed_phases": self.current_state.completed_phases,
                    "last_saved": self.current_state.last_saved,
                },
                "phases": {
                    name: {
                        "status": phase.status.value,
                        "started_at": phase.started_at,
                        "completed_at": phase.completed_at,
                        "errors": phase.errors,
                        "warnings": phase.warnings,
                        "duration_seconds": phase.duration_seconds,
                    }
                    for name, phase in self.current_state.phases.items()
                },
                "data": {
                    "design_system": self.current_state.design_system_data,
                    "layout": self.current_state.layout_data,
                    "components": self.current_state.component_selections,
                    "backend": self.current_state.backend_schema,
                }
            }
            
            with open(state_file, "w") as f:
                json.dump(data, f, indent=2)
            
            # Also update active state pointer
            active_file = self.state_dir / "active_state.json"
            with open(active_file, "w") as f:
                json.dump({
                    "active_id": self.current_state.generation_id,
                    "project_name": self.current_state.project_name,
                    "progress": f"{self.current_state.get_progress():.0f}%",
                    "last_saved": self.current_state.last_saved,
                }, f, indent=2)
            
            logger.debug(f"State saved: {self.current_state.generation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False
    
    def load(self, generation_id: str = None) -> Optional[GenerationState]:
        """Load state from disk"""
        
        # If no ID, load the active state
        if generation_id is None:
            active_file = self.state_dir / "active_state.json"
            if active_file.exists():
                with open(active_file, "r") as f:
                    active = json.load(f)
                generation_id = active.get("active_id")
            
            if not generation_id:
                # Find most recent state file
                state_files = sorted(
                    self.state_dir.glob("*.json"),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                for sf in state_files:
                    if sf.name not in ["active_state.json"]:
                        generation_id = sf.stem
                        break
        
        if not generation_id:
            return None
        
        state_file = self.state_dir / f"{generation_id}.json"
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
            
            meta = data.get("meta", {})
            phases_data = data.get("phases", {})
            saved_data = data.get("data", {})
            
            state = GenerationState(
                generation_id=meta.get("generation_id", generation_id),
                project_name=meta.get("project_name", ""),
                prompt=meta.get("prompt", ""),
                created_at=meta.get("created_at", ""),
                version=meta.get("version", "2.6.0"),
                resumed=True,
                resume_count=meta.get("resume_count", 0) + 1,
                current_phase=meta.get("current_phase", ""),
                total_phases=meta.get("total_phases", 0),
                completed_phases=meta.get("completed_phases", 0),
            )
            
            # Restore phases
            for name, pdata in phases_data.items():
                phase = PhaseState(phase_name=name)
                phase.status = PhaseStatus(pdata.get("status", "pending"))
                phase.started_at = pdata.get("started_at")
                phase.completed_at = pdata.get("completed_at")
                phase.errors = pdata.get("errors", [])
                phase.warnings = pdata.get("warnings", [])
                phase.duration_seconds = pdata.get("duration_seconds", 0)
                state.phases[name] = phase
            
            # Restore data
            state.design_system_data = saved_data.get("design_system")
            state.layout_data = saved_data.get("layout")
            state.component_selections = saved_data.get("components")
            state.backend_schema = saved_data.get("backend")
            
            self.current_state = state
            
            logger.info(f"State loaded: {generation_id} (resume #{state.resume_count})")
            return state
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None
    
    def list_saved_states(self) -> List[Dict]:
        """List all saved generation states"""
        states = []
        for sf in sorted(self.state_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            if sf.name == "active_state.json":
                continue
            try:
                with open(sf, "r") as f:
                    data = json.load(f)
                meta = data.get("meta", {})
                states.append({
                    "id": meta.get("generation_id", sf.stem),
                    "project": meta.get("project_name", "Unknown"),
                    "progress": f"{meta.get('completed_phases', 0)}/{meta.get('total_phases', 0)}",
                    "phase": meta.get("current_phase", ""),
                    "saved": meta.get("last_saved", ""),
                })
            except Exception:
                pass
        return states
    
    def cleanup_old_states(self, max_age_days: int = 7):
        """Remove state files older than specified days"""
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)
        for sf in self.state_dir.glob("*.json"):
            if sf.name == "active_state.json":
                continue
            if sf.stat().st_mtime < cutoff:
                sf.unlink()
                logger.info(f"Cleaned up old state: {sf.name}")