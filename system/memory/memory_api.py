"""
NOVARYX - Memory API
Unified API for all memory operations.
"""

import logging
from typing import Dict, List, Optional, Any
from .memory_store import MemoryStore, ProjectMemory
from .project_indexer import ProjectIndexer
from .similarity_engine import SimilarityEngine

logger = logging.getLogger("novaryx.memory_api")


class MemoryAPI:
    """
    Unified API for the entire memory system.
    
    One interface for:
    - Storing generations
    - Retrieving similar projects
    - Getting recommendations
    - Memory statistics
    """
    
    def __init__(self):
        self.store = MemoryStore()
        self.indexer = ProjectIndexer(self.store)
        self.similarity = SimilarityEngine(self.store)
    
    def remember(
        self,
        prompt: str,
        project_name: str,
        project_type: str = "unknown",
        design_system: Dict = None,
        layout_type: str = "",
        pages: list = None,
        components: list = None,
        success: bool = True,
        quality_score: float = 0.7,
    ) -> str:
        """Store a generation in memory"""
        return self.indexer.index_generation(
            prompt=prompt,
            project_name=project_name,
            project_type=project_type,
            design_system=design_system,
            layout_type=layout_type,
            pages=pages,
            components=components,
            success=success,
            quality_score=quality_score,
        )
    
    def recall(self, query: str, project_type: str = None) -> List[Dict]:
        """Search memory for similar projects"""
        similar = self.similarity.find_similar(query, project_type)
        return [
            {
                "name": mem.project_name,
                "type": mem.project_type,
                "similarity": f"{score:.0%}",
                "components": mem.components_used[:5],
                "success": mem.success,
                "created": mem.created_at,
            }
            for mem, score in similar
        ]
    
    def recommend(self, prompt: str, project_type: str = None) -> Dict:
        """Get recommendations based on past projects"""
        return self.similarity.get_recommendations(prompt, project_type)
    
    def stats(self) -> Dict:
        """Get memory statistics"""
        return self.store.get_stats()
    
    def recent(self, limit: int = 5) -> List[Dict]:
        """Get recent generations"""
        return [m.to_dict() for m in self.store.get_recent(limit)]
    
    def forget(self, memory_id: str) -> bool:
        """Delete a memory"""
        return self.store.delete(memory_id)


# ---- Test ----

def test_memory_api():
    """Test the memory system"""
    
    print("\n" + "=" * 60)
    print("🧪 MEMORY SYSTEM TEST")
    print("=" * 60)
    
    api = MemoryAPI()
    
    # Store some test memories
    print(f"\n   Storing test memories...")
    
    api.remember(
        prompt="Build a dark purple SaaS dashboard with analytics",
        project_name="PurpleDash Pro",
        project_type="saas_dashboard",
        design_system={"colors": {"primary": "#7c3aed"}, "mode": "dark"},
        layout_type="dashboard",
        components=["sidebar", "stats_card", "chart_widget", "data_table"],
        success=True,
        quality_score=0.85
    )
    
    api.remember(
        prompt="Create a modern landing page for an AI startup",
        project_name="AI Launch Pro",
        project_type="landing_page",
        design_system={"colors": {"primary": "#6366f1"}, "mode": "dark"},
        layout_type="landing",
        components=["navbar", "hero", "features_grid", "cta_section"],
        success=True,
        quality_score=0.9
    )
    
    api.remember(
        prompt="Build an admin panel with user management",
        project_name="AdminHub",
        project_type="admin_panel",
        design_system={"colors": {"primary": "#64748b"}, "mode": "light"},
        layout_type="admin",
        components=["data_table", "sidebar", "crud_form"],
        success=True,
        quality_score=0.75
    )
    
    # Test recall
    print(f"\n   Testing recall...")
    results = api.recall("dashboard with purple theme")
    for r in results:
        print(f"      - {r['name']}: {r['similarity']} similar ({r['type']})")
    
    # Test recommendations
    print(f"\n   Testing recommendations...")
    recs = api.recommend("purple analytics dashboard")
    if recs.get("has_recommendations"):
        print(f"      Components: {recs.get('recommended_components', [])}")
        print(f"      Color: {recs.get('recommended_color')}")
    
    # Test stats
    print(f"\n   Memory Stats:")
    stats = api.stats()
    print(f"      Projects: {stats['total_projects']}")
    print(f"      Success Rate: {stats['success_rate']}")
    
    # Test recent
    print(f"\n   Recent generations:")
    for mem in api.recent(3):
        print(f"      - {mem['project_name']} ({mem['project_type']})")
    
    api.store.display_stats()
    
    print("\n✅ Memory System test complete")
    
    return api


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_memory_api()