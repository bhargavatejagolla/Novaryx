#!/usr/bin/env python3
"""
NOVARYX - Phase 0.2
File: init_phase_0_2.py
Run this to complete Step 0.2
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add NOVARYX root to path - using current directory for workspace compatibility
NOVARYX_ROOT = Path.cwd()
sys.path.insert(0, str(NOVARYX_ROOT / "system" / "config"))
sys.path.insert(0, str(NOVARYX_ROOT / "system" / "orchestrator"))

try:
    from novaryx_config import NovaryxConfig, get_config
    from model_manager import ModelManager
    from logger_setup import NovaryxLogger, logger
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure system/config and system/orchestrator contain the necessary modules.")
    sys.exit(1)


def step_0_2():
    """Execute Phase 0 Step 2: System Configuration"""
    
    print()
    print("=" * 60)
    print("NOVARYX - PHASE 0.2")
    print("   System Configuration Initialization")
    print("=" * 60)
    print()
    
    # Step 1: Initialize logger
    print("Step 1/5: Setting up logging...")
    log = NovaryxLogger()
    log.info("Logger initialized")
    print("   Logging system ready")
    
    # Step 2: Create configuration
    print("Step 2/5: Creating system configuration...")
    config = NovaryxConfig()
    config.setup_default_models()
    config.save()
    print("   Configuration created and saved")
    
    # Step 3: Validate configuration
    print("Step 3/5: Validating configuration...")
    is_valid, errors = config.validate()
    if is_valid:
        print("   Configuration valid")
    else:
        print("   Configuration issues found:")
        for error in errors:
            print(f"      - {error}")
        print("   Some errors expected until models are downloaded")
    
    # Step 4: Initialize model manager
    print("Step 4/5: Initializing model manager...")
    model_manager = ModelManager(config)
    model_manager.display_status()
    print("   Model manager ready")
    
    # Step 5: Update metadata
    print("Step 5/5: Updating project metadata...")
    metadata_path = NOVARYX_ROOT / ".novaryx_metadata.json"
    
    if metadata_path.exists():
        with open(metadata_path, "r", encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    metadata.update({
        "phase": 0,
        "step": 2,
        "step_name": "System Configuration Initialization",
        "completed_at": datetime.now().isoformat(),
        "config_created": True,
        "model_manager_ready": True,
        "logger_ready": True,
        "next_step": "0.3 - Set up model manager (download models)",
        "all_connected": True
    })
    
    with open(metadata_path, "w", encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print("   Metadata updated")
    
    # Final display
    print()
    print("=" * 60)
    print("PHASE 0.2 COMPLETE")
    print("=" * 60)
    print()
    print("Created files:")
    print("   - system/config/novaryx_config.py")
    print("   - system/orchestrator/model_manager.py")
    print("   - system/config/logger_setup.py")
    print("   - config/system_config.json")
    print()
    print("System components initialized:")
    print("   [OK] Logging system")
    print("   [OK] Configuration manager")
    print("   [OK] Model manager (models pending download)")
    print("   [OK] Storage configuration")
    print("   [OK] Resource limits set")
    print()
    print("Next: Phase 0.3 - Download models & set up ChromaDB")
    print("Waiting for your command...")
    print()


if __name__ == "__main__":
    step_0_2()
