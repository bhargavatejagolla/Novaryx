"""
NOVARYX - Ollama Setup CLI
Run once to install and tune all required models.

Usage:
    python -m system.inference.ollama_setup
    python -m system.inference.ollama_setup --status
    python -m system.inference.ollama_setup --pull-only
"""

import sys
import json
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("novaryx.setup")

REQUIRED_BASE_MODELS = [
    "qwen2.5-coder:7b",
    "deepseek-coder:6.7b",
    "nomic-embed-text:latest",
]

TUNED_MODEL_NAMES = [
    "novaryx-qwen",
    "novaryx-deepseek",
]


def print_banner():
    print("\n" + "=" * 60)
    print("  NOVARYX -- Ollama Setup & Model Tuning")
    print("=" * 60)


def check_status(provider) -> dict:
    """Check status of all models"""
    available = provider.get_available_models()

    status = {
        "ollama_running": provider.is_available(),
        "base_models": {},
        "tuned_models": {},
    }

    for m in REQUIRED_BASE_MODELS:
        base = m.split(":")[0]
        installed = any(base in a for a in available)
        status["base_models"][m] = installed

    for m in TUNED_MODEL_NAMES:
        installed = any(m in a for a in available)
        status["tuned_models"][m] = installed

    return status


def run_setup(pull_only: bool = False):
    print_banner()

    try:
        from system.inference.ollama_provider import OllamaProvider
    except ImportError as e:
        print(f"❌ Cannot import OllamaProvider: {e}")
        sys.exit(1)

    provider = OllamaProvider()

    # 1. Check Ollama is running
    print("\n[*] Checking Ollama server...")
    if not provider.is_available():
        print("[ERROR] Ollama is NOT running!")
        print("   Start it with: ollama serve")
        print("   Then re-run this script.")
        sys.exit(1)

    print("[OK] Ollama is running")
    available = provider.get_available_models()
    print(f"   Installed models: {available}")

    # 2. Pull missing base models
    print("\n📦 Checking base models...")
    all_pulled = True
    for model in REQUIRED_BASE_MODELS:
        base = model.split(":")[0]
        installed = any(base in a for a in available)
        if installed:
            print(f"   ✅ {model} — already installed")
        else:
            print(f"   ⬇️  Pulling {model} ...")
            success = provider.auto_pull(model)
            if success:
                print(f"   ✅ {model} — pulled successfully")
            else:
                print(f"   ❌ {model} — pull failed (check internet connection)")
                all_pulled = False

    if not all_pulled:
        print("\n⚠️  Some models failed to pull. Continuing with what's available...")

    # 3. Create tuned Modelfiles
    if not pull_only:
        print("\n[*] Creating tuned Modelfiles...")
        results = provider.setup_tuned_models()

        for model_name, success in results.items():
            if success:
                print(f"   [OK] {model_name} -- created successfully")
            else:
                print(f"   [WARN] {model_name} -- using base model fallback")

    # 4. Final status
    print("\n" + "-" * 60)
    print("[STATUS] Final Status:")
    status = check_status(provider)

    for m, installed in status["base_models"].items():
        icon = "[OK]" if installed else "[ERR]"
        print(f"   {icon} Base: {m}")

    for m, installed in status["tuned_models"].items():
        icon = "[OK]" if installed else "[WARN] (will use base fallback)"
        print(f"   {icon} Tuned: {m}")

    print("\n" + "=" * 60)
    print("[DONE] NOVARYX Ollama setup complete!")
    print("   Generation model : novaryx-qwen  (qwen2.5-coder:7b tuned)")
    print("   Repair model     : novaryx-deepseek  (deepseek-coder:6.7b tuned)")
    print("   Embedding model  : nomic-embed-text")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="NOVARYX Ollama Setup")
    parser.add_argument("--status", action="store_true", help="Show model status only")
    parser.add_argument("--pull-only", action="store_true", help="Pull models only, skip Modelfile creation")
    args = parser.parse_args()

    if args.status:
        print_banner()
        try:
            from system.inference.ollama_provider import OllamaProvider
            provider = OllamaProvider()
            status = check_status(provider)
            print(json.dumps(status, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        return

    run_setup(pull_only=args.pull_only)


if __name__ == "__main__":
    main()
