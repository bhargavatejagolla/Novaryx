"""
NOVARYX - Autonomous Dependency Governor
Orchestrates dependency integrity, stack enforcement, and pre-build validation.
"""

import logging
import json
import re
from typing import Dict, List, Any, Set
from system.intelligence.stack_profiles import get_stack_profile
from system.verification.dependency_checker import DependencyChecker

logger = logging.getLogger("novaryx.dependency_governor")

class DependencyGovernor:
    """
    Governor for project-wide dependency integrity.
    Checks for missing packages, enforces stack versions, and repairs package.json.
    """
    
    def __init__(self):
        self.checker = DependencyChecker()
        
    def govern_project(self, files: Dict[str, str], project_type: str = "vite_react") -> Dict[str, str]:
        """
        Main entry point for dependency governance.
        Modifies files (primarily package.json) to ensure integrity.
        """
        if "package.json" not in files:
            logger.warning("No package.json found in project files. Skipping governance.")
            return files
            
        working_files = files.copy()
        pkg_json_content = working_files["package.json"]
        
        # 1. Stack Normalization (Inforce baseline dependencies)
        profile = get_stack_profile(project_type)
        updated_pkg_json = self._enforce_stack(pkg_json_content, profile)
        
        # 2. Heuristic Discovery (Scan imports for missing deps)
        missing_pkgs = []
        errors = self.checker.check_missing_packages(working_files, updated_pkg_json)
        for err in errors:
            if "is imported but not defined" in err["message"]:
                # Extract package name from message (heuristic)
                match = re.search(r"Module (.*) is imported", err["message"])
                if match:
                    missing_pkgs.append(match.group(1))
        
        # 3. Apply Repairs
        if missing_pkgs:
            logger.info(f"Discovery found missing packages: {missing_pkgs}")
            updated_pkg_json = self.checker.repair_package_json(updated_pkg_json, missing_pkgs)
            
        working_files["package.json"] = updated_pkg_json
        return working_files

    def _enforce_stack(self, package_json: str, profile: Dict[str, Any]) -> str:
        """
        Merge mandatory stack dependencies into package.json.
        """
        try:
            data = json.loads(package_json)
            
            # Ensure keys exist
            if "dependencies" not in data: data["dependencies"] = {}
            if "devDependencies" not in data: data["devDependencies"] = {}
            
            # Merit merge: keep existing version if provided, otherwise use profile's stable version
            for pkg, version in profile["dependencies"].items():
                if pkg not in data["dependencies"] and pkg not in data["devDependencies"]:
                    data["dependencies"][pkg] = version
                    
            for pkg, version in profile["devDependencies"].items():
                if pkg not in data["dependencies"] and pkg not in data["devDependencies"]:
                    data["devDependencies"][pkg] = version
            
            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Stack enforcement failed: {e}")
            return package_json
            
    def validate_integrity(self, files: Dict[str, str]) -> List[str]:
        """
        High-level integrity check. Returns list of warning/error messages.
        """
        if "package.json" not in files:
            return ["CRITICAL: Missing package.json"]
            
        errors = self.checker.check_missing_packages(files, files["package.json"])
        return [e["message"] for e in errors]
