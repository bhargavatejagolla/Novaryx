"""
NOVARYX - Repair Validator
Validates that fixes actually resolved the bugs.
"""

from typing import List, Tuple
from .bug_detector import BugDetector, Bug


class RepairValidator:
    """Validates that repairs were successful"""
    
    def __init__(self):
        self.detector = BugDetector()
    
    def validate_repair(
        self,
        file_path: str,
        original_content: str,
        repaired_content: str,
        original_bugs: List[Bug]
    ) -> Tuple[bool, List[Bug], str]:
        """
        Validate that a repair fixed the bugs without introducing new ones.
        
        Returns:
            (is_fixed, remaining_bugs, message)
        """
        
        # Check content changed
        if repaired_content == original_content:
            return False, original_bugs, "Content unchanged - no repair applied"
        
        # Scan repaired content
        new_bugs = self.detector.scan_file(file_path, repaired_content)
        
        # Check if original bugs are resolved
        original_bug_types = {b.bug_type for b in original_bugs}
        new_bug_types = {b.bug_type for b in new_bugs}
        
        resolved = original_bug_types - new_bug_types
        
        if len(resolved) == len(original_bug_types):
            if len(new_bugs) == 0:
                return True, [], f"All {len(original_bugs)} bugs fixed, no new bugs"
            else:
                return True, new_bugs, f"Original bugs fixed, but {len(new_bugs)} new bugs found"
        elif len(resolved) > 0:
            remaining = original_bug_types - resolved
            return False, new_bugs, f"Partially fixed: resolved {len(resolved)}, remaining {len(remaining)}"
        else:
            return False, new_bugs, f"Fix did not resolve any bugs"
    
    def get_repair_report(
        self,
        files_before: dict,
        files_after: dict,
        bugs_before: dict
    ) -> dict:
        """Generate a complete repair report"""
        
        total_bugs_before = sum(len(b) for b in bugs_before.values())
        
        # Scan after
        bugs_after = {}
        for file_path, content in files_after.items():
            bugs_after[file_path] = self.detector.scan_file(file_path, content)
        
        total_bugs_after = sum(len(b) for b in bugs_after.values())
        
        return {
            "bugs_before": total_bugs_before,
            "bugs_after": total_bugs_after,
            "bugs_fixed": total_bugs_before - total_bugs_after,
            "files_repaired": len(files_after) - len(files_before) if len(files_after) > len(files_before) else len(files_after),
            "repair_success_rate": (
                (total_bugs_before - total_bugs_after) / max(total_bugs_before, 1) * 100
            )
        }
