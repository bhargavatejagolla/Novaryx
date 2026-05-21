"""
NOVARYX - Ollama Provider (Upgraded)
Primary local inference via Ollama API (http://localhost:11434)

Models (auto-tuned via custom Modelfiles):
  - novaryx-qwen       → Main generation (qwen2.5-coder:7b tuned)
  - novaryx-deepseek   → Repair & debugging (deepseek-coder:6.7b tuned)
  - nomic-embed-text   → Embeddings (274 MB)

Features:
  - Auto-pull missing models
  - Custom Modelfiles with optimized parameters
  - Streaming generation (token by token)
  - Role-based model routing
"""

import requests
import json
import time
import logging
import subprocess
import os
from typing import Optional, Dict, Any, List, Iterator
from .base_provider import BaseProvider, GenerationResult

logger = logging.getLogger("novaryx.ollama")

# Custom Modelfile content for qwen2.5-coder (main generation)
QWEN_MODELFILE = """FROM qwen2.5-coder:7b

SYSTEM \"\"\"You are NOVARYX, an elite code generation AI. You generate production-grade React/TypeScript/Next.js code.

Rules:
- Output ONLY the requested code — no explanations, no markdown unless asked
- Use TypeScript with proper types always
- Use Tailwind CSS for styling
- Generate complete, working files
- Follow React best practices (hooks, proper state management)
- Include all necessary imports
\"\"\"

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 8192
PARAMETER num_predict 4096
PARAMETER stop \"<|im_end|>\"
PARAMETER stop \"<|endoftext|>\"
"""

# Custom Modelfile content for deepseek-coder (repair)
DEEPSEEK_MODELFILE = """FROM deepseek-coder:6.7b

SYSTEM \"\"\"You are NOVARYX Repair, an elite code debugging AI. You fix bugs in React/TypeScript code.

Rules:
- Fix ONLY the reported bugs — do not change working code
- Output the COMPLETE fixed file content
- Do not add explanations or markdown wrappers
- Preserve all existing functionality
- Ensure all imports are correct
\"\"\"

PARAMETER temperature 0.05
PARAMETER top_p 0.9
PARAMETER top_k 20
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 8192
PARAMETER num_predict 4096
PARAMETER stop \"<|EOT|>\"
PARAMETER stop \"<|endoftext|>\"
"""


class OllamaProvider(BaseProvider):
    """Ollama local inference provider — upgraded with streaming & auto-tuning"""

    # Model role mapping — prefers custom-tuned models, falls back to base
    MODEL_ROLES = {
        "generation": "novaryx-qwen",
        "repair":     "novaryx-deepseek",
        "planning":   "novaryx-qwen",
        "embedding":  "nomic-embed-text:latest",
        "default":    "novaryx-qwen",
    }

    # Base model fallbacks (if custom models not yet created)
    BASE_FALLBACKS = {
        "novaryx-qwen":      "qwen2.5-coder:7b",
        "novaryx-deepseek":  "deepseek-coder:6.7b",
    }

    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(name="ollama", priority=200)  # High priority local provider
        self.base_url = base_url.rstrip("/")
        self.api_generate  = f"{self.base_url}/api/generate"
        self.api_embeddings = f"{self.base_url}/api/embeddings"
        self.api_tags       = f"{self.base_url}/api/tags"
        self.api_create     = f"{self.base_url}/api/create"
        self._cached_models: Optional[List[str]] = None

    # ------------------------------------------------------------------
    # Availability & model discovery
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(self.api_tags, timeout=5)
            if response.status_code == 200:
                self._available = True
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                self._cached_models = model_names
                logger.info(f"Ollama available — models: {model_names}")
                return True
        except requests.exceptions.ConnectionError:
            logger.debug("Ollama not running on port 11434")
        except Exception as e:
            logger.warning(f"Ollama check failed: {e}")

        self._available = False
        return False

    def get_available_models(self) -> List[str]:
        """Get list of installed Ollama models"""
        if self._cached_models is not None:
            return self._cached_models
        try:
            response = requests.get(self.api_tags, timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                self._cached_models = [m["name"] for m in models]
                return self._cached_models
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
        return []

    def get_model_for_role(self, role: str) -> str:
        """Get the best model for a given task role, with fallback chain"""
        available = self.get_available_models()
        preferred = self.MODEL_ROLES.get(role, self.MODEL_ROLES["default"])

        # Check if custom tuned model is available
        for model in available:
            if preferred.split(":")[0] in model:
                return model

        # Try base fallback
        base = self.BASE_FALLBACKS.get(preferred)
        if base:
            for model in available:
                if base.split(":")[0] in model:
                    logger.info(f"Using base model '{model}' instead of tuned '{preferred}'")
                    return model

        # Last resort: first available model
        if available:
            logger.warning(f"No model for role '{role}', using {available[0]}")
            return available[0]

        return preferred

    # ------------------------------------------------------------------
    # Auto-pull missing models
    # ------------------------------------------------------------------

    def auto_pull(self, model: str) -> bool:
        """Pull a model if not already installed"""
        available = self.get_available_models()
        base_name = model.split(":")[0]

        for installed in available:
            if base_name in installed:
                logger.info(f"Model '{model}' already installed as '{installed}'")
                return True

        logger.info(f"Pulling model: {model} ...")
        try:
            result = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True, text=True, timeout=600
            )
            if result.returncode == 0:
                self._cached_models = None  # Invalidate cache
                logger.info(f"Successfully pulled: {model}")
                return True
            else:
                logger.error(f"Failed to pull {model}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Auto-pull failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Custom Modelfile creation (auto-tuning)
    # ------------------------------------------------------------------

    def create_tuned_modelfile(self, model_name: str, modelfile_content: str) -> bool:
        """Create a custom tuned model via ollama CLI"""
        import tempfile
        import os
        try:
            # Write Modelfile to a temp file
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='', prefix='Modelfile_', delete=False, encoding='utf-8'
            ) as f:
                f.write(modelfile_content)
                tmp_path = f.name

            # Run: ollama create <model_name> -f <Modelfile>
            result = subprocess.run(
                ["ollama", "create", model_name, "-f", tmp_path],
                capture_output=True, text=True, timeout=120
            )

            os.unlink(tmp_path)  # Clean up temp file

            if result.returncode == 0:
                logger.info(f"Created tuned model: {model_name}")
                self._cached_models = None
                return True
            else:
                logger.warning(f"Modelfile creation failed for {model_name}: {result.stderr[:200]}")
                return False
        except Exception as e:
            logger.warning(f"Could not create modelfile for {model_name}: {e}")
            return False

    def setup_tuned_models(self) -> Dict[str, bool]:
        """Create all tuned Modelfiles. Returns {model_name: success}"""
        results = {}

        logger.info("Setting up tuned Modelfiles...")

        results["novaryx-qwen"] = self.create_tuned_modelfile(
            "novaryx-qwen", QWEN_MODELFILE
        )
        results["novaryx-deepseek"] = self.create_tuned_modelfile(
            "novaryx-deepseek", DEEPSEEK_MODELFILE
        )

        # Invalidate cached models after creation
        self._cached_models = None

        return results

    # ------------------------------------------------------------------
    # Generation (non-streaming)
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
        role: str = "default",
        response_format: str = None,
        **kwargs
    ) -> GenerationResult:
        """Generate text using Ollama"""

        start_time = time.time()
        model = model or self.get_model_for_role(role)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": min(max_tokens, 4096),
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 40),
                "repeat_penalty": kwargs.get("repeat_penalty", 1.15),
                "num_ctx": kwargs.get("num_ctx", 8192),
            }
        }

        if response_format == "json":
            payload["format"] = "json"

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(
                self.api_generate,
                json=payload,
                timeout=120  # 2 minutes (Bulletproof API timeout)
            )

            if response.status_code != 200:
                return GenerationResult(
                    text="", model=model, provider="ollama",
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text[:200]}"
                )

            data = response.json()
            result_text = data.get("response", "")
            elapsed = (time.time() - start_time) * 1000

            logger.info(
                f"Ollama OK: model={model}, "
                f"tokens≈{len(result_text)//4}, time={elapsed:.0f}ms"
            )

            return GenerationResult(
                text=result_text,
                model=model,
                provider="ollama",
                tokens_used=len(result_text) // 4,
                generation_time_ms=elapsed,
                success=True
            )

        except requests.exceptions.Timeout:
            logger.error(f"Ollama timed out after 120s (model={model})")
            return GenerationResult(
                text="", model=model, provider="ollama",
                success=False, error="Request timed out after 120s"
            )
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return GenerationResult(
                text="", model=model, provider="ollama",
                success=False, error=str(e)
            )

    # ------------------------------------------------------------------
    # Streaming generation
    # ------------------------------------------------------------------

    def generate_stream(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        role: str = "default",
        response_format: str = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Stream generation token by token.
        Yields token strings. Raises StopIteration when done.
        """
        model = model or self.get_model_for_role(role)

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": min(max_tokens, 4096),
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 40),
                "repeat_penalty": kwargs.get("repeat_penalty", 1.15),
                "num_ctx": kwargs.get("num_ctx", 8192),
            }
        }

        if response_format == "json":
            payload["format"] = "json"

        if system_prompt:
            payload["system"] = system_prompt

        try:
            with requests.post(
                self.api_generate,
                json=payload,
                stream=True,
                timeout=120
            ) as response:
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield token
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.Timeout:
            logger.error("Ollama streaming timed out")
        except Exception as e:
            logger.error(f"Ollama stream failed: {e}")

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using nomic-embed-text"""
        embedding_model = self.get_model_for_role("embedding")

        payload = {"model": embedding_model, "prompt": text}

        try:
            response = requests.post(
                self.api_embeddings,
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
            else:
                logger.error(f"Embedding failed: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    def supports_embeddings(self) -> bool:
        return True

    def supports_streaming(self) -> bool:
        return True


# ---------------------------------------------------------------------------
# Backward-compat ModelManager shim
# ---------------------------------------------------------------------------

class ModelManager:
    """
    Simplified model manager that delegates to OllamaProvider.
    Preserves backward compatibility with older NOVARYX code.
    """

    def __init__(self):
        self.ollama = OllamaProvider()

    def is_ready(self) -> bool:
        return self.ollama.is_available()

    def generate(
        self,
        prompt: str,
        role: str = "generation",
        system_prompt: str = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        result = self.ollama.generate(
            prompt=prompt,
            role=role,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result.text if result.success else f"[ERROR: {result.error}]"

    def swap_model(self, role: str):
        logger.info(f"Switching to model for role: {role}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "available": self.is_ready(),
            "models": self.ollama.get_available_models(),
            "provider": "ollama"
        }