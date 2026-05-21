#!/usr/bin/env python3
"""
NOVARYX - Phase 0.1
System Initialization & Configuration
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Root directory - using current directory for workspace compatibility
NOVARYX_ROOT = Path.cwd()

class NovaryxInitializer:
    """Initialize the NOVARYX system foundation"""
    
    def __init__(self):
        self.root = NOVARYX_ROOT
        self.config = {}
        
    def run(self):
        print("=" * 60)
        print("NOVARYX SYSTEM INITIALIZATION")
        print("=" * 60)
        print()
        
        self.create_structure()
        self.create_env_file()
        self.create_gitignore()
        self.create_system_config()
        self.create_readme()
        self.create_metadata()
        self.verify_structure()
        
        print()
        print("Phase 0.1 Complete - System structure ready")
        print(f"Location: {self.root}")
        print()
        print("Next: Phase 0.2 - Initialize system configuration")
        
    def create_structure(self):
        """Create all required directories"""
        print("Creating directory structure...")
        
        directories = [
            # Core system
            "system/orchestrator/state_machine",
            "system/orchestrator/prompt_parser",
            "system/orchestrator/intent_classifier",
            "system/orchestrator/resource_manager",
            "system/orchestrator/task_scheduler",
            
            # Agents
            "system/agents/architect_agent",
            "system/agents/frontend_agent",
            "system/agents/backend_agent",
            "system/agents/design_agent",
            "system/agents/content_agent",
            "system/agents/seo_agent",
            "system/agents/security_agent",
            
            # RAG Engine
            "system/rag_engine/chromadb/collections",
            "system/rag_engine/chromadb/metadata",
            "system/rag_engine/chromadb/backups",
            "system/rag_engine/embeddings",
            "system/rag_engine/retrievers",
            "system/rag_engine/indexers",
            "system/rag_engine/context_builder",
            
            # Templates
            "system/templates/saas_dashboard",
            "system/templates/saas_landing",
            "system/templates/ecommerce",
            "system/templates/portfolio",
            "system/templates/blog",
            "system/templates/admin_panel",
            "system/templates/social_app",
            "system/templates/documentation",
            "system/templates/auth_system",
            "system/templates/marketing_site",
            
            # Repair Engine
            "system/repair_engine/diagnostics",
            "system/repair_engine/fixers",
            "system/repair_engine/validators",
            "system/repair_engine/rollback_manager",
            
            # Generation Engine
            "system/generation_engine/page_generator",
            "system/generation_engine/component_generator",
            "system/generation_engine/schema_generator",
            "system/generation_engine/api_generator",
            "system/generation_engine/asset_generator",
            
            # Verification Engine
            "system/verification_engine/syntax_checker",
            "system/verification_engine/type_checker",
            "system/verification_engine/import_validator",
            "system/verification_engine/route_validator",
            "system/verification_engine/component_validator",
            "system/verification_engine/build_checker",
            "system/verification_engine/lighthouse_checker",
            
            # Deployment Engine
            "system/deployment_engine/docker_generator",
            "system/deployment_engine/env_configurator",
            "system/deployment_engine/ci_cd_generator",
            "system/deployment_engine/local_deployer",
            "system/deployment_engine/cloud_deployer",
            
            # Storage
            "projects/active",
            "projects/archived",
            "projects/showcase",
            "snapshots/automatic",
            "snapshots/manual",
            "snapshots/pre_deploy",
            
            # Assets
            "assets_library/3d_models",
            "assets_library/images",
            "assets_library/fonts",
            "assets_library/icons",
            "assets_library/animations",
            "assets_library/shaders",
            "assets_library/audio",
            
            # Deployments
            "deployments/running",
            "deployments/stopped",
            "deployments/logs",
            "deployments/configs",
            
            # Logs
            "logs/generation",
            "logs/errors",
            "logs/performance",
            "logs/usage",
            "logs/system",
            
            # Config
            "config/models",
            "config/agents",
            "config/generation_presets",
            "config/deployment_presets",
            "config/security",
            
            # Tests
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tests/fixtures",
            "tests/benchmarks",
            
            # Docs
            "docs/architecture",
            "docs/api",
            "docs/user_guide",
            "docs/development",
            "docs/templates",
            
            # Models
            "system/models/qwen",
            "system/models/deepseek",
            "system/models/embeddings_model",
            
            # Shared
            "system/shared_deps",
        ]
        
        for directory in directories:
            dir_path = self.root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            # Add .gitkeep to empty directories
            (dir_path / ".gitkeep").touch(exist_ok=True)
            
        print("   Directory structure created")
        
    def create_env_file(self):
        """Create .env file for NOVARYX configuration"""
        print("Creating environment configuration...")
        
        env_content = """# NOVARYX Environment Configuration
# Generated: {timestamp}

# System
NOVARYX_ROOT={root}
NOVARYX_ENV=development
LOG_LEVEL=INFO

# Models
QWEN_MODEL_PATH={root}/system/models/qwen
DEEPSEEK_MODEL_PATH={root}/system/models/deepseek
EMBEDDING_MODEL_PATH={root}/system/models/embeddings_model
DEFAULT_CODING_MODEL=qwen
DEFAULT_PLANNING_MODEL=deepseek

# Model Parameters
MAX_CONTEXT_LENGTH=8192
TEMPERATURE=0.1
TOP_P=0.9
MAX_TOKENS_PER_REQUEST=2048

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST_DIR={root}/system/rag_engine/chromadb

# PocketBase
POCKETBASE_VERSION=0.22.0
POCKETBASE_PORT=8090

# Generation
MAX_REPAIR_ATTEMPTS=3
GENERATION_TIMEOUT_SECONDS=600
MAX_PAGES_PER_GENERATION=20
SNAPSHOT_ENABLED=true

# Resource Limits
MAX_MEMORY_USAGE_GB=14
MAX_CPU_CORES=4
MAX_PARALLEL_AGENTS=2

# Deployment
DEFAULT_DEPLOY_PORT=3000
DEFAULT_DOCKER_TAG=latest
""".format(
            timestamp=datetime.now().isoformat(),
            root=str(self.root).replace("\\", "/")
        )
        
        with open(self.root / ".env", "w", encoding='utf-8') as f:
            f.write(env_content)
            
        # Also create .env.example without sensitive values
        with open(self.root / ".env.example", "w", encoding='utf-8') as f:
            f.write(env_content)
            
        print("   Environment files created")
        
    def create_gitignore(self):
        """Create comprehensive .gitignore"""
        print("Creating .gitignore...")
        
        gitignore_content = """# NOVARYX .gitignore

# Models (large files)
system/models/

# Environment
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
dist/
build/
*.egg

# Node
node_modules/
.pnpm-store/

# ChromaDB data
system/rag_engine/chromadb/collections/
*.bin
*.pickle

# Logs
logs/
*.log

# Generated projects
projects/
deployments/

# Snapshots (keep index, ignore zips)
snapshots/**/*.zip
snapshots/**/*.tar.gz

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temporary
tmp/
temp/
*.tmp
.cache/

# Test outputs
tests/fixtures/output/
coverage/

# Database
*.db
*.sqlite
*.sqlite3
"""
        
        with open(self.root / ".gitignore", "w", encoding='utf-8') as f:
            f.write(gitignore_content)
            
        print("   .gitignore created")
        
    def create_system_config(self):
        """Create main system configuration"""
        print("Creating system configuration...")
        
        config = {
            "system": {
                "name": "NOVARYX",
                "version": "0.1.0",
                "codename": "Phase 0",
                "created_at": datetime.now().isoformat(),
                "architecture": "modular-orchestrator",
                "description": "AI-Powered Autonomous Application Builder"
            },
            "phases": {
                "0": {"name": "Foundation", "status": "in_progress", "steps_completed": ["structure", "config", "env"]},
                "1": {"name": "Template Building", "status": "pending", "steps_completed": []},
                "2": {"name": "Intent Parser", "status": "pending", "steps_completed": []},
                "3": {"name": "Generation Pipeline", "status": "pending", "steps_completed": []},
                "4": {"name": "Verification System", "status": "pending", "steps_completed": []},
                "5": {"name": "Deployment Engine", "status": "pending", "steps_completed": []},
                "6": {"name": "Integration & Testing", "status": "pending", "steps_completed": []},
                "7": {"name": "Polish & Launch", "status": "pending", "steps_completed": []}
            },
            "hardware_profile": {
                "ram_gb": 16,
                "gpu": "integrated",
                "storage_gb": "auto_detect",
                "recommended_models": ["qwen2.5-coder-7b", "deepseek-coder-7b"]
            },
            "storage": {
                "root": str(self.root),
                "projects_dir": str(self.root / "projects"),
                "snapshots_dir": str(self.root / "snapshots"),
                "templates_dir": str(self.root / "system/templates"),
                "models_dir": str(self.root / "system/models")
            }
        }
        
        with open(self.root / "config" / "system_config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
        print("   System configuration created")
        
    def create_readme(self):
        """Create initial README"""
        print("Creating README...")
        
        readme_content = """# NOVARYX

## AI-Powered Autonomous Application Builder

**Status:** Phase 0 - Foundation (In Progress)

### What is NOVARYX?

NOVARYX is an AI orchestration system that generates complete, production-ready web applications from a single prompt. It combines template-first architecture with intelligent adaptation to produce premium, deployable software.

### Architecture
Prompt -> Intent Parser -> Architecture Planner ->
Generation Engine -> Verification -> Repair ->
Deployment -> Production App

### System Requirements

- 16GB RAM minimum
- Local LLM support (Qwen 2.5 Coder 7B + DeepSeek Coder 7B)
- PocketBase for backend
- ChromaDB for RAG
- Python 3.10+
- Node.js 18+

### Project Structure
novaryx/
├── system/ # Core engine
├── projects/ # Generated applications
├── snapshots/ # Version rollback points
├── assets_library/ # Shared assets
├── deployments/ # Active deployments
├── logs/ # System logs
├── config/ # Configuration
├── tests/ # Test suites
└── docs/ # Documentation

### Phase Status

- [ ] Phase 0: Foundation Setup
- [ ] Phase 1: Template Building
- [ ] Phase 2: Intent Parser
- [ ] Phase 3: Generation Pipeline
- [ ] Phase 4: Verification System
- [ ] Phase 5: Deployment Engine
- [ ] Phase 6: Integration & Testing
- [ ] Phase 7: Polish & Launch

---
*Built with discipline. Not AI chaos.*
"""
        
        with open(self.root / "README.md", "w", encoding='utf-8') as f:
            f.write(readme_content)
            
        print("   README created")
        
    def create_metadata(self):
        """Create project metadata file"""
        print("Creating metadata...")
        
        metadata = {
            "project_name": "NOVARYX",
            "initialized_at": datetime.now().isoformat(),
            "phase": 0,
            "step": 1,
            "directory_count": 0,  # Will be updated by verify
            "file_count": 0,
            "next_step": "0.2 - Initialize system configuration",
            "all_connected": True
        }
        
        # Count actual directories created
        dir_count = sum(1 for _ in self.root.rglob("*") if _.is_dir())
        file_count = sum(1 for _ in self.root.rglob("*") if _.is_file())
        
        metadata["directory_count"] = dir_count
        metadata["file_count"] = file_count
        
        with open(self.root / ".novaryx_metadata.json", "w", encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"   Metadata created ({dir_count} directories, {file_count} files)")

        
    def verify_structure(self):
        """Verify all directories are created and connected"""
        print()
        print("Verifying structure...")
        
        checks = {
            "Root exists": self.root.exists(),
            "System dir": (self.root / "system").exists(),
            "Agents dir": (self.root / "system/agents").exists(),
            "Templates dir": (self.root / "system/templates").exists(),
            "RAG Engine dir": (self.root / "system/rag_engine").exists(),
            "Projects dir": (self.root / "projects").exists(),
            "Snapshots dir": (self.root / "snapshots").exists(),
            "Config dir": (self.root / "config").exists(),
            "Logs dir": (self.root / "logs").exists(),
            ".env file": (self.root / ".env").exists(),
            ".gitignore": (self.root / ".gitignore").exists(),
            "README": (self.root / "README.md").exists(),
            "System config": (self.root / "config/system_config.json").exists(),
            "Metadata": (self.root / ".novaryx_metadata.json").exists(),
        }
        
        all_passed = True
        for check, passed in checks.items():
            status = "[OK]" if passed else "[FAIL]"
            if not passed:
                all_passed = False
            print(f"   {status} {check}")
        
        if all_passed:
            print()
            print("All components connected and verified!")
        else:
            print()
            print("Some checks failed. Review and re-run initialization.")
            
        return all_passed

if __name__ == "__main__":
    initializer = NovaryxInitializer()
    initializer.run()
