"""
NOVARYX - Checkpoint Manager
Creates named checkpoints during generation for precise rollback.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger("novaryx.checkpoint")


class CheckpointManager:
    """Manages generation checkpoints for granular recovery"""
    
    def __init__(self, state_dir: str = None):
        if state_dir is None:
            state_dir = str(Path.home() / "novaryx" / "state" / "checkpoints")
        self.checkpoint_dir = Path(state_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints: Dict[str, Dict] = {}
    
    def create_checkpoint(
        self,
        generation_id: str,
        name: str,
        files: Dict[str, str] = None,
        metadata: Dict = None
    ) -> str:
        """Create a named checkpoint"""
        
        checkpoint_id = f"{generation_id}_{name}_{datetime.now().strftime('%H%M%S')}"
        checkpoint_path = self.checkpoint_dir / generation_id
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "generation_id": generation_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "file_count": len(files) if files else 0,
        }
        
        # Save files if provided
        if files:
            files_dir = checkpoint_path / f"{name}_files"
            files_dir.mkdir(exist_ok=True)
            for filepath, content in files.items():
                full_path = files_dir / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
            checkpoint_data["files_dir"] = str(files_dir)
        
        # Save checkpoint metadata
        meta_path = checkpoint_path / f"{name}_checkpoint.json"
        with open(meta_path, "w") as f:
            json.dump(checkpoint_data, f, indent=2)
        
        self.checkpoints[checkpoint_id] = checkpoint_data
        
        logger.info(f"Checkpoint created: {name} ({checkpoint_data['file_count']} files)")
        return checkpoint_id
    
    def restore_checkpoint(self, generation_id: str, name: str) -> Optional[Dict[str, str]]:
        """Restore files from a checkpoint"""
        
        checkpoint_path = self.checkpoint_dir / generation_id
        files_dir = checkpoint_path / f"{name}_files"
        
        if not files_dir.exists():
            logger.warning(f"Checkpoint not found: {name}")
            return None
        
        files = {}
        for file_path in files_dir.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(files_dir))
                with open(file_path, "r", encoding="utf-8") as f:
                    files[rel_path] = f.read()
        
        logger.info(f"Checkpoint restored: {name} ({len(files)} files)")
        return files
    
    def list_checkpoints(self, generation_id: str) -> List[Dict]:
        """List all checkpoints for a generation"""
        checkpoint_path = self.checkpoint_dir / generation_id
        
        if not checkpoint_path.exists():
            return []
        
        checkpoints = []
        for meta_file in sorted(checkpoint_path.glob("*_checkpoint.json"), reverse=True):
            with open(meta_file, "r") as f:
                data = json.load(f)
            checkpoints.append({
                "id": data.get("checkpoint_id", ""),
                "name": data.get("name", ""),
                "created": data.get("created_at", ""),
                "files": data.get("file_count", 0),
            })
        
        return checkpoints
    
    def cleanup_checkpoints(self, generation_id: str, keep_latest: int = 3):
        """Keep only the most recent checkpoints"""
        checkpoints = self.list_checkpoints(generation_id)
        
        if len(checkpoints) <= keep_latest:
            return
        
        for cp in checkpoints[keep_latest:]:
            cp_path = self.checkpoint_dir / generation_id / f"{cp['name']}_checkpoint.json"
            if cp_path.exists():
                cp_path.unlink()
            
            files_dir = self.checkpoint_dir / generation_id / f"{cp['name']}_files"
            if files_dir.exists():
                import shutil
                shutil.rmtree(files_dir)
        
        logger.info(f"Cleaned up {len(checkpoints) - keep_latest} old checkpoints")