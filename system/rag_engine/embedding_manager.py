"""
NOVARYX - Embedding Manager
Generates embeddings using Ollama (nomic-embed-text) or fallback methods.

Compatible with ChromaDB v0.5+
"""

import logging
import json
import numpy as np
from typing import List, Optional, Any

logger = logging.getLogger("novaryx.embeddings")


class EmbeddingManager:
    """
    Manages text embeddings for ChromaDB.
    
    Primary: Ollama nomic-embed-text (local, free)
    Fallback: sentence-transformers (if installed)
    """
    
    def __init__(self, use_ollama: bool = True):
        self.use_ollama = use_ollama
        self._ollama_url = "http://localhost:11434/api/embeddings"
        self._embedding_model = "nomic-embed-text:latest"
        self._sentence_transformer = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize the embedding system"""
        if self.use_ollama:
            if self._check_ollama():
                self._initialized = True
                logger.info("Embedding: Using Ollama nomic-embed-text")
                return True
        
        # Fallback to sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            self._sentence_transformer = SentenceTransformer("all-MiniLM-L6-v2")
            self._initialized = True
            logger.info("Embedding: Using sentence-transformers (all-MiniLM-L6-v2)")
            return True
        except ImportError:
            logger.warning("sentence-transformers not installed")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformer: {e}")
        
        logger.error("No embedding method available")
        return False
    
    def _check_ollama(self) -> bool:
        """Check if Ollama embedding model is available"""
        import requests
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                if "nomic-embed-text:latest" in model_names:
                    return True
                logger.warning("nomic-embed-text not found in Ollama")
        except Exception:
            logger.debug("Ollama not reachable for embeddings")
        return False
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        if not self._initialized:
            self.initialize()
        
        if self.use_ollama:
            embedding = self._ollama_embed(text)
            if embedding:
                return embedding
        
        if self._sentence_transformer:
            return self._sentence_transformer.encode(text).tolist()
        
        logger.error("Cannot generate embedding - no method available")
        return []
    
    def _ollama_embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding via Ollama"""
        import requests
        try:
            response = requests.post(
                self._ollama_url,
                json={
                    "model": self._embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                embedding = data.get("embedding", [])
                if embedding and isinstance(embedding, list):
                    return [float(x) for x in embedding]
                else:
                    logger.warning(f"Unexpected embedding format: {type(embedding)}")
                    return None
        except Exception as e:
            logger.debug(f"Ollama embedding failed: {e}")
        return None
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self.generate_embedding(text) for text in texts]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of generated embeddings"""
        test_embedding = self.generate_embedding("test")
        return len(test_embedding) if test_embedding else 768


class OllamaEmbeddingFunction:
    """
    ChromaDB-compatible embedding function using Ollama.
    Returns 2D numpy arrays (N x D) for maximum compatibility.
    """
    
    def __init__(self, model_name: str = "nomic-embed-text:latest"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/embeddings"
    
    def _call_ollama_api(self, prompt: str) -> np.ndarray:
        """Make a single API call to Ollama."""
        import requests
        try:
            response = requests.post(
                self.api_url,
                json={"model": self.model_name, "prompt": prompt},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                embedding = data.get("embedding", [])
                if isinstance(embedding, list) and len(embedding) > 0:
                    # Return vector as 1D array
                    val = embedding[0] if isinstance(embedding[0], list) else embedding
                    return np.array(val, dtype=np.float32)
                return np.zeros(768, dtype=np.float32)
            return np.zeros(768, dtype=np.float32)
        except Exception:
            return np.zeros(768, dtype=np.float32)
    
    def __call__(self, input):
        """
        Generate embeddings for a list of documents.
        ChromaDB expects List[np.ndarray] or 2D np.ndarray.
        """
        if isinstance(input, str):
            texts = [input]
        else:
            texts = list(input)
            
        embeddings = [self._call_ollama_api(text) for text in texts]
        return np.array(embeddings, dtype=np.float32)
