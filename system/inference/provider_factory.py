"""
NOVARYX - Provider Factory (Fixed)
Selects the best LLM provider per role with smart routing.

Priority (auto mode):
  planning   → Groq (fastest reasoning) → Ollama qwen → Gemini
  generation → Ollama novaryx-qwen (local, no rate limits, best for large code blocks)
  repair     → Ollama novaryx-deepseek (tuned for code repair)
  embedding  → Ollama nomic-embed-text (always local)
  default    → Groq → Ollama → Gemini

Usage:
  from system.inference.provider_factory import get_provider, get_provider_for_role
  provider = get_provider_for_role("generation")
  result = provider.generate(prompt="...", role="generation")
"""

import logging
import os
from typing import Optional, List
from .base_provider import BaseProvider
from .ollama_provider import OllamaProvider

logger = logging.getLogger("novaryx.provider_factory")

# Global instance cache
_groq_instance:   Optional[BaseProvider] = None
_ollama_instance: Optional[OllamaProvider] = None
_gemini_instance: Optional[BaseProvider] = None
_initialized = False


def _init_providers(force: bool = False):
    """Initialize all available providers (idempotent)."""
    global _groq_instance, _ollama_instance, _gemini_instance, _initialized

    if _initialized and not force:
        return

    # ── Groq (cloud, fastest for planning) ─────────────────────────────
    if _groq_instance is None:
        try:
            from .groq_provider import GroqProvider
            _groq_instance = GroqProvider()
            _groq_instance.is_available()
        except ImportError:
            logger.debug("Groq provider module not found, skipping")
            _groq_instance = None
        except Exception as e:
            logger.warning(f"Groq init failed: {e}")
            _groq_instance = None

    # ── Ollama (local, preferred for generation) ────────────────────────
    if _ollama_instance is None:
        _ollama_instance = OllamaProvider()
        _ollama_instance.is_available()

    # ── Gemini (cloud fallback) ─────────────────────────────────────────
    if _gemini_instance is None:
        try:
            from .gemini_provider import GeminiProvider
            _gemini_instance = GeminiProvider()
            _gemini_instance.is_available()
        except ImportError:
            logger.debug("Gemini SDK not installed, skipping")
            _gemini_instance = None
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}")
            _gemini_instance = None

    _initialized = True


def get_provider_for_role(role: str) -> BaseProvider:
    """
    Smart provider routing by task role.

    Role routing strategy:
      - planning   → Groq (superior reasoning for planning tasks) → Ollama → Gemini
      - generation → Ollama (no rate limits, best for large code output) → Groq → Gemini
      - repair     → Ollama (tuned deepseek model, no rate limits) → Groq → Gemini
      - embedding  → Ollama ALWAYS (only Ollama has nomic-embed-text)
      - default    → Groq → Ollama → Gemini
    """
    _init_providers()

    groq_ok   = _groq_instance   is not None and _groq_instance._available
    ollama_ok = _ollama_instance is not None and _ollama_instance._available
    gemini_ok = _gemini_instance is not None and _gemini_instance._available

    # Embeddings always use Ollama
    if role == "embedding":
        if ollama_ok:
            return _ollama_instance
        raise RuntimeError("Ollama required for embeddings — run: ollama serve")

    # Smart Routing: If Groq cloud is available and PREFER_CLOUD is active (default),
    # use high-speed Groq (300+ tps) for all cognitive tasks to avoid local CPU slow-downs!
    prefer_cloud = os.environ.get("PREFER_CLOUD", "true").lower() == "true"
    if prefer_cloud and groq_ok:
        logger.debug(f"Smart Routing: Routing role={role} to high-speed cloud provider Groq")
        return _groq_instance

    # Repair: prefer Ollama (tuned deepseek, no rate limits)
    if role == "repair":
        if ollama_ok:
            logger.debug(f"Role=repair → Ollama (novaryx-deepseek)")
            return _ollama_instance
        if groq_ok:
            logger.info("Role=repair → Groq (Ollama unavailable)")
            return _groq_instance
        if gemini_ok:
            return _gemini_instance
        raise RuntimeError("No provider available for repair")

    # Generation: prefer Ollama (no rate limits, large output, tuned qwen)
    if role == "generation":
        if ollama_ok:
            logger.debug(f"Role=generation → Ollama (novaryx-qwen)")
            return _ollama_instance
        if groq_ok:
            logger.info("Role=generation → Groq (Ollama unavailable)")
            return _groq_instance
        if gemini_ok:
            return _gemini_instance
        raise RuntimeError("No provider available for generation")

    # Planning: prefer Groq (fastest reasoning, good for structured JSON)
    if role == "planning":
        if groq_ok:
            logger.debug(f"Role=planning → Groq")
            return _groq_instance
        if ollama_ok:
            logger.info("Role=planning → Ollama (Groq unavailable)")
            return _ollama_instance
        if gemini_ok:
            return _gemini_instance
        raise RuntimeError("No provider available for planning")

    # Default: Groq → Ollama → Gemini
    if groq_ok:
        return _groq_instance
    if ollama_ok:
        return _ollama_instance
    if gemini_ok:
        return _gemini_instance

    raise RuntimeError(
        "No LLM provider available.\n"
        "  - Start Ollama: ollama serve\n"
        "  - Or set GROQ_API_KEY in .env\n"
        "  - Or set GEMINI_API_KEY in .env"
    )


def get_provider(prefer: str = "auto") -> BaseProvider:
    """
    Get the best available LLM provider (backward-compatible).

    Args:
        prefer: "auto", "groq", "ollama", or "gemini"
    """
    _init_providers()

    groq_ok   = _groq_instance   is not None and _groq_instance._available
    ollama_ok = _ollama_instance is not None and _ollama_instance._available
    gemini_ok = _gemini_instance is not None and _gemini_instance._available

    if prefer == "groq" and groq_ok:
        return _groq_instance
    if prefer == "ollama" and ollama_ok:
        return _ollama_instance
    if prefer == "gemini" and gemini_ok:
        return _gemini_instance

    # Auto: Groq → Ollama → Gemini
    if groq_ok:
        logger.info("Provider: Groq (cloud, fastest)")
        return _groq_instance
    if ollama_ok:
        logger.info("Provider: Ollama (local)")
        return _ollama_instance
    if gemini_ok:
        logger.info("Provider: Gemini (cloud)")
        return _gemini_instance

    raise RuntimeError(
        "No LLM provider available.\n"
        "  - Start Ollama: ollama serve\n"
        "  - Or set GROQ_API_KEY in .env\n"
        "  - Or set GEMINI_API_KEY in .env"
    )


def list_available_providers() -> List[dict]:
    """List all providers and their status."""
    _init_providers()

    providers = []

    groq_ok = _groq_instance is not None and _groq_instance._available
    providers.append({
        "name":     "groq",
        "available": groq_ok,
        "priority": 200,
        "role":     "planning (preferred)",
        "models":   _groq_instance.get_available_models() if groq_ok else [],
        "type":     "cloud",
        "cost":     "free tier / paid",
    })

    ollama_ok = _ollama_instance is not None and _ollama_instance._available
    providers.append({
        "name":     "ollama",
        "available": ollama_ok,
        "priority": 150,
        "role":     "generation + repair + embedding (preferred)",
        "models":   _ollama_instance.get_available_models() if ollama_ok else [],
        "type":     "local",
        "cost":     "free",
    })

    gemini_ok = _gemini_instance is not None and _gemini_instance._available
    providers.append({
        "name":     "gemini",
        "available": gemini_ok,
        "priority": 50,
        "role":     "fallback",
        "models":   ["gemini-2.0-flash"] if gemini_ok else [],
        "type":     "cloud",
        "cost":     "paid (per token)",
    })

    return providers


def get_current_provider_info() -> dict:
    """Get info about the default active provider."""
    try:
        provider = get_provider()
        return {
            "name":                provider.name,
            "available":           provider._available,
            "models":              provider.get_available_models(),
            "supports_streaming":  provider.supports_streaming(),
            "supports_embeddings": provider.supports_embeddings(),
        }
    except RuntimeError as e:
        return {"name": "none", "available": False, "error": str(e)}


def reset_providers():
    """Reset provider cache (useful for testing)."""
    global _groq_instance, _ollama_instance, _gemini_instance, _initialized
    _groq_instance   = None
    _ollama_instance = None
    _gemini_instance = None
    _initialized     = False


def test_providers():
    """Test all providers and print status."""
    print("\n" + "=" * 55)
    print("🔍 NOVARYX — Provider Status Check")
    print("=" * 55)

    _init_providers()

    groq_ok   = _groq_instance   is not None and _groq_instance._available
    ollama_ok = _ollama_instance is not None and _ollama_instance._available
    gemini_ok = _gemini_instance is not None and _gemini_instance._available

    print(f"\n⚡ GROQ  (planning-preferred, cloud)")
    print(f"   Status: {'🟢 ONLINE' if groq_ok else '🔴 NO KEY / OFFLINE'}")
    if groq_ok:
        models = _groq_instance.get_available_models()
        print(f"   Models: {len(models)} available")

    print(f"\n📦 OLLAMA  (generation + repair + embeddings, local)")
    print(f"   Status: {'🟢 ONLINE' if ollama_ok else '🔴 NOT RUNNING'}")
    if ollama_ok:
        print(f"   Models: {_ollama_instance.get_available_models()}")

    print(f"\n☁️  GEMINI  (fallback, cloud)")
    print(f"   Status: {'🟢 Configured' if gemini_ok else '🔴 No API key'}")

    print("\n" + "─" * 55)
    print("Role routing:")
    for role in ["planning", "generation", "repair", "embedding"]:
        try:
            p = get_provider_for_role(role)
            print(f"   {role:<12} → {p.name}  ({p.get_model_for_role(role)})")
        except RuntimeError as e:
            print(f"   {role:<12} → ❌ {e}")

    print("=" * 55 + "\n")


if __name__ == "__main__":
    test_providers()