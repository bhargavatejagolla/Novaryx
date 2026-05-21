"""
NOVARYX - Build Checker
Tests if the project can build successfully.
"""

import subprocess
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

logger = logging.getLogger("novaryx.build_checker")


class BuildChecker:
    """Tests project build"""
    
    def __init__(self):
        self.build_output = ""
        self.build_success = False
    
    def check_build(self, project_dir: str) -> Tuple[bool, str]:
        """
        Attempt to build the project.
        
        Args:
            project_dir: Path to project directory
        
        Returns:
            (success, output)
        """
        project_path = Path(project_dir)
        
        if not project_path.exists():
            return False, f"Project directory not found: {project_dir}"
        
        # Check if node_modules exists
        if not (project_path / "node_modules").exists():
            logger.info("Installing dependencies...")
            try:
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=str(project_path),
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode != 0:
                    return False, f"npm install failed:\n{result.stderr[:500]}"
            except subprocess.TimeoutExpired:
                return False, "npm install timed out"
            except FileNotFoundError:
                return False, "npm not found. Install Node.js"
        
        # Run build
        logger.info("Running build...")
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            self.build_output = result.stdout + "\n" + result.stderr
            self.build_success = result.returncode == 0
            
            if self.build_success:
                return True, "Build successful"
            else:
                # Extract meaningful error
                errors = [l for l in result.stderr.split('\n') if 'error' in l.lower()]
                return False, f"Build failed with {len(errors)} errors:\n" + "\n".join(errors[:5])
                
        except subprocess.TimeoutExpired:
            return False, "Build timed out"
        except Exception as e:
            return False, f"Build check failed: {e}"
    
    def quick_check(self, files: Dict[str, str]) -> Tuple[bool, list]:
        """
        Quick static check without installing/building.
        Checks for common build-breaking issues.
        """
        issues = []
        
        # Check for index.html
        if 'index.html' not in files:
            issues.append("Missing index.html")
        
        # Check for package.json
        if 'package.json' not in files:
            issues.append("Missing package.json")
        
        # Check for main entry
        has_main = any('src/main.tsx' in f or 'src/main.jsx' in f for f in files)
        if not has_main:
            issues.append("Missing entry point (src/main.tsx)")
        
        # Check for App component
        has_app = any('src/App.tsx' in f or 'src/App.jsx' in f for f in files)
        if not has_app:
            issues.append("Missing App component (src/App.tsx)")
        
        return len(issues) == 0, issues