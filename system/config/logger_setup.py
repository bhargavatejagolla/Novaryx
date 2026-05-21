#!/usr/bin/env python3
"""
NOVARYX - Phase 0.2
File: system/config/logger_setup.py
Centralized logging configuration
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

# Root directory
NOVARYX_ROOT = Path.cwd()

class NovaryxLogger:
    """Centralized logging for NOVARYX system"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.log_dir = NOVARYX_ROOT / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("novaryx")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # Console handler (INFO and above)
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console.setFormatter(console_format)
        
        # File handler (DEBUG and above - everything)
        log_file = self.log_dir / f"novaryx_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
        )
        file_handler.setFormatter(file_format)
        
        # Error file handler (ERROR and above)
        error_file = self.log_dir / f"novaryx_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        
        # Add handlers
        self.logger.addHandler(console)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        self._initialized = True
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a logger instance"""
        if name:
            return logging.getLogger(f"novaryx.{name}")
        return self.logger
    
    @staticmethod
    def info(msg):
        NovaryxLogger().logger.info(msg)
    
    @staticmethod
    def debug(msg):
        NovaryxLogger().logger.debug(msg)
    
    @staticmethod
    def warning(msg):
        NovaryxLogger().logger.warning(msg)
    
    @staticmethod
    def error(msg):
        NovaryxLogger().logger.error(msg)
    
    @staticmethod
    def critical(msg):
        NovaryxLogger().logger.critical(msg)


# Initialize on import
logger = NovaryxLogger()
