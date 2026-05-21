"""
NOVARYX - Template Registry
Manages template files on disk and syncs with ChromaDB RAG system.

Connects:
  - Template files (on disk)
  - ChromaDB (metadata + embeddings)
  - RAG Retriever (semantic search)
  - Generation Pipeline (template adaptation)
"""

from .template_registry import TemplateRegistry
from .template_validator import TemplateValidator
from .template_adapter import TemplateAdapter, AdaptationRule

__all__ = [
    "TemplateRegistry",
    "TemplateValidator",
    "TemplateAdapter",
    "AdaptationRule"
]