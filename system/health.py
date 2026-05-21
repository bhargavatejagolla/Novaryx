"""
NOVARYX - Health Check System
Single command that checks all subsystems and gives actionable fixes.

Usage:
    python system/health.py
    python system/health.py --json
    python system/health.py --fix
"""
import sys
import json
import logging
import subprocess
import os
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))
logger = logging.getLogger("novaryx.health")


def check_ollama() -> Dict[str, Any]:
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            required = ["qwen2.5-coder", "deepseek-coder", "nomic-embed-text"]
            missing = [r for r in required if not any(r in m for m in models)]
            return {
                "status": "ok" if not missing else "warning",
                "running": True,
                "models": models,
                "missing_models": missing,
                "fix": f"ollama pull {missing[0]}" if missing else None
            }
        return {"status": "error", "running": False, "fix": "ollama serve"}
    except Exception:
        return {
            "status": "error", "running": False,
            "models": [], "missing_models": [],
            "fix": "Start Ollama: ollama serve"
        }


def check_providers() -> Dict[str, Any]:
    try:
        from system.inference.provider_factory import list_available_providers, get_provider
        providers = list_available_providers()
        available = [p for p in providers if p["available"]]
        try:
            active = get_provider()
            active_name = active.name
        except Exception:
            active_name = "none"

        return {
            "status": "ok" if available else "error",
            "active": active_name,
            "providers": providers,
            "fix": "Start Ollama or set GROQ_API_KEY in .env" if not available else None
        }
    except Exception as e:
        return {"status": "error", "active": "none", "error": str(e),
                "fix": "Check system/inference/ modules"}


def check_chromadb() -> Dict[str, Any]:
    try:
        import chromadb
        persist_dir = os.environ.get(
            "CHROMA_PERSIST_DIR",
            str(Path(__file__).parent / "rag_engine" / "chromadb")
        )
        client = chromadb.PersistentClient(path=persist_dir)
        collections = client.list_collections()
        col_names = [c.name for c in collections]

        # Check if seeded
        seeded = False
        if "novaryx_components" in col_names:
            col = client.get_collection("novaryx_components")
            count = col.count()
            seeded = count > 0
            return {
                "status": "ok" if seeded else "warning",
                "collections": col_names,
                "component_count": count,
                "seeded": seeded,
                "fix": "python -m system.rag_engine.seed_knowledge" if not seeded else None
            }
        return {
            "status": "warning", "collections": col_names,
            "seeded": False, "fix": "python -m system.rag_engine.seed_knowledge"
        }
    except ImportError:
        return {"status": "warning", "fix": "pip install chromadb"}
    except Exception as e:
        return {"status": "warning", "error": str(e),
                "fix": "python -m system.rag_engine.seed_knowledge"}


def check_python_deps() -> Dict[str, Any]:
    required = ["requests", "fastapi", "uvicorn", "dotenv"]
    optional = ["chromadb", "groq"]
    missing_req = []
    missing_opt = []

    for pkg in required:
        try:
            __import__(pkg if pkg != "dotenv" else "dotenv")
        except ImportError:
            missing_req.append(pkg)

    for pkg in optional:
        try:
            __import__(pkg)
        except ImportError:
            missing_opt.append(pkg)

    status = "error" if missing_req else ("warning" if missing_opt else "ok")
    fix = None
    if missing_req:
        fix = f"pip install {' '.join(missing_req)}"
    elif missing_opt:
        fix = f"pip install {' '.join(missing_opt)} (optional)"

    return {
        "status": status,
        "missing_required": missing_req,
        "missing_optional": missing_opt,
        "fix": fix
    }


def check_env() -> Dict[str, Any]:
    env_file = Path(__file__).parent.parent / ".env"
    issues = []

    if not env_file.exists():
        return {"status": "error", "fix": "Create .env file from .env.example"}

    # Load env
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        pass

    groq_key = os.environ.get("GROQ_API_KEY", "")
    if not groq_key:
        issues.append("GROQ_API_KEY not set (Ollama will be used instead)")

    return {
        "status": "ok" if not issues else "info",
        "env_file": str(env_file),
        "groq_configured": bool(groq_key),
        "issues": issues,
        "fix": "Set GROQ_API_KEY in .env for faster cloud inference" if not groq_key else None
    }


def check_tuned_models() -> Dict[str, Any]:
    """Check if our custom Modelfiles are created"""
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code != 200:
            return {"status": "warning", "tuned": False, "fix": "Start Ollama first"}
        models = [m["name"] for m in resp.json().get("models", [])]
        has_qwen = any("novaryx-qwen" in m for m in models)
        has_deepseek = any("novaryx-deepseek" in m for m in models)
        ok = has_qwen and has_deepseek
        return {
            "status": "ok" if ok else "warning",
            "novaryx-qwen": has_qwen,
            "novaryx-deepseek": has_deepseek,
            "fix": "python -m system.inference.ollama_setup" if not ok else None
        }
    except Exception:
        return {"status": "warning", "fix": "Start Ollama: ollama serve"}


def run_health_check(output_json: bool = False, auto_fix: bool = False) -> Dict[str, Any]:
    # Load .env
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
    except ImportError:
        pass

    results = {
        "env":          check_env(),
        "python_deps":  check_python_deps(),
        "ollama":       check_ollama(),
        "tuned_models": check_tuned_models(),
        "providers":    check_providers(),
        "chromadb":     check_chromadb(),
    }

    # Overall status
    statuses = [v.get("status", "ok") for v in results.values()]
    if "error" in statuses:
        results["overall"] = "error"
    elif "warning" in statuses:
        results["overall"] = "warning"
    else:
        results["overall"] = "ok"

    if output_json:
        print(json.dumps(results, indent=2, default=str))
        return results

    # Pretty print
    STATUS_ICONS = {"ok": "✅", "warning": "⚠️ ", "error": "❌", "info": "ℹ️ "}

    print("\n" + "=" * 60)
    print("  NOVARYX — System Health Check")
    print("=" * 60)

    labels = {
        "env": "Environment (.env)",
        "python_deps": "Python Dependencies",
        "ollama": "Ollama Server",
        "tuned_models": "Tuned Modelfiles",
        "providers": "LLM Providers",
        "chromadb": "ChromaDB / RAG",
    }

    for key, label in labels.items():
        check = results[key]
        icon = STATUS_ICONS.get(check.get("status", "ok"), "❓")
        print(f"\n  {icon} {label}")

        if key == "ollama" and check.get("running"):
            print(f"     Models: {check.get('models', [])}")
            if check.get("missing_models"):
                print(f"     Missing: {check['missing_models']}")

        if key == "tuned_models":
            print(f"     novaryx-qwen:     {'✓' if check.get('novaryx-qwen') else '✗'}")
            print(f"     novaryx-deepseek: {'✓' if check.get('novaryx-deepseek') else '✗'}")

        if key == "providers":
            print(f"     Active: {check.get('active', 'none')}")

        if key == "chromadb":
            count = check.get("component_count", 0)
            print(f"     Components seeded: {count}")

        fix = check.get("fix")
        if fix:
            print(f"     👉 Fix: {fix}")

    overall_icon = STATUS_ICONS.get(results["overall"], "❓")
    print(f"\n  {'─' * 56}")
    print(f"  {overall_icon} Overall: {results['overall'].upper()}")

    if results["overall"] == "ok":
        print("  🚀 NOVARYX is ready! Run: python novaryx_e2e.py --test")
    elif results["overall"] == "warning":
        print("  ⚠️  Some optional components missing. Generation will still work.")
    else:
        print("  ❌ Fix the errors above before generating.")

    print("=" * 60 + "\n")

    # Auto-fix suggestions
    if auto_fix:
        fixes = [v.get("fix") for v in results.values() if v.get("fix") and v.get("status") == "error"]
        if fixes:
            print("Auto-fix commands:")
            for f in fixes:
                print(f"  → {f}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NOVARYX Health Check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fix", action="store_true", help="Show fix commands")
    args = parser.parse_args()
    result = run_health_check(output_json=args.json, auto_fix=args.fix)
    sys.exit(0 if result["overall"] != "error" else 1)
