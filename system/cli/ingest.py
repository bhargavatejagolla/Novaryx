#!/usr/bin/env python3
"""
NOVARYX - CLI Ingestion System (Phase 13)
Allows manual or automated ingestion of codebases, components, and templates into ChromaDB.
Usage:
  python system/cli/ingest.py --path ./components --type component
"""

import os
import argparse
import logging
from pathlib import Path

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from system.rag_engine.chromadb_client import ChromaDBClient

logger = logging.getLogger("novaryx.cli.ingest")

def ingest_directory(path: str, ingest_type: str):
    logger.info(f"Ingesting directory: {path} as {ingest_type}")
    
    target_path = Path(path)
    if not target_path.exists() or not target_path.is_dir():
        logger.error(f"Path does not exist or is not a directory: {path}")
        return
        
    client = ChromaDBClient()
    
    count = 0
    for root, _, files in os.walk(target_path):
        for file in files:
            if file.endswith(('.tsx', '.jsx', '.ts', '.py')):
                file_path = Path(root) / file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if ingest_type == "component":
                    comp_id = f"custom_{file_path.stem}"
                    client.add_component(
                        component_id=comp_id,
                        name=file_path.stem,
                        component_type="custom",
                        code=content,
                        metadata={"source": "cli_ingest", "path": str(file_path)}
                    )
                    count += 1
                elif ingest_type == "bug":
                    # Pseudo bug ingestion
                    pass
                
    logger.info(f"Ingested {count} files successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="NOVARYX Ingestion CLI")
    parser.add_argument("--path", type=str, required=True, help="Path to ingest")
    parser.add_argument("--type", type=str, required=True, choices=["component", "bug", "architecture", "domain"], help="Type of data being ingested")
    
    args = parser.parse_args()
    ingest_directory(args.path, args.type)
