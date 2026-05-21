"""
NOVARYX - Hybrid Search Engine
Combines semantic search (embeddings) with keyword search (BM25-style).

Provides:
  - Semantic understanding via embeddings
  - Exact matching via keyword search
  - Hybrid ranking that combines both
  - Filtered search by type, date, quality
  - Search result explanations
"""

import logging
import math
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter

from .memory_store import MemoryStore, ProjectMemory

logger = logging.getLogger("novaryx.hybrid_search")


class BM25Scorer:
    """Simple BM25-style keyword scoring"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
    
    def score(self, query: str, document: str, avg_doc_length: float = 100) -> float:
        """Score a document against a query"""
        query_terms = query.lower().split()
        doc_terms = document.lower().split()
        doc_length = len(doc_terms)
        
        score = 0.0
        
        for term in query_terms:
            if term in doc_terms:
                tf = doc_terms.count(term)
                idf = self._idf(term, doc_terms)
                
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / max(avg_doc_length, 1))
                
                score += idf * (numerator / denominator)
        
        return score
    
    def _idf(self, term: str, doc_terms: List[str]) -> float:
        """Inverse document frequency (simplified)"""
        tf = doc_terms.count(term)
        return math.log(1 + (len(doc_terms) - tf + 0.5) / (tf + 0.5))


class HybridSearch:
    """
    Combined semantic + keyword search for project memory.
    
    Uses:
    - Semantic search via ChromaDB embeddings
    - Keyword search via BM25
    - Hybrid ranking (weighted combination)
    - Filtering by type, date, quality
    """
    
    def __init__(self, memory_store: MemoryStore = None):
        self.memory_store = memory_store or MemoryStore()
        self.bm25 = BM25Scorer()
        
        # Hybrid weights
        self.semantic_weight = 0.6
        self.keyword_weight = 0.4
    
    def search(
        self,
        query: str,
        project_type: str = None,
        top_k: int = 10,
        min_quality: float = 0.0,
        success_only: bool = False,
        days_recent: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search across all memories.
        
        Args:
            query: Search query
            project_type: Filter by project type
            top_k: Max results
            min_quality: Minimum quality score
            success_only: Only return successful projects
            days_recent: Only return projects from last N days
        
        Returns:
            Ranked list of results with explanations
        """
        
        memories = list(self.memory_store.memories.values())
        
        # Apply filters
        if project_type:
            memories = [m for m in memories if m.project_type == project_type]
        if min_quality > 0:
            memories = [m for m in memories if m.quality_score >= min_quality]
        if success_only:
            memories = [m for m in memories if m.success]
        if days_recent:
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=days_recent)
            memories = [m for m in memories if datetime.fromisoformat(m.created_at) > cutoff]
        
        if not memories:
            return []
        
        # Semantic scoring via ChromaDB
        semantic_scores = self._semantic_search(query, memories)
        
        # Keyword scoring via BM25
        keyword_scores = self._keyword_search(query, memories)
        
        # Hybrid ranking
        results = []
        for mem in memories:
            sem_score = semantic_scores.get(mem.memory_id, 0.0)
            kw_score = keyword_scores.get(mem.memory_id, 0.0)
            
            # Combine scores
            hybrid_score = (sem_score * self.semantic_weight) + (kw_score * self.keyword_weight)
            
            # Boost factors
            if mem.success:
                hybrid_score *= 1.1
            if mem.quality_score > 0.8:
                hybrid_score *= 1.1
            
            results.append({
                "memory_id": mem.memory_id,
                "project_name": mem.project_name,
                "project_type": mem.project_type,
                "hybrid_score": hybrid_score,
                "semantic_score": sem_score,
                "keyword_score": kw_score,
                "components": mem.components_used[:5],
                "primary_color": mem.primary_color,
                "success": mem.success,
                "quality": mem.quality_score,
                "created": mem.created_at,
                "explanation": self._explain_result(query, mem, hybrid_score, sem_score, kw_score),
            })
        
        # Sort by hybrid score
        results.sort(key=lambda r: r["hybrid_score"], reverse=True)
        
        logger.info(f"Hybrid search: '{query[:50]}' → {len(results)} results")
        
        return results[:top_k]
    
    def _semantic_search(self, query: str, memories: List[ProjectMemory]) -> Dict[str, float]:
        """Semantic search using ChromaDB"""
        scores = {}
        
        try:
            chroma = self.memory_store._get_chroma()
            if chroma:
                results = chroma.query_templates(query, n_results=min(len(memories), 20))
                for result in results:
                    mem_id = result.get("id", "").replace("mem_", "")
                    distance = result.get("distance", 1.0)
                    scores[mem_id] = max(0, 1.0 - distance)
        except Exception as e:
            logger.debug(f"Semantic search skipped: {e}")
        
        # Fallback: simple embedding-like scoring
        if not scores:
            query_words = set(query.lower().split())
            for mem in memories:
                desc_words = set(mem.prompt.lower().split())
                if query_words and desc_words:
                    overlap = len(query_words & desc_words)
                    scores[mem.memory_id] = overlap / max(len(query_words), 1)
        
        return scores
    
    def _keyword_search(self, query: str, memories: List[ProjectMemory]) -> Dict[str, float]:
        """Keyword search using BM25"""
        scores = {}
        
        # Calculate average document length
        avg_length = sum(len(m.prompt.split()) for m in memories) / max(len(memories), 1)
        
        for mem in memories:
            doc_text = f"{mem.project_name} {mem.prompt} {' '.join(mem.components_used)} {mem.project_type}"
            score = self.bm25.score(query, doc_text, avg_length)
            scores[mem.memory_id] = score
        
        # Normalize scores to 0-1
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _explain_result(
        self,
        query: str,
        memory: ProjectMemory,
        hybrid_score: float,
        semantic_score: float,
        keyword_score: float
    ) -> str:
        """Generate human-readable explanation for search result"""
        reasons = []
        
        query_lower = query.lower()
        
        # Check keyword matches
        if query_lower in memory.project_name.lower():
            reasons.append("Project name matches query")
        
        matching_components = [c for c in memory.components_used if c.replace("_", " ") in query_lower]
        if matching_components:
            reasons.append(f"Uses matching components: {', '.join(matching_components[:3])}")
        
        if memory.primary_color and memory.primary_color in query_lower:
            reasons.append(f"Uses requested color: {memory.primary_color}")
        
        if memory.project_type and memory.project_type.replace("_", " ") in query_lower:
            reasons.append(f"Same project type: {memory.project_type}")
        
        if semantic_score > 0.7:
            reasons.append("Semantically very similar")
        elif keyword_score > 0.7:
            reasons.append("Strong keyword match")
        
        if not reasons:
            reasons.append("General similarity match")
        
        return " | ".join(reasons[:3])
    
    def search_similar_prompts(self, prompt: str, top_k: int = 5) -> List[Dict]:
        """Find projects generated from similar prompts"""
        return self.search(prompt, top_k=top_k)
    
    def search_by_components(self, components: List[str], top_k: int = 5) -> List[Dict]:
        """Find projects using specific components"""
        query = " ".join(components)
        return self.search(query, top_k=top_k)
    
    def get_trending(self, days: int = 30, top_k: int = 5) -> List[Dict]:
        """Get trending/popular project patterns"""
        memories = list(self.memory_store.memories.values())
        
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        recent = [m for m in memories if datetime.fromisoformat(m.created_at) > cutoff]
        
        # Count patterns
        component_trends = Counter()
        color_trends = Counter()
        type_trends = Counter()
        
        for mem in recent:
            for comp in mem.components_used:
                component_trends[comp] += 1
            if mem.primary_color:
                color_trends[mem.primary_color] += 1
            if mem.project_type:
                type_trends[mem.project_type] += 1
        
        return {
            "trending_components": component_trends.most_common(top_k),
            "trending_colors": color_trends.most_common(top_k),
            "trending_types": type_trends.most_common(top_k),
            "period_days": days,
            "total_projects_analyzed": len(recent),
        }


# ---- Test ----

def test_hybrid_search():
    """Test hybrid search"""
    
    print("\n" + "=" * 60)
    print("🧪 HYBRID SEARCH TEST")
    print("=" * 60)
    
    from .memory_store import MemoryStore
    from .project_indexer import ProjectIndexer
    
    store = MemoryStore()
    indexer = ProjectIndexer(store)
    
    # Index test projects
    test_data = [
        ("PurpleDash Pro", "saas_dashboard", ["sidebar", "stats_card", "chart_widget", "data_table"], "#7c3aed"),
        ("BlueAnalytics", "saas_dashboard", ["sidebar", "chart_widget", "data_table", "activity_feed"], "#3b82f6"),
        ("GreenLanding", "landing_page", ["navbar", "hero", "features_grid", "cta_section", "footer"], "#10b981"),
        ("AdminHub Pro", "admin_panel", ["sidebar", "data_table", "crud_form", "modal"], "#64748b"),
        ("OrangePortfolio", "portfolio", ["navbar", "hero_3d", "project_grid", "contact_form"], "#f97316"),
    ]
    
    for name, ptype, comps, color in test_data:
        indexer.index_generation(
            prompt=f"Build a {color} {ptype} named {name}",
            project_name=name,
            project_type=ptype,
            design_system={"colors": {"primary": color}, "mode": "dark"},
            components=comps,
            success=True,
            quality_score=0.7 + (len(comps) * 0.03),
        )
    
    # Test search
    search = HybridSearch(store)
    
    print(f"\n   Search: 'dashboard with charts and purple'")
    results = search.search("dashboard with charts and purple")
    for r in results:
        print(f"      - {r['project_name']}: score={r['hybrid_score']:.2f}")
        print(f"        {r['explanation']}")
    
    print(f"\n   Search: 'landing page' (type filter)")
    results = search.search("landing page", project_type="landing_page")
    for r in results:
        print(f"      - {r['project_name']}: {r['explanation']}")
    
    print(f"\n   Trending:")
    trends = search.get_trending(days=365)
    print(f"      Components: {trends['trending_components']}")
    print(f"      Colors: {trends['trending_colors']}")
    
    print("\n✅ Hybrid Search test complete")
    
    return search


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_hybrid_search()