"""
NOVARYX - Error Intelligence Layer
Classifies, ranks, and strategizes repair for every error type.

Philosophy:
  NOT all errors deserve AI repair.
  NOT all repairs need the full project context.
  MOST errors have deterministic fixes.
  SURGICAL scoping = 80-90% faster repair.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


class RepairStrategy(Enum):
    """How to repair this error class"""
    DETERMINISTIC   = "deterministic"   # Pattern regex — zero latency
    PACKAGE_RESOLVE = "package_resolve" # Add/fix import statements
    ROUTE_GRAPH     = "route_graph"     # Fix routing connectivity
    LOCAL_PATCH     = "local_patch"     # Small targeted LLM patch (1 file, tiny context)
    STYLE_REPAIR    = "style_repair"    # Fix Tailwind / CSS class issues
    IGNORE          = "ignore"           # Not worth repairing — accept partial


class ErrorSeverity(Enum):
    """Repair priority"""
    CRITICAL = 1   # Fix immediately — blocks build
    HIGH     = 2   # Fix in first repair pass
    MEDIUM   = 3   # Fix in second pass
    LOW      = 4   # Defer — cosmetic / linting only
    IGNORE   = 5   # Never repair — waste of time


@dataclass
class ClassifiedError:
    """A scoped, classified, stratified error ready for surgical repair"""
    file_path: str
    error_type: str                         # BugType.value string
    severity: ErrorSeverity
    strategy: RepairStrategy
    description: str
    problematic_code: str
    suggested_fix: str
    # Scope context — minimal set of files needed to repair this error
    scope_files: List[str] = field(default_factory=list)
    # Direct imports/deps needed in context
    context_deps: List[str] = field(default_factory=list)
    # Whether a deterministic fixer already exists
    has_deterministic_fix: bool = False

    @property
    def repair_cost(self) -> int:
        """Estimated relative cost: 1=free, 10=expensive LLM"""
        if self.strategy == RepairStrategy.DETERMINISTIC:
            return 1
        if self.strategy == RepairStrategy.PACKAGE_RESOLVE:
            return 1
        if self.strategy == RepairStrategy.STYLE_REPAIR:
            return 2
        if self.strategy == RepairStrategy.ROUTE_GRAPH:
            return 3
        if self.strategy == RepairStrategy.LOCAL_PATCH:
            return 7
        return 0  # IGNORE


# ─────────────────────────────────────────────────────────────────────────────
# STRATEGY TABLE
# Maps (error_type, severity_string) → (ErrorSeverity, RepairStrategy, has_det_fix)
# ─────────────────────────────────────────────────────────────────────────────

ERROR_STRATEGY_MAP: Dict[str, tuple] = {
    # JSX
    "double_brace_jsx":       (ErrorSeverity.CRITICAL, RepairStrategy.DETERMINISTIC,   True),
    "unclosed_tag":           (ErrorSeverity.HIGH,     RepairStrategy.DETERMINISTIC,   True),
    "invalid_jsx_expression": (ErrorSeverity.HIGH,     RepairStrategy.DETERMINISTIC,   False),

    # Imports
    "missing_import":         (ErrorSeverity.HIGH,     RepairStrategy.PACKAGE_RESOLVE, True),
    "unused_import":          (ErrorSeverity.LOW,      RepairStrategy.IGNORE,          False),
    "incorrect_import_path":  (ErrorSeverity.HIGH,     RepairStrategy.PACKAGE_RESOLVE, True),

    # TypeScript
    "type_mismatch":          (ErrorSeverity.MEDIUM,   RepairStrategy.LOCAL_PATCH,     False),
    "missing_type":           (ErrorSeverity.LOW,      RepairStrategy.IGNORE,          False),
    "invalid_interface":      (ErrorSeverity.MEDIUM,   RepairStrategy.LOCAL_PATCH,     False),

    # React
    "missing_key_prop":       (ErrorSeverity.LOW,      RepairStrategy.DETERMINISTIC,   True),
    "invalid_hook_usage":     (ErrorSeverity.MEDIUM,   RepairStrategy.LOCAL_PATCH,     False),
    "undefined_component":    (ErrorSeverity.HIGH,     RepairStrategy.PACKAGE_RESOLVE, True),

    # Tailwind
    "invalid_tailwind_class": (ErrorSeverity.LOW,      RepairStrategy.STYLE_REPAIR,    True),
    "conflicting_classes":    (ErrorSeverity.LOW,      RepairStrategy.STYLE_REPAIR,    True),

    # General
    "syntax_error":           (ErrorSeverity.CRITICAL, RepairStrategy.DETERMINISTIC,   True),
    "empty_file":             (ErrorSeverity.HIGH,     RepairStrategy.DETERMINISTIC,   True),
    "duplicate_export":       (ErrorSeverity.MEDIUM,   RepairStrategy.DETERMINISTIC,   False),
    "incorrect_export":       (ErrorSeverity.MEDIUM,   RepairStrategy.DETERMINISTIC,   True),
}


class ErrorClassifier:
    """
    Classifies raw Bug objects into ClassifiedErrors with:
      - severity ranking
      - repair strategy
      - minimal scope context
      - repair cost estimation
    """

    # Only these file types are relevant for scoping context
    SOURCE_EXTENSIONS = {".tsx", ".ts", ".jsx", ".js", ".css"}

    def classify(self, bug, all_file_paths: List[str]) -> ClassifiedError:
        """Classify a single Bug into a ClassifiedError"""
        bug_type_str = bug.bug_type.value
        severity_str = bug.severity  # "critical" / "error" / "warning"

        # Look up strategy table
        if bug_type_str in ERROR_STRATEGY_MAP:
            sev, strategy, has_det = ERROR_STRATEGY_MAP[bug_type_str]
        else:
            # Unknown error — map raw severity
            sev = self._map_raw_severity(severity_str)
            strategy = RepairStrategy.LOCAL_PATCH if sev.value <= 2 else RepairStrategy.IGNORE
            has_det = False

        # Compute scope: just the broken file (surgical!)
        scope = [bug.file_path] if bug.file_path else []

        # If it's an import error, also include potential target files
        if strategy == RepairStrategy.PACKAGE_RESOLVE:
            scope = self._expand_import_scope(bug.file_path, bug.description, all_file_paths)

        return ClassifiedError(
            file_path=bug.file_path,
            error_type=bug_type_str,
            severity=sev,
            strategy=strategy,
            description=bug.description,
            problematic_code=bug.problematic_code[:200],
            suggested_fix=bug.suggested_fix[:200],
            scope_files=scope,
            has_deterministic_fix=has_det,
        )

    def classify_all(self, bugs: list, all_file_paths: List[str]) -> List[ClassifiedError]:
        """Classify all bugs, return sorted by severity (most critical first)"""
        classified = [self.classify(b, all_file_paths) for b in bugs]
        return sorted(classified, key=lambda e: (e.severity.value, e.repair_cost))

    def filter_actionable(self, errors: List[ClassifiedError]) -> List[ClassifiedError]:
        """Return only errors worth repairing (exclude IGNORE strategy)"""
        return [e for e in errors if e.strategy != RepairStrategy.IGNORE]

    def group_by_file(
        self, errors: List[ClassifiedError]
    ) -> Dict[str, List[ClassifiedError]]:
        """Group errors by their file_path for surgical per-file repair"""
        groups: Dict[str, List[ClassifiedError]] = {}
        for err in errors:
            path = err.file_path
            if path not in groups:
                groups[path] = []
            groups[path].append(err)
        return groups

    def has_critical_errors(self, errors: List[ClassifiedError]) -> bool:
        """True if any error is CRITICAL severity"""
        return any(e.severity == ErrorSeverity.CRITICAL for e in errors)

    def get_repair_summary(self, errors: List[ClassifiedError]) -> dict:
        """Quick stats for logging"""
        by_sev = {}
        by_strat = {}
        for e in errors:
            by_sev[e.severity.name] = by_sev.get(e.severity.name, 0) + 1
            by_strat[e.strategy.value] = by_strat.get(e.strategy.value, 0) + 1
        return {
            "total": len(errors),
            "by_severity": by_sev,
            "by_strategy": by_strat,
            "ignored": sum(1 for e in errors if e.strategy == RepairStrategy.IGNORE),
        }

    # ──────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────

    def _map_raw_severity(self, raw: str) -> ErrorSeverity:
        mapping = {
            "critical": ErrorSeverity.CRITICAL,
            "error":    ErrorSeverity.HIGH,
            "warning":  ErrorSeverity.MEDIUM,
        }
        return mapping.get(raw, ErrorSeverity.LOW)

    def _expand_import_scope(
        self, broken_file: str, description: str, all_files: List[str]
    ) -> List[str]:
        """
        For import errors, find candidate files that might satisfy the import.
        Returns: [broken_file, ...up to 2 candidate targets]
        Maximum 3 files total — stay surgical.
        """
        scope = [broken_file]

        # Extract component name from description e.g. "Component 'Navbar' is used but not imported"
        name = None
        if "'" in description:
            parts = description.split("'")
            if len(parts) >= 2:
                name = parts[1]

        if name:
            candidates = [
                f for f in all_files
                if name.lower() in f.lower() and f != broken_file
            ]
            scope.extend(candidates[:2])  # At most 2 extra files

        return scope
