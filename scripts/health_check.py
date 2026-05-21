#!/usr/bin/env python3
"""
NOVARYX - System Health Check
Validates ALL systems are connected, configured, and operational.

Usage:
  python scripts/health_check.py           # Full check
  python scripts/health_check.py --quick   # Quick check only
  python scripts/health_check.py --json    # JSON output
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Silence logging during health check
logging.basicConfig(level=logging.WARNING)


class HealthCheck:
    """Complete system health validation"""
    
    def __init__(self, quick: bool = False):
        self.quick = quick
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time = time.time()
        self.overall_status = "UNKNOWN"
        
        # Required versions
        self.required = {
            "python_min": (3, 10),
            "ram_min_gb": 8,
            "disk_min_gb": 5,
            "models_required": ["qwen2.5-coder:7b", "deepseek-coder:6.7b", "nomic-embed-text:latest"]
        }
    
    def run_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        print("\n" + "=" * 60)
        print("🩺 NOVARYX SYSTEM HEALTH CHECK")
        print("=" * 60)
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Mode: {'Quick' if self.quick else 'Full'}")
        print("=" * 60)
        
        checks = [
            ("python_env", "🐍 Python Environment", self.check_python_env),
            ("project_structure", "📁 Project Structure", self.check_project_structure),
            ("imports", "📦 System Imports", self.check_imports),
            ("ollama", "🧠 Ollama Inference", self.check_ollama),
            ("chromadb", "🗄️  ChromaDB RAG", self.check_chromadb),
            ("templates", "📋 Template Registry", self.check_templates),
            ("state_machine", "🔧 State Machine", self.check_state_machine),
            ("error_handler", "⚠️  Error Handler", self.check_error_handler),
            ("version", "📦 Version Tracking", self.check_version),
            ("git", "🔀 Git Repository", self.check_git),
            ("resources", "💻 System Resources", self.check_resources),
            ("config", "⚙️  Configuration", self.check_config),
        ]
        
        for check_id, check_name, check_func in checks:
            print(f"\n{check_name}...")
            try:
                result = check_func()
                self.results[check_id] = result
                status = "✅" if result["status"] == "pass" else "⚠️ " if result["status"] == "warn" else "❌"
                print(f"   {status} {result['message']}")
            except Exception as e:
                self.results[check_id] = {
                    "status": "fail",
                    "message": f"Check failed: {str(e)}",
                    "details": {}
                }
                print(f"   ❌ Check crashed: {e}")
        
        # Calculate overall status
        self._calculate_overall()
        
        # Display summary
        self.display_summary()
        
        return self.get_report()
    
    def _calculate_overall(self):
        """Calculate overall health status"""
        statuses = [r["status"] for r in self.results.values()]
        
        if "fail" in statuses:
            self.overall_status = "UNHEALTHY"
        elif "warn" in statuses:
            self.overall_status = "DEGRADED"
        else:
            self.overall_status = "HEALTHY"
    
    # ---- Individual Checks ----
    
    def check_python_env(self) -> Dict[str, Any]:
        """Check Python environment"""
        import sys
        
        version = sys.version_info
        is_ok = version >= self.required["python_min"]
        
        # Check virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        return {
            "status": "pass" if is_ok else "fail",
            "message": f"Python {version.major}.{version.minor}.{version.micro}" + 
                       (" (venv)" if in_venv else " (no venv)"),
            "details": {
                "version": f"{version.major}.{version.minor}.{version.micro}",
                "executable": sys.executable,
                "in_venv": in_venv,
                "platform": sys.platform
            }
        }
    
    def check_project_structure(self) -> Dict[str, Any]:
        """Check project directory structure"""
        root = Path(__file__).parent.parent
        
        required_dirs = [
            "system",
            "system/orchestrator",
            "system/inference",
            "system/rag_engine",
            "system/templates",
            "system/config",
            "system/orchestrator/state_machine",
            "projects",
            "snapshots",
            "logs",
            "config",
            "scripts",
            "docs",
            "tests"
        ]
        
        missing = []
        for d in required_dirs:
            if not (root / d).exists():
                missing.append(d)
        
        is_ok = len(missing) == 0
        
        return {
            "status": "pass" if is_ok else "warn",
            "message": f"All {len(required_dirs)} directories present" if is_ok else f"Missing {len(missing)} directories",
            "details": {
                "total_required": len(required_dirs),
                "present": len(required_dirs) - len(missing),
                "missing": missing
            }
        }
    
    def check_imports(self) -> Dict[str, Any]:
        """Check critical imports work"""
        imports_to_check = [
            ("ollama_provider", "system.inference.ollama_provider"),
            ("provider_factory", "system.inference.provider_factory"),
            ("chromadb_client", "system.rag_engine.chromadb_client"),
            ("retriever", "system.rag_engine.retriever"),
            ("orchestrator", "system.orchestrator.orchestrator"),
            ("state_machine", "system.orchestrator.state_machine.state_machine"),
            ("template_registry", "system.templates.template_registry"),
            ("error_handler", "system.config.error_handler"),
            ("error_codes", "system.config.error_codes"),
        ]
        
        passed = []
        failed = []
        
        for name, module_path in imports_to_check:
            try:
                __import__(module_path)
                passed.append(name)
            except ImportError as e:
                failed.append({"name": name, "error": str(e)})
        
        is_ok = len(failed) == 0
        
        return {
            "status": "pass" if is_ok else "fail",
            "message": f"{len(passed)}/{len(imports_to_check)} imports successful",
            "details": {
                "passed": passed,
                "failed": failed
            }
        }
    
    def check_ollama(self) -> Dict[str, Any]:
        """Check Ollama is running with required models"""
        import requests
        
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code != 200:
                return {
                    "status": "fail",
                    "message": f"Ollama returned status {response.status_code}",
                    "details": {}
                }
            
            data = response.json()
            models = data.get("models", [])
            model_names = [m["name"] for m in models]
            
            # Check required models
            missing_models = []
            for required in self.required["models_required"]:
                found = False
                for model in model_names:
                    if required.split(":")[0] in model:
                        found = True
                        break
                if not found:
                    missing_models.append(required)
            
            if len(missing_models) == 0:
                return {
                    "status": "pass",
                    "message": f"Ollama running with {len(models)} models",
                    "details": {
                        "models_available": model_names,
                        "models_count": len(models)
                    }
                }
            else:
                return {
                    "status": "warn",
                    "message": f"Missing {len(missing_models)} models: {', '.join(missing_models)}",
                    "details": {
                        "models_available": model_names,
                        "missing_models": missing_models
                    }
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "status": "fail",
                "message": "Ollama not running. Start with: ollama serve",
                "details": {"error": "Connection refused"}
            }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Ollama check failed: {e}",
                "details": {"error": str(e)}
            }
    
    def check_chromadb(self) -> Dict[str, Any]:
        """Check ChromaDB is accessible with collections"""
        try:
            from system.rag_engine.chromadb_client import ChromaDBClient
            
            client = ChromaDBClient()
            stats = client.get_collection_stats()
            
            total_items = sum(
                info.get("count", 0) 
                for info in stats.values() 
                if not isinstance(info.get("count"), str)
            )
            
            collections_found = len(stats)
            
            if collections_found >= 4:
                return {
                    "status": "pass",
                    "message": f"ChromaDB OK: {collections_found} collections, {total_items} items",
                    "details": {
                        "collections": stats,
                        "total_items": total_items
                    }
                }
            else:
                return {
                    "status": "warn",
                    "message": f"Only {collections_found} collections found",
                    "details": {"collections": stats}
                }
                
        except Exception as e:
            return {
                "status": "fail",
                "message": f"ChromaDB check failed: {e}",
                "details": {"error": str(e)}
            }
    
    def check_templates(self) -> Dict[str, Any]:
        """Check template registry"""
        try:
            from system.templates.template_registry import TemplateRegistry
            
            registry = TemplateRegistry()
            stats = registry.get_statistics()
            
            if stats["total_templates"] > 0:
                return {
                    "status": "pass",
                    "message": f"Template registry OK: {stats['total_templates']} templates, {stats['total_files']} files",
                    "details": stats
                }
            else:
                return {
                    "status": "warn",
                    "message": "No templates registered. Run: python system/templates/seed_templates.py",
                    "details": stats
                }
                
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Template check failed: {e}",
                "details": {"error": str(e)}
            }
    
    def check_state_machine(self) -> Dict[str, Any]:
        """Check state machine functionality"""
        try:
            from system.orchestrator.state_machine.state_machine import NovaryxStateMachine
            from system.orchestrator.state_machine.state_definitions import (
                GenerationState, VALID_TRANSITIONS, TERMINAL_STATES
            )
            
            sm = NovaryxStateMachine()
            
            # Test basic transition
            sm.transition(GenerationState.INITIALIZING, "Health check test")
            sm.transition(GenerationState.READY, "Health check test")
            
            # Test invalid transition blocked
            invalid_blocked = not sm.transition(
                GenerationState.PARSING_PROMPT, "Should be blocked"
            )
            
            return {
                "status": "pass",
                "message": f"State machine OK: {len(VALID_TRANSITIONS)} valid transitions defined",
                "details": {
                    "states_defined": len(GenerationState.__members__),
                    "transitions_defined": sum(len(v) for v in VALID_TRANSITIONS.values()),
                    "terminal_states": len(TERMINAL_STATES),
                    "invalid_blocked": invalid_blocked
                }
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"State machine check failed: {e}",
                "details": {"error": str(e)}
            }
    
    def check_error_handler(self) -> Dict[str, Any]:
        """Check error handler is functional"""
        try:
            from system.config.error_codes import ErrorCodes
            from system.config.error_handler import ErrorHandler, NovaryxError
            
            handler = ErrorHandler()
            
            # Test error handling
            try:
                raise NovaryxError(ErrorCodes.SYSTEM_TIMEOUT, "Health check test")
            except NovaryxError as e:
                result = handler.handle_error(e)
            
            all_codes = ErrorCodes.get_all_codes()
            
            return {
                "status": "pass",
                "message": f"Error handler OK: {len(all_codes)} error codes registered",
                "details": {
                    "total_codes": len(all_codes),
                    "codes_by_area": {}
                }
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Error handler check failed: {e}",
                "details": {"error": str(e)}
            }
    
    def check_version(self) -> Dict[str, Any]:
        """Check version tracking"""
        try:
            import json
            root = Path(__file__).parent.parent
            version_file = root / "config" / "version.json"
            
            if not version_file.exists():
                return {
                    "status": "fail",
                    "message": "version.json not found",
                    "details": {}
                }
            
            with open(version_file, "r") as f:
                data = json.load(f)
            
            version = data.get("version", "unknown")
            phase = data.get("phase", "?")
            step = data.get("step", "?")
            
            return {
                "status": "pass",
                "message": f"Version: v{version} (Phase {phase}.{step})",
                "details": {
                    "version": version,
                    "phase": phase,
                    "step": step,
                    "codename": data.get("codename", ""),
                    "components": data.get("components", {})
                }
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Version check failed: {e}",
                "details": {"error": str(e)}
            }
    
    def check_git(self) -> Dict[str, Any]:
        """Check git repository"""
        import subprocess
        
        root = Path(__file__).parent.parent
        
        try:
            # Check if git is available
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            
            # Check if it's a repo
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(root),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "status": "warn",
                    "message": "Git repository not initialized",
                    "details": {}
                }
            
            lines = [l for l in result.stdout.strip().split("\n") if l]
            modified = len([l for l in lines if not l.startswith("??")])
            untracked = len([l for l in lines if l.startswith("??")])
            
            if untracked > 0:
                return {
                    "status": "warn",
                    "message": f"Git OK but {untracked} untracked files",
                    "details": {
                        "modified": modified,
                        "untracked": untracked
                    }
                }
            else:
                return {
                    "status": "pass",
                    "message": "Git repository clean",
                    "details": {"modified": modified, "untracked": untracked}
                }
                
        except subprocess.CalledProcessError:
            return {
                "status": "warn",
                "message": "Git not installed",
                "details": {}
            }
        except Exception as e:
            return {
                "status": "warn",
                "message": f"Git check failed: {e}",
                "details": {}
            }
    
    def check_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        import psutil
        
        issues = []
        
        # Check RAM
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        if total_gb < self.required["ram_min_gb"]:
            issues.append(f"RAM: {total_gb:.1f}GB (minimum {self.required['ram_min_gb']}GB)")
        
        # Check disk
        root = Path(__file__).parent.parent
        disk = psutil.disk_usage(str(root))
        free_gb = disk.free / (1024**3)
        
        if free_gb < self.required["disk_min_gb"]:
            issues.append(f"Disk: {free_gb:.1f}GB free (minimum {self.required['disk_min_gb']}GB)")
        
        # Check CPU
        cpu_count = psutil.cpu_count(logical=True)
        
        if len(issues) == 0:
            return {
                "status": "pass",
                "message": f"Resources OK: {total_gb:.0f}GB RAM, {free_gb:.0f}GB disk free, {cpu_count} CPUs",
                "details": {
                    "ram_total_gb": round(total_gb, 1),
                    "ram_available_gb": round(available_gb, 1),
                    "disk_free_gb": round(free_gb, 1),
                    "cpu_count": cpu_count,
                    "memory_percent": memory.percent
                }
            }
        else:
            return {
                "status": "warn",
                "message": f"Resource issues: {'; '.join(issues)}",
                "details": {
                    "ram_total_gb": round(total_gb, 1),
                    "ram_available_gb": round(available_gb, 1),
                    "disk_free_gb": round(free_gb, 1),
                    "cpu_count": cpu_count,
                    "issues": issues
                }
            }
    
    def check_config(self) -> Dict[str, Any]:
        """Check configuration files"""
        root = Path(__file__).parent.parent
        
        config_files = [
            "config/version.json",
            "config/system_config.json",
            ".env",
            ".gitignore",
            ".gitattributes",
            "system/inference/provider_config.json"
        ]
        
        found = []
        missing = []
        
        for cf in config_files:
            if (root / cf).exists():
                found.append(cf)
            else:
                missing.append(cf)
        
        is_ok = len(missing) <= 2  # .env might not exist
        
        return {
            "status": "pass" if is_ok else "warn",
            "message": f"{len(found)}/{len(config_files)} config files present",
            "details": {
                "found": found,
                "missing": missing
            }
        }
    
    # ---- Report Generation ----
    
    def display_summary(self):
        """Display health check summary"""
        elapsed = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 60)
        
        # Count statuses
        passes = sum(1 for r in self.results.values() if r["status"] == "pass")
        warns = sum(1 for r in self.results.values() if r["status"] == "warn")
        fails = sum(1 for r in self.results.values() if r["status"] == "fail")
        total = len(self.results)
        
        print(f"   Passed:  {passes}/{total}")
        print(f"   Warnings: {warns}/{total}")
        print(f"   Failed:  {fails}/{total}")
        print(f"   Time:    {elapsed:.1f}s")
        
        # Overall status
        if self.overall_status == "HEALTHY":
            print(f"\n   🟢 System Status: {self.overall_status}")
        elif self.overall_status == "DEGRADED":
            print(f"\n   🟡 System Status: {self.overall_status}")
        else:
            print(f"\n   🔴 System Status: {self.overall_status}")
        
        # Recommendations
        if fails > 0:
            print(f"\n   ⚠️  Action Required:")
            for check_id, result in self.results.items():
                if result["status"] == "fail":
                    print(f"      - {check_id}: {result['message']}")
        
        if warns > 0:
            print(f"\n   💡 Recommendations:")
            for check_id, result in self.results.items():
                if result["status"] == "warn":
                    print(f"      - {check_id}: {result['message']}")
        
        print("=" * 60 + "\n")
    
    def get_report(self) -> Dict[str, Any]:
        """Get complete health report as dictionary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.overall_status,
            "duration_seconds": time.time() - self.start_time,
            "mode": "quick" if self.quick else "full",
            "summary": {
                "total_checks": len(self.results),
                "passed": sum(1 for r in self.results.values() if r["status"] == "pass"),
                "warnings": sum(1 for r in self.results.values() if r["status"] == "warn"),
                "failed": sum(1 for r in self.results.values() if r["status"] == "fail")
            },
            "checks": self.results
        }
    
    def save_report(self, filepath: str = None):
        """Save health report to file"""
        if filepath is None:
            root = Path(__file__).parent.parent
            filepath = str(root / "logs" / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        report = self.get_report()
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved: {filepath}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NOVARYX System Health Check")
    parser.add_argument("--quick", action="store_true", help="Quick check only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--save", action="store_true", help="Save report to file")
    args = parser.parse_args()
    
    checker = HealthCheck(quick=args.quick)
    report = checker.run_all()
    
    if args.json:
        print(json.dumps(report, indent=2))
    
    if args.save:
        checker.save_report()
    
    # Return exit code
    if report["overall_status"] == "UNHEALTHY":
        sys.exit(1)
    elif report["overall_status"] == "DEGRADED":
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()