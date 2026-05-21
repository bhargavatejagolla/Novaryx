"""
NOVARYX - Preview Panel
Manages the live preview of generated projects.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("novaryx.preview_panel")


class PreviewPanel:
    """Manages project preview"""
    
    def __init__(self):
        self.preview_dir = Path.home() / "novaryx" / "preview"
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        self.current_project: Optional[str] = None
        self.is_running = False
    
    def start_preview(self, project_name: str, files: Dict[str, str]):
        """Start preview with generated files"""
        self.current_project = project_name
        self.is_running = True
        
        # Write files to preview directory
        for filepath, content in files.items():
            full_path = self.preview_dir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        
        logger.info(f"Preview started: {project_name} ({len(files)} files)")
    
    def update_file(self, filepath: str, content: str):
        """Update a single file in preview"""
        full_path = self.preview_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def get_preview_url(self) -> str:
        """Get preview URL"""
        return "http://localhost:3000"
    
    def get_status(self) -> Dict:
        """Get preview status"""
        files = []
        if self.preview_dir.exists():
            for f in self.preview_dir.rglob("*"):
                if f.is_file():
                    files.append({
                        "path": str(f.relative_to(self.preview_dir)),
                        "size": f.stat().st_size,
                    })
        
        return {
            "running": self.is_running,
            "project": self.current_project,
            "url": self.get_preview_url(),
            "files_count": len(files),
            "files": files[:20],
        }
    
    def stop_preview(self):
        """Stop preview"""
        self.is_running = False
        logger.info("Preview stopped")
        