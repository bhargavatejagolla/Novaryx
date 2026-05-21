"""
NOVARYX - Context Window Optimizer
Smart context management to prevent token overflow.

Handles:
  - Token budget calculation
  - Relevance scoring for context pieces
  - Smart pruning of irrelevant context
  - Progressive context loading
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger("novaryx.context_optimizer")


@dataclass
class ContextChunk:
    """A piece of context with relevance scoring"""
    content: str
    source: str
    relevance_score: float = 0.0
    priority: int = 1
    token_estimate: int = 0
    can_prune: bool = True
    
    def __repr__(self):
        return f"Chunk({self.source}, score={self.relevance_score:.2f}, tokens≈{self.token_estimate})"


class TokenBudget:
    """Manages token budgets for different models"""
    
    # Model token limits
    MODEL_LIMITS = {
        "qwen2.5-coder:7b": 8192,
        "deepseek-coder:6.7b": 8192,
        "gemini-2.0-flash": 1048576,
        "default": 4096,
    }
    
    # Reserved for response
    RESPONSE_RESERVE = 2048
    
    # Reserved for system prompt
    SYSTEM_RESERVE = 500
    
    @classmethod
    def get_limit(cls, model: str) -> int:
        """Get token limit for a model"""
        return cls.MODEL_LIMITS.get(model, cls.MODEL_LIMITS["default"])
    
    @classmethod
    def get_available(cls, model: str) -> int:
        """Get available tokens after reserves"""
        return cls.get_limit(model) - cls.RESPONSE_RESERVE - cls.SYSTEM_RESERVE
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Quick token estimation (4 chars ≈ 1 token)"""
        return max(1, len(text) // 4)
    
    @staticmethod
    def estimate_tokens_detailed(text: str) -> Dict[str, int]:
        """Detailed token estimation"""
        words = len(text.split())
        chars = len(text)
        return {
            "word_count": words,
            "char_count": chars,
            "token_estimate": max(1, chars // 4),
            "token_estimate_alt": max(1, int(words * 1.3)),
        }


class ContextOptimizer:
    """
    Optimizes context for LLM prompts.
    
    Ensures:
    - Context fits within model token limits
    - Most relevant information is prioritized
    - Irrelevant context is pruned
    - Progressive loading for large contexts
    """
    
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        self.model = model
        self.token_limit = TokenBudget.get_available(model)
        self.chunks: List[ContextChunk] = []
    
    def add_chunk(
        self,
        content: str,
        source: str,
        priority: int = 1,
        can_prune: bool = True
    ):
        """Add a context chunk"""
        chunk = ContextChunk(
            content=content,
            source=source,
            priority=priority,
            token_estimate=TokenBudget.estimate_tokens(content),
            can_prune=can_prune,
        )
        self.chunks.append(chunk)
    
    def add_project_spec(self, spec: Any):
        """Add project specification as context"""
        if hasattr(spec, 'to_dict'):
            data = spec.to_dict()
        elif isinstance(spec, dict):
            data = spec
        else:
            return
        
        # Core info - high priority, can't prune
        core = {
            "type": data.get("project_type", ""),
            "name": data.get("project_name", ""),
            "complexity": data.get("complexity", "medium"),
        }
        self.add_chunk(
            f"Project: {json.dumps(core)}",
            "project_core",
            priority=10,
            can_prune=False
        )
        
        # Design - high priority
        design = data.get("design", {})
        if design:
            self.add_chunk(
                f"Design: {json.dumps(design)}",
                "project_design",
                priority=8,
                can_prune=False
            )
        
        # Pages - medium priority
        pages = data.get("pages", [])
        if pages:
            page_summary = [{"name": p.get("name", ""), "route": p.get("route", "")} for p in pages[:10]]
            self.add_chunk(
                f"Pages: {json.dumps(page_summary)}",
                "project_pages",
                priority=6,
                can_prune=True
            )
        
        # Features - medium priority
        features = data.get("features", [])
        if features:
            feature_names = [f.get("name", "") for f in features[:15]]
            self.add_chunk(
                f"Features: {', '.join(feature_names)}",
                "project_features",
                priority=5,
                can_prune=True
            )
    
    def add_similar_projects(self, similar: List[Tuple[Any, float]]):
        """Add similar project context"""
        if not similar:
            return
        
        summaries = []
        for mem, score in similar[:5]:
            summaries.append({
                "name": mem.project_name,
                "similarity": f"{score:.0%}",
                "components": mem.components_used[:5],
                "success": mem.success,
            })
        
        self.add_chunk(
            f"Similar projects: {json.dumps(summaries)}",
            "similar_projects",
            priority=4,
            can_prune=True
        )
    
    def add_components_library(self, components: List[str]):
        """Add available components context"""
        if components:
            self.add_chunk(
                f"Available components: {', '.join(components[:20])}",
                "component_library",
                priority=7,
                can_prune=True
            )
    
    def score_relevance(self, query: str):
        """Score all chunks by relevance to query"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for chunk in self.chunks:
            content_lower = chunk.content.lower()
            
            # Word overlap scoring
            content_words = set(content_lower.split())
            overlap = len(query_words & content_words)
            
            # Keyword bonus
            bonus = 0
            important_keywords = ["color", "design", "component", "layout", "page", "route", "feature"]
            for kw in important_keywords:
                if kw in query_lower and kw in content_lower:
                    bonus += 0.1
            
            chunk.relevance_score = min(1.0, (overlap / max(len(query_words), 1)) * 0.7 + bonus + (chunk.priority * 0.05))
    
    def optimize(self, max_tokens: int = None) -> str:
        """
        Optimize context to fit within token budget.
        
        Returns optimized context string.
        """
        if max_tokens is None:
            max_tokens = self.token_limit
        
        # Sort by relevance (then priority for ties)
        self.chunks.sort(key=lambda c: (c.relevance_score, c.priority), reverse=True)
        
        # Build context until token budget exhausted
        selected = []
        used_tokens = 0
        
        for chunk in self.chunks:
            if used_tokens + chunk.token_estimate > max_tokens:
                if chunk.can_prune:
                    continue
                else:
                    # Truncate if essential
                    available = max_tokens - used_tokens
                    if available > 100:
                        truncated = chunk.content[:available * 4] + "..."
                        selected.append(truncated)
                        used_tokens += TokenBudget.estimate_tokens(truncated)
                    break
            
            selected.append(chunk.content)
            used_tokens += chunk.token_estimate
        
        logger.info(f"Context optimized: {len(selected)}/{len(self.chunks)} chunks, "
                   f"~{used_tokens}/{max_tokens} tokens")
        
        return "\n\n".join(selected)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get report on context optimization"""
        total_tokens = sum(c.token_estimate for c in self.chunks)
        return {
            "total_chunks": len(self.chunks),
            "total_tokens_estimated": total_tokens,
            "token_limit": self.token_limit,
            "within_limit": total_tokens <= self.token_limit,
            "reduction_needed": f"{(1 - self.token_limit / max(total_tokens, 1)) * 100:.0f}%" if total_tokens > self.token_limit else "0%",
            "chunks_by_priority": {
                p: len([c for c in self.chunks if c.priority == p])
                for p in set(c.priority for c in self.chunks)
            }
        }


# Helper to make import work
import json