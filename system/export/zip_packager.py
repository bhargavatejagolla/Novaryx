"""
NOVARYX - ZIP Packager
Creates production-ready ZIP archives of generated projects.
"""

import zipfile
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger("novaryx.zip_packager")


class ZipPackager:
    """Creates ZIP archives for download/deployment"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = str(Path.home() / "novaryx" / "exports")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_zip(self, files: Dict[str, str], project_name: str) -> str:
        """
        Create a ZIP archive from files dict.
        
        Args:
            files: {relative_path: content}
            project_name: Project name for filename
        
        Returns:
            Path to created ZIP file
        """
        slug = project_name.lower().replace(" ", "-")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{slug}_{timestamp}.zip"
        zip_path = self.output_dir / zip_filename
        
        print(f"\n📦 Creating ZIP: {zip_filename}")
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filepath, content in files.items():
                zf.writestr(filepath, content)
        
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Created: {zip_filename} ({size_mb:.1f} MB)")
        print(f"   Location: {zip_path}")
        
        return str(zip_path)
    
    def create_zip_from_dir(self, project_dir: str) -> str:
        """Create ZIP from a directory on disk"""
        project_path = Path(project_dir)
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project directory not found: {project_dir}")
        
        project_name = project_path.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{project_name}_{timestamp}.zip"
        zip_path = self.output_dir / zip_filename
        
        print(f"\n📦 Archiving: {project_name}")
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in project_path.rglob("*"):
                if file_path.is_file():
                    # Skip node_modules and .git
                    if "node_modules" in file_path.parts or ".git" in file_path.parts:
                        continue
                    arcname = str(file_path.relative_to(project_path))
                    zf.write(file_path, arcname)
        
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Created: {zip_filename} ({size_mb:.1f} MB)")
        
        return str(zip_path)
    
    def list_exports(self) -> list:
        """List all exported ZIP files"""
        exports = []
        for zf in sorted(self.output_dir.glob("*.zip"), key=lambda x: x.stat().st_mtime, reverse=True):
            exports.append({
                "name": zf.name,
                "size_mb": round(zf.stat().st_size / (1024 * 1024), 1),
                "created": datetime.fromtimestamp(zf.stat().st_mtime).isoformat(),
            })
        return exports