"""
NOVARYX - LLM Repairer (Upgraded)
Uses tuned novaryx-deepseek model for complex bug fixes.
Context-window-safe with diff-validation.
"""

import sys
import time
import logging
import concurrent.futures
from pathlib import Path
from typing import Optional, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .bug_detector import Bug

logger = logging.getLogger("novaryx.llm_repairer")

MAX_CODE_CHARS = 10000  # ~2500 tokens — safe for 8K context window


class LLMRepairer:
    """LLM-powered repair for complex bugs using tuned deepseek-coder"""

    def __init__(self):
        self._inference = None

    def _get_inference(self):
        if self._inference is None:
            try:
                from system.inference.provider_factory import get_provider_for_role
                self._inference = get_provider_for_role("repair")
            except Exception as e:
                logger.warning(f"Repair inference unavailable: {e}")
        return self._inference

    def repair(self, file_path: str, content: str, bugs: List[Bug]) -> Optional[str]:
        """
        Use LLM to repair bugs in a file.
        Context-window-safe: truncates if needed.
        Diff-validates: rejects repairs that are too short (truncation indicator).
        """
        provider = self._get_inference()
        if not provider:
            return None

        try:
            from system.intelligence.prompt_engine import get_prompt_engine
            engine = get_prompt_engine()
            system_prompt, user_prompt = engine.build_repair_prompt(
                file_path=file_path,
                code=content,
                bugs=bugs,
                max_code_chars=MAX_CODE_CHARS
            )
        except ImportError:
            # Fallback if prompt engine not available
            bug_descriptions = "\n".join([
                f"- Line {getattr(b, 'line_number', '?')}: "
                f"[{getattr(b, 'bug_type', b)}] {getattr(b, 'description', str(b))}"
                for b in bugs
            ])
            truncated_code = content[:MAX_CODE_CHARS]
            system_prompt = "You are an expert React/TypeScript debugger. Fix bugs. Return ONLY complete fixed code."
            user_prompt = (
                f"FILE: {file_path}\nBUGS:\n{bug_descriptions}\n"
                f"CODE:\n{truncated_code}\n\nFixed code:"
            )

        try:
            # Hard 120-second timeout per LLM call — prevents pipeline hangs
            def _do_llm():
                return provider.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    role="repair",
                    temperature=0.05,
                    max_tokens=4096,
                )

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as _ex:
                _fut = _ex.submit(_do_llm)
                try:
                    result = _fut.result(timeout=120)
                except concurrent.futures.TimeoutError:
                    logger.warning(f"LLM repair timed out after 120s for {file_path}, skipping")
                    return None

            if not result.success or not result.text:
                return None

            repaired = result.text.strip()

            # Strip markdown fences
            if repaired.startswith("```"):
                lines = repaired.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                repaired = "\n".join(lines).strip()

            # Diff-validation: reject if result is suspiciously short
            min_acceptable = max(50, int(len(content) * 0.7))
            if len(repaired) < min_acceptable:
                logger.warning(
                    f"Repair rejected for {file_path}: "
                    f"result ({len(repaired)} chars) < 70% of original ({len(content)} chars)"
                )
                return None

            logger.info(f"LLM repaired {file_path}: {len(repaired)} chars")
            return repaired

        except Exception as e:
            logger.error(f"LLM repair failed: {e}")
            return None

    def repair_batch(self, files: dict, bug_map: dict) -> dict:
        """
        Repair multiple files. Rate-limit aware (1s delay between calls).
        """
        repaired_files = {}

        for file_path, bugs in bug_map.items():
            content = files.get(file_path, "")
            if not content or not bugs:
                continue

            # Only use LLM for bugs that pattern fixers can't handle
            complex_bugs = [
                b for b in bugs
                if getattr(b, "bug_type", None) and
                   b.bug_type.value not in ["double_brace_jsx", "empty_file"]
            ]

            if complex_bugs:
                repaired = self.repair(file_path, content, complex_bugs)
                if repaired:
                    repaired_files[file_path] = repaired

                # Small delay to avoid hammering local Ollama
                time.sleep(0.5)

        return repaired_files
