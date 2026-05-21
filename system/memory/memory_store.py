"""
NOVARYX - Long-Term Memory Store
Persistent storage for every generated project with embeddings and metadata.

Stores:
  - Full project files
  - Design tokens
  - Component selections
  - Success metrics
  - Prompt → Result mappings
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict, fields
from datetime import datetime
import uuid

logger = logging.getLogger("novaryx.memory_store")


@dataclass
class ProjectMemory:
    """Complete memory record of a generated project"""
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    project_name: str = ""
    prompt: str = ""
    project_type: str = ""
    
    # Design
    design_tokens: Dict[str, Any] = field(default_factory=dict)
    primary_color: str = ""
    mode: str = "dark"
    font: str = "Inter"
    
    # Structure
    layout_type: str = ""
    pages: List[Dict] = field(default_factory=list)
    components_used: List[str] = field(default_factory=list)
    components_3d: List[str] = field(default_factory=list)
    
    # Quality
    success: bool = True
    quality_score: float = 0.0
    bugs_found: int = 0
    bugs_fixed: int = 0
    generation_time_seconds: float = 0.0
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    user_rating: int = 0
    
    # Full text for embedding
    full_description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "project_name": self.project_name,
            "prompt": self.prompt[:300],
            "project_type": self.project_type,
            "primary_color": self.primary_color,
            "mode": self.mode,
            "font": self.font,
            "layout_type": self.layout_type,
            "pages_count": len(self.pages),
            "components_count": len(self.components_used),
            "success": self.success,
            "quality_score": self.quality_score,
            "bugs_fixed": self.bugs_fixed,
            "generation_time_s": f"{self.generation_time_seconds:.1f}",
            "created_at": self.created_at,
            "tags": self.tags,
        }
    
    def serialize(self) -> Dict:
        """Complete serialization for persistence"""
        return asdict(self)
    
    def to_embedding_text(self) -> str:
        """Generate text for embedding"""
        return f"""Project: {self.project_name}
Type: {self.project_type}
Prompt: {self.prompt}
Design: {self.primary_color}, {self.mode} mode, {self.font}
Layout: {self.layout_type}
Components: {', '.join(self.components_used[:10])}
Quality: {self.quality_score:.0%}, {'Success' if self.success else 'Failed'}
Pages: {', '.join([p.get('name', '') for p in self.pages])}
Tags: {', '.join(self.tags)}"""


class MemoryStore:
    """
    Long-term persistent memory for all generations.
    
    Uses:
    - JSON files for metadata
    - ChromaDB for embeddings and search
    - File system for project files
    """
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            memory_dir = str(Path.home() / "novaryx" / "memory")
        
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.projects_dir = self.memory_dir / "projects"
        self.projects_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.memory_dir / "memory_index.json"
        self.memories: Dict[str, ProjectMemory] = {}
        
        self._load_index()
        self._chroma = None
        
        logger.info(f"MemoryStore initialized: {len(self.memories)} memories loaded")
    
    def _load_index(self):
        """Load memory index from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                
                # Get valid fields for ProjectMemory to filter out extra keys
                valid_fields = {f.name for f in fields(ProjectMemory)}
                
                for mem_data in data.get("memories", []):
                    # Filter data to only include valid fields
                    filtered_data = {k: v for k, v in mem_data.items() if k in valid_fields}
                    
                    # Special handling for renamed or missing fields if needed
                    if "generation_time_s" in mem_data and "generation_time_seconds" not in filtered_data:
                        try:
                            filtered_data["generation_time_seconds"] = float(mem_data["generation_time_s"])
                        except (ValueError, TypeError):
                            pass
                    
                    mem = ProjectMemory(**filtered_data)
                    self.memories[mem.memory_id] = mem
            except Exception as e:
                logger.error(f"Failed to load memory index: {e}")
    
    def _save_index(self):
        """Save memory index to disk"""
        data = {
            "version": "4.1.0",
            "updated_at": datetime.now().isoformat(),
            "total_memories": len(self.memories),
            "memories": [mem.serialize() for mem in self.memories.values()]
        }
        
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def store(self, memory: ProjectMemory) -> str:
        """Store a new project memory"""
        
        # Save memory metadata
        self.memories[memory.memory_id] = memory
        
        # Save project files if they exist
        project_dir = self.projects_dir / memory.memory_id
        project_dir.mkdir(exist_ok=True)
        
        # Save individual memory JSON
        mem_file = project_dir / "memory.json"
        with open(mem_file, "w") as f:
            json.dump(memory.serialize(), f, indent=2)
        
        # Index in ChromaDB for search
        self._index_in_chroma(memory)
        
        # Update index
        self._save_index()
        
        logger.info(f"Memory stored: {memory.project_name} ({memory.memory_id})")
        return memory.memory_id
    
    def _index_in_chroma(self, memory: ProjectMemory):
        """Index memory in ChromaDB for semantic search"""
        try:
            chroma = self._get_chroma()
            if chroma:
                chroma.add_template(
                    template_id=f"mem_{memory.memory_id}",
                    name=memory.project_name,
                    description=memory.full_description or memory.prompt,
                    metadata={
                        "type": memory.project_type,
                        "primary_color": memory.primary_color,
                        "mode": memory.mode,
                        "layout": memory.layout_type,
                        "success": str(memory.success),
                        "quality_score": str(memory.quality_score),
                        "components": json.dumps(memory.components_used),
                        "created_at": memory.created_at,
                    }
                )
        except Exception as e:
            logger.debug(f"ChromaDB indexing skipped: {e}")
    
    def _get_chroma(self):
        """Lazy load ChromaDB"""
        if self._chroma is None:
            try:
                from system.rag_engine.chromadb_client import ChromaDBClient
                self._chroma = ChromaDBClient()
            except Exception:
                pass
        return self._chroma
    
    def get(self, memory_id: str) -> Optional[ProjectMemory]:
        """Get a memory by ID"""
        return self.memories.get(memory_id)
    
    def get_by_project_name(self, name: str) -> Optional[ProjectMemory]:
        """Find memory by project name"""
        for mem in self.memories.values():
            if mem.project_name.lower() == name.lower():
                return mem
        return None
    
    def get_recent(self, limit: int = 10) -> List[ProjectMemory]:
        """Get most recent memories"""
        sorted_mems = sorted(
            self.memories.values(),
            key=lambda m: m.created_at,
            reverse=True
        )
        return sorted_mems[:limit]
    
    def get_successful(self, limit: int = 10) -> List[ProjectMemory]:
        """Get successful generations"""
        return [m for m in self.memories.values() if m.success][:limit]
    
    def get_by_type(self, project_type: str) -> List[ProjectMemory]:
        """Get memories by project type"""
        return [m for m in self.memories.values() if m.project_type == project_type]
    
    def get_by_color(self, color: str) -> List[ProjectMemory]:
        """Get memories using a specific primary color"""
        return [m for m in self.memories.values() if color in m.primary_color]
    
    def search(self, query: str, top_k: int = 5) -> List[ProjectMemory]:
        """Simple keyword search across memories"""
        query_lower = query.lower()
        results = []
        
        for mem in self.memories.values():
            score = 0
            if query_lower in mem.project_name.lower():
                score += 10
            if query_lower in mem.prompt.lower():
                score += 5
            if query_lower in mem.project_type.lower():
                score += 3
            if query_lower in ' '.join(mem.components_used).lower():
                score += 2
            
            if score > 0:
                results.append((score, mem))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in results[:top_k]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total = len(self.memories)
        successful = sum(1 for m in self.memories.values() if m.success)
        failed = total - successful
        
        # By type
        by_type = {}
        for mem in self.memories.values():
            ptype = mem.project_type or "unknown"
            by_type[ptype] = by_type.get(ptype, 0) + 1
        
        # By color
        by_color = {}
        for mem in self.memories.values():
            if mem.primary_color:
                by_color[mem.primary_color] = by_color.get(mem.primary_color, 0) + 1
        
        # Average quality
        avg_quality = sum(m.quality_score for m in self.memories.values()) / max(total, 1)
        
        return {
            "total_projects": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / max(total, 1)) * 100:.0f}%",
            "by_type": by_type,
            "by_color": by_color,
            "avg_quality": f"{avg_quality:.0%}",
            "storage_location": str(self.memory_dir),
        }
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            
            # Remove project files
            project_dir = self.projects_dir / memory_id
            if project_dir.exists():
                import shutil
                shutil.rmtree(project_dir)
            
            self._save_index()
            logger.info(f"Memory deleted: {memory_id}")
            return True
        return False
    
    def display_stats(self):
        """Display memory statistics"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("🧠 LONG-TERM MEMORY STORE")
        print("=" * 60)
        print(f"   Projects: {stats['total_projects']}")
        print(f"   Success Rate: {stats['success_rate']}")
        print(f"   Avg Quality: {stats['avg_quality']}")
        print(f"   Types: {stats['by_type']}")
        print(f"   Colors: {stats['by_color']}")
        print(f"   Location: {stats['storage_location']}")
        print("=" * 60)