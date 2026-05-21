"""
NOVARYX - Error Handler
Centralized error handling with recovery strategies.
"""

import sys
import traceback
import logging
from typing import Optional, Callable, Dict, Any, Type
from datetime import datetime
from functools import wraps

from .error_codes import ErrorCodes, ErrorCode, ErrorSeverity, ErrorArea

logger = logging.getLogger("novaryx.error_handler")


class NovaryxError(Exception):
    """Base exception for all NOVARYX errors"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        details: str = "",
        original_error: Exception = None
    ):
        self.error_code = error_code
        self.details = details
        self.original_error = original_error
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc() if original_error else ""
        
        message = f"[{error_code.code}] {error_code.message}"
        if details:
            message += f": {details}"
        
        super().__init__(message)


class ErrorContext:
    """Context information when an error occurs"""
    
    def __init__(self):
        self.operation: str = ""
        self.task_id: str = ""
        self.project_name: str = ""
        self.additional_data: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "task_id": self.task_id,
            "project_name": self.project_name,
            **self.additional_data
        }


class ErrorHandler:
    """
    Centralized error handler for NOVARYX.
    
    Provides:
    - Consistent error logging
    - Recovery strategy selection
    - Graceful degradation
    - Error statistics tracking
    """
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_history: list = []
        self.max_history: int = 100
        self.recovery_hooks: Dict[str, Callable] = {}
        self.fallback_hooks: Dict[str, Callable] = {}
        
        logger.info("ErrorHandler initialized")
    
    def handle_error(
        self,
        error: Exception,
        context: ErrorContext = None,
        severity_override: ErrorSeverity = None
    ) -> Dict[str, Any]:
        """
        Handle any error with appropriate strategy.
        
        Args:
            error: The exception that occurred
            context: Operation context when error happened
            severity_override: Override error severity
        
        Returns:
            Dict with handling result
        """
        
        # If it's our custom error, use its code
        if isinstance(error, NovaryxError):
            error_code = error.error_code
            details = error.details
        else:
            # Map common exceptions to our error codes
            error_code = self._map_exception(error)
            details = str(error)
        
        # Override severity if needed
        if severity_override:
            severity = severity_override
        else:
            severity = error_code.severity
        
        # Build error record
        error_record = {
            "code": error_code.code,
            "severity": severity.value,
            "area": error_code.area.value,
            "message": error_code.message,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "recoverable": error_code.recoverable,
            "suggested_action": error_code.suggested_action,
            "context": context.to_dict() if context else {},
            "traceback": traceback.format_exc()[:500]  # Last 500 chars
        }
        
        # Track counts
        self.error_counts[error_code.code] = self.error_counts.get(error_code.code, 0) + 1
        
        # Store in history
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
        
        # Log appropriately
        self._log_error(error_record)
        
        # Try recovery if possible
        recovery_result = None
        if error_code.recoverable:
            recovery_result = self._attempt_recovery(error_code, context)
            error_record["recovery_attempted"] = True
            error_record["recovery_result"] = recovery_result
        
        # Critical errors - consider system halt
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR: {error_code.code} - {error_code.message}")
            self._handle_critical(error_code, context)
        
        return error_record
    
    def _map_exception(self, error: Exception) -> ErrorCode:
        """Map Python exceptions to NOVARYX error codes"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        # Memory errors
        if isinstance(error, MemoryError) or "memory" in error_msg:
            return ErrorCodes.SYSTEM_MEMORY_CRITICAL
        
        # Timeout errors
        if isinstance(error, TimeoutError) or "timeout" in error_msg:
            return ErrorCodes.SYSTEM_TIMEOUT
        
        # Connection errors
        if "connection" in error_msg or "connect" in error_msg:
            return ErrorCodes.INFERENCE_PROVIDER_UNAVAILABLE
        
        # File/IO errors
        if isinstance(error, (FileNotFoundError, IOError)):
            return ErrorCodes.TEMPLATE_NOT_FOUND
        
        # Import errors
        if isinstance(error, ImportError) or isinstance(error, ModuleNotFoundError):
            return ErrorCodes.SYSTEM_INIT_FAILED
        
        # JSON/config errors
        if isinstance(error, (ValueError, KeyError)) and ("json" in error_msg or "config" in error_msg):
            return ErrorCodes.SYSTEM_CONFIG_INVALID
        
        # Default: system error
        return ErrorCode(
            code="NOV-1999",
            severity=ErrorSeverity.ERROR,
            area=ErrorArea.SYSTEM,
            message=f"Unexpected error: {type(error).__name__}",
            recoverable=True,
            suggested_action="Check logs for details",
            retry_allowed=True,
            max_retries=1
        )
    
    def _log_error(self, error_record: Dict[str, Any]):
        """Log error with appropriate level"""
        severity = error_record["severity"]
        code = error_record["code"]
        message = error_record["message"]
        details = error_record.get("details", "")
        
        log_msg = f"[{code}] {message}"
        if details:
            log_msg += f" | {details[:200]}"
        
        if severity == "critical":
            logger.critical(log_msg)
        elif severity == "error":
            logger.error(log_msg)
        elif severity == "warning":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
    
    def _attempt_recovery(
        self,
        error_code: ErrorCode,
        context: ErrorContext = None
    ) -> Optional[Dict[str, Any]]:
        """Attempt to recover from an error"""
        
        recovery_key = error_code.code
        
        # Check for registered recovery hook
        if recovery_key in self.recovery_hooks:
            try:
                result = self.recovery_hooks[recovery_key](error_code, context)
                logger.info(f"Recovery attempted for {recovery_key}: success")
                return {"success": True, "result": result}
            except Exception as e:
                logger.warning(f"Recovery failed for {recovery_key}: {e}")
                return {"success": False, "error": str(e)}
        
        # Default recovery: just log and continue
        logger.info(f"No specific recovery for {recovery_key}, using default")
        return {"success": True, "method": "default_continue"}
    
    def _handle_critical(self, error_code: ErrorCode, context: ErrorContext = None):
        """Handle critical errors"""
        # Try to save state before potentially crashing
        try:
            from system.orchestrator.state_machine.state_persistence import StatePersistence
            persistence = StatePersistence()
            # Save whatever state we can
            logger.info("Attempting to save state before handling critical error...")
        except Exception:
            pass
        
        # Execute fallback hooks
        if error_code.code in self.fallback_hooks:
            try:
                self.fallback_hooks[error_code.code](error_code, context)
            except Exception as e:
                logger.critical(f"Fallback hook also failed: {e}")
    
    def register_recovery_hook(self, error_code: str, hook: Callable):
        """Register a custom recovery function for an error code"""
        self.recovery_hooks[error_code] = hook
        logger.info(f"Recovery hook registered for: {error_code}")
    
    def register_fallback_hook(self, error_code: str, hook: Callable):
        """Register a fallback function for critical errors"""
        self.fallback_hooks[error_code] = hook
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        stats = {
            "total_errors": sum(self.error_counts.values()),
            "unique_errors": len(self.error_counts),
            "by_code": dict(self.error_counts),
            "by_severity": {"critical": 0, "error": 0, "warning": 0, "info": 0},
            "recent_errors": self.error_history[-5:]
        }
        
        for record in self.error_history:
            severity = record.get("severity", "info")
            if severity in stats["by_severity"]:
                stats["by_severity"][severity] += 1
        
        return stats
    
    def display_stats(self):
        """Display error statistics"""
        stats = self.get_error_stats()
        
        print("\n" + "=" * 50)
        print("📊 ERROR STATISTICS")
        print("=" * 50)
        print(f"   Total Errors: {stats['total_errors']}")
        print(f"   Unique Types: {stats['unique_errors']}")
        
        if stats["by_severity"]:
            print(f"   By Severity:")
            for sev, count in stats["by_severity"].items():
                if count > 0:
                    icon = {"critical": "🔴", "error": "🟠", "warning": "🟡", "info": "🔵"}
                    print(f"      {icon.get(sev, '⚪')} {sev}: {count}")
        
        if stats["recent_errors"]:
            print(f"\n   Recent Errors:")
            for err in stats["recent_errors"][-3:]:
                print(f"      [{err['code']}] {err['message'][:50]}")
        
        print("=" * 50 + "\n")
    
    def clear_history(self):
        """Clear error history"""
        self.error_history = []
        self.error_counts = {}
        logger.info("Error history cleared")


def handle_errors(
    error_code: ErrorCode = None,
    context_operation: str = "",
    reraise: bool = False
):
    """
    Decorator for automatic error handling.
    
    Usage:
        @handle_errors(context_operation="generate_page")
        def generate_page(self, page_spec):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ctx = ErrorContext()
            ctx.operation = context_operation or func.__name__
            
            try:
                return func(*args, **kwargs)
            except NovaryxError as e:
                handler = ErrorHandler()
                handler.handle_error(e, ctx)
                if reraise:
                    raise
                return None
            except Exception as e:
                handler = ErrorHandler()
                mapped_code = handler._map_exception(e)
                novaryx_error = NovaryxError(mapped_code, str(e), e)
                handler.handle_error(novaryx_error, ctx)
                if reraise:
                    raise novaryx_error
                return None
        
        return wrapper
    return decorator


# Global handler instance
_global_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get or create the global error handler"""
    global _global_handler
    if _global_handler is None:
        _global_handler = ErrorHandler()
    return _global_handler


# ---- Test ----

def test_error_handler():
    """Test the error handling system"""
    
    print("\n" + "=" * 60)
    print("🧪 ERROR HANDLER TEST")
    print("=" * 60)
    
    handler = ErrorHandler()
    
    # Test 1: Custom NOVARYX error
    print("\n📋 Test 1: Custom error")
    try:
        raise NovaryxError(
            ErrorCodes.INFERENCE_GENERATION_FAILED,
            details="Model returned empty response"
        )
    except NovaryxError as e:
        handler.handle_error(e, ErrorContext())
    
    # Test 2: Python exception mapping
    print("\n📋 Test 2: Exception mapping")
    try:
        raise ConnectionError("Failed to connect to Ollama")
    except Exception as e:
        handler.handle_error(e, ErrorContext())
    
    # Test 3: Memory warning
    print("\n📋 Test 3: Memory warning")
    try:
        raise MemoryError("Cannot allocate 8GB")
    except Exception as e:
        handler.handle_error(e, ErrorContext())
    
    # Test 4: Recovery hook
    print("\n📋 Test 4: Recovery hook")
    
    def my_recovery(error_code, context):
        print(f"      Custom recovery for {error_code.code}!")
        return "recovered"
    
    handler.register_recovery_hook("NOV-2103", my_recovery)
    
    try:
        raise NovaryxError(ErrorCodes.INFERENCE_GENERATION_FAILED, "Test recovery")
    except NovaryxError as e:
        handler.handle_error(e, ErrorContext())
    
    # Display stats
    handler.display_stats()
    
    # Display all error codes
    ErrorCodes.display_all()
    
    print("✅ Error handler test complete\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_error_handler()