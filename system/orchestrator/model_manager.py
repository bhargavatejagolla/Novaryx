#!/usr/bin/env python3
"""
NOVARYX - Phase 0.2
File: system/orchestrator/model_manager.py
Handles model loading, unloading, and swapping on 16GB constraint
"""

import os
import gc
import time
import psutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Will be used when models are downloaded
# from llama_cpp import Llama

logger = logging.getLogger("novaryx.model_manager")


class ModelStatus(Enum):
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    SWAPPING = "swapping"


@dataclass
class ModelInfo:
    """Runtime information about a loaded model"""
    name: str
    status: ModelStatus
    memory_usage_mb: float = 0.0
    loaded_at: float = 0.0
    tokens_generated: int = 0
    last_used: float = 0.0


class ModelManager:
    """
    Manages local LLM models with memory-aware loading/unloading.
    
    Strategy for 16GB:
    - Only ONE large model loaded at a time
    - Small embedding model stays loaded
    - Swap models by unloading first, then loading
    - Monitor memory continuously
    """
    
    def __init__(self, config):
        self.config = config
        self.loaded_models: Dict[str, Any] = {}  # model_name -> Llama instance
        self.model_info: Dict[str, ModelInfo] = {}
        self.memory_threshold_mb = config.resources.max_memory_gb * 1024 * 0.85  # 85% threshold
        
        # Initialize model info for all configured models
        for model_name, model_config in config.models.items():
            self.model_info[model_name] = ModelInfo(
                name=model_config.name,
                status=ModelStatus.UNLOADED
            )
        
        logger.info("ModelManager initialized")
        
    def get_available_memory(self) -> float:
        """Get available system memory in MB"""
        memory = psutil.virtual_memory()
        return memory.available / (1024 * 1024)
    
    def get_current_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    
    def can_load_model(self, estimated_size_mb: float = 6000) -> bool:
        """Check if enough memory to load a model"""
        available = self.get_available_memory()
        current = self.get_current_usage()
        
        # Need estimated model size + 2GB buffer for system
        required = estimated_size_mb + 2048
        
        can_load = available >= required
        
        logger.info(f"Memory check: Available={available:.0f}MB, "
                   f"Current={current:.0f}MB, Required={required:.0f}MB, Can Load={can_load}")
        
        return can_load
    
    def load_model(self, model_key: str, force: bool = False) -> bool:
        """
        Load a model by key (e.g., 'qwen', 'deepseek')
        Handles automatic unloading if memory is tight
        """
        if model_key not in self.config.models:
            logger.error(f"Unknown model: {model_key}")
            return False
        
        model_config = self.config.models[model_key]
        model_info = self.model_info[model_key]
        
        # Already loaded
        if model_info.status == ModelStatus.LOADED:
            logger.info(f"Model {model_key} already loaded")
            model_info.last_used = time.time()
            return True
        
        # Check memory
        if not self.can_load_model() and not force:
            logger.warning("Insufficient memory. Attempting to free...")
            self.unload_all_unused()
            
            if not self.can_load_model():
                logger.error("Still insufficient memory after cleanup")
                return False
        
        try:
            logger.info(f"Loading model: {model_config.name} from {model_config.path}")
            model_info.status = ModelStatus.LOADING
            
            # TODO: Replace with actual model loading when models are downloaded
            # model = Llama(
            #     model_path=str(Path(model_config.path) / "model.gguf"),
            #     n_ctx=model_config.context_length,
            #     n_threads=model_config.threads,
            #     n_gpu_layers=model_config.gpu_layers,
            #     verbose=False
            # )
            # self.loaded_models[model_key] = model
            
            # Placeholder for now
            self.loaded_models[model_key] = None
            
            model_info.status = ModelStatus.LOADED
            model_info.loaded_at = time.time()
            model_info.last_used = time.time()
            model_info.memory_usage_mb = 6000  # Estimated, will measure later
            
            logger.info(f"Model {model_key} loaded successfully")
            logger.info(f"   Memory usage: {self.get_current_usage():.0f}MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_key}: {e}")
            model_info.status = ModelStatus.ERROR
            return False
    
    def unload_model(self, model_key: str) -> bool:
        """Unload a model and free memory"""
        if model_key not in self.loaded_models:
            return True
        
        try:
            logger.info(f"Unloading model: {model_key}")
            
            # Remove from loaded models
            if model_key in self.loaded_models:
                del self.loaded_models[model_key]
            
            # Update info
            self.model_info[model_key].status = ModelStatus.UNLOADED
            self.model_info[model_key].memory_usage_mb = 0.0
            
            # Force garbage collection
            gc.collect()
            
            logger.info(f"Model {model_key} unloaded")
            logger.info(f"   Available memory: {self.get_available_memory():.0f}MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload model {model_key}: {e}")
            return False
    
    def swap_models(self, unload_key: str, load_key: str) -> bool:
        """
        Swap one model for another - critical for 16GB
        Example: swap_models('qwen', 'deepseek') for repair mode
        """
        logger.info(f"Swapping models: {unload_key} -> {load_key}")
        
        self.model_info[load_key].status = ModelStatus.SWAPPING
        
        # Step 1: Unload current model
        success_unload = self.unload_model(unload_key)
        if not success_unload:
            logger.error(f"Swap failed: could not unload {unload_key}")
            return False
        
        # Step 2: Small delay for memory cleanup
        time.sleep(1)
        gc.collect()
        
        # Step 3: Load new model
        success_load = self.load_model(load_key)
        if not success_load:
            logger.error(f"Swap failed: could not load {load_key}")
            # Try to reload the original
            self.load_model(unload_key)
            return False
        
        logger.info(f"Swap complete: {load_key} is now active")
        return True
    
    def unload_all_unused(self):
        """Unload models not recently used (keep last 5 minutes)"""
        current_time = time.time()
        for model_key in list(self.loaded_models.keys()):
            info = self.model_info[model_key]
            if current_time - info.last_used > 300:  # 5 minutes
                self.unload_model(model_key)
    
    def unload_all(self):
        """Emergency: unload everything"""
        logger.warning("Emergency unload all models")
        for model_key in list(self.loaded_models.keys()):
            self.unload_model(model_key)
    
    def get_active_model(self) -> Optional[str]:
        """Get the currently loaded large model"""
        for key, model in self.loaded_models.items():
            if self.config.models[key].type.value != "embedding":
                return key
        return None
    
    def generate(self, model_key: str, prompt: str, **kwargs) -> str:
        """
        Generate text using a loaded model
        Handles context management
        """
        if model_key not in self.loaded_models:
            success = self.load_model(model_key)
            if not success:
                return f"[ERROR: Could not load model {model_key}]"
        
        model_info = self.model_info[model_key]
        model_info.last_used = time.time()
        
        # TODO: Actual generation when models are available
        return "[MODEL NOT YET DOWNLOADED - Placeholder response]"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of all models"""
        status = {
            "memory_available_mb": self.get_available_memory(),
            "memory_used_mb": self.get_current_usage(),
            "active_model": self.get_active_model(),
            "models": {}
        }
        
        for key, info in self.model_info.items():
            status["models"][key] = {
                "name": info.name,
                "status": info.status.value,
                "memory_mb": info.memory_usage_mb,
                "tokens_generated": info.tokens_generated,
                "loaded_for_seconds": time.time() - info.loaded_at if info.loaded_at > 0 else 0
            }
        
        return status
    
    def display_status(self):
        """Display current model status"""
        status = self.get_status()
        print("\n" + "=" * 50)
        print("MODEL MANAGER STATUS")
        print("=" * 50)
        print(f"Memory: {status['memory_used_mb']:.0f}MB used / {status['memory_available_mb']:.0f}MB available")
        print(f"Active: {status['active_model'] or 'None'}")
        print()
        for key, info in status["models"].items():
            indicator = "[ACTIVE]" if info["status"] == "loaded" else "[IDLE]"
            print(f"  {indicator} {key}: {info['status']}")
        print("=" * 50)
