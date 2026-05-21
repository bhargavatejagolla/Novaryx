"""
NOVARYX - Dependency Checker
Validates module dependencies, circular imports, and package alignment.
"""

import re
import logging
from typing import Dict, List, Set, Tuple

logger = logging.getLogger("novaryx.dependency_checker")

class DependencyChecker:
    """
    Checks for structural dependency issues in generated code.
    """
    
    def __init__(self):
        self.import_pattern = re.compile(r"import\s+.*\s+from\s+['\"](.*)['\"]")
        
    def check_circular_dependencies(self, files: Dict[str, str]) -> List[Dict]:
        """
        Detect recursive imports (A -> B -> A).
        Simplified version focusing on page-component boundaries.
        """
        errors = []
        # Pages should not import each other usually
        # Components should not import pages
        
        for path, content in files.items():
            if "src/components/" in path:
                # Component importing a page is a violation in NOVARYX architecture
                if "import" in content and "from '../pages/" in content:
                    errors.append({
                        "file": path,
                        "type": "dependency_violation",
                        "message": "Architectural Violation: Component cannot import from pages.",
                        "severity": "error"
                    })
                    
        return errors

    def check_missing_packages(self, files: Dict[str, str], package_json: str) -> List[Dict]:
        """
        Check if imported external packages are in package.json.
        """
        errors = []
        if not package_json:
            return errors
            
        try:
            import json
            pkg_data = json.loads(package_json)
            deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
            
            # Common built-in or peer deps to ignore
            ignore = {"react", "react-dom", "lucide-react", "framer-motion", "@/lib/utils", "clsx", "tailwind-merge"}
            
            for path, content in files.items():
                if not path.endswith((".tsx", ".ts", ".js", ".mjs")):
                    continue
                
                # Special case: Scan vite.config.js for plugins
                if "vite.config" in path:
                    # Also look for require('@vitejs/plugin-react') patterns
                    require_matches = re.findall(r"require\(['\"](.*)['\"]\)", content)
                    imports = self.import_pattern.findall(content) + require_matches
                else:
                    imports = self.import_pattern.findall(content)
                
                for imp in imports:
                    if imp.startswith((".", "@/", "http")):
                        continue
                        
                    # Extract root package name (e.g. lodash/fp -> lodash)
                    pkg_name = imp.split("/")[0]
                    if pkg_name.startswith("@"): # handle scoped packages
                        parts = imp.split("/")
                        if len(parts) >= 2:
                            pkg_name = f"{parts[0]}/{parts[1]}"
                            
                    if pkg_name not in deps and pkg_name not in ignore:
                        errors.append({
                            "file": path,
                            "type": "missing_package",
                            "message": f"Module {pkg_name} is imported but not defined in package.json",
                            "severity": "warning"
                        })
        except Exception as e:
            logger.debug(f"Missing package check failed: {e}")
            
        return errors

    def repair_package_json(self, package_json: str, missing_pkgs: List[str]) -> str:
        """
        Inject missing packages into package.json with semantic compatibility.
        """
        import json
        from system.intelligence.stack_profiles import resolve_compatible_version
        try:
            data = json.loads(package_json)
            if "devDependencies" not in data:
                data["devDependencies"] = {}
                
            # Determine parent stack (usually vite)
            parent_pkg = "vite"
            parent_version = data.get("devDependencies", {}).get("vite", 
                            data.get("dependencies", {}).get("vite", "5.1.0"))
            
            for pkg in missing_pkgs:
                if pkg not in data.get("dependencies", {}) and pkg not in data["devDependencies"]:
                    # Resolve compatible version based on stack
                    version = resolve_compatible_version(pkg, parent_pkg, parent_version)
                    data["devDependencies"][pkg] = version
                    logger.info(f"Surgically added {pkg}@{version} to devDependencies (compatible with {parent_pkg}@{parent_version})")
                    
            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Failed to repair package.json: {e}")
            return package_json
