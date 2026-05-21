"""
NOVARYX - RAG Engine
ChromaDB-based retrieval augmented generation system.

Collections:
  - templates: Full template metadata and structure
  - components: Individual component patterns
  - architectures: Architecture patterns and designs
  - generation_history: Past generations for learning
"""

from .chromadb_client import ChromaDBClient
from .retriever import TemplateRetriever
from .embedding_manager import EmbeddingManager

__all__ = ["ChromaDBClient", "TemplateRetriever", "EmbeddingManager"]