"""
NOVARYX - Task Definitions
Standardized task and step tracking for the orchestrator.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json


class TaskStatus(Enum):
    """Status of a generation task"""
    PENDING = "pending"
    PARSING = "parsing"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    GENERATING = "generating"
    VERIFYING = "verifying"
    REPAIRING = "repairing"
    PACKAGING = "packaging"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStep(Enum):
    """Individual steps in the generation pipeline"""
    PARSE_PROMPT = "parse_prompt"
    DOMAIN_UNDERSTANDING = "domain_understanding"
    PLAN_ARCHITECTURE = "plan_architecture"
    GENERATE_BLUEPRINT = "generate_blueprint"
    RETRIEVE_TEMPLATES = "retrieve_templates"
    RETRIEVE_COMPONENTS = "retrieve_components"
    GENERATE_BACKEND = "generate_backend"
    GENERATE_ROUTES = "generate_routes"
    GENERATE_LAYOUT = "generate_layout"
    GENERATE_SHARED_COMPONENTS = "generate_shared_components"
    GENERATE_PAGES = "generate_pages"
    GENERATE_API = "generate_api"
    ASSEMBLE_PROJECT = "assemble_project"
    VERIFY_SYNTAX = "verify_syntax"
    VERIFY_IMPORTS = "verify_imports"
    VERIFY_TYPES = "verify_types"
    VERIFY_ROUTES = "verify_routes"
    VERIFY_BUILD = "verify_build"
    REPAIR_ISSUES = "repair_issues"
    PACKAGE_OUTPUT = "package_output"
    DEPLOY_LOCAL = "deploy_local"
    GENERATE_DOCS = "generate_docs"
    COMPLETE = "complete"


@dataclass
class StepResult:
    """Result of a single pipeline step"""
    step: TaskStep
    status: str  # "success", "failed", "skipped"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step.value,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "output": self.output,
            "error": self.error,
            "retry_count": self.retry_count
        }


@dataclass
class GenerationTask:
    """
    Complete generation task with full state tracking.
    This is the primary data structure passed through the pipeline.
    """
    
    # Core identification
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: datetime = field(default_factory=datetime.now)
    
    # Input
    user_prompt: str = ""
    project_spec: Optional[Dict[str, Any]] = None
    mode: str = "balanced"  # lite, balanced, deep
    
    # Status tracking
    status: TaskStatus = TaskStatus.PENDING
    current_step: Optional[TaskStep] = None
    steps_completed: List[StepResult] = field(default_factory=list)
    steps_remaining: List[TaskStep] = field(default_factory=list)
    
    # Generation context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Output
    output_dir: Optional[str] = None
    generated_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metrics
    total_generation_time_ms: float = 0.0
    repair_attempts: int = 0
    max_repair_attempts: int = 3
    
    def __post_init__(self):
        # Configure dynamically based on mode
        if self.mode == "lite":
            self.max_repair_attempts = 1
        elif self.mode == "deep":
            self.max_repair_attempts = 3
        else:
            self.max_repair_attempts = 2
    
    # Project specific
    project_name: Optional[str] = None
    project_type: Optional[str] = None
    
    def get_progress_percentage(self) -> float:
        """Calculate completion percentage"""
        total_steps = len(self.steps_completed) + len(self.steps_remaining)
        if total_steps == 0:
            return 0.0
        return (len(self.steps_completed) / total_steps) * 100
    
    def add_step_result(self, result: StepResult):
        """Record a completed step"""
        self.steps_completed.append(result)
        if result.status == "failed":
            self.errors.append(f"{result.step.value}: {result.error}")
    
    def can_repair(self) -> bool:
        """Check if more repair attempts are allowed"""
        return self.repair_attempts < self.max_repair_attempts
    
    def needs_repair(self) -> bool:
        """Check if any step failed"""
        return any(r.status == "failed" for r in self.steps_completed)
    
    def is_complete(self) -> bool:
        """Check if task is finished"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "created_at": self.created_at.isoformat(),
            "user_prompt": self.user_prompt[:200],
            "mode": self.mode,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "status": self.status.value,
            "current_step": self.current_step.value if self.current_step else None,
            "progress": f"{self.get_progress_percentage():.0f}%",
            "steps_completed": len(self.steps_completed),
            "steps_remaining": len(self.steps_remaining),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "repair_attempts": self.repair_attempts,
            "generated_files": len(self.generated_files)
        }
    
    def display_progress(self):
        """Display current task progress"""
        print("\n" + "=" * 60)
        print(f"📋 TASK: {self.task_id}")
        print("=" * 60)
        print(f"   Project: {self.project_name or 'Unknown'}")
        print(f"   Type: {self.project_type or 'Unknown'}")
        print(f"   Status: {self.status.value.upper()}")
        print(f"   Progress: {self.get_progress_percentage():.0f}%")
        print(f"   Current Step: {self.current_step.value if self.current_step else 'None'}")
        print(f"   Completed: {len(self.steps_completed)} steps")
        print(f"   Errors: {len(self.errors)}")
        print(f"   Repairs: {self.repair_attempts}/{self.max_repair_attempts}")
        
        if self.steps_completed:
            print(f"\n   Steps:")
            for step in self.steps_completed[-5:]:  # Last 5 steps
                icon = "✅" if step.status == "success" else "❌" if step.status == "failed" else "⏭️"
                print(f"      {icon} {step.step.value}")
        
        print("=" * 60 + "\n")


class TaskSerializer:
    """Save and load tasks to/from disk"""
    
    @staticmethod
    def save(task: GenerationTask, filepath: str):
        """Save task state to JSON"""
        data = {
            "task_id": task.task_id,
            "created_at": task.created_at.isoformat(),
            "user_prompt": task.user_prompt,
            "mode": task.mode,
            "project_spec": task.project_spec,
            "status": task.status.value,
            "current_step": task.current_step.value if task.current_step else None,
            "steps_completed": [s.to_dict() for s in task.steps_completed],
            "steps_remaining": [s.value for s in task.steps_remaining],
            "context": task.context,
            "output_dir": task.output_dir,
            "generated_files": task.generated_files,
            "errors": task.errors,
            "warnings": task.warnings,
            "repair_attempts": task.repair_attempts,
            "max_repair_attempts": task.max_repair_attempts,
            "project_name": task.project_name,
            "project_type": task.project_type
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load(filepath: str) -> Optional[GenerationTask]:
        """Load task state from JSON"""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            task = GenerationTask(
                task_id=data.get("task_id", ""),
                user_prompt=data.get("user_prompt", ""),
                project_spec=data.get("project_spec"),
                project_name=data.get("project_name"),
                project_type=data.get("project_type"),
                mode=data.get("mode", "balanced")
            )
            
            task.status = TaskStatus(data.get("status", "pending"))
            task.current_step = TaskStep(data["current_step"]) if data.get("current_step") else None
            task.steps_remaining = [TaskStep(s) for s in data.get("steps_remaining", [])]
            task.context = data.get("context", {})
            task.output_dir = data.get("output_dir")
            task.generated_files = data.get("generated_files", [])
            task.errors = data.get("errors", [])
            task.warnings = data.get("warnings", [])
            task.repair_attempts = data.get("repair_attempts", 0)
            task.max_repair_attempts = data.get("max_repair_attempts", 3)
            
            # Rebuild step results
            for step_data in data.get("steps_completed", []):
                result = StepResult(
                    step=TaskStep(step_data["step"]),
                    status=step_data["status"]
                )
                if step_data.get("started_at"):
                    result.started_at = datetime.fromisoformat(step_data["started_at"])
                if step_data.get("completed_at"):
                    result.completed_at = datetime.fromisoformat(step_data["completed_at"])
                result.output = step_data.get("output")
                result.error = step_data.get("error")
                result.retry_count = step_data.get("retry_count", 0)
                task.steps_completed.append(result)
            
            return task
            
        except Exception as e:
            import logging
            logging.getLogger("novaryx.task").error(f"Failed to load task: {e}")
            return None