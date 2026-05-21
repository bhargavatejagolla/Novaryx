"""
NOVARYX - Base Provider
Abstract interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Generator
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Standardized result from any provider"""
    text: str
    model: str
    provider: str
    tokens_used: int = 0
    generation_time_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


class BaseProvider(ABC):
    """
    Abstract base for all LLM providers.
    Every provider (Ollama, Gemini, future ones) implements this.
    """
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority  # Higher = preferred
        self._available = False
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is ready to use"""
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        stream: bool = False,
        **kwargs
    ) -> GenerationResult:
        """Generate text from a prompt"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> list[str]:
        """List models available from this provider"""
        pass
    
    @abstractmethod
    def get_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for text"""
        pass
    
    def supports_streaming(self) -> bool:
        """Does this provider support token-by-token streaming?"""
        return False
    
    def supports_embeddings(self) -> bool:
        """Does this provider support embedding generation?"""
        return False
    
    def get_priority(self) -> int:
        return self.priority
    
    def __repr__(self):
        return f"{self.name}(available={self._available}, priority={self.priority})"