"""
NOVARYX - Google Gemini Provider (OPTIONAL)
Cloud-based inference when API key is available.

Models:
  - gemini-2.0-flash       → Fast, affordable
  - gemini-2.0-pro         → Better reasoning (more expensive)
  - gemini-embedding       → Embeddings

Usage:
  Set GEMINI_API_KEY in .env file
  Set USE_GEMINI=true in .env
"""

import os
import time
import logging
from typing import Optional, List
from .base_provider import BaseProvider, GenerationResult

logger = logging.getLogger("novaryx.gemini")

# Try importing Google AI SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.info("google-generativeai not installed. Gemini provider will be unavailable.")


class GeminiProvider(BaseProvider):
    """Google Gemini cloud inference provider (OPTIONAL)"""
    
    MODEL_MAP = {
        "generation": "gemini-2.0-flash",
        "planning": "gemini-2.0-flash",
        "repair": "gemini-2.0-flash",
        "default": "gemini-2.0-flash",
        "pro": "gemini-2.0-pro-exp-02-05"
    }
    
    def __init__(self, api_key: str = None):
        super().__init__(name="gemini", priority=50)  # Lower priority than Ollama
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._configured = False
        self._model_cache = {}
        
        if GEMINI_AVAILABLE and self.api_key:
            self._setup()
    
    def _setup(self):
        """Configure Gemini SDK"""
        try:
            genai.configure(api_key=self.api_key)
            self._configured = True
            logger.info("Gemini provider configured")
        except Exception as e:
            logger.error(f"Gemini setup failed: {e}")
            self._configured = False
    
    def is_available(self) -> bool:
        """Check if Gemini is ready"""
        if not GEMINI_AVAILABLE:
            return False
        if not self.api_key:
            return False
        if not self._configured:
            self._setup()
        
        self._available = self._configured
        return self._available
    
    def get_available_models(self) -> List[str]:
        """List available Gemini models"""
        if not self.is_available():
            return []
        
        try:
            models = genai.list_models()
            return [m.name for m in models if "gemini" in m.name.lower()]
        except Exception as e:
            logger.error(f"Failed to list Gemini models: {e}")
            return list(self.MODEL_MAP.values())
    
    def get_model_for_role(self, role: str) -> str:
        return self.MODEL_MAP.get(role, self.MODEL_MAP["default"])
    
    def generate(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        stream: bool = False,
        role: str = "default",
        **kwargs
    ) -> GenerationResult:
        """Generate text using Gemini"""
        
        if not self.is_available():
            return GenerationResult(
                text="",
                model="gemini",
                provider="gemini",
                success=False,
                error="Gemini not available. Set GEMINI_API_KEY in .env"
            )
        
        start_time = time.time()
        model_name = model or self.get_model_for_role(role)
        
        try:
            # Get or create model instance
            if model_name not in self._model_cache:
                self._model_cache[model_name] = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                        "top_p": kwargs.get("top_p", 0.9),
                    }
                )
            
            gemini_model = self._model_cache[model_name]
            
            # Build content
            contents = []
            if system_prompt:
                contents.append({"role": "user", "parts": [system_prompt]})
                contents.append({"role": "model", "parts": ["Understood."]})
            contents.append({"role": "user", "parts": [prompt]})
            
            response = gemini_model.generate_content(contents)
            
            elapsed = (time.time() - start_time) * 1000
            
            result_text = response.text if response.text else ""
            
            logger.info(
                f"Gemini generation complete: model={model_name}, "
                f"time={elapsed:.0f}ms"
            )
            
            return GenerationResult(
                text=result_text,
                model=model_name,
                provider="gemini",
                tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                generation_time_ms=elapsed,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return GenerationResult(
                text="",
                model=model_name,
                provider="gemini",
                success=False,
                error=str(e)
            )
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini embedding model"""
        if not self.is_available():
            return []
        
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result.get("embedding", [])
        except Exception as e:
            logger.error(f"Gemini embedding failed: {e}")
            return []
    
    def supports_embeddings(self) -> bool:
        return self.is_available()


def is_gemini_configured() -> bool:
    """Check if Gemini API key is set"""
    return bool(os.getenv("GEMINI_API_KEY"))