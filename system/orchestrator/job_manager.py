"""
NOVARYX - Job Manager (Phase 1)
Handles generation job IDs, state checkpointing, and resumption.
Prevents data loss on disconnects by serializing state to disk.
"""

import os
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("novaryx.job_manager")

class JobManager:
    def __init__(self, projects_dir: str = None):
        if not projects_dir:
            self.projects_dir = Path(os.getcwd()) / "projects"
        else:
            self.projects_dir = Path(projects_dir)
            
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        
    def create_job(self, prompt: str, mode: str = "balanced") -> str:
        """Creates a new job ID and initializes its state."""
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job_dir = self.projects_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        initial_state = {
            "job_id": job_id,
            "prompt": prompt,
            "mode": mode,
            "status": "initialized",
            "current_step": "PARSE_PROMPT",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "context": {},
            "generated_files": {},
            "errors": []
        }
        
        self.save_checkpoint(job_id, initial_state)
        logger.info(f"Created new generation job: {job_id}")
        return job_id
        
    def save_checkpoint(self, job_id: str, state: Dict[str, Any]) -> bool:
        """Serializes the current generation state to disk."""
        checkpoint_path = self.projects_dir / job_id / "checkpoint.json"
        
        # Ensure updated_at is refreshed
        state["updated_at"] = datetime.now().isoformat()
        
        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            logger.debug(f"Saved checkpoint for job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save checkpoint for {job_id}: {e}")
            return False
            
    def load_checkpoint(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Loads a generation state from disk for resumption."""
        checkpoint_path = self.projects_dir / job_id / "checkpoint.json"
        
        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found for job: {job_id}")
            return None
            
        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            logger.info(f"Successfully loaded checkpoint for {job_id}. Status: {state.get('status')}")
            return state
        except Exception as e:
            logger.error(f"Failed to load checkpoint for {job_id}: {e}")
            return None
            
    def list_jobs(self) -> List[Dict[str, Any]]:
        """Returns a list of all jobs and their current status."""
        jobs = []
        if not self.projects_dir.exists():
            return jobs
            
        for job_dir in self.projects_dir.iterdir():
            if job_dir.is_dir():
                state = self.load_checkpoint(job_dir.name)
                if state:
                    jobs.append({
                        "job_id": state.get("job_id"),
                        "status": state.get("status"),
                        "current_step": state.get("current_step"),
                        "updated_at": state.get("updated_at")
                    })
        
        # Sort by most recent first
        return sorted(jobs, key=lambda x: x.get("updated_at", ""), reverse=True)
