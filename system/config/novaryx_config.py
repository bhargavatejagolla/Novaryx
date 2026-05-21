#!/usr/bin/env python3
"""
NOVARYX - Phase 0.2
File: system/config/novaryx_config.py
Core system configuration with validation
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List
from enum import Enum

# Use current workspace root
NOVARYX_ROOT = Path.cwd()

class ModelType(Enum):
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    EMBEDDING = "embedding"


class GenerationPhase(Enum):
    IDLE = "idle"
    PARSING_PROMPT = "parsing_prompt"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    GENERATING = "generating"
    VERIFYING = "verifying"
    REPAIRING = "repairing"
    DEPLOYING = "deploying"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class ModelConfig:
    """Configuration for a single model"""
    name: str
    path: str
    type: ModelType
    context_length: int = 8192
    temperature: float = 0.1
    top_p: float = 0.9
    max_tokens: int = 2048
    gpu_layers: int = 0
    threads: int = 4
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d['type'] = self.type.value
        return d


@dataclass
class ResourceLimits:
    """System resource constraints"""
    max_memory_gb: float = 14.0
    max_cpu_cores: int = 4
    max_parallel_agents: int = 2
    generation_timeout_seconds: int = 600
    max_pages_per_generation: int = 20
    max_repair_attempts: int = 3


@dataclass
class StorageConfig:
    """Storage paths and limits"""
    novaryx_root: Path = NOVARYX_ROOT
    projects_dir: Path = None
    snapshots_dir: Path = None
    templates_dir: Path = None
    models_dir: Path = None
    logs_dir: Path = None
    chromadb_dir: Path = None
    deployments_dir: Path = None
    max_project_size_mb: int = 500
    auto_cleanup_days: int = 30
    
    def __post_init__(self):
        if self.projects_dir is None:
            self.projects_dir = self.novaryx_root / "projects"
        if self.snapshots_dir is None:
            self.snapshots_dir = self.novaryx_root / "snapshots"
        if self.templates_dir is None:
            self.templates_dir = self.novaryx_root / "system" / "templates"
        if self.models_dir is None:
            self.models_dir = self.novaryx_root / "system" / "models"
        if self.logs_dir is None:
            self.logs_dir = self.novaryx_root / "logs"
        if self.chromadb_dir is None:
            self.chromadb_dir = self.novaryx_root / "system" / "rag_engine" / "chromadb"
        if self.deployments_dir is None:
            self.deployments_dir = self.novaryx_root / "deployments"


@dataclass
class ChromaDBConfig:
    """ChromaDB vector database configuration"""
    host: str = "localhost"
    port: int = 8000
    persist_directory: str = ""
    collection_name: str = "novaryx_templates"
    embedding_dimension: int = 384
    distance_metric: str = "cosine"
    index_size: int = 10000
    
    def __post_init__(self):
        if not self.persist_directory:
            self.persist_directory = str(
                NOVARYX_ROOT / "system" / "rag_engine" / "chromadb"
            )


@dataclass
class PocketBaseConfig:
    """PocketBase backend configuration"""
    version: str = "0.22.0"
    port: int = 8090
    data_dir: str = ""
    public_dir: str = ""
    admin_email: str = "admin@novaryx.local"
    
    def __post_init__(self):
        if not self.data_dir:
            self.data_dir = str(NOVARYX_ROOT / "system" / "pocketbase" / "data")
        if not self.public_dir:
            self.public_dir = str(NOVARYX_ROOT / "system" / "pocketbase" / "public")


@dataclass
class GenerationPreset:
    """Predefined generation presets"""
    name: str
    temperature: float
    max_tokens: int
    repair_attempts: int
    creativity_level: str  # "strict", "balanced", "creative"
    template_priority: str  # "performance", "animation", "minimal"


class NovaryxConfig:
    """Master configuration for NOVARYX system"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.root = NOVARYX_ROOT
        self.config_path = config_path or (self.root / "config" / "system_config.json")
        
        # Initialize with defaults
        self.models: Dict[str, ModelConfig] = {}
        self.resources = ResourceLimits()
        self.storage = StorageConfig()
        self.chromadb = ChromaDBConfig()
        self.pocketbase = PocketBaseConfig()
        self.current_phase = GenerationPhase.IDLE
        
        # Generation presets
        self.presets: Dict[str, GenerationPreset] = {
            "production": GenerationPreset(
                name="production",
                temperature=0.1,
                max_tokens=2048,
                repair_attempts=3,
                creativity_level="strict",
                template_priority="performance"
            ),
            "startup": GenerationPreset(
                name="startup",
                temperature=0.2,
                max_tokens=3072,
                repair_attempts=2,
                creativity_level="balanced",
                template_priority="animation"
            ),
            "creative": GenerationPreset(
                name="creative",
                temperature=0.3,
                max_tokens=4096,
                repair_attempts=1,
                creativity_level="creative",
                template_priority="animation"
            )
        }
        
        # Load existing config if available
        self.load()
        
    def setup_default_models(self):
        """Configure default local models"""
        self.models = {
            "qwen": ModelConfig(
                name="qwen2.5-coder-7b-instruct",
                path=str(self.storage.models_dir / "qwen"),
                type=ModelType.QWEN,
                context_length=8192,
                temperature=0.1,
                max_tokens=2048,
                gpu_layers=0,
                threads=4
            ),
            "deepseek": ModelConfig(
                name="deepseek-coder-7b-instruct",
                path=str(self.storage.models_dir / "deepseek"),
                type=ModelType.DEEPSEEK,
                context_length=8192,
                temperature=0.1,
                max_tokens=2048,
                gpu_layers=0,
                threads=4
            ),
            "embedding": ModelConfig(
                name="all-MiniLM-L6-v2",
                path=str(self.storage.models_dir / "embeddings_model"),
                type=ModelType.EMBEDDING,
                context_length=512,
                temperature=0.0,
                max_tokens=512,
                gpu_layers=0,
                threads=2
            )
        }
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate configuration completeness"""
        errors = []
        
        # Check root exists
        if not self.root.exists():
            errors.append(f"Root directory not found: {self.root}")
        
        # Check model paths
        for model_name, model in self.models.items():
            model_path = Path(model.path)
            if not model_path.exists():
                errors.append(f"Model directory not found: {model_name} at {model_path}")
        
        # Check storage directories
        storage_checks = [
            ("projects", self.storage.projects_dir),
            ("templates", self.storage.templates_dir),
            ("logs", self.storage.logs_dir),
            ("chromadb", self.storage.chromadb_dir),
        ]
        for name, path in storage_checks:
            if not Path(path).exists():
                errors.append(f"Storage directory missing: {name} at {path}")
        
        # Validate resource limits
        if self.resources.max_memory_gb > 14:
            errors.append(f"Memory limit too high for 16GB system: {self.resources.max_memory_gb}GB")
        
        if self.resources.max_parallel_agents > 3:
            errors.append(f"Too many parallel agents for 16GB: {self.resources.max_parallel_agents}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def save(self):
        """Save configuration to disk"""
        config_data = {
            "version": "0.2.0",
            "root": str(self.root),
            "current_phase": self.current_phase.value,
            "models": {name: model.to_dict() for name, model in self.models.items()},
            "resources": asdict(self.resources),
            "storage": {k: str(v) if isinstance(v, Path) else v for k, v in asdict(self.storage).items()},
            "chromadb": asdict(self.chromadb),
            "pocketbase": asdict(self.pocketbase),
            "presets": {name: asdict(preset) for name, preset in self.presets.items()}
        }
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
    
    def load(self):
        """Load configuration from disk"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding='utf-8') as f:
                data = json.load(f)
            
            # Load models
            if "models" in data:
                for name, model_data in data["models"].items():
                    model_data['type'] = ModelType(model_data['type'])
                    self.models[name] = ModelConfig(**model_data)
            
            # Load resources
            if "resources" in data:
                self.resources = ResourceLimits(**data["resources"])
            
            # Load storage
            if "storage" in data:
                storage_data = data["storage"].copy()
                storage_data.pop("novaryx_root", None)
                storage_data.pop("root", None)  # Handle legacy key from Phase 0.1
                # Convert strings back to Paths where appropriate
                for k, v in storage_data.items():
                    if k.endswith('_dir') and v:
                        storage_data[k] = Path(v)
                self.storage = StorageConfig(**storage_data)
            
            # Load chromadb
            if "chromadb" in data:
                self.chromadb = ChromaDBConfig(**data["chromadb"])
            
            # Load phase
            if "current_phase" in data:
                self.current_phase = GenerationPhase(data["current_phase"])
            
            return True
        return False
    
    def display(self):
        """Display current configuration"""
        print("=" * 60)
        print("NOVARYX SYSTEM CONFIGURATION")
        print("=" * 60)
        print(f"Location: {self.root}")
        print(f"Phase: {self.current_phase.value}")
        print()
        print("Models:")
        for name, model in self.models.items():
            print(f"   * {name}: {model.name}")
            print(f"     Context: {model.context_length} tokens")
            print(f"     Temperature: {model.temperature}")
        print()
        print("Resources:")
        print(f"   * Max Memory: {self.resources.max_memory_gb}GB")
        print(f"   * Max CPU Cores: {self.resources.max_cpu_cores}")
        print(f"   * Max Parallel Agents: {self.resources.max_parallel_agents}")
        print(f"   * Generation Timeout: {self.resources.generation_timeout_seconds}s")
        print(f"   * Max Repair Attempts: {self.resources.max_repair_attempts}")
        print()
        print("Storage:")
        print(f"   * Projects: {self.storage.projects_dir}")
        print(f"   * Templates: {self.storage.templates_dir}")
        print(f"   * Snapshots: {self.storage.snapshots_dir}")
        print(f"   * Max Project Size: {self.storage.max_project_size_mb}MB")
        print()
        print("Presets:")
        for name, preset in self.presets.items():
            print(f"   * {name}: creativity={preset.creativity_level}, priority={preset.template_priority}")
        print("=" * 60)


# Singleton instance
_config_instance = None

def get_config() -> NovaryxConfig:
    """Get or create the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = NovaryxConfig()
    return _config_instance
