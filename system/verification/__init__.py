"""
NOVARYX - Verification Pipeline
Validates generated projects for correctness and quality.

Connected to:
  - Repair Engine (verify → repair loop)
  - Assembly Engine (post-generation verify)
  - Project Builder (pre-output verify)

Checks:
  - TypeScript compilation
  - Import resolution
  - Build success
  - Quality thresholds
"""

from .verification_pipeline import VerificationPipeline, VerificationResult
from .typescript_checker import TypeScriptChecker
from .import_checker import ImportChecker
from .build_checker import BuildChecker
from .quality_gate import QualityGate

__all__ = [
    "VerificationPipeline",
    "VerificationResult",
    "TypeScriptChecker",
    "ImportChecker",
    "BuildChecker",
    "QualityGate",
]