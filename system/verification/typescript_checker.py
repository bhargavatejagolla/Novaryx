"""
NOVARYX - TypeScript Checker
Validates TypeScript in generated projects.
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("novaryx.ts_checker")


class TypeScriptChecker:
    """Validates TypeScript compilation"""
    
    def __init__(self):
        self.errors: List[dict] = []
        self.warnings: List[dict] = []
    
    def check_file(self, file_path: str, content: str) -> Tuple[bool, List[dict]]:
        """
        Check a single TypeScript file for syntax errors.
        
        Uses basic static analysis since we may not have tsc installed.
        """
        errors = []
        
        # Check 1: Balanced braces and parens
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            errors.append({
                "file": file_path,
                "type": "syntax",
                "message": f"Unbalanced braces: {open_braces} open, {close_braces} close",
                "severity": "error"
            })
        
        open_parens = content.count('(')
        close_parens = content.count(')')
        if open_parens != close_parens:
            errors.append({
                "file": file_path,
                "type": "syntax",
                "message": f"Unbalanced parentheses: {open_parens} open, {close_parens} close",
                "severity": "error"
            })
        
        # Check 2: Interface/type usage
        interfaces = set()
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('interface ') or line.startswith('type '):
                name = line.split()[1].split('<')[0].split('{')[0].strip()
                interfaces.add(name)
        
        # Check 3: Common TS mistakes
        if 'export default' in content and 'export {' in content:
            errors.append({
                "file": file_path,
                "type": "export",
                "message": "Mixing default and named exports may cause issues",
                "severity": "warning"
            })
        
        # Check 4: Any type usage
        any_count = content.count(': any') + content.count(': any[]')
        if any_count > 3:
            errors.append({
                "file": file_path,
                "type": "types",
                "message": f"Excessive 'any' type usage ({any_count} instances). Consider using proper types",
                "severity": "warning"
            })
        
        return len([e for e in errors if e["severity"] == "error"]) == 0, errors
    
    def check_project(self, files: Dict[str, str]) -> Tuple[bool, List[dict]]:
        """Check all TypeScript files in a project"""
        all_errors = []
        has_errors = False
        
        ts_files = {k: v for k, v in files.items() if k.endswith(('.ts', '.tsx'))}
        
        for file_path, content in ts_files.items():
            ok, errors = self.check_file(file_path, content)
            if not ok:
                has_errors = True
            all_errors.extend(errors)
        
        logger.info(f"TS Check: {len(ts_files)} files, {len(all_errors)} issues")
        
        return not has_errors, all_errors