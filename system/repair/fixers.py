"""
NOVARYX - Fix Registry
Pattern-based fix functions for common bugs.

Each fixer is a standalone function that takes code and returns fixed code.
No LLM needed for these - they're deterministic pattern replacements.
"""

import re
from typing import Tuple, Optional
from .bug_detector import Bug, BugType


class FixRegistry:
    """Registry of all pattern-based fix functions"""
    
    @staticmethod
    def fix_double_braces(content: str, bug: Bug) -> Tuple[str, bool]:
        """Fix JSX double braces like onClick={{...}} → onClick={...}"""
        # Pattern: onClick={{code}} → onClick={code}
        fixed = re.sub(
            r'(on\w+)=\{\{(.+?)\}\}',
            r'\1={\2}',
            content
        )
        
        # Pattern: className={{ "..." }} → className="..."
        fixed = re.sub(
            r'className=\{\{\s*([\'"].+?[\'"])\s*\}\}',
            r'className=\1',
            fixed
        )
        
        changed = fixed != content
        return fixed, changed
    
    @staticmethod
    def fix_missing_import(content: str, bug: Bug) -> Tuple[str, bool]:
        """Add a missing import statement"""
        component_name = bug.description.split("'")[1] if "'" in bug.description else ""
        if not component_name:
            return content, False
        
        import_line = f"import {{ {component_name} }} from './components/{component_name}';"
        
        # Find last import line
        lines = content.split('\n')
        last_import_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('import '):
                last_import_idx = i
        
        if last_import_idx >= 0:
            lines.insert(last_import_idx + 1, import_line)
        else:
            lines.insert(0, import_line)
        
        return '\n'.join(lines), True
    
    @staticmethod
    def fix_unclosed_tag(content: str, bug: Bug) -> Tuple[str, bool]:
        """Attempt to close an unclosed JSX tag"""
        tag_name = bug.description.split('<')[1].split('>')[0] if '<' in bug.description else ""
        if not tag_name:
            return content, False
        
        # Only attempt to auto-close if it's a valid HTML element or PascalCase Component
        # to avoid accidentally closing TypeScript generics like <void> or <User>.
        # We also allow dots for things like motion.div
        if not re.match(r'^[a-z\.]+$|^[A-Z][a-zA-Z0-9\.]*$', tag_name):
            return content, False
            
        # Find the last occurrence of this tag
        pattern = f'<{tag_name}(?:\\s+[^>]*?)?>'
        matches = list(re.finditer(pattern, content))
        if not matches:
            return content, False
        
        last_match = matches[-1]
        
        # Check if it's already closed
        after_tag = content[last_match.end():]
        close_pattern = f'</{tag_name}>'
        if close_pattern in after_tag:
            return content, False  # Already closed
        
        # Add closing tag at the end of the file
        fixed = content.rstrip() + f'\n</{tag_name}>'
        return fixed, True
    
    @staticmethod
    def fix_missing_key_prop(content: str, bug: Bug) -> Tuple[str, bool]:
        """Add key prop to list items"""
        # Simple case: add key={index} to first element after map
        map_end = bug.column + len(bug.problematic_code)
        after_map = content[map_end:map_end + 100]
        
        # If the first element after map is a JSX tag without key
        first_tag = re.search(r'<(\w+)', after_map)
        if first_tag:
            tag_start = map_end + first_tag.start()
            insert_pos = tag_start + len(first_tag.group(0))
            fixed = content[:insert_pos] + ' key={index}' + content[insert_pos:]
            return fixed, True
        
        return content, False
    
    @staticmethod
    def fix_empty_file(content: str, bug: Bug) -> Tuple[str, bool]:
        """Add minimal component to empty file"""
        file_name = bug.file_path.split('/')[-1].replace('.tsx', '').replace('.ts', '')
        
        fixed = f"""import React from 'react';

interface {file_name}Props {{
  className?: string;
}}

export function {file_name}({{ className = '' }}: {file_name}Props) {{
  return (
    <div className={{className}}>
      {{/* {file_name} component */}}
    </div>
  );
}}
"""
        return fixed, True
    
    @staticmethod
    def fix_incorrect_export(content: str, bug: Bug) -> Tuple[str, bool]:
        """Add export statement to component file"""
        if 'export' in content:
            return content, False
        
        file_name = bug.file_path.split('/')[-1].replace('.tsx', '').replace('.ts', '')
        
        # Check if there's a function definition
        func_match = re.search(r'(?:function|const)\s+(\w+)', content)
        if func_match:
            func_name = func_match.group(1)
            # Add export before the function
            fixed = content.replace(f'function {func_name}', f'export function {func_name}')
            fixed = fixed.replace(f'const {func_name}', f'export const {func_name}')
            return fixed, True
        
        return content, False
    
    @staticmethod
    def fix_syntax_error_braces(content: str, bug: Bug) -> Tuple[str, bool]:
        """Fix unmatched braces by adding missing ones"""
        open_count = content.count('{')
        close_count = content.count('}')
        
        if open_count > close_count:
            return content + '\n' + '}' * (open_count - close_count), True
        elif close_count > open_count:
            return '{' * (close_count - open_count) + '\n' + content, True
        
        return content, False
    
    @staticmethod
    def fix_invalid_tailwind(content: str, bug: Bug) -> Tuple[str, bool]:
        """Fix common invalid Tailwind patterns"""
        fixed = content
        
        # Fix bg-[var(--xyz)]-hover → hover:bg-[var(--xyz)]
        fixed = re.sub(
            r'(\w+)-\[var\(--([^)]+)\)\]-hover',
            r'hover:\1-[var(--\2)]',
            fixed
        )
        
        # Fix text-[var(--xyz)]-hover → hover:text-[var(--xyz)]
        fixed = re.sub(
            r'text-\[var\(--([^)]+)\)\]-hover',
            r'hover:text-[var(--\1)]',
            fixed
        )
        
        return fixed, fixed != content

    @staticmethod
    def fix_invalid_import_identifier(content: str, bug: Bug) -> Tuple[str, bool]:
        """Fix spaces in import identifiers: { User Management } → { UserManagement }"""
        # Find the specific block with the error
        match = re.search(r"import\s+\{(.*?)\}\s+from", content, re.MULTILINE)
        if not match:
            return content, False
            
        block = match.group(1)
        # Remove spaces within each identifier
        identifiers = [i.strip().replace(" ", "") for i in block.split(",")]
        new_block = ", ".join(identifiers)
        
        fixed = content.replace(f"{{ {block} }}", f"{{ {new_block} }}")
        fixed = fixed.replace(f"{{{block}}}", f"{{ {new_block} }}")
        
        return fixed, fixed != content

    @staticmethod
    def fix_filename_spaces(content: str, bug: Bug) -> Tuple[str, bool]:
        """Sanitize import paths containing spaces: from './User Management' → './UserManagement'"""
        # Replace spaces in paths inside quotes
        fixed = re.sub(
            r"(from\s+['\"])(.+?)(['\"])", 
            lambda m: m.group(1) + m.group(2).replace(" ", "") + m.group(3),
            content
        )
        return fixed, fixed != content


# Map bug types to their fix functions
FIX_MAP = {
    BugType.DOUBLE_BRACE_JSX: FixRegistry.fix_double_braces,
    BugType.MISSING_IMPORT: FixRegistry.fix_missing_import,
    BugType.UNCLOSED_TAG: FixRegistry.fix_unclosed_tag,
    BugType.MISSING_KEY_PROP: FixRegistry.fix_missing_key_prop,
    BugType.EMPTY_FILE: FixRegistry.fix_empty_file,
    BugType.INCORRECT_EXPORT: FixRegistry.fix_incorrect_export,
    BugType.SYNTAX_ERROR: FixRegistry.fix_syntax_error_braces,
    BugType.INVALID_TAILWIND_CLASS: FixRegistry.fix_invalid_tailwind,
    BugType.INVALID_IMPORT_IDENTIFIER: FixRegistry.fix_invalid_import_identifier,
    BugType.INVALID_FILE_PATH: FixRegistry.fix_filename_spaces,
}


def get_fixer(bug_type: BugType):
    """Get the fix function for a bug type"""
    return FIX_MAP.get(bug_type)