"""
NOVARYX - Quality Gate
Defines quality thresholds that projects must meet.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class QualityThresholds:
    """Quality thresholds for generated projects"""
    max_typescript_errors: int = 0
    max_import_errors: int = 0
    max_syntax_errors: int = 0
    min_component_count: int = 2
    max_file_size_bytes: int = 100000
    min_css_variables: int = 10
    required_files: List[str] = None
    
    def __post_init__(self):
        if self.required_files is None:
            self.required_files = [
                "src/App.tsx",
                "src/main.tsx",
                "index.html",
                "package.json",
            ]


class QualityGate:
    """Validates projects meet quality standards"""
    
    def __init__(self, thresholds: QualityThresholds = None):
        self.thresholds = thresholds or QualityThresholds()
    
    def validate(self, files: Dict[str, str], errors: List[dict] = None) -> Tuple[bool, List[str], Dict]:
        """
        Validate project against quality thresholds.
        
        Returns:
            (passed, failures, report)
        """
        failures = []
        report = {
            "checks": {},
            "overall": "PASS"
        }
        
        # Check 1: Required files
        missing_files = [f for f in self.thresholds.required_files if f not in files]
        report["checks"]["required_files"] = {
            "passed": len(missing_files) == 0,
            "missing": missing_files,
            "threshold": self.thresholds.required_files
        }
        if missing_files:
            failures.append(f"Missing required files: {', '.join(missing_files)}")
        
        # Check 2: Error count
        if errors:
            ts_errors = [e for e in errors if e.get("type") == "syntax" and e.get("severity") == "error"]
            report["checks"]["typescript_errors"] = {
                "passed": len(ts_errors) <= self.thresholds.max_typescript_errors,
                "count": len(ts_errors),
                "threshold": self.thresholds.max_typescript_errors
            }
            if len(ts_errors) > self.thresholds.max_typescript_errors:
                failures.append(f"Too many TypeScript errors: {len(ts_errors)}")
        
        # Check 3: Component count
        component_files = [f for f in files if 'component' in f.lower() and f.endswith('.tsx')]
        report["checks"]["component_count"] = {
            "passed": len(component_files) >= self.thresholds.min_component_count,
            "count": len(component_files),
            "threshold": self.thresholds.min_component_count
        }
        if len(component_files) < self.thresholds.min_component_count:
            failures.append(f"Too few components: {len(component_files)}")
        
        # Check 4: File sizes
        oversized = []
        for f, content in files.items():
            if len(content) > self.thresholds.max_file_size_bytes:
                oversized.append(f)
        report["checks"]["file_sizes"] = {
            "passed": len(oversized) == 0,
            "oversized": oversized,
            "threshold_bytes": self.thresholds.max_file_size_bytes
        }
        if oversized:
            failures.append(f"Files exceed size limit: {', '.join(oversized)}")
        
        # Check 5: CSS variables (design token coverage)
        css_files = {k: v for k, v in files.items() if k.endswith('.css')}
        total_vars = sum(c.count('--') for c in css_files.values())
        report["checks"]["css_variables"] = {
            "passed": total_vars >= self.thresholds.min_css_variables,
            "count": total_vars,
            "threshold": self.thresholds.min_css_variables
        }
        if total_vars < self.thresholds.min_css_variables:
            failures.append(f"Too few CSS variables: {total_vars}")
        
        passed = len(failures) == 0
        report["overall"] = "PASS" if passed else "FAIL"
        report["failures"] = failures
        
        return passed, failures, report
    
    def display_report(self, report: dict):
        """Display quality report"""
        print("\n" + "=" * 50)
        print("📊 QUALITY GATE REPORT")
        print("=" * 50)
        
        for check_name, result in report.get("checks", {}).items():
            icon = "✅" if result.get("passed") else "❌"
            print(f"   {icon} {check_name}: {result}")
        
        print(f"\n   Overall: {report['overall']}")
        
        if report.get("failures"):
            print(f"   Failures:")
            for f in report["failures"]:
                print(f"      - {f}")
        
        print("=" * 50)