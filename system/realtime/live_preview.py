"""
NOVARYX - Live Preview Manager
Syncs generated files to a live preview that updates in real-time.

Connected to:
  - WebSocket Server (broadcasts updates)
  - E2E Pipeline (hooks into generation)
  - Project Builder (writes files)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .websocket_server import WebSocketServer

logger = logging.getLogger("novaryx.live_preview")


class LivePreviewManager:
    """
    Manages live preview during generation.
    
    Hooks into the generation pipeline and:
    - Streams progress to browser via WebSocket
    - Writes files incrementally for hot-reload
    - Tracks which files have been updated
    """
    
    def __init__(self, websocket_server: WebSocketServer = None, preview_dir: str = None):
        self.ws = websocket_server or WebSocketServer()
        
        if preview_dir is None:
            preview_dir = str(Path.home() / "novaryx" / "preview")
        self.preview_dir = Path(preview_dir)
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_generation_id: Optional[str] = None
        self.files_generated: List[str] = []
        self.generation_active = False
        
        logger.info(f"LivePreview initialized: {self.preview_dir}")
    
    def start_generation(self, generation_id: str, project_name: str, total_phases: int):
        """Signal start of a new generation"""
        self.current_generation_id = generation_id
        self.files_generated = []
        self.generation_active = True
        
        self.ws.broadcast("generation.start", {
            "generation_id": generation_id,
            "project": project_name,
            "total_phases": total_phases,
        })
        
        logger.info(f"Live preview started: {project_name}")
    
    def on_phase_start(self, phase_name: str, phase_num: int, total: int):
        """Called when a phase starts"""
        self.ws.broadcast_phase_start(phase_name, phase_num, total)
    
    def on_phase_complete(self, phase_name: str, result: Dict = None):
        """Called when a phase completes"""
        self.ws.broadcast_phase_complete(phase_name, result)
    
    def on_file_generated(self, filepath: str, content: str):
        """Called when a file is generated"""
        
        # Write to preview directory
        full_path = self.preview_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.files_generated.append(filepath)
        
        # Broadcast
        self.ws.broadcast_file_generated(filepath, len(content))
    
    def on_component_selected(self, component_name: str, slot: str):
        """Called when a component is selected"""
        self.ws.broadcast_component(component_name, slot)
    
    def on_agent_status(self, agent_id: str, status: str, task: str = ""):
        """Called when agent status changes"""
        self.ws.broadcast_agent_status(agent_id, status, task)
    
    def on_error(self, error: str, phase: str = ""):
        """Called when an error occurs"""
        self.ws.broadcast_error(error, phase)
    
    def complete_generation(self, project_name: str):
        """Signal generation complete"""
        self.generation_active = False
        self.ws.broadcast_complete(project_name, len(self.files_generated))
        
        logger.info(f"Live preview complete: {project_name} ({len(self.files_generated)} files)")
    
    def get_preview_url(self) -> str:
        """Get the preview URL"""
        return f"http://localhost:3000"
    
    def get_generated_files(self) -> List[Dict]:
        """Get list of generated files with metadata"""
        files = []
        for filepath in self.files_generated:
            full_path = self.preview_dir / filepath
            if full_path.exists():
                files.append({
                    "path": filepath,
                    "size": full_path.stat().st_size,
                    "type": filepath.split(".")[-1] if "." in filepath else "unknown",
                })
        return files
    
    def get_status(self) -> Dict[str, Any]:
        """Get current preview status"""
        return {
            "active": self.generation_active,
            "generation_id": self.current_generation_id,
            "files_count": len(self.files_generated),
            "preview_dir": str(self.preview_dir),
            "preview_url": self.get_preview_url(),
            "recent_files": self.files_generated[-10:] if self.files_generated else [],
        }
    
    def cleanup_preview(self):
        """Clean up preview directory"""
        if self.preview_dir.exists():
            import shutil
            shutil.rmtree(self.preview_dir)
            self.preview_dir.mkdir()
        self.files_generated = []
        logger.info("Preview cleaned up")