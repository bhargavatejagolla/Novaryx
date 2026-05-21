"""
NOVARYX - Architecture Rule Engine
Enforces structural governance, import boundaries, and naming conventions
before the pipeline touches heavy semantic validation or LLM patching.
"""

import re
import logging
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

logger = logging.getLogger("novaryx.rule_engine")

@dataclass
class ArchitectureViolation:
    file_path: str
    rule_type: str
    message: str
    severity: str = "error"  # error, warning


class ArchitectureRuleEngine:
    """
    Enforces deterministic architectural constraints.
    Prevents cross-contamination (e.g. components importing pages),
    enforces folder layouts, and ensures naming consistency.
    """
    
    ALLOWED_FOLDERS = [
        "src/app", "src/pages", "src/components", "src/layouts", 
        "src/lib", "src/utils", "src/hooks", "src/styles", "src/types",
        "backend", "public"
    ]
    
    # Regex for catching imports: import { X } from 'path'; or import X from "path";
    IMPORT_REGEX = re.compile(r"import\s+(?:(?:\{[^}]*\}|\*\s+as\s+[a-zA-Z0-9_]+|[a-zA-Z0-9_]+)\s*,?\s*)+\s+from\s+['\"](.*?)['\"]", re.MULTILINE)

    def validate_architecture(self, files: Dict[str, str]) -> List[ArchitectureViolation]:
        """Run all architectural governance checks over a file set."""
        violations = []
        
        for file_path, content in files.items():
            if file_path.endswith('.tsx') or file_path.endswith('.ts'):
                violations.extend(self._check_folder_topology(file_path))
                violations.extend(self._check_naming_conventions(file_path))
                violations.extend(self._check_import_boundaries(file_path, content))
                
        return violations

    def _check_folder_topology(self, file_path: str) -> List[ArchitectureViolation]:
        """Ensure files are placed in standardized structural directories."""
        # Top level files like main.tsx, vite.config.js are ignored
        parts = file_path.split('/')
        if len(parts) <= 2:
            return []
            
        is_valid_dir = False
        for allowed in self.ALLOWED_FOLDERS:
            if file_path.startswith(allowed):
                is_valid_dir = True
                break
                
        if not is_valid_dir and file_path.startswith("src/"):
            return [ArchitectureViolation(
                file_path=file_path,
                rule_type="folder_topology",
                message=f"Unauthorized folder structure. Must use standard domains ({', '.join(self.ALLOWED_FOLDERS)})",
                severity="error"
            )]
            
        # New check: Spaces in file names
        if " " in file_path:
            return [ArchitectureViolation(
                file_path=file_path,
                rule_type="naming_convention",
                message=f"Invalid file path: '{file_path}' contains spaces. Use PascalCase or kebab-case.",
                severity="error"
            )]
            
        return []

    def _check_naming_conventions(self, file_path: str) -> List[ArchitectureViolation]:
        """Ensure components/pages are PascalCase and utils are kebab-case."""
        filename = file_path.split('/')[-1]
        name_without_ext = filename.split('.')[0]
        
        # Pages and Components should be PascalCase
        if "src/components/" in file_path or "src/pages/" in file_path or "src/layouts/" in file_path:
            # Basic PascalCase check: starts with capital, no dashes/underscores
            if not name_without_ext[0].isupper() or '-' in name_without_ext or '_' in name_without_ext:
                return [ArchitectureViolation(
                    file_path=file_path,
                    rule_type="naming_convention",
                    message=f"React component/page '{name_without_ext}' must use PascalCase (e.g., UserProfile).",
                    severity="error"
                )]
        
        # Utils/Hooks should typically be camelCase or kebab-case (no Capitals)
        if "src/hooks/" in file_path or "src/utils/" in file_path:
            if name_without_ext[0].isupper():
                return [ArchitectureViolation(
                    file_path=file_path,
                    rule_type="naming_convention",
                    message=f"Hooks and utils '{name_without_ext}' should use camelCase or kebab-case, not PascalCase.",
                    severity="warning"
                )]
        
        return []

    def _check_import_boundaries(self, file_path: str, content: str) -> List[ArchitectureViolation]:
        """
        Enforce strict dependency flow:
        - Pages can import anything.
        - Components can import other components, hooks, utils.
        - Components CANNOT import pages.
        - Utils CANNOT import components.
        """
        violations = []
        imports = self.IMPORT_REGEX.findall(content)
        
        is_component = "src/components/" in file_path
        is_util = "src/utils/" in file_path or "src/hooks/" in file_path
        
        for imp_path in imports:
            # Component constraint
            if is_component:
                if "pages" in imp_path or "app/" in imp_path:
                    violations.append(ArchitectureViolation(
                        file_path=file_path,
                        rule_type="import_boundary",
                        message=f"Circular boundary violation: Component tried to import a Page layer ({imp_path}).",
                        severity="error"
                    ))
            
            # Util constraint
            if is_util:
                if "components" in imp_path or "pages" in imp_path or ".tsx" in imp_path:
                    violations.append(ArchitectureViolation(
                        file_path=file_path,
                        rule_type="import_boundary",
                        message=f"Domain boundary violation: Util/Hook layer tried to import UI layer ({imp_path}).",
                        severity="error"
                    ))

        # New check: Invalid identifiers in imports (e.g. import { User Management })
        # This matches the { ... } block specifically
        identifier_blocks = re.findall(r"import\s+\{(.*?)\}\s+from", content, re.MULTILINE)
        for block in identifier_blocks:
            if " " in block.strip():
                # Split by comma and check each identifier
                identifiers = [i.strip() for i in block.split(",")]
                for ident in identifiers:
                    if " " in ident:
                         violations.append(ArchitectureViolation(
                            file_path=file_path,
                            rule_type="syntax_error",
                            message=f"Invalid import identifier '{ident}': identifiers cannot contain spaces.",
                            severity="error"
                        ))

        return violations
