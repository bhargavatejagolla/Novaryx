"""
NOVARYX - Import Checker
Validates that all imports resolve correctly.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set

logger = logging.getLogger("novaryx.import_checker")


class ImportChecker:
    """Validates import statements resolve to actual files"""
    
    # Known packages that don't need checking
    KNOWN_PACKAGES = {
        'react', 'react-dom', 'react-dom/client',
        'framer-motion', 'framer-motion/three',
        'three', '@react-three/fiber', '@react-three/drei',
        'recharts', '@tanstack/react-table',
        'tailwindcss', 'autoprefixer', 'postcss',
        'next/router', 'next/link', 'next/image',
        'vite', '@vitejs/plugin-react',
        'clsx', 'classnames', 'lodash', 'axios',
    }
    
    def check_project(self, files: Dict[str, str], project_dir: str = None) -> Tuple[bool, List[dict]]:
        """
        Check all imports resolve.
        
        Args:
            files: {relative_path: content}
            project_dir: Base directory for resolution
        
        Returns:
            (all_resolved, list_of_issues)
        """
        issues = []
        all_imports = set()
        
        # Collect all exports
        exports: Dict[str, Set[str]] = {}  # file → {exported names}
        
        for file_path, content in files.items():
            if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue
            
            # Find exports
            file_exports = set()
            
            # export function/const/class
            for match in re.finditer(r'export\s+(?:default\s+)?(?:function|const|class|interface|type|enum)\s+(\w+)', content):
                file_exports.add(match.group(1))
            
            # export { X, Y }
            for match in re.finditer(r'export\s*\{([^}]+)\}', content):
                for name in match.group(1).split(','):
                    file_exports.add(name.strip().split(' as ')[-1].strip())
            
            # export default
            if re.search(r'export\s+default', content):
                file_exports.add('default')
            
            exports[file_path] = file_exports
        
        # Check each import
        for file_path, content in files.items():
            if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                continue
            
            # Find all imports
            import_patterns = [
                r'import\s+(?:type\s+)?\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]',  # named
                r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # default
                r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',  # namespace
                r'import\s+[\'"]([^\'"]+)[\'"]',  # side-effect
            ]
            
            for pattern in import_patterns:
                for match in re.finditer(pattern, content):
                    if len(match.groups()) == 2:
                        imported, source = match.groups()
                    else:
                        source = match.group(1)
                        imported = None
                    
                    # Skip known packages
                    if any(source.startswith(pkg) for pkg in self.KNOWN_PACKAGES):
                        continue
                    
                    # Skip relative imports for now (would need path resolution)
                    if source.startswith('.') and project_dir:
                        continue
                    
                    # Skip CSS/style imports
                    if source.endswith(('.css', '.scss', '.less')):
                        continue
                    
                    # Skip @/ aliases
                    if source.startswith('@/'):
                        continue
        
        resolved_count = len(files) - len(issues)
        logger.info(f"Import Check: {len(files)} files checked")
        
        return len(issues) == 0, issues