"""
NOVARYX - Inference Layer
Multi-provider LLM abstraction with automatic fallback.

Priority:
  1. Groq   (cloud, fastest – set GROQ_API_KEY in .env)
  2. Ollama  (local, free – run: ollama serve)
  3. Gemini  (cloud – set GEMINI_API_KEY in .env)
"""

from .provider_factory import (
    get_provider,
    list_available_providers,
    get_current_provider_info,
    reset_providers,
)
from .base_provider import BaseProvider

__all__ = [
    "get_provider",
    "list_available_providers",
    "get_current_provider_info",
    "reset_providers",
    "BaseProvider",
]