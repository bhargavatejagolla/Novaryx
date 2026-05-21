"""
NOVARYX - Advanced RAG & Memory System
Long-term memory, learning engine, and hybrid search.

Phase 4 makes NOVARYX smarter with every generation.
"""

from .memory_store import MemoryStore, ProjectMemory
from .project_indexer import ProjectIndexer
from .similarity_engine import SimilarityEngine
from .learning_engine import LearningEngine
# from .preference_learner import PreferenceLearner
from .context_optimizer import ContextOptimizer
from .hybrid_search import HybridSearch
from .memory_api import MemoryAPI

__all__ = [
    "MemoryStore",
    "ProjectMemory",
    "ProjectIndexer",
    "SimilarityEngine",
    "LearningEngine",
    # "PreferenceLearner",
    "ContextOptimizer",
    "HybridSearch",
    "MemoryAPI",
]