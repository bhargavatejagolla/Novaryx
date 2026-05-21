"""
NOVARYX - UX Enforcer
Heuristic checks for accessibility, responsiveness, and design system adherence.
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger("novaryx.ux_checker")

class UXChecker:
    """
    Validates UI/UX quality of generated React components.
    """
    
    def __init__(self):
        # Patterns for common UX issues
        self.missing_alt = re.compile(r"<img(?![^>]*alt=)[^>]*>")
        self.missing_aria = re.compile(r"<(button|a|input)(?![^>]*aria-label=)(?![^>]*aria-labelledby=)[^>]*>")
        self.hardcoded_colors = re.compile(r"(?:color|bg|border)-(?:red|blue|gray|green|purple|indigo|pink|yellow)-\d+")
        
    def check_ux_quality(self, files: Dict[str, str]) -> List[Dict]:
        """
        Run heuristic checks across all UI files.
        """
        errors = []
        
        for path, content in files.items():
            if not path.endswith(".tsx") or "src/components/" not in path:
                continue
                
            # Check 1: Missing image alt tags
            if self.missing_alt.search(content):
                errors.append({
                    "file": path,
                    "type": "ux_violation",
                    "message": "Accessibility: <img> tag missing alt attribute.",
                    "severity": "warning"
                })
                
            # Check 2: Interactive elements without labels
            # Only flag if there's no visible text content (heuristic)
            # This is complex in regex, so we'll do a simple check for empty buttons/links
            if self.missing_aria.search(content):
                # Only flag if there's no obvious text inside or label
                errors.append({
                    "file": path,
                    "type": "ux_violation",
                    "message": "Accessibility: Interactive element missing aria-label.",
                    "severity": "warning"
                })
                
            # Check 3: Hardcoded Tailwind colors (should use design tokens/vars)
            hardcoded = self.hardcoded_colors.findall(content)
            if hardcoded:
                errors.append({
                    "file": path,
                    "type": "ux_violation",
                    "message": f"Design System: Hardcoded Tailwind classes found ({', '.join(set(hardcoded[:2]))}). Use design tokens instead.",
                    "severity": "warning"
                })
                
            # Check 4: Layout responsiveness
            if "flex" not in content and "grid" not in content and ("width:" in content or "w-" in content):
                 if "w-full" not in content and "max-w-" not in content:
                    errors.append({
                        "file": path,
                        "type": "ux_violation",
                        "message": "Responsiveness: Component may have fixed width without flex/grid container.",
                        "severity": "warning"
                    })
                    
        return errors
