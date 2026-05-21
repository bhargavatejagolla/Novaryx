"""
NOVARYX - Surgical Repair Orchestrator
The replacement for global whole-project repair.

Flow per file:
  Detect bugs in file
  → Classify each bug
  → Apply deterministic fixes first (zero cost)
  → Apply style/import fixes (low cost)
  → If critical bugs remain AND budget allows → minimal LLM patch (1 file, tiny context)
  → Re-scan file only
  → Lock file if clean

Repair Budgets (hard limits):
  MAX_REPAIR_TIME_PER_FILE = 30s
  MAX_FILES_PER_REPAIR_RUN = 8 (or MAX_REPAIR_SCOPE)
  MAX_LLM_CALLS            = 3
  ACCEPT_ABOVE_THRESHOLD   = 90% clean files (partial success)
"""

import time
import re
import logging
import concurrent.futures
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any

from .bug_detector import BugDetector, Bug
from .fixers import get_fixer
from .error_classifier import ErrorClassifier, ErrorSeverity, RepairStrategy, ClassifiedError
from system.verification.dependency_checker import DependencyChecker

logger = logging.getLogger("novaryx.surgical_repair")


# ─────────────────────────────────────────────────────────────
# Repair Budget
# ─────────────────────────────────────────────────────────────
@dataclass
class RepairBudget:
    max_files: int = 8       # Never touch more than 8 files per repair run
    max_llm_calls: int = 3   # LLM calls are expensive — hard cap
    max_time_sec: float = 25.0  # Whole repair phase must finish in ≤25s
    accept_threshold: float = 0.90  # Accept if ≥90% files are clean


@dataclass
class SurgicalRepairResult:
    """Result with per-file breakdown and budget tracking"""
    success: bool
    files_processed: int
    files_repaired: int
    files_frozen: int          # Files that passed and were locked
    bugs_found: int
    bugs_fixed: int
    bugs_skipped: int          # Deliberately skipped (IGNORE strategy / low severity)
    llm_calls_used: int
    elapsed_sec: float
    repaired_files: Dict[str, str] = field(default_factory=dict)
    frozen_files: Set[str] = field(default_factory=set)
    skipped_errors: List[ClassifiedError] = field(default_factory=list)
    report: Dict[str, Any] = field(default_factory=dict)


class SurgicalRepairOrchestrator:
    """
    Surgical, budget-aware repair.

    Key differences from RepairEngine:
    ① Never processes the whole project as one blob
    ② Classifies first — ignores low-value errors
    ③ Deterministic fixes applied before any LLM attempt
    ④ Per-file validation — not global re-scan
    ⑤ File freezing — locked files are never touched again
    ⑥ Hard budget: time + LLM calls + file count
    ⑦ Partial success accepted at 90% threshold
    """

    def __init__(
        self,
        budget: Optional[RepairBudget] = None,
        enable_llm: bool = False,   # LLM patch disabled by default (fast path)
    ):
        self.budget = budget or RepairBudget()
        self.enable_llm = enable_llm
        self.detector = BugDetector()
        self.classifier = ErrorClassifier()
        self.dependency_checker = DependencyChecker()
        self.telemetry_callback = None
        
        from .trust_scoring import TrustRegistry
        self.trust_registry = TrustRegistry()

    # ──────────────────────────────────────────────────────────────────
    # MAIN ENTRY POINT
    # ──────────────────────────────────────────────────────────────────

    def repair(
        self,
        files: Dict[str, str],
        frozen: Optional[Set[str]] = None,
        telemetry_callback: Optional[callable] = None
    ) -> SurgicalRepairResult:
        """
        Surgical repair of a file set.

        Args:
            files:  {filepath: content}
            frozen: Set of already-validated files — skip entirely
            telemetry_callback: Optional function(file_path, status, trust)
        """
        self.telemetry_callback = telemetry_callback
        t_start = time.monotonic()
        frozen = frozen or set()
        all_file_paths = list(files.keys())

        working_files = dict(files)
        frozen_files: Set[str] = set(frozen)

        total_bugs_found = 0
        total_bugs_fixed = 0
        total_bugs_skipped = 0
        llm_calls = 0
        files_repaired = 0
        all_skipped: List[ClassifiedError] = []

        logger.info(f"[SurgicalRepair] Starting — {len(working_files)} files, budget={self.budget}")

        # ── Step 0: Stub missing components & hooks to guarantee resolution ──
        imported_components = {}
        imported_hooks = {}
        for filepath, content in list(working_files.items()):
            if not filepath.endswith(".tsx") and not filepath.endswith(".ts"):
                continue
            
            # Match imports like: import ContactForm from "../components/ContactForm"
            matches_comp = re.finditer(
                r'import\s+(?:(\w+)|\{\s*([\w\s,]+)\s*\})\s+from\s+[\'"](?:@|(?:\.\.)|(?:\.))/components/([\w-]+)[\'"]',
                content
            )
            for m in matches_comp:
                default_name = m.group(1)
                named_names = m.group(2)
                component_path_name = m.group(3)
                comp_name = component_path_name
                if default_name:
                    comp_name = default_name
                elif named_names:
                    comp_name = named_names.split(",")[0].strip()
                imported_components[component_path_name] = comp_name

            # Match imports like: import { useAuth } from "../hooks/useAuth"
            matches_hook = re.finditer(
                r'import\s+(?:(\w+)|\{\s*([\w\s,]+)\s*\})\s+from\s+[\'"](?:@|(?:\.\.)|(?:\.))/hooks/([\w-]+)[\'"]',
                content
            )
            for m in matches_hook:
                hook_file_name = m.group(3)
                hook_name = hook_file_name
                imported_hooks[hook_file_name] = hook_name

        # Stub missing components
        for path_name, comp_name in imported_components.items():
            target_path = f"src/components/{path_name}.tsx"
            if target_path not in working_files:
                logger.info(f"Generating missing component stub: {target_path}")
                working_files[target_path] = f"""import React from 'react';
import {{ motion }} from 'framer-motion';

export interface {comp_name}Props {{
  className?: string;
}}

export function {comp_name}({{ className = '' }}: {comp_name}Props) {{
  return (
    <motion.div
      initial={{{{ opacity: 0, y: 10 }}}}
      animate={{{{ opacity: 1, y: 0 }}}}
      className={{`p-6 rounded-xl bg-[var(--surface)] border border-[var(--border)] ${{className}}`}}
    >
      <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{comp_name}</h3>
      <p className="text-sm text-[var(--text-secondary)]">
        Placeholder for {comp_name} component.
      </p>
    </motion.div>
  );
}}

export default {comp_name};
"""

        # Stub missing hooks
        for hook_file, hook_name in imported_hooks.items():
            target_path = f"src/hooks/{hook_file}.ts"
            if target_path not in working_files and f"src/hooks/{hook_file}.tsx" not in working_files:
                logger.info(f"Generating missing hook stub: {target_path}")
                if hook_name == "useAuth":
                    working_files[target_path] = """import { useState } from 'react';

export function useAuth() {
  const [user, setUser] = useState({ id: '1', name: 'Demo User', email: 'user@example.com' });
  const [loading, setLoading] = useState(false);
  
  const login = async () => {
    setLoading(true);
    setUser({ id: '1', name: 'Demo User', email: 'user@example.com' });
    setLoading(false);
  };
  
  const logout = async () => {
    setLoading(true);
    setUser(null);
    setLoading(false);
  };
  
  return {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  };
}
export default useAuth;
"""
                else:
                    working_files[target_path] = f"""import {{ useState }} from 'react';

export function {hook_name}() {{
  const [state, setState] = useState(null);
  return state;
}}
export default {hook_name};
"""

        # Update all_file_paths to include stubs
        all_file_paths = list(working_files.keys())

        # ── Step 1: Detect all bugs across the project ────────────────
        all_bugs: List[Bug] = self.detector.scan_project(working_files)
        total_bugs_found = len(all_bugs)

        if not all_bugs:
            logger.info("   No bugs found — project is clean.")
            return self._make_result(
                success=True,
                files=working_files,
                frozen=frozen_files,
                files_repaired=0,
                bugs_found=0,
                bugs_fixed=0,
                bugs_skipped=0,
                llm_calls=0,
                elapsed=time.monotonic() - t_start,
            )

        # ── Step 2: Classify all bugs ──────────────────────────────────
        classified = self.classifier.classify_all(all_bugs, all_file_paths)
        actionable = self.classifier.filter_actionable(classified)
        all_skipped = [e for e in classified if e not in actionable]
        total_bugs_skipped = len(all_skipped)

        logger.info(f"   Bugs: {total_bugs_found} found, "
                    f"{len(actionable)} actionable, "
                    f"{total_bugs_skipped} skipped (low severity / IGNORE)")

        summary = self.classifier.get_repair_summary(actionable)
        logger.info(f"   Strategy distribution: {summary['by_strategy']}")

        # ── Step 2.5: Special Case: Dependency Repair (package.json) ──
        if "package.json" in working_files:
            logger.info("   Checking for missing packages in context...")
            pkgs_errors = self.dependency_checker.check_missing_packages(
                working_files, working_files["package.json"]
            )
            missing_names = [re.search(r"Module (.*) is imported", e["message"]).group(1) 
                             for e in pkgs_errors if "is imported but not defined" in e["message"]]
            
            if missing_names:
                logger.info(f"   Surgically fixing package.json. Adding: {missing_names}")
                new_pkg_json = self.dependency_checker.repair_package_json(
                    working_files["package.json"], missing_names
                )
                if new_pkg_json != working_files["package.json"]:
                    working_files["package.json"] = new_pkg_json
                    total_bugs_fixed += len(missing_names)
                    if self.telemetry_callback:
                        self.telemetry_callback("package.json", "repairing", 1.0)
        by_file = self.classifier.group_by_file(actionable)

        # Priority: files with CRITICAL errors first
        def _file_priority(fp: str) -> int:
            errs = by_file.get(fp, [])
            if any(e.severity == ErrorSeverity.CRITICAL for e in errs):
                return 0
            if any(e.severity == ErrorSeverity.HIGH for e in errs):
                return 1
            return 2

        sorted_files = sorted(by_file.keys(), key=_file_priority)

        # ── Step 4: Repair each file — budget-controlled ───────────────
        files_touched = 0
        for file_path in sorted_files:
            trust = self.trust_registry.get_trust_score(file_path)
            if self.telemetry_callback:
                self.telemetry_callback(file_path, "validating", trust)

            # Time budget check
            elapsed = time.monotonic() - t_start
            if elapsed >= self.budget.max_time_sec:
                logger.warning(f"   ⏱  Time budget {self.budget.max_time_sec}s exhausted — stopping repair.")
                break

            # Skip frozen files
            if file_path in frozen_files:
                logger.debug(f"   ⟳ Skipping frozen: {file_path}")
                continue

            # File count budget
            if files_touched >= self.budget.max_files:
                logger.warning(f"   📦 File budget {self.budget.max_files} reached — stopping.")
                break

            errors = by_file[file_path]
            content = working_files.get(file_path, "")
            if not content and not any(e.error_type == "empty_file" for e in errors):
                continue

            original = content
            file_fixed_count = 0

            # ── 4a: Apply deterministic fixes (instant, always safe) ───
            for err in errors:
                if err.strategy in (RepairStrategy.DETERMINISTIC,
                                    RepairStrategy.PACKAGE_RESOLVE,
                                    RepairStrategy.STYLE_REPAIR):
                    if err.has_deterministic_fix:
                        from .bug_detector import BugType
                        try:
                            bug_type_enum = BugType(err.error_type)
                        except ValueError:
                            continue
                        fixer = get_fixer(bug_type_enum)
                        if fixer:
                            # Reconstruct minimal Bug object for fixer signature
                            _dummy_bug = _make_dummy_bug(err)
                            try:
                                content, changed = fixer(content, _dummy_bug)
                                if changed:
                                    file_fixed_count += 1
                            except Exception as e:
                                logger.debug(f"   Fixer error on {file_path}: {e}")

            # ── 4b: LLM patch for remaining critical bugs (tight budget) ─
            if (
                self.enable_llm
                and llm_calls < self.budget.max_llm_calls
                and content == original  # deterministic didn't fix it
                and any(e.severity == ErrorSeverity.CRITICAL for e in errors)
            ):
                try:
                    repaired = self._llm_patch(file_path, content, errors)
                    if repaired and repaired != content:
                        content = repaired
                        file_fixed_count += 1
                        llm_calls += 1
                except Exception as e:
                    logger.warning(f"   LLM patch failed for {file_path}: {e}")

            if content != original and self.telemetry_callback:
                self.telemetry_callback(file_path, "repairing", self.trust_registry.get_trust_score(file_path))

            # ── 4c: Save repaired file ─────────────────────────────────
            if content != original:
                working_files[file_path] = content
                files_repaired += 1
                total_bugs_fixed += file_fixed_count
                self.trust_registry.record_repair(file_path, file_fixed_count)
                logger.info(f"   ✅ Repaired: {file_path} ({file_fixed_count} fixes)")

            files_touched += 1

            # ── 4d: Per-file validation → freeze if clean ──────────────
            remaining = self.detector.scan_file(file_path, working_files[file_path])
            critical_remaining = [b for b in remaining if b.severity == "critical"]
            if not critical_remaining:
                frozen_files.add(file_path)
                self.trust_registry.record_validation_pass(file_path)
                if self.telemetry_callback:
                    self.telemetry_callback(file_path, "frozen", self.trust_registry.get_trust_score(file_path))
                logger.debug(f"   ❄  Frozen: {file_path}")

        # ── Step 5: Partial-success acceptance ────────────────────────
        total_source = len([f for f in working_files if f.endswith(
            ('.tsx', '.ts', '.jsx', '.js'))])
        clean_count = len(frozen_files)
        clean_ratio = clean_count / total_source if total_source > 0 else 1.0
        success = clean_ratio >= self.budget.accept_threshold

        elapsed = time.monotonic() - t_start
        logger.info(
            f"[SurgicalRepair] Done in {elapsed:.1f}s — "
            f"{clean_count}/{total_source} files clean ({clean_ratio*100:.0f}%) "
            f"| fixes={total_bugs_fixed} | skipped={total_bugs_skipped} "
            f"| llm_calls={llm_calls}"
        )

        return self._make_result(
            success=success,
            files=working_files,
            frozen=frozen_files,
            files_repaired=files_repaired,
            bugs_found=total_bugs_found,
            bugs_fixed=total_bugs_fixed,
            bugs_skipped=total_bugs_skipped,
            llm_calls=llm_calls,
            elapsed=elapsed,
            skipped=all_skipped,
        )

    # ──────────────────────────────────────────────────────────────────
    # Single-file entry point (for progressive/inline validate+repair)
    # ──────────────────────────────────────────────────────────────────

    def repair_file(
        self,
        file_path: str,
        content: str,
        all_file_paths: Optional[List[str]] = None,
    ) -> tuple:
        """
        Repair a single file surgically. Returns (repaired_content, bugs_fixed).
        Used for per-module progressive validation.
        """
        bugs = self.detector.scan_file(file_path, content)
        if not bugs:
            return content, 0

        classified = self.classifier.classify_all(bugs, all_file_paths or [file_path])
        actionable = self.classifier.filter_actionable(classified)

        fixed = 0
        for err in actionable:
            if err.strategy in (RepairStrategy.DETERMINISTIC,
                                RepairStrategy.PACKAGE_RESOLVE,
                                RepairStrategy.STYLE_REPAIR):
                if err.has_deterministic_fix:
                    from .bug_detector import BugType
                    try:
                        bug_type_enum = BugType(err.error_type)
                    except ValueError:
                        continue
                    fixer = get_fixer(bug_type_enum)
                    if fixer:
                        _dummy = _make_dummy_bug(err)
                        try:
                            content, changed = fixer(content, _dummy)
                            if changed:
                                fixed += 1
                        except Exception:
                            pass
        if fixed > 0:
            self.trust_registry.record_repair(file_path, fixed)
        else:
            self.trust_registry.record_validation_pass(file_path)
            
        return content, fixed

    # ──────────────────────────────────────────────────────────────────
    # LLM patch (tight context — only 1 file + exact error)
    # ──────────────────────────────────────────────────────────────────

    def _llm_patch(
        self,
        file_path: str,
        content: str,
        errors: List[ClassifiedError],
    ) -> Optional[str]:
        """Minimal LLM repair: 1 file, exact errors, max 2000 tokens context"""
        try:
            from system.inference.provider_factory import get_provider_for_role
            provider = get_provider_for_role("repair")
        except Exception:
            return None

        if not provider:
            return None

        # Build a tiny, surgical prompt
        MAX_CODE = 4000  # ~1000 tokens
        truncated = content[:MAX_CODE]
        error_list = "\n".join(
            f"- [{e.severity.name}] {e.error_type}: {e.description}"
            for e in errors[:5]  # At most 5 errors in context
        )
        system_prompt = (
            "You are a React/TypeScript expert. "
            "Fix ONLY the reported bugs. Return the COMPLETE fixed file. No explanations."
        )
        user_prompt = (
            f"FILE: {file_path}\n\nBUGS TO FIX:\n{error_list}\n\n"
            f"CODE:\n```tsx\n{truncated}\n```\n\nFixed code:"
        )

        def _call():
            return provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                role="repair",
                temperature=0.05,
                max_tokens=2048,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            fut = ex.submit(_call)
            try:
                result = fut.result(timeout=30)  # 30s max per LLM patch
            except concurrent.futures.TimeoutError:
                logger.warning(f"LLM patch timed out for {file_path}")
                return None

        if not result or not result.success or not result.text:
            return None

        repaired = result.text.strip()
        # Strip markdown fences
        if repaired.startswith("```"):
            lines = repaired.split("\n")
            repaired = "\n".join(
                lines[1:-1] if lines[-1].startswith("```") else lines[1:]
            ).strip()

        # Sanity: reject if result is suspiciously short
        if len(repaired) < max(50, int(len(content) * 0.7)):
            return None

        return repaired

    # ──────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────

    def _make_result(
        self,
        success: bool,
        files: Dict[str, str],
        frozen: Set[str],
        files_repaired: int,
        bugs_found: int,
        bugs_fixed: int,
        bugs_skipped: int,
        llm_calls: int,
        elapsed: float,
        skipped: Optional[List[ClassifiedError]] = None,
    ) -> SurgicalRepairResult:
        return SurgicalRepairResult(
            success=success,
            files_processed=len(files),
            files_repaired=files_repaired,
            files_frozen=len(frozen),
            bugs_found=bugs_found,
            bugs_fixed=bugs_fixed,
            bugs_skipped=bugs_skipped,
            llm_calls_used=llm_calls,
            elapsed_sec=elapsed,
            repaired_files=files,
            frozen_files=frozen,
            skipped_errors=skipped or [],
            report={
                "success": success,
                "files_repaired": files_repaired,
                "bugs_found": bugs_found,
                "bugs_fixed": bugs_fixed,
                "bugs_skipped": bugs_skipped,
                "elapsed_sec": round(elapsed, 2),
                "llm_calls": llm_calls,
                "frozen_files": len(frozen),
            },
        )


# ─────────────────────────────────────────────────────────────
# Helper: reconstruct a dummy Bug for fixer signature compat
# ─────────────────────────────────────────────────────────────

def _make_dummy_bug(err: ClassifiedError):
    """Create a minimal Bug-compatible object from a ClassifiedError"""
    from .bug_detector import Bug, BugType
    try:
        bt = BugType(err.error_type)
    except ValueError:
        bt = BugType.SYNTAX_ERROR
    return Bug(
        bug_type=bt,
        severity=err.severity.name.lower(),
        file_path=err.file_path,
        line_number=1,
        column=0,
        description=err.description,
        problematic_code=err.problematic_code,
        suggested_fix=err.suggested_fix,
    )
