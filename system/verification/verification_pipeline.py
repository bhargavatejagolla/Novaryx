"""
NOVARYX - Verification Pipeline
Complete verification orchestrator with repair integration.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .typescript_checker import TypeScriptChecker
from .import_checker import ImportChecker
from .build_checker import BuildChecker
from .quality_gate import QualityGate, QualityThresholds
from .dependency_checker import DependencyChecker
from .ux_checker import UXChecker

logger = logging.getLogger("novaryx.verification")


@dataclass
class VerificationResult:
    """Complete verification result"""
    passed: bool
    checks_run: List[str]
    errors: List[dict]
    quality_report: dict
    verified_files: Dict[str, str]
    requires_repair: bool
    repair_suggestions: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def warnings(self) -> List[dict]:
        return [e for e in self.errors if e.get("severity") == "warning"]


class VerificationPipeline:
    """
    Complete verification pipeline.
    
    Runs all checks and determines if repair is needed.
    """
    
    def __init__(self, project_dir: str = None):
        self.project_dir = project_dir
        self.ts_checker = TypeScriptChecker()
        self.import_checker = ImportChecker()
        self.build_checker = BuildChecker()
        self.quality_gate = QualityGate()
        self.dependency_checker = DependencyChecker()
        self.ux_checker = UXChecker()
        
        from system.intelligence.rule_engine import ArchitectureRuleEngine
        self.rule_engine = ArchitectureRuleEngine()
    
    def verify(self, files: Dict[str, str]) -> VerificationResult:
        """
        Run full verification on project files.
        
        Args:
            files: {filepath: content}
        
        Returns:
            Complete VerificationResult
        """
        
        print("\n" + "=" * 60)
        print("🔍 VERIFICATION PIPELINE")
        print("=" * 60)
        
        all_errors = []
        checks_run = []
        repair_suggestions = []
        
        # Check 0: Architecture Governance
        print("\n🏛️ Architecture Governance...")
        arch_violations = self.rule_engine.validate_architecture(files)
        checks_run.append("architecture")
        
        for v in arch_violations:
            all_errors.append({
                "file": v.file_path,
                "type": v.rule_type,
                "message": v.message,
                "severity": v.severity
            })
            
        icon = "✅" if not arch_violations else "⚠️"
        print(f"   {icon} {len(arch_violations)} structural violations")
        
        if arch_violations:
            repair_suggestions.append("Apply strict folder/routing naming conventions.")
        
        # Check 1: TypeScript
        print("\n📝 TypeScript Check...")
        ts_ok, ts_errors = self.ts_checker.check_project(files)
        checks_run.append("typescript")
        all_errors.extend(ts_errors)
        
        ts_count = len(ts_errors)
        icon = "✅" if ts_ok else "⚠️"
        print(f"   {icon} {ts_count} issues")
        
        if not ts_ok:
            repair_suggestions.append("Fix TypeScript errors")
        
        # Check 2: Imports
        print("\n📦 Import Check...")
        import_ok, import_issues = self.import_checker.check_project(files)
        checks_run.append("imports")
        all_errors.extend(import_issues)
        
        icon = "✅" if import_ok else "⚠️"
        print(f"   {icon} {len(import_issues)} issues")
        
        if not import_ok:
            repair_suggestions.append("Fix import resolution errors")
        
        # Check 3: Build (quick check)
        print("\n🔨 Build Check...")
        build_ok, build_issues = self.build_checker.quick_check(files)
        checks_run.append("build")
        
        if isinstance(build_issues, list):
            for issue in build_issues:
                all_errors.append({"type": "build", "message": issue, "severity": "error"})
        
        icon = "✅" if build_ok else "❌"
        print(f"   {icon} {len(build_issues) if isinstance(build_issues, list) else 0} issues")
        
        if not build_ok:
            repair_suggestions.append("Fix build configuration")
        
        # Check 4: Advanced Dependency & Architecture
        print("\n🖇️ Dependency Check...")
        dep_errors = self.dependency_checker.check_circular_dependencies(files)
        pkg_errors = self.dependency_checker.check_missing_packages(files, files.get("package.json", ""))
        all_errors.extend(dep_errors)
        all_errors.extend(pkg_errors)
        checks_run.append("dependencies")
        print(f"   ✅ {len(dep_errors) + len(pkg_errors)} dependency issues")

        # Check 5: UX & Accessibility
        print("\n✨ UX & Accessibility Check...")
        ux_errors = self.ux_checker.check_ux_quality(files)
        all_errors.extend(ux_errors)
        checks_run.append("ux")
        print(f"   ✅ {len(ux_errors)} UX suggestions")
        
        # Check 4: Quality Gate
        print("\n🏆 Quality Gate...")
        quality_passed, quality_failures, quality_report = self.quality_gate.validate(
            files, all_errors
        )
        checks_run.append("quality")
        
        icon = "✅" if quality_passed else "❌"
        print(f"   {icon} {len(quality_failures)} failures")
        
        if not quality_passed:
            repair_suggestions.extend(quality_failures)
        
        # Determine overall result
        critical_errors = [e for e in all_errors if e.get("severity") == "error"]
        passed = len(critical_errors) == 0 and quality_passed
        
        result = VerificationResult(
            passed=passed,
            checks_run=checks_run,
            errors=all_errors,
            quality_report=quality_report,
            verified_files=files,
            requires_repair=not passed and len(repair_suggestions) > 0,
            repair_suggestions=repair_suggestions
        )
        
        # Summary
        print(f"\n   --- Verification Complete ---")
        print(f"   Overall: {'✅ PASSED' if passed else '❌ FAILED'}")
        print(f"   Checks: {', '.join(checks_run)}")
        print(f"   Total Issues: {len(all_errors)}")
        print(f"   Needs Repair: {'Yes' if result.requires_repair else 'No'}")
        
        if result.requires_repair:
            print(f"   Suggestions:")
            for s in repair_suggestions[:5]:
                print(f"      - {s}")
        
        print("=" * 60)
        
        return result


# ---- Quick verify function ----

def verify_project(files: Dict[str, str]) -> VerificationResult:
    """Quick verification of project files"""
    pipeline = VerificationPipeline()
    return pipeline.verify(files)


# ---- Test ----

def test_verification():
    """Test the verification pipeline"""
    
    print("\n" + "=" * 60)
    print("🧪 VERIFICATION PIPELINE TEST")
    print("=" * 60)
    
    # Create test files
    test_files = {
        "src/App.tsx": """
import React from 'react';
import { ThemeProvider } from './components/ThemeProvider';

export default function App() {
  return (
    <ThemeProvider>
      <div className="app">
        <h1>Hello NOVARYX</h1>
      </div>
    </ThemeProvider>
  );
}
""",
        "src/main.tsx": """
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/tokens.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""",
        "src/components/ThemeProvider.tsx": """
import React, { createContext, useContext, useState } from 'react';

interface ThemeContextType {
  theme: string;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({ theme: 'dark', toggleTheme: () => {} });

export function useTheme() { return useContext(ThemeContext); }

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState('dark');
  const toggleTheme = () => setTheme(t => t === 'dark' ? 'light' : 'dark');
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
""",
        "src/styles/tokens.css": """
:root {
  --primary: #7c3aed;
  --primary-light: #a78bfa;
  --background: #0f0f1a;
  --surface: #1e1e32;
  --text-primary: #f1f1f6;
  --text-secondary: #a0a0b8;
  --border: rgba(255,255,255,0.08);
  --radius-md: 12px;
  --shadow-md: 0 4px 12px rgba(0,0,0,0.3);
  --transition-normal: 250ms ease;
  --font-primary: 'Inter', sans-serif;
}
""",
        "index.html": "<!DOCTYPE html><html><head><title>Test</title></head><body><div id='root'></div></body></html>",
        "package.json": '{"name":"test","version":"1.0.0","scripts":{"dev":"vite","build":"tsc && vite build"}}',
    }
    
    pipeline = VerificationPipeline()
    result = pipeline.verify(test_files)
    
    print(f"\n   Passed: {result.passed}")
    print(f"   Checks: {result.checks_run}")
    print(f"   Needs Repair: {result.requires_repair}")
    
    print("\n✅ Verification Pipeline test complete")
    
    return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_verification()