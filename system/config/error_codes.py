"""
NOVARYX - Error Codes
Centralized error code registry for the entire system.

Format: NOV-XXXX
  - First digit: Severity (1=critical, 2=error, 3=warning, 4=info)
  - Second digit: System area (0=system, 1=inference, 2=rag, 3=orchestrator, 4=generation, 5=verification, 6=deployment)
  - Last two: Specific error
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class ErrorSeverity(Enum):
    CRITICAL = "critical"   # System cannot continue
    ERROR = "error"         # Current operation failed
    WARNING = "warning"     # Something unexpected but recoverable
    INFO = "info"           # Informational only


class ErrorArea(Enum):
    SYSTEM = "system"
    INFERENCE = "inference"
    RAG = "rag"
    ORCHESTRATOR = "orchestrator"
    GENERATION = "generation"
    VERIFICATION = "verification"
    DEPLOYMENT = "deployment"
    TEMPLATE = "template"
    STATE = "state"


@dataclass
class ErrorCode:
    code: str
    severity: ErrorSeverity
    area: ErrorArea
    message: str
    recoverable: bool
    suggested_action: str
    retry_allowed: bool = True
    max_retries: int = 3


class ErrorCodes:
    """Complete registry of all NOVARYX error codes"""
    
    # ---- System Errors (1xx) ----
    SYSTEM_INIT_FAILED = ErrorCode(
        code="NOV-1001",
        severity=ErrorSeverity.CRITICAL,
        area=ErrorArea.SYSTEM,
        message="System initialization failed",
        recoverable=False,
        suggested_action="Check logs, verify all dependencies installed",
        retry_allowed=False,
        max_retries=0
    )
    
    SYSTEM_MEMORY_CRITICAL = ErrorCode(
        code="NOV-1002",
        severity=ErrorSeverity.CRITICAL,
        area=ErrorArea.SYSTEM,
        message="System memory critically low",
        recoverable=True,
        suggested_action="Free memory by unloading models, restart system",
        retry_allowed=True,
        max_retries=1
    )
    
    SYSTEM_MEMORY_WARNING = ErrorCode(
        code="NOV-3001",
        severity=ErrorSeverity.WARNING,
        area=ErrorArea.SYSTEM,
        message="System memory running low",
        recoverable=True,
        suggested_action="Consider unloading unused models",
        retry_allowed=True,
        max_retries=3
    )
    
    SYSTEM_TIMEOUT = ErrorCode(
        code="NOV-1003",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.SYSTEM,
        message="Operation timed out",
        recoverable=True,
        suggested_action="Increase timeout or reduce workload",
        retry_allowed=True,
        max_retries=2
    )
    
    SYSTEM_CONFIG_INVALID = ErrorCode(
        code="NOV-1004",
        severity=ErrorSeverity.CRITICAL,
        area=ErrorArea.SYSTEM,
        message="System configuration is invalid",
        recoverable=False,
        suggested_action="Check config/system_config.json for errors",
        retry_allowed=False,
        max_retries=0
    )
    
    SYSTEM_DISK_FULL = ErrorCode(
        code="NOV-1005",
        severity=ErrorSeverity.CRITICAL,
        area=ErrorArea.SYSTEM,
        message="Disk storage is full",
        recoverable=True,
        suggested_action="Free disk space, clean old projects and snapshots",
        retry_allowed=True,
        max_retries=1
    )
    
    # ---- Inference Errors (2xx) ----
    INFERENCE_PROVIDER_UNAVAILABLE = ErrorCode(
        code="NOV-2101",
        severity=ErrorSeverity.CRITICAL,
        area=ErrorArea.INFERENCE,
        message="No inference provider available",
        recoverable=False,
        suggested_action="Start Ollama: 'ollama serve' or set GEMINI_API_KEY",
        retry_allowed=False,
        max_retries=0
    )
    
    INFERENCE_MODEL_NOT_FOUND = ErrorCode(
        code="NOV-2102",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.INFERENCE,
        message="Requested model not found",
        recoverable=True,
        suggested_action="Pull the model: 'ollama pull <model_name>'",
        retry_allowed=False,
        max_retries=0
    )
    
    INFERENCE_GENERATION_FAILED = ErrorCode(
        code="NOV-2103",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.INFERENCE,
        message="Text generation failed",
        recoverable=True,
        suggested_action="Retry with different parameters or model",
        retry_allowed=True,
        max_retries=3
    )
    
    INFERENCE_EMBEDDING_FAILED = ErrorCode(
        code="NOV-2104",
        severity=ErrorSeverity.WARNING,
        area=ErrorArea.INFERENCE,
        message="Embedding generation failed",
        recoverable=True,
        suggested_action="Fallback to sentence-transformers or retry",
        retry_allowed=True,
        max_retries=2
    )
    
    INFERENCE_CONTEXT_OVERFLOW = ErrorCode(
        code="NOV-2105",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.INFERENCE,
        message="Context window exceeded",
        recoverable=True,
        suggested_action="Reduce prompt size, split into chunks",
        retry_allowed=True,
        max_retries=2
    )
    
    INFERENCE_RATE_LIMITED = ErrorCode(
        code="NOV-2106",
        severity=ErrorSeverity.WARNING,
        area=ErrorArea.INFERENCE,
        message="API rate limit reached",
        recoverable=True,
        suggested_action="Wait and retry, or switch to local model",
        retry_allowed=True,
        max_retries=5
    )
    
    # ---- RAG Errors (3xx) ----
    RAG_COLLECTION_NOT_FOUND = ErrorCode(
        code="NOV-2201",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.RAG,
        message="ChromaDB collection not found",
        recoverable=True,
        suggested_action="Reinitialize ChromaDB: run init_rag.py",
        retry_allowed=True,
        max_retries=1
    )
    
    RAG_EMBEDDING_FAILED = ErrorCode(
        code="NOV-2202",
        severity=ErrorSeverity.WARNING,
        area=ErrorArea.RAG,
        message="Embedding generation failed for retrieval",
        recoverable=True,
        suggested_action="Check embedding model availability",
        retry_allowed=True,
        max_retries=3
    )
    
    RAG_NO_RESULTS = ErrorCode(
        code="NOV-3201",
        severity=ErrorSeverity.WARNING,
        area=ErrorArea.RAG,
        message="No matching results in vector search",
        recoverable=True,
        suggested_action="Use fallback template, broaden search query",
        retry_allowed=False,
        max_retries=0
    )
    
    RAG_INDEX_CORRUPTED = ErrorCode(
        code="NOV-2203",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.RAG,
        message="ChromaDB index may be corrupted",
        recoverable=True,
        suggested_action="Reset ChromaDB: run init_rag.py --reset",
        retry_allowed=True,
        max_retries=1
    )
    
    # ---- Orchestrator Errors (4xx) ----
    ORCHESTRATOR_PIPELINE_FAILED = ErrorCode(
        code="NOV-2301",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.ORCHESTRATOR,
        message="Generation pipeline step failed",
        recoverable=True,
        suggested_action="Check step logs, retry or repair",
        retry_allowed=True,
        max_retries=3
    )
    
    ORCHESTRATOR_INVALID_STATE = ErrorCode(
        code="NOV-2302",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.ORCHESTRATOR,
        message="Invalid state transition attempted",
        recoverable=True,
        suggested_action="Check state machine, recover from saved state",
        retry_allowed=True,
        max_retries=1
    )
    
    ORCHESTRATOR_AGENT_FAILED = ErrorCode(
        code="NOV-2303",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.ORCHESTRATOR,
        message="Agent execution failed",
        recoverable=True,
        suggested_action="Route to repair agent, retry generation",
        retry_allowed=True,
        max_retries=3
    )
    
    # ---- Generation Errors (5xx) ----
    GENERATION_PAGE_FAILED = ErrorCode(
        code="NOV-2401",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.GENERATION,
        message="Page generation failed",
        recoverable=True,
        suggested_action="Retry page generation with reduced complexity",
        retry_allowed=True,
        max_retries=2
    )
    
    GENERATION_COMPONENT_FAILED = ErrorCode(
        code="NOV-2402",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.GENERATION,
        message="Component generation failed",
        recoverable=True,
        suggested_action="Retry component generation",
        retry_allowed=True,
        max_retries=3
    )
    
    GENERATION_SCHEMA_FAILED = ErrorCode(
        code="NOV-2403",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.GENERATION,
        message="Database schema generation failed",
        recoverable=True,
        suggested_action="Retry schema generation with simpler model",
        retry_allowed=True,
        max_retries=2
    )
    
    GENERATION_OUTPUT_TOO_LARGE = ErrorCode(
        code="NOV-3401",
        severity=ErrorSeverity.WARNING,
        area=ErrorArea.GENERATION,
        message="Generated output exceeds size limit",
        recoverable=True,
        suggested_action="Split generation into smaller chunks",
        retry_allowed=True,
        max_retries=1
    )
    
    # ---- Verification Errors (6xx) ----
    VERIFICATION_SYNTAX_ERROR = ErrorCode(
        code="NOV-2501",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.VERIFICATION,
        message="Syntax errors found in generated code",
        recoverable=True,
        suggested_action="Route to repair agent for fixing",
        retry_allowed=True,
        max_retries=3
    )
    
    VERIFICATION_TYPE_ERROR = ErrorCode(
        code="NOV-2502",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.VERIFICATION,
        message="TypeScript type errors found",
        recoverable=True,
        suggested_action="Route to repair agent for type fixing",
        retry_allowed=True,
        max_retries=3
    )
    
    VERIFICATION_IMPORT_ERROR = ErrorCode(
        code="NOV-2503",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.VERIFICATION,
        message="Import resolution errors found",
        recoverable=True,
        suggested_action="Fix import paths, add missing dependencies",
        retry_allowed=True,
        max_retries=2
    )
    
    VERIFICATION_BUILD_FAILED = ErrorCode(
        code="NOV-2504",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.VERIFICATION,
        message="Project build failed",
        recoverable=True,
        suggested_action="Check build configuration, fix errors",
        retry_allowed=True,
        max_retries=3
    )
    
    # ---- Deployment Errors (7xx) ----
    DEPLOYMENT_DOCKER_FAILED = ErrorCode(
        code="NOV-2601",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.DEPLOYMENT,
        message="Docker deployment failed",
        recoverable=True,
        suggested_action="Check Dockerfile, verify Docker is running",
        retry_allowed=True,
        max_retries=2
    )
    
    DEPLOYMENT_LOCAL_FAILED = ErrorCode(
        code="NOV-2602",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.DEPLOYMENT,
        message="Local deployment failed",
        recoverable=True,
        suggested_action="Check port availability, dependencies",
        retry_allowed=True,
        max_retries=2
    )
    
    # ---- Template Errors (8xx) ----
    TEMPLATE_NOT_FOUND = ErrorCode(
        code="NOV-2701",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.TEMPLATE,
        message="Template not found in registry",
        recoverable=True,
        suggested_action="Check template ID, reseed templates",
        retry_allowed=False,
        max_retries=0
    )
    
    TEMPLATE_VALIDATION_FAILED = ErrorCode(
        code="NOV-2702",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.TEMPLATE,
        message="Template validation failed",
        recoverable=True,
        suggested_action="Fix template structure, check required files",
        retry_allowed=False,
        max_retries=0
    )
    
    # ---- State Machine Errors (9xx) ----
    STATE_TRANSITION_INVALID = ErrorCode(
        code="NOV-2801",
        severity=ErrorSeverity.ERROR,
        area=ErrorArea.STATE,
        message="Invalid state transition",
        recoverable=True,
        suggested_action="Check valid transitions, recover from saved state",
        retry_allowed=True,
        max_retries=1
    )
    
    STATE_RECOVERY_FAILED = ErrorCode(
        code="NOV-2802",
        severity=ErrorSeverity.CRITICAL,
        area=ErrorArea.STATE,
        message="State recovery failed",
        recoverable=False,
        suggested_action="Reset to IDLE state, check logs",
        retry_allowed=False,
        max_retries=0
    )
    
    # ---- Registry ----
    _registry: Dict[str, ErrorCode] = {}
    
    @classmethod
    def get_all_codes(cls) -> Dict[str, ErrorCode]:
        """Get all registered error codes"""
        if not cls._registry:
            for attr_name in dir(cls):
                attr = getattr(cls, attr_name)
                if isinstance(attr, ErrorCode):
                    cls._registry[attr.code] = attr
        return cls._registry
    
    @classmethod
    def get_error(cls, code: str) -> Optional[ErrorCode]:
        """Get error by code"""
        return cls.get_all_codes().get(code)
    
    @classmethod
    def get_errors_by_area(cls, area: ErrorArea) -> list:
        """Get all errors for a specific area"""
        return [e for e in cls.get_all_codes().values() if e.area == area]
    
    @classmethod
    def get_errors_by_severity(cls, severity: ErrorSeverity) -> list:
        """Get all errors of a specific severity"""
        return [e for e in cls.get_all_codes().values() if e.severity == severity]
    
    @classmethod
    def display_all(cls):
        """Display all error codes"""
        print("\n" + "=" * 70)
        print("📋 NOVARYX ERROR CODE REGISTRY")
        print("=" * 70)
        
        by_area = {}
        for error in cls.get_all_codes().values():
            area = error.area.value
            if area not in by_area:
                by_area[area] = []
            by_area[area].append(error)
        
        for area, errors in sorted(by_area.items()):
            print(f"\n  [{area.upper()}]")
            for e in errors:
                sev_icon = {"critical": "🔴", "error": "🟠", "warning": "🟡", "info": "🔵"}
                icon = sev_icon.get(e.severity.value, "⚪")
                rec = "↻" if e.recoverable else "✕"
                print(f"    {icon} {e.code}: {e.message} [{rec}]")
        
        print("\n" + "=" * 70)
        print(f"  Total: {len(cls.get_all_codes())} error codes")
        print("=" * 70 + "\n")