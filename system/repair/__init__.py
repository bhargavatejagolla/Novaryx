"""
NOVARYX - Automatic Repair Engine
Detects, diagnoses, and fixes bugs in generated code.

Architecture:
  error_classifier.py   — classifies bugs into severity/strategy/scope
  surgical_repair.py    — budget-aware, per-file surgical orchestrator
  repair_engine.py      — legacy whole-project (kept for compat)
  bug_detector.py       — pattern-based detection
  fixers.py             — deterministic regex fixers
  llm_repairer.py       — LLM repair with 60s timeout (backup only)
"""

from .repair_engine import RepairEngine, RepairResult
from .bug_detector import BugDetector, BugType, Bug
from .fixers import FixRegistry
from .llm_repairer import LLMRepairer
from .repair_validator import RepairValidator
from .error_classifier import ErrorClassifier, ErrorSeverity, RepairStrategy, ClassifiedError
from .surgical_repair import SurgicalRepairOrchestrator, SurgicalRepairResult, RepairBudget

__all__ = [
    "RepairEngine", "RepairResult",
    "BugDetector", "BugType", "Bug",
    "FixRegistry", "LLMRepairer", "RepairValidator",
    "ErrorClassifier", "ErrorSeverity", "RepairStrategy", "ClassifiedError",
    "SurgicalRepairOrchestrator", "SurgicalRepairResult", "RepairBudget",
]