"""
NOVARYX - Logging Configuration
Unified logging setup for the entire system.

Features:
- Console + file logging
- JSON structured logs for analysis
- Log rotation
- Debug mode toggle
- Performance timing
"""

import os
import sys
import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from typing import Optional
from functools import wraps
import time


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        
        if hasattr(record, "error_code"):
            log_data["error_code"] = record.error_code
        
        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = str(record.exc_info[1])
        
        return json.dumps(log_data)


class NovaryxLogger:
    """
    Centralized logging configuration for NOVARYX.
    """
    
    _instance: Optional['NovaryxLogger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Determine log directory
        if os.getenv("NOVARYX_ENV") == "production":
            self.log_dir = Path.home() / "novaryx" / "logs"
        else:
            # Check if we're in the project directory
            cwd = Path.cwd()
            if (cwd / "system").exists():
                self.log_dir = cwd / "logs"
            else:
                self.log_dir = Path.home() / "novaryx" / "logs"
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log level from environment or default
        log_level_str = os.getenv("NOVARYX_LOG_LEVEL", "INFO")
        self.log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        
        # Configure root logger
        self.root_logger = logging.getLogger("novaryx")
        self.root_logger.setLevel(self.log_level)
        self.root_logger.handlers.clear()
        
        # Add handlers
        self._add_console_handler()
        self._add_file_handler()
        self._add_json_handler()
        self._add_error_handler()
        
        # Silence noisy third-party loggers
        self._silence_third_party()
        
        self._initialized = True
        
        self.root_logger.info(f"Logging initialized (level={log_level_str})")
    
    def _add_console_handler(self):
        """Add colored console output"""
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(self.log_level)
        console.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(message)s',
            datefmt='%H:%M:%S'
        ))
        self.root_logger.addHandler(console)
    
    def _add_file_handler(self):
        """Add rotating file handler"""
        log_file = self.log_dir / f"novaryx_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.root_logger.addHandler(file_handler)
    
    def _add_json_handler(self):
        """Add JSON structured logging"""
        json_file = self.log_dir / f"novaryx_structured_{datetime.now().strftime('%Y%m%d')}.json"
        
        json_handler = logging.handlers.RotatingFileHandler(
            json_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JsonFormatter())
        self.root_logger.addHandler(json_handler)
    
    def _add_error_handler(self):
        """Add separate error log file"""
        error_file = self.log_dir / f"novaryx_errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.root_logger.addHandler(error_handler)
    
    def _silence_third_party(self):
        """Reduce noise from third-party libraries"""
        for lib in ["chromadb", "urllib3", "httpx", "httpcore", "asyncio"]:
            logging.getLogger(lib).setLevel(logging.WARNING)
        
        # Keep httpx quieter
        logging.getLogger("httpx").setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a specific module"""
        if name.startswith("novaryx."):
            return logging.getLogger(name)
        return logging.getLogger(f"novaryx.{name}")
    
    @classmethod
    def set_level(cls, level: str):
        """Change log level at runtime"""
        instance = cls()
        instance.log_level = getattr(logging, level.upper(), logging.INFO)
        instance.root_logger.setLevel(instance.log_level)
        for handler in instance.root_logger.handlers:
            if not isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.setLevel(instance.log_level)
    
    @classmethod
    def enable_debug(cls):
        """Enable debug logging"""
        cls.set_level("DEBUG")
    
    @classmethod
    def disable_debug(cls):
        """Disable debug logging"""
        cls.set_level("INFO")
    
    @classmethod
    def get_log_files(cls) -> list:
        """Get list of log files"""
        instance = cls()
        return sorted(instance.log_dir.glob("*.log"), reverse=True)
    
    @classmethod
    def clean_old_logs(cls, days: int = 30):
        """Remove logs older than specified days"""
        instance = cls()
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for log_file in instance.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
                print(f"Deleted old log: {log_file.name}")


def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"novaryx.{func.__module__}")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.time() - start) * 1000
            logger.debug(f"{func.__name__} completed in {elapsed:.0f}ms")
            return result
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            logger.error(f"{func.__name__} failed after {elapsed:.0f}ms: {e}")
            raise
    return wrapper


class TaskLogger:
    """Logger adapter that includes task context"""
    
    def __init__(self, task_id: str, logger_name: str = "task"):
        self.task_id = task_id
        self.logger = logging.getLogger(f"novaryx.{logger_name}")
    
    def _log(self, level: int, msg: str, **kwargs):
        extra = kwargs.pop("extra", {})
        extra["task_id"] = self.task_id
        self.logger.log(level, f"[{self.task_id[:8]}] {msg}", extra=extra, **kwargs)
    
    def info(self, msg, **kwargs):
        self._log(logging.INFO, msg, **kwargs)
    
    def debug(self, msg, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)
    
    def warning(self, msg, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)
    
    def error(self, msg, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)
    
    def critical(self, msg, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)


# Initialize on import
logger = NovaryxLogger()