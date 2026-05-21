"""
NOVARYX - ChromaDB Client
Vector database wrapper for template and component storage.

Collections:
  1. templates          - Full template metadata
  2. components         - Individual UI components
  3. architecture_plans - Architecture patterns
  4. generation_history - Past generation context
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  Install chromadb: pip install chromadb")

logger = logging.getLogger("novaryx.chromadb")


class ChromaDBClient:
    """ChromaDB vector database for NOVARYX RAG system"""
    
    COLLECTIONS = {
        "templates": {
            "name": "novaryx_templates",
            "description": "Full template metadata and structure",
            "metadata": {"type": "template"}
        },
        "components": {
            "name": "novaryx_components",
            "description": "Individual UI component patterns",
            "metadata": {"type": "component"}
        },
        "architecture_plans": {
            "name": "novaryx_architectures",
            "description": "Architecture patterns and system designs",
            "metadata": {"type": "architecture"}
        },
        "generation_history": {
            "name": "novaryx_history",
            "description": "Past generations for learning and improvement",
            "metadata": {"type": "history"}
        },
        "bug_memory": {
            "name": "novaryx_bugs",
            "description": "Known bugs, fixes, and anti-patterns",
            "metadata": {"type": "bug"}
        },
        "domain_memory": {
            "name": "novaryx_domain",
            "description": "Domain-specific patterns (ML, CV, Healthcare, etc.)",
            "metadata": {"type": "domain"}
        },
        "user_memory": {
            "name": "novaryx_user",
            "description": "User preferences, styles, and workflows",
            "metadata": {"type": "user"}
        },
        "package_memory": {
            "name": "novaryx_package",
            "description": "Package integrations and compatibility patterns",
            "metadata": {"type": "package"}
        },
        "project_graph_memory": {
            "name": "novaryx_project_graph",
            "description": "Page, API, and DB relationships across projects",
            "metadata": {"type": "project_graph"}
        }
    }
    
    def __init__(self, persist_dir: str = None, embedding_function=None, reset: bool = False):
        """
        Initialize ChromaDB client.
        
        Args:
            persist_dir: Path to persistent storage
            embedding_function: Custom embedding function
            reset: If True, delete and recreate all collections
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb not installed. Run: pip install chromadb")
        
        # Set persistence directory
        if persist_dir is None:
            persist_dir = os.environ.get("CHROMA_PERSIST_DIR")
            if not persist_dir:
                novaryx_root = Path.home() / "novaryx"
                persist_dir = str(novaryx_root / "system" / "rag_engine" / "chromadb")
        
        self.persist_dir = persist_dir
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Store embedding function
        self.embedding_function = embedding_function
        
        # Initialize collections
        self.collections = {}
        
        if reset:
            self._reset_all_collections()
        
        self._init_collections()
        
        logger.info(f"ChromaDB initialized at: {persist_dir}")
    
    def _reset_all_collections(self):
        """Delete all existing NOVARYX collections"""
        logger.warning("Resetting all ChromaDB collections...")
        for key, config in self.COLLECTIONS.items():
            collection_name = config["name"]
            try:
                self.client.delete_collection(name=collection_name)
                logger.info(f"Deleted: {collection_name}")
            except Exception:
                logger.debug(f"Collection {collection_name} does not exist, skipping")
    
    def _init_collections(self):
        """Create or load all collections"""
        for key, config in self.COLLECTIONS.items():
            collection_name = config["name"]
            
            try:
                # Try to get existing collection with our embedding function
                self.collections[key] = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
                count = self.collections[key].count()
                logger.info(f"Loaded collection: {collection_name} ({count} items)")
                
            except Exception as e:
                error_msg = str(e)
                
                # Collection doesn't exist - create it
                if "does not exist" in error_msg.lower() or "not found" in error_msg.lower():
                    try:
                        self.collections[key] = self.client.create_collection(
                            name=collection_name,
                            metadata=config["metadata"],
                            embedding_function=self.embedding_function
                        )
                        logger.info(f"Created collection: {collection_name}")
                    except Exception as create_error:
                        logger.error(f"Failed to create {collection_name}: {create_error}")
                        raise
                
                # Collection exists but with different embedding function
                elif "embedding" in error_msg.lower():
                    logger.warning(f"Collection '{collection_name}' has different embedding, recreating...")
                    try:
                        self.client.delete_collection(name=collection_name)
                        self.collections[key] = self.client.create_collection(
                            name=collection_name,
                            metadata=config["metadata"],
                            embedding_function=self.embedding_function
                        )
                        logger.info(f"Recreated collection: {collection_name}")
                    except Exception as recreate_error:
                        logger.error(f"Failed to recreate {collection_name}: {recreate_error}")
                        raise
                else:
                    logger.error(f"Unexpected error loading {collection_name}: {e}")
                    raise
    
    def add_template(
        self,
        template_id: str,
        name: str,
        description: str,
        metadata: Dict[str, Any],
        documents: List[str] = None
    ):
        """Add a template to the templates collection"""
        collection = self.collections["templates"]
        
        # Build search text
        search_text = f"{name}: {description}"
        if "features" in metadata:
            features = metadata["features"]
            if isinstance(features, list):
                search_text += f" Features: {', '.join(features)}"
        if "pages" in metadata:
            pages = metadata["pages"]
            if isinstance(pages, list):
                search_text += f" Pages: {', '.join(pages)}"
        
        # Convert metadata values to strings
        safe_metadata = {
            "name": name,
            "description": description,
        }
        for k, v in metadata.items():
            if isinstance(v, (list, dict)):
                safe_metadata[k] = json.dumps(v)
            else:
                safe_metadata[k] = str(v)
        
        try:
            existing = collection.get(ids=[template_id])
            if existing and existing.get("ids") and len(existing["ids"]) > 0:
                collection.update(
                    ids=[template_id],
                    documents=[search_text],
                    metadatas=[safe_metadata]
                )
                logger.info(f"Updated template: {name}")
            else:
                collection.add(
                    ids=[template_id],
                    documents=[search_text],
                    metadatas=[safe_metadata]
                )
                logger.info(f"Added template: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add template {name}: {e}")
            return False
    
    def add_component(
        self,
        component_id: str,
        name: str,
        component_type: str,
        code: str,
        metadata: Dict[str, Any] = None
    ):
        """Add a component to the components collection"""
        collection = self.collections["components"]
        
        search_text = f"{component_type}: {name}"
        if metadata and "description" in metadata:
            search_text += f" - {metadata['description']}"
        
        safe_metadata = {
            "name": name,
            "type": component_type,
            "code": code,
            **(metadata or {})
        }
        
        try:
            existing = collection.get(ids=[component_id])
            if existing and existing.get("ids") and len(existing["ids"]) > 0:
                collection.update(
                    ids=[component_id],
                    documents=[search_text],
                    metadatas=[safe_metadata]
                )
                logger.info(f"Updated component: {name}")
            else:
                collection.add(
                    ids=[component_id],
                    documents=[search_text],
                    metadatas=[safe_metadata]
                )
                logger.info(f"Added component: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add component {name}: {e}")
            return False
    
    def add_architecture(
        self,
        arch_id: str,
        name: str,
        description: str,
        pattern: Dict[str, Any]
    ):
        """Add an architecture pattern"""
        collection = self.collections["architecture_plans"]
        
        safe_metadata = {
            "name": name,
            "description": description,
            "pattern": json.dumps(pattern)
        }
        
        try:
            existing = collection.get(ids=[arch_id])
            if existing and existing.get("ids") and len(existing["ids"]) > 0:
                collection.update(
                    ids=[arch_id],
                    documents=[f"{name}: {description}"],
                    metadatas=[safe_metadata]
                )
                logger.info(f"Updated architecture: {name}")
            else:
                collection.add(
                    ids=[arch_id],
                    documents=[f"{name}: {description}"],
                    metadatas=[safe_metadata]
                )
                logger.info(f"Added architecture: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add architecture {name}: {e}")
            return False
    
    def add_generation_record(
        self,
        generation_id: str,
        prompt: str,
        result_summary: str,
        success: bool,
        metadata: Dict[str, Any] = None
    ):
        """Record a generation for history"""
        collection = self.collections["generation_history"]
        
        try:
            collection.add(
                ids=[generation_id],
                documents=[f"Prompt: {prompt[:500]}\nResult: {result_summary}"],
                metadatas=[{
                    "prompt": prompt[:1000],
                    "result_summary": result_summary,
                    "success": str(success),
                    "timestamp": datetime.now().isoformat(),
                    **(metadata or {})
                }]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to record generation: {e}")
            return False
    
    def query_templates(
        self,
        query: str,
        n_results: int = 5,
        filter_criteria: Dict = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant templates"""
        collection = self.collections["templates"]
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_criteria
            )
            
            formatted_results = []
            if results.get("ids") and results["ids"][0]:
                for i, template_id in enumerate(results["ids"][0]):
                    metadata = results.get("metadatas", [[]])[0]
                    if i < len(metadata):
                        meta = metadata[i]
                    else:
                        meta = {}
                    
                    # Parse JSON strings back
                    parsed_metadata = {}
                    for k, v in meta.items():
                        try:
                            parsed_metadata[k] = json.loads(v)
                        except (json.JSONDecodeError, TypeError):
                            parsed_metadata[k] = v
                    
                    formatted_results.append({
                        "id": template_id,
                        "document": results.get("documents", [[""]])[0][i] if results.get("documents") else "",
                        "metadata": parsed_metadata,
                        "distance": results.get("distances", [[0]])[0][i] if results.get("distances") else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Template query failed: {e}")
            return []
    
    def query_components(
        self,
        query: str,
        component_type: str = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant components"""
        collection = self.collections["components"]
        
        filter_criteria = None
        if component_type:
            filter_criteria = {"type": component_type}
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_criteria
            )
            
            formatted_results = []
            if results.get("ids") and results["ids"][0]:
                for i, comp_id in enumerate(results["ids"][0]):
                    metadata = results.get("metadatas", [[]])[0]
                    meta = metadata[i] if i < len(metadata) else {}
                    
                    formatted_results.append({
                        "id": comp_id,
                        "name": meta.get("name", ""),
                        "type": meta.get("type", ""),
                        "code": meta.get("code", ""),
                        "distance": results.get("distances", [[0]])[0][i] if results.get("distances") else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Component query failed: {e}")
            return []
    
    def query_architectures(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for architecture patterns"""
        collection = self.collections["architecture_plans"]
        
        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            formatted_results = []
            if results.get("ids") and results["ids"][0]:
                for i, arch_id in enumerate(results["ids"][0]):
                    metadata = results.get("metadatas", [[]])[0]
                    meta = metadata[i] if i < len(metadata) else {}
                    
                    pattern = {}
                    if "pattern" in meta:
                        try:
                            pattern = json.loads(meta["pattern"])
                        except:
                            pass
                    
                    formatted_results.append({
                        "id": arch_id,
                        "name": meta.get("name", ""),
                        "description": meta.get("description", ""),
                        "pattern": pattern,
                        "distance": results.get("distances", [[0]])[0][i] if results.get("distances") else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Architecture query failed: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        stats = {}
        for key, collection in self.collections.items():
            try:
                count = collection.count()
                stats[key] = {
                    "name": self.COLLECTIONS[key]["name"],
                    "count": count,
                    "description": self.COLLECTIONS[key]["description"]
                }
            except Exception as e:
                stats[key] = {"error": str(e)}
        return stats
    
    def reset_all(self):
        """Reset all collections"""
        self._reset_all_collections()
        self._init_collections()
    
    def display_stats(self):
        """Display collection statistics"""
        print("\n" + "=" * 50)
        print("📊 CHROMADB COLLECTION STATS")
        print("=" * 50)
        stats = self.get_collection_stats()
        for key, info in stats.items():
            count = info.get("count", "?")
            desc = info.get("description", "")
            print(f"  📦 {key}: {count} items - {desc}")
        print("=" * 50 + "\n")