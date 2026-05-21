"""
NOVARYX - RAG Trainer (Continuous Semantic Learning Engine)
Scans past generated exports and ingests TSX components into ChromaDB
to create a deep-learning autonomous feedback loop.
"""

import sys
import logging
from pathlib import Path

# Add project root to path if running directly
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from system.rag_engine.chromadb_client import ChromaDBClient
except ImportError as e:
    print(f"Error importing ChromaDB client: {e}")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("novaryx.rag_trainer")

def train_from_exports(exports_path: str = "exports"):
    """Scan exports directory and ingest TSX components into vector DB."""
    client = ChromaDBClient()
    
    exports_dir = Path(exports_path)
    if not exports_dir.exists():
        logger.error(f"Exports directory {exports_dir.absolute()} not found.")
        return
        
    logger.info("=" * 60)
    logger.info("🧠 NOVARYX CONTINUOUS SEMANTIC LEARNING")
    logger.info("=" * 60)
        
    total_ingested = 0
    projects = [d for d in exports_dir.iterdir() if d.is_dir()]
    
    if not projects:
        logger.warning(f"No projects found in {exports_dir}")
        return
        
    for project_dir in projects:
        project_name = project_dir.name
        logger.info(f"\n📁 Scanning project: {project_name}")
        
        # We target pages and layouts to learn application structure
        target_patterns = ["src/pages/*.tsx", "src/layouts/*.tsx", "src/components/*.tsx"]
        tsx_files = []
        for pattern in target_patterns:
            tsx_files.extend(list(project_dir.glob(pattern)))
            
        if not tsx_files:
            logger.info(f"   No TSX components found in {project_name}")
            continue
            
        for file_path in tsx_files:
            try:
                name = file_path.stem
                
                # Intelligent component classification for better retrieval
                comp_type = "component"
                name_lower = name.lower()
                if "layout" in name_lower:
                    comp_type = "layout"
                elif any(k in name_lower for k in ["dashboard", "stats", "analytics"]):
                    comp_type = "stats"
                elif any(k in name_lower for k in ["login", "register", "auth", "protected"]):
                    comp_type = "auth"
                elif any(k in name_lower for k in ["setting", "profile"]):
                    comp_type = "settings"
                elif file_path.parent.name == "pages":
                    comp_type = "page"
                
                content = file_path.read_text(encoding="utf-8")
                
                # Skip massive files (probably bundled or not real components)
                if len(content) > 25000:
                    logger.warning(f"   Skipping {name} (too large: {len(content)} bytes)")
                    continue
                
                component_id = f"{project_name}_{comp_type}_{name}"
                
                logger.info(f"   ► Ingesting: {name} [{comp_type}]")
                client.add_component(
                    component_id=component_id,
                    name=name,
                    component_type=comp_type,
                    code=content,
                    metadata={
                        "source": "auto_trainer", 
                        "project": project_name, 
                        "framework": "react-vite",
                        "learned_at": "auto"
                    }
                )
                total_ingested += 1
                
            except Exception as e:
                logger.error(f"   ❌ Failed to ingest {file_path.name}: {e}")
                
    logger.info("=" * 60)
    logger.info(f"✅ Deep Learning Cycle Complete. Ingested {total_ingested} components.")
    logger.info("   These components will now be dynamically injected into prompt context.")
    logger.info("=" * 60)
    
if __name__ == "__main__":
    train_from_exports()
