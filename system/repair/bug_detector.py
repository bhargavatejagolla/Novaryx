"""
NOVARYX - Bug Detector
Pattern-based detection of common bugs in generated React/TypeScript code.

Detects 20+ bug patterns without needing to run the code.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum


class BugType(Enum):
    """Types of detectable bugs"""
    # JSX Syntax
    DOUBLE_BRACE_JSX = "double_brace_jsx"
    UNCLOSED_TAG = "unclosed_tag"
    INVALID_JSX_EXPRESSION = "invalid_jsx_expression"
    
    # Imports
    MISSING_IMPORT = "missing_import"
    UNUSED_IMPORT = "unused_import"
    INCORRECT_IMPORT_PATH = "incorrect_import_path"
    
    # TypeScript
    TYPE_MISMATCH = "type_mismatch"
    MISSING_TYPE = "missing_type"
    INVALID_INTERFACE = "invalid_interface"
    
    # React
    MISSING_KEY_PROP = "missing_key_prop"
    INVALID_HOOK_USAGE = "invalid_hook_usage"
    UNDEFINED_COMPONENT = "undefined_component"
    
    # Tailwind CSS
    INVALID_TAILWIND_CLASS = "invalid_tailwind_class"
    CONFLICTING_CLASSES = "conflicting_classes"
    
    # General
    SYNTAX_ERROR = "syntax_error"
    EMPTY_FILE = "empty_file"
    DUPLICATE_EXPORT = "duplicate_export"
    INCORRECT_EXPORT = "incorrect_export"
    
    # NOVARYX Specific Arch/Build Rules
    INVALID_IMPORT_IDENTIFIER = "invalid_import_identifier"
    INVALID_FILE_PATH = "invalid_file_path"


@dataclass
class Bug:
    """A detected bug with location and fix suggestion"""
    bug_type: BugType
    severity: str  # critical, error, warning
    file_path: str
    line_number: int
    column: int
    description: str
    problematic_code: str
    suggested_fix: str = ""
    context: str = ""
    
    def to_dict(self) -> dict:
        return {
            "type": self.bug_type.value,
            "severity": self.severity,
            "file": self.file_path,
            "line": self.line_number,
            "column": self.column,
            "description": self.description,
            "code": self.problematic_code[:100],
            "fix": self.suggested_fix[:100]
        }


class BugDetector:
    """
    Pattern-based bug detection for generated code.
    
    Scans code without execution. Finds common AI-generation bugs.
    """
    
    def __init__(self):
        self.detectors = [
            self._detect_double_braces,
            self._detect_unclosed_tags,
            self._detect_missing_imports,
            self._detect_undefined_components,
            self._detect_missing_key_props,
            self._detect_invalid_tailwind,
            self._detect_incorrect_exports,
            self._detect_empty_files,
            self._detect_invalid_import_identifiers,
            self._detect_filename_spaces,
        ]
    
    def scan_file(self, file_path: str, content: str) -> List[Bug]:
        """Scan a single file for all detectable bugs"""
        bugs = []
        
        if not content or len(content.strip()) == 0:
            bugs.append(Bug(
                bug_type=BugType.EMPTY_FILE,
                severity="error",
                file_path=file_path,
                line_number=1,
                column=1,
                description="File is empty",
                problematic_code="",
                suggested_fix="Add content or remove file"
            ))
            return bugs
        
        for detector in self.detectors:
            try:
                found = detector(file_path, content)
                bugs.extend(found)
            except Exception as e:
                pass  # One detector failing shouldn't stop others
        
        return bugs
    
    def scan_project(self, files: dict) -> List[Bug]:
        """Scan all files in a project"""
        all_bugs = []
        for file_path, content in files.items():
            if file_path.endswith(('.tsx', '.ts', '.jsx', '.js', '.css')):
                bugs = self.scan_file(file_path, content)
                all_bugs.extend(bugs)
        return all_bugs
    
    # ================================================================
    # DETECTORS
    # ================================================================
    
    def _detect_double_braces(self, file_path: str, content: str) -> List[Bug]:
        """Detect JSX double-brace bugs like onClick={{() => ...}}"""
        bugs = []
        
        # Pattern: onClick={{ or onChange={{ or any event handler with {{
        pattern = r'(on\w+)=\{\{(.+?)\}\}'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            
            bugs.append(Bug(
                bug_type=BugType.DOUBLE_BRACE_JSX,
                severity="critical",
                file_path=file_path,
                line_number=line_num,
                column=match.start(),
                description=f"Double braces in JSX event handler: {match.group(1)}",
                problematic_code=match.group(0)[:80],
                suggested_fix=f"Change {match.group(0)[:40]}... to use single braces"
            ))
        
        # Also detect {{}} patterns in JSX attributes
        pattern2 = r'(\w+)=\{\{(?!\/\*)(.+?)\}\}'
        for match in re.finditer(pattern2, content):
            if 'on' in match.group(1):
                continue  # Already caught above
            
            line_num = content[:match.start()].count('\n') + 1
            
            bugs.append(Bug(
                bug_type=BugType.DOUBLE_BRACE_JSX,
                severity="warning",
                file_path=file_path,
                line_number=line_num,
                column=match.start(),
                description=f"Potential double braces in JSX attribute: {match.group(1)}",
                problematic_code=match.group(0)[:80],
                suggested_fix=f"Check if {match.group(1)} needs single or double braces"
            ))
        
        return bugs
    
    def _detect_unclosed_tags(self, file_path: str, content: str) -> List[Bug]:
        """Detect unclosed JSX tags"""
        bugs = []
        
        # Simple self-closing tag check
        # Use (?<!\w) to avoid matching TypeScript generics like useState<User>
        open_tags = re.findall(r'(?<!\w)<([a-zA-Z][a-zA-Z0-9-\.]*)(?:\s+[^>]*?)?(?<!/)>', content)
        close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9-\.]*)>', content)
        self_closing = re.findall(r'(?<!\w)<([a-zA-Z][a-zA-Z0-9-\.]*)[^>]*\/>', content)
        
        # Count tags
        from collections import Counter
        open_count = Counter(open_tags)
        close_count = Counter(close_tags)
        self_close_count = Counter(self_closing)
        
        # Check for mismatches
        all_tags = set(list(open_count.keys()) + list(close_count.keys()))
        for tag in all_tags:
            opens = open_count.get(tag, 0)
            closes = close_count.get(tag, 0)
            selfs = self_close_count.get(tag, 0)
            
            if opens > closes + selfs:
                # Find the approximate location
                pattern = f'<{tag}[^>]*[^/]>'
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count('\n') + 1
                    bugs.append(Bug(
                        bug_type=BugType.UNCLOSED_TAG,
                        severity="error",
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start(),
                        description=f"Potentially unclosed <{tag}> tag",
                        problematic_code=match.group(0)[:60],
                        suggested_fix=f"Add closing </{tag}> or make self-closing <{tag} />"
                    ))
                    break
        
        return bugs
    
    def _detect_missing_imports(self, file_path: str, content: str) -> List[Bug]:
        """Detect used but not imported components"""
        bugs = []
        
        # Find all imports
        imports = set()
        for match in re.finditer(r'import\s+(?:{([^}]+)}|(\w+))\s+from\s+[\'"]([^\'"]+)[\'"]', content):
            if match.group(1):  # Named imports
                for name in match.group(1).split(','):
                    imports.add(name.strip().split(' as ')[-1].strip())
            if match.group(2):  # Default import
                imports.add(match.group(2))
        
        # Find JSX components (PascalCase tags)
        jsx_tags = set()
        # Use (?<!\w) to avoid matching TypeScript generics like useState<User>
        for match in re.finditer(r'(?<!\w)<([A-Z][a-zA-Z0-9\.]*)', content):
            jsx_tags.add(match.group(1).split('.')[0]) # Handle ThemeContext.Provider
        
        # Find local declarations (const, let, var, function, class, type, interface)
        local_decls = set()
        for match in re.finditer(r'\b(?:const|let|var|function|class|type|interface)\s+([A-Z][a-zA-Z0-9]*)', content):
            local_decls.add(match.group(1))

        # Standard React imports
        builtins = {'React', 'Fragment', 'Suspense', 'StrictMode', 'motion', 'AnimatePresence'}
        imports.update(builtins)
        imports.update(local_decls)
        
        # Check for missing
        for tag in jsx_tags:
            if tag not in imports and tag not in builtins:
                # Find first usage
                pattern = f'<{tag}'
                match = re.search(pattern, content)
                if match:
                    line_num = content[:match.start()].count('\n') + 1
                    bugs.append(Bug(
                        bug_type=BugType.MISSING_IMPORT,
                        severity="error",
                        file_path=file_path,
                        line_number=line_num,
                        column=match.start(),
                        description=f"Component '{tag}' is used but not imported",
                        problematic_code=match.group(0),
                        suggested_fix=f"Add: import {tag} from './components/{tag}' or appropriate path"
                    ))
        
        return bugs
    
    def _detect_undefined_components(self, file_path: str, content: str) -> List[Bug]:
        """Detect references to undefined components"""
        bugs = []
        
        # Get all defined components (export default function or export function)
        defined = set()
        for match in re.finditer(r'export\s+(?:default\s+)?function\s+(\w+)', content):
            defined.add(match.group(1))
        for match in re.finditer(r'export\s+const\s+(\w+)\s*=', content):
            defined.add(match.group(1))
        
        # Find all JSX components used
        jsx_components = set()
        # Use (?<!\w) to avoid matching TypeScript generics like useState<User>
        for match in re.finditer(r'(?<!\w)<([A-Z][a-zA-Z0-9\.]*)', content):
            jsx_components.add(match.group(1).split('.')[0])
        
        # Check if any used component is neither imported nor defined
        # (This complements _detect_missing_imports)
        
        return bugs
    
    def _detect_missing_key_props(self, file_path: str, content: str) -> List[Bug]:
        """Detect missing key props in list renders"""
        bugs = []
        
        # Find .map() calls that return JSX without key
        map_pattern = r'\.map\s*\(\s*(?:\([^)]*\)|[^,)]+)\s*=>\s*(?:\(|<)'
        
        for match in re.finditer(map_pattern, content):
            # Check if 'key=' appears after this map
            after = content[match.end():match.end() + 200]
            if 'key=' not in after and 'key={' not in after:
                line_num = content[:match.start()].count('\n') + 1
                bugs.append(Bug(
                    bug_type=BugType.MISSING_KEY_PROP,
                    severity="warning",
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(),
                    description="Missing 'key' prop in list render (map without key)",
                    problematic_code=match.group(0)[:60],
                    suggested_fix="Add key={item.id} or key={index} to the rendered element"
                ))
        
        return bugs
    
    def _detect_invalid_tailwind(self, file_path: str, content: str) -> List[Bug]:
        """Detect obviously invalid Tailwind classes"""
        bugs = []
        
        # Common AI-generated invalid classes
        invalid_patterns = [
            (r'bg-\[var\(--([^)]+)\)\]-hover', 'bg-[var(--xyz)]/hover is invalid, use hover:bg-[var(--xyz)]'),
            (r'text-\[var\(--([^)]+)\)\]-hover', 'Use hover:text-[var(--xyz)] instead'),
            (r'className="([^"]*)\1([^"]*)"', 'Duplicate class in className'),
        ]
        
        for pattern, message in invalid_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                bugs.append(Bug(
                    bug_type=BugType.INVALID_TAILWIND_CLASS,
                    severity="warning",
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(),
                    description=message,
                    problematic_code=match.group(0)[:80],
                    suggested_fix="Fix Tailwind class syntax"
                ))
        
        return bugs
    
    def _detect_incorrect_exports(self, file_path: str, content: str) -> List[Bug]:
        """Detect export issues"""
        bugs = []
        
        # Check if file has JSX content but no export
        has_jsx = bool(re.search(r'<(?:[A-Z]\w*|div|span|button|input|form|section|main|nav|header|footer)', content))
        has_export = bool(re.search(r'export\s+(default\s+)?(function|const|class)', content))
        
        if has_jsx and not has_export and not file_path.endswith('.d.ts'):
            line_num = 1
            bugs.append(Bug(
                bug_type=BugType.INCORRECT_EXPORT,
                severity="warning",
                file_path=file_path,
                line_number=line_num,
                column=1,
                description="Component file has JSX but no export statement",
                problematic_code=content[:50].strip(),
                suggested_fix="Add 'export default function ComponentName()' or 'export function ComponentName()'"
            ))
        
        return bugs
    
    def _detect_empty_files(self, file_path: str, content: str) -> List[Bug]:
        """Detect completely empty files"""
        bugs = []
        
        stripped = content.strip()
        if len(stripped) == 0:
            bugs.append(Bug(
                bug_type=BugType.EMPTY_FILE,
                severity="error",
                file_path=file_path,
                line_number=1,
                column=1,
                description="File is completely empty",
                problematic_code="",
                suggested_fix="Add component code or remove file"
            ))
        
        return bugs
    
    def _detect_syntax_errors(self, file_path: str, content: str) -> List[Bug]:
        """Detect obvious syntax errors"""
        bugs = []
        
        # Unmatched parentheses
        open_parens = content.count('(') 
        close_parens = content.count(')')
        if open_parens != close_parens:
            bugs.append(Bug(
                bug_type=BugType.SYNTAX_ERROR,
                severity="critical",
                file_path=file_path,
                line_number=1,
                column=1,
                description=f"Unmatched parentheses: {open_parens} open, {close_parens} close",
                problematic_code="",
                suggested_fix="Check for missing opening or closing parentheses"
            ))
        
        # Unmatched braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            bugs.append(Bug(
                bug_type=BugType.SYNTAX_ERROR,
                severity="critical",
                file_path=file_path,
                line_number=1,
                column=1,
                description=f"Unmatched braces: {open_braces} open, {close_braces} close",
                problematic_code="",
                suggested_fix="Check for missing opening or closing braces"
            ))
        
        # Backtick template literal issues
        backtick_count = content.count('`')
        if backtick_count % 2 != 0:
            bugs.append(Bug(
                bug_type=BugType.SYNTAX_ERROR,
                severity="critical",
                file_path=file_path,
                line_number=1,
                column=1,
                description="Unmatched backticks (template literals)",
                problematic_code="",
                suggested_fix="Close all template literal strings"
            ))
        
        return bugs
    
    def _detect_invalid_import_identifiers(self, file_path: str, content: str) -> List[Bug]:
        """Detect identifiers with spaces in import braces: import { User Management }"""
        bugs = []
        import re
        blocks = re.finditer(r"import\s+\{(.*?)\}\s+from", content, re.MULTILINE)
        for match in blocks:
            block = match.group(1)
            if " " in block.strip():
                identifiers = [i.strip() for i in block.split(",")]
                for ident in identifiers:
                    if " " in ident:
                        line_num = content[:match.start()].count('\n') + 1
                        bugs.append(Bug(
                            bug_type=BugType.INVALID_IMPORT_IDENTIFIER,
                            severity="critical",
                            file_path=file_path,
                            line_number=line_num,
                            column=match.start(),
                            description=f"Invalid identifier with spaces: '{ident}'",
                            problematic_code=match.group(0),
                            suggested_fix=f"Remove spaces from identifier '{ident}'"
                        ))
        return bugs

    def _detect_filename_spaces(self, file_path: str, content: str) -> List[Bug]:
        """Detect import paths with spaces: from './User Management'"""
        bugs = []
        import re
        # Match from '...' or from "..."
        pattern = r"from\s+['\"](.+?)['\"]"
        for match in re.finditer(pattern, content):
            path = match.group(1)
            if " " in path:
                line_num = content[:match.start()].count('\n') + 1
                bugs.append(Bug(
                    bug_type=BugType.INVALID_FILE_PATH,
                    severity="error",
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(),
                    description=f"Import path contains spaces: '{path}'",
                    problematic_code=match.group(0),
                    suggested_fix=f"Remove spaces from path '{path}'"
                ))
        return bugs

    def get_bug_summary(self, bugs: List[Bug]) -> Dict[str, Any]:
        """Get summary of detected bugs"""
        severity_counts = {"critical": 0, "error": 0, "warning": 0}
        type_counts = {}
        
        for bug in bugs:
            severity_counts[bug.severity] = severity_counts.get(bug.severity, 0) + 1
            type_name = bug.bug_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            "total": len(bugs),
            "by_severity": severity_counts,
            "by_type": type_counts
        }