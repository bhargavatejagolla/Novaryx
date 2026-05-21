"""
NOVARYX - Similarity Engine
Scores how similar new prompts are to past projects for smart reuse.
"""

import logging
from typing import Dict, List, Tuple, Optional
from .memory_store import MemoryStore, ProjectMemory

logger = logging.getLogger("novaryx.similarity")


class SimilarityEngine:
    """Finds similar past projects for a new prompt"""
    
    def __init__(self, memory_store: MemoryStore = None):
        self.memory_store = memory_store or MemoryStore()
    
    def find_similar(
        self,
        prompt: str,
        project_type: str = None,
        top_k: int = 5,
        min_score: float = 0.2
    ) -> List[Tuple[ProjectMemory, float]]:
        """
        Find past projects similar to the new prompt.
        
        Returns list of (memory, similarity_score) sorted by score.
        """
        
        prompt_lower = prompt.lower()
        scores = []
        
        for mem in self.memory_store.memories.values():
            score = self._calculate_similarity(prompt_lower, mem)
            
            # Boost if same project type
            if project_type and mem.project_type == project_type:
                score *= 1.5
            
            # Boost successful projects
            if mem.success:
                score *= 1.2
            
            if score >= min_score:
                scores.append((mem, min(score, 1.0)))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
    def _calculate_similarity(self, prompt_lower: str, memory: ProjectMemory) -> float:
        """Calculate similarity score between prompt and memory"""
        score = 0.0
        
        # Word overlap
        prompt_words = set(prompt_lower.split())
        memory_words = set(memory.prompt.lower().split())
        
        if prompt_words and memory_words:
            overlap = len(prompt_words & memory_words)
            score += (overlap / max(len(prompt_words), 1)) * 0.4
        
        # Component overlap (check if requesting similar components)
        for comp in memory.components_used:
            comp_lower = comp.lower().replace("_", " ")
            if comp_lower in prompt_lower:
                score += 0.1
        
        # Design similarity
        if memory.primary_color and memory.primary_color in prompt_lower:
            score += 0.1
        if memory.mode and memory.mode in prompt_lower:
            score += 0.05
        if memory.font and memory.font.lower() in prompt_lower:
            score += 0.05
        
        # Page type similarity
        page_names = [p.get("name", "").lower() for p in memory.pages]
        for pname in page_names:
            if pname in prompt_lower:
                score += 0.1
        
        return min(score, 1.0)
    
    def get_best_match(self, prompt: str, project_type: str = None) -> Optional[ProjectMemory]:
        """Get the single best matching past project"""
        similar = self.find_similar(prompt, project_type, top_k=1)
        if similar:
            return similar[0][0]
        return None
    
    def get_recommendations(self, prompt: str, project_type: str = None) -> Dict:
        """Get recommendations based on similar past projects"""
        similar = self.find_similar(prompt, project_type, top_k=5)
        
        if not similar:
            return {"has_recommendations": False, "message": "No similar projects found"}
        
        # Aggregate recommendations
        all_components = []
        all_colors = []
        all_layouts = []
        
        for mem, score in similar:
            all_components.extend(mem.components_used)
            if mem.primary_color:
                all_colors.append(mem.primary_color)
            if mem.layout_type:
                all_layouts.append(mem.layout_type)
        
        # Get most common
        from collections import Counter
        
        return {
            "has_recommendations": True,
            "similar_count": len(similar),
            "top_match": similar[0][0].project_name if similar else "",
            "recommended_components": [c[0] for c in Counter(all_components).most_common(5)],
            "recommended_color": Counter(all_colors).most_common(1)[0][0] if all_colors else None,
            "recommended_layout": Counter(all_layouts).most_common(1)[0][0] if all_layouts else None,
            "similar_projects": [
                {"name": mem.project_name, "score": f"{score:.0%}", "success": mem.success}
                for mem, score in similar
            ]
        }