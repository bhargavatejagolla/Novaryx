"""
NOVARYX - Groq Provider
Highest-priority cloud inference via Groq API (OpenAI-compatible).

Priority: 200 (beats Ollama=100, Gemini=50)

Why Groq first?
  - Fastest inference (300+ tokens/sec)
  - No local memory required
  - No timeout issues (typical 5-10s for 4K tokens)
  - Large context windows (8K–128K depending on model)

Models:
  - llama-3.3-70b-versatile  → generation / repair / planning / default (high quality)
  - llama-3.1-8b-instant     → fallback / fast tasks

Rate limits (free tier):
  - ~30 req/min per model
  - ~6000 tokens/min
  Auto-retry with backoff is built in for 429s.
"""

import os
import time
import json
import logging
import requests
from typing import Optional, List, Dict, Any
from .base_provider import BaseProvider, GenerationResult

logger = logging.getLogger("novaryx.groq")

GROQ_API_BASE = "https://api.groq.com/openai/v1"


class GroqProvider(BaseProvider):
    """Groq cloud inference provider (OpenAI-compatible API)."""

    # Model role mapping – all have 131K context
    MODEL_ROLES: Dict[str, str] = {
        "generation": "llama-3.3-70b-versatile",
        "repair":     "llama-3.3-70b-versatile",
        "planning":   "llama-3.3-70b-versatile",
        "embedding":  "llama-3.1-8b-instant",   # Groq has no embedding; returns empty
        "default":    "llama-3.3-70b-versatile",
    }

    # Token limit per request – stay well under context to avoid ctx_length_exceeded
    MAX_TOKENS_HARD_CAP = 8000

    def __init__(self):
        super().__init__(name="groq", priority=100)  # High priority, but behind Ollama
        self.api_key = (
            os.environ.get("GROQ_API_KEY")
            or os.environ.get("GROQ_API_KEY_OVERRIDE")
            or ""
        )
        # Allow per-role model overrides via env
        self.MODEL_ROLES = dict(self.MODEL_ROLES)
        env_gen = os.environ.get("GROQ_MODEL_GENERATION")
        env_plan = os.environ.get("GROQ_MODEL_PLANNING")
        if env_gen:
            self.MODEL_ROLES["generation"] = env_gen
            self.MODEL_ROLES["repair"] = env_gen
            self.MODEL_ROLES["default"] = env_gen
        if env_plan:
            self.MODEL_ROLES["planning"] = env_plan

        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # BaseProvider interface
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check if Groq API key is set and reachable."""
        if not self.api_key:
            logger.debug("GROQ_API_KEY not set – Groq unavailable")
            self._available = False
            return False

        try:
            resp = requests.get(
                f"{GROQ_API_BASE}/models",
                headers=self._headers,
                timeout=8,
            )
            if resp.status_code == 200:
                models = [m["id"] for m in resp.json().get("data", [])]
                logger.info(f"Groq available – {len(models)} models")
                self._available = True
                self._groq_models = models
                return True
            else:
                logger.warning(f"Groq returned HTTP {resp.status_code}")
        except requests.exceptions.Timeout:
            logger.warning("Groq availability check timed out")
        except Exception as e:
            logger.warning(f"Groq check failed: {e}")

        self._available = False
        return False

    def get_available_models(self) -> List[str]:
        models = getattr(self, "_groq_models", None)
        if models:
            return models
        # Re-check
        self.is_available()
        return getattr(self, "_groq_models", list(self.MODEL_ROLES.values()))

    def get_model_for_role(self, role: str) -> str:
        return self.MODEL_ROLES.get(role, self.MODEL_ROLES["default"])

    def generate(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
        role: str = "default",
        **kwargs,
    ) -> GenerationResult:
        """Generate text using Groq's chat completions endpoint."""

        start_time = time.time()
        model = model or self.get_model_for_role(role)

        # Enforce hard token cap to avoid context errors
        safe_max_tokens = min(max_tokens, self.MAX_TOKENS_HARD_CAP)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": safe_max_tokens,
            "top_p": kwargs.get("top_p", 0.9),
            "stream": False,  # Always collect full response; streaming handled separately
        }

        # Retry loop for rate-limit errors
        max_retries = 5
        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    f"{GROQ_API_BASE}/chat/completions",
                    headers=self._headers,
                    json=payload,
                    timeout=120,  # 2 minutes – more than enough for Groq
                )

                # Rate limit – back off and retry
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("retry-after", 60))
                    if retry_after > 10:
                        logger.warning(
                            f"Groq rate limit hit (attempt {attempt+1}/{max_retries}). "
                            f"Required wait time ({retry_after}s) exceeds threshold (10s). "
                            "Aborting Groq request to trigger fallback."
                        )
                        return GenerationResult(
                            text="",
                            model=model,
                            provider="groq",
                            success=False,
                            error=f"Groq rate limit exceeded (requires {retry_after}s wait)",
                        )
                    
                    logger.warning(
                        f"Groq rate limit hit (attempt {attempt+1}/{max_retries}). "
                        f"Waiting {retry_after}s…"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    return GenerationResult(
                        text="",
                        model=model,
                        provider="groq",
                        success=False,
                        error="Groq rate limit exceeded after retries",
                    )

                if resp.status_code != 200:
                    error_info = ""
                    try:
                        error_info = resp.json().get("error", {}).get("message", resp.text[:300])
                    except Exception:
                        error_info = resp.text[:300]
                    logger.error(f"Groq HTTP {resp.status_code}: {error_info}")
                    return GenerationResult(
                        text="",
                        model=model,
                        provider="groq",
                        success=False,
                        error=f"Groq HTTP {resp.status_code}: {error_info}",
                    )

                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                tokens_used = usage.get("total_tokens", len(text) // 4)
                elapsed = (time.time() - start_time) * 1000

                logger.info(
                    f"Groq OK: model={model}, tokens={tokens_used}, time={elapsed:.0f}ms"
                )

                return GenerationResult(
                    text=text,
                    model=model,
                    provider="groq",
                    tokens_used=tokens_used,
                    generation_time_ms=elapsed,
                    success=True,
                )

            except requests.exceptions.Timeout:
                logger.error(f"Groq request timed out (attempt {attempt+1})")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return GenerationResult(
                    text="",
                    model=model,
                    provider="groq",
                    success=False,
                    error="Groq request timed out after 120s",
                )
            except Exception as e:
                logger.error(f"Groq generation error: {e}")
                return GenerationResult(
                    text="",
                    model=model,
                    provider="groq",
                    success=False,
                    error=str(e),
                )

        # Should never reach here
        return GenerationResult(
            text="", model=model, provider="groq", success=False,
            error="Max retries exceeded"
        )

    def get_embedding(self, text: str) -> List[float]:
        """Groq does not provide embeddings – return empty list (Ollama handles this)."""
        return []

    def supports_embeddings(self) -> bool:
        return False

    def supports_streaming(self) -> bool:
        return True
