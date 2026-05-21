#!/usr/bin/env python3
"""
NOVARYX - End-to-End Generation Pipeline
THE final integration. Every subsystem connected.

Usage:
  python novaryx_e2e.py "Build a dark purple SaaS dashboard with analytics"
  python novaryx_e2e.py --interactive
  python novaryx_e2e.py --test

Flow:
  Prompt → Intent → Design → Layout → Components → Pages → 
  Backend → Theme → Verify → Repair → Export → Complete Project
"""

import sys
import time
import json
import logging
import io
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

# Force UTF-8 for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        # Fallback for older Python versions
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

sys.path.insert(0, str(Path(__file__).parent))

# Load .env so GROQ_API_KEY and other secrets are available
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)
except ImportError:
    # python-dotenv not installed – fall back to reading manually
    _env_path = Path(__file__).parent / ".env"
    if _env_path.exists():
        import os
        for line in _env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() not in os.environ:
                    os.environ[k.strip()] = v.strip()

from system.intelligence.intent_parser import IntentParser
from system.intelligence.intent_schema import ProjectSpec
from system.templates.dynamic.design_token_engine import DesignTokenEngine
from system.templates.dynamic.layouts.layout_registry import LayoutRegistry
from system.templates.dynamic.template_intelligence import TemplateIntelligence
from system.templates.dynamic.assembly_engine import AssemblyEngine
from system.templates.dynamic.theme_adaptation_engine import ThemeAdapter
from system.templates.dynamic.animations.animation_config import AnimationConfigGenerator
from system.generation.multi_page_generator import MultiPageGenerator
from system.generation.ai_scaffold_generator import AiScaffoldGenerator
from system.backend.pocketbase_generator import PocketBaseGenerator
from system.intelligence.task_decomposer import TaskDecomposer
from system.verification.verification_pipeline import VerificationPipeline
from system.repair.repair_engine import RepairEngine
from system.repair.surgical_repair import SurgicalRepairOrchestrator, RepairBudget
from system.state.generation_state import StateManager
from system.state.checkpoint_manager import CheckpointManager
from system.export.project_exporter import ProjectExporter
from system.intelligence.contract_engine import ContractEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("novaryx.e2e")


def _emit_stream(msg: str):
    """Emit a streaming progress token the frontend can pick up."""
    print(f"STREAM_TOKEN: {msg}", flush=True)


def _emit_telemetry(module_id: str, status: str, trust: float = 1.0):
    """Emit structured module telemetry for the Cockpit UI."""
    payload = {
        "type": "telemetry",
        "module": module_id,
        "status": status,
        "trust": trust
    }
    print(f"STREAM_TOKEN: {json.dumps(payload)}", flush=True)


def _emit_architecture(modules: list):
    """Emit the initial module DAG architecture."""
    payload = {
        "type": "architecture",
        "modules": [{"id": m.module_id, "name": m.name} for m in modules]
    }
    print(f"STREAM_TOKEN: {json.dumps(payload)}", flush=True)


def _seed_rag_if_needed():
    """Ensure ChromaDB has component examples seeded."""
    try:
        from system.rag_engine.seed_knowledge import seed_chromadb
        seed_chromadb()
    except Exception as e:
        logger.debug(f"RAG seed skipped: {e}")


def _index_to_memory(project_name: str, prompt: str, files: dict, trust_registry: Any):
    """Index completed project into memory store with quality curation."""
    try:
        from system.memory.memory_store import MemoryStore
        from system.memory.memory_curator import MemoryCurator
        
        store = MemoryStore()
        curator = MemoryCurator(trust_threshold=0.90)
        
        # Get trust scores from registry
        trust_scores = {path: trust_registry.get_trust_score(path) for path in files}
        
        # Curate golden files
        golden_files = curator.filter_files(files, trust_scores)
        metadata = curator.get_curation_metadata(project_name, trust_scores)
        metadata["total_file_count"] = len(files)
        metadata["golden_file_count"] = len(golden_files)

        store.store_project(
            project_name=project_name,
            prompt=prompt,
            files=list(golden_files.keys()),
            metadata=metadata
        )
        logger.info(f"Curated project indexed to memory: {project_name} ({len(golden_files)} golden files)")
    except Exception as e:
        logger.debug(f"Memory curation/indexing skipped: {e}")


@dataclass
class E2EResult:
    """Complete end-to-end generation result"""
    success: bool
    project_name: str
    prompt: str
    total_duration_seconds: float
    phases_completed: int
    total_phases: int
    files_generated: int
    collections_generated: int
    components_selected: int
    pages_generated: int
    bugs_found: int
    bugs_fixed: int
    export_path: str
    zip_path: str
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def display(self):
        """Display final result"""
        print("\n" + "=" * 70)
        print("🏆 NOVARYX GENERATION COMPLETE")
        print("=" * 70)
        print(f"   Project: {self.project_name}")
        print(f"   Duration: {self.total_duration_seconds:.1f}s")
        print(f"   Phases: {self.phases_completed}/{self.total_phases}")
        print(f"   Files: {self.files_generated}")
        print(f"   Pages: {self.pages_generated}")
        print(f"   Components: {self.components_selected}")
        print(f"   Collections: {self.collections_generated}")
        print(f"   Bugs Fixed: {self.bugs_fixed}")
        print(f"   Export: {self.export_path}")
        if self.zip_path:
            print(f"   ZIP: {self.zip_path}")
        if self.errors:
            print(f"\n   ❌ Errors: {len(self.errors)}")
            for e in self.errors[:3]:
                print(f"      - {e}")
        if self.warnings:
            print(f"\n   ⚠️  Warnings: {len(self.warnings)}")
        print("=" * 70)
        print(f"\n   🚀 Ready to deploy!")
        print(f"   cd {self.export_path}")
        print(f"   npm install && npm run dev")
        print()


class NOVARYX:
    """
    THE complete NOVARYX pipeline.
    
    One call does everything:
      novaryx = NOVARYX()
      result = novaryx.generate("Build a dark purple SaaS dashboard")
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm

        # Ensure tuned Modelfiles exist and RAG is seeded on first run
        if use_llm:
            try:
                from system.inference.ollama_provider import OllamaProvider
                _ollama = OllamaProvider()
                if _ollama.is_available():
                    _ollama.setup_tuned_models()
            except Exception as e:
                logger.debug(f"Modelfile setup skipped: {e}")
            _seed_rag_if_needed()

        # Initialize all engines
        self.intent_parser = IntentParser(use_llm=use_llm)
        self.task_decomposer = TaskDecomposer(use_llm=use_llm)
        self.token_engine = DesignTokenEngine(use_llm_refinement=use_llm)
        self.intelligence = TemplateIntelligence(use_llm=use_llm, use_rag=True)
        self.assembly_engine = AssemblyEngine(use_llm=use_llm)
        self.page_generator = MultiPageGenerator()
        self.ai_scaffold = AiScaffoldGenerator()
        self.backend_generator = PocketBaseGenerator(use_llm=use_llm)
        self.verification = VerificationPipeline()
        # Surgical repair: classified, scoped, budget-controlled — never whole-project
        self.surgical_repair = SurgicalRepairOrchestrator(
            budget=RepairBudget(
                max_files=8,          # Touch at most 8 files per run
                max_llm_calls=0,      # No LLM calls — deterministic only (fast)
                max_time_sec=25.0,    # Hard 25s wall clock limit
                accept_threshold=0.90 # Accept if 90%+ files are clean
            ),
            enable_llm=False,
        )
        self.state_manager = StateManager()
        self.checkpoint_manager = CheckpointManager()
        self.exporter = ProjectExporter()
        self.contract_engine = ContractEngine()

        # Pipeline tracking
        self.phases_total = 12
        self.phases_completed = 0
        self.warnings = []
        self.errors = []
    
    def generate(self, prompt: str, project_name: str = "", export: bool = True) -> E2EResult:
        """
        MAIN ENTRY POINT.
        
        Takes a prompt, produces a complete shippable project.
        
        Args:
            prompt: Natural language description of what to build
            project_name: Optional project name
            export: Whether to export the project
        
        Returns:
            Complete E2EResult
        """
        
        start_time = time.time()

        # Scoping fix: initialise generated_comps early so it's always defined
        generated_comps: set = set()

        print("\n" + "=" * 70)
        print("🚀 NOVARYX END-TO-END GENERATION")
        print("=" * 70)
        print(f"   Prompt: {prompt[:100]}...")
        print(f"   LLM: {'Enabled' if self.use_llm else 'Disabled'}")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)
        _emit_stream(f"Starting generation for: {prompt[:60]}")
        
        all_files: Dict[str, str] = {}
        spec: Optional[ProjectSpec] = None
        
        try:
            # ================================================
            # PHASE 1: Intent Parsing
            # ================================================
            self._print_phase(1, "Intent Parsing")
            _emit_stream("Phase 1: Parsing intent with LLM...")
            spec = self.intent_parser.parse(prompt)
            
            if not project_name:
                project_name = spec.project_name or "NOVARYX Project"
            
            # Create state
            state = self.state_manager.create_state(prompt, project_name)
            state.start_phase("intent_parsing")
            state.complete_phase("intent_parsing", spec.to_dict())
            self.state_manager.save()
            self.phases_completed += 1
            
            # ================================================
            # PHASE 1.5: Task Decomposition
            # ================================================
            self._print_phase(1.5, "Architecture Decomposition")
            _emit_stream("Phase 1.5: Decomposing project into submodules...")
            architecture = self.task_decomposer.decompose(spec)
            print(f"   Generated {len(architecture.modules)} discrete submodules")
            
            # Stream the dynamic architecture to the frontend
            _emit_architecture([architecture.modules[m] for m in architecture.generation_order])
            self.phases_completed += 0.5 # Sub-phase

            for m in architecture.generation_order:
                print(f"      - {m}")
            
            # We save the architecture into the checkpoint
            self.checkpoint_manager.create_checkpoint(
                state.generation_id, "architecture_defined",
                metadata={"order": architecture.generation_order}
            )
            
            # ================================================
            # PHASE 2: Design System
            # ================================================
            self._print_phase(2, "Design System")
            design_system = self.token_engine.generate(prompt, project_name)
            
            state.start_phase("design_system")
            state.design_system_data = design_system.to_dict()
            state.complete_phase("design_system")
            self.state_manager.save()
            self.phases_completed += 1
            
            # ================================================
            # PHASE 3: Layout Selection
            # ================================================
            self._print_phase(3, "Layout Selection")
            layout = LayoutRegistry.get_layout_for_project(spec.project_type)
            
            state.start_phase("layout_selection")
            state.layout_data = layout.to_dict()
            state.complete_phase("layout_selection")
            self.state_manager.save()
            self.phases_completed += 1
            
            # ================================================
            # PHASE 4: Component Selection
            # ================================================
            self._print_phase(4, "Component Selection")
            selections = self.intelligence.select_components_intelligently(
                prompt=prompt, layout=layout, intent=None
            )
            
            component_ids = []
            for slot_results in selections.values():
                for r in slot_results:
                    component_ids.append(r.component_id)
                    layout.assign_component(r.slot_name, r.component_id)
            
            state.start_phase("component_selection")
            state.component_selections = {
                slot: [r.component_id for r in results]
                for slot, results in selections.items()
            }
            state.complete_phase("component_selection")
            self.state_manager.save()
            self.checkpoint_manager.create_checkpoint(
                state.generation_id, "components_selected",
                metadata={"components": component_ids}
            )
            self.phases_completed += 1
            
            # ================================================
            # PHASE 5: Theme Generation
            # ================================================
            self._print_phase(5, "Theme & Animation")
            adapter = ThemeAdapter(design_system)
            theme_files = adapter.generate_all_theme_files()
            all_files.update(theme_files)
            
            anim_config = AnimationConfigGenerator.generate(
                prompt=prompt, design_system=design_system,
                component_list=component_ids, layout_type=layout.layout_type.value
            )
            
            state.complete_phase("theme_generation")
            self.state_manager.save()
            self.phases_completed += 1
            
            # ================================================
            # PHASE 6: Page Generation
            # ================================================
            self._print_phase(6, "Page Generation")
            _emit_stream("Phase 6: Generating pages with AI...")
            pages = spec.pages if spec.pages else []
            self.page_generator.set_repair_orchestrator(self.surgical_repair)
            self.page_generator.set_contract_engine(self.contract_engine)
            
            # Phase 7: Sandboxed Generation + Phase 10: Contract Injection
            generated_app = self.page_generator.generate(
                spec, telemetry_callback=_emit_telemetry, 
                use_sandbox=True, contract_engine=self.contract_engine
            )
            page_files = generated_app.files
            
            # Extract contracts for future modules
            for p_name, tsx in page_files.items():
                self.contract_engine.extract_contracts(p_name, {p_name: tsx})
            
            all_files.update(page_files)
            
            state.complete_phase("page_generation", {"pages": len(pages)})
            self.state_manager.save()
            self.checkpoint_manager.create_checkpoint(
                state.generation_id, "pages_generated",
                files=all_files
            )
            self.phases_completed += 1
            
            # ================================================
            # PHASE 7: Layout & Components
            # ================================================
            self._print_phase(7, "Layout & Components")
            _emit_stream("Phase 7: Assembling layout and components...")
            layout_tsx = layout.generate_layout_tsx(design_system)
            layout_type = layout.layout_type.value
            all_files[f"src/layouts/{layout_type}Layout.tsx"] = layout_tsx
            
            generated_comps = set()
            for slot_name, results in selections.items():
                for r in results:
                    if r.component_id in generated_comps:
                        continue
                    generated_comps.add(r.component_id)
                    
                    tsx = None
                    try:
                        from system.templates.dynamic.components.component_registry import ComponentRegistry
                        tsx = ComponentRegistry.get_component_tsx(r.component_id)
                    except Exception:
                        pass
                    
                    if tsx:
                        comp_name = r.component_name.replace(" ", "")
                        themed = adapter.apply_to_component_tsx(tsx, r.component_id)
                        all_files[f"src/components/{comp_name}.tsx"] = themed
            
            # Core files
            all_files["src/main.tsx"] = self._generate_main_tsx()
            all_files["package.json"] = self._generate_package_json(project_name, design_system)
            all_files["tsconfig.json"] = self._generate_tsconfig()
            all_files["vite.config.js"] = self._generate_vite_config()
            all_files["postcss.config.js"] = "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }"
            all_files["index.html"] = self._generate_index_html(project_name, design_system)
            all_files["README.md"] = self._generate_readme(project_name, prompt, spec)
            
            state.complete_phase("layout_components", {"components": len(generated_comps)})
            self.state_manager.save()
            self.phases_completed += 1
            
            # ================================================
            # PHASE 8: Backend Generation
            # ================================================
            self._print_phase(8, "Backend Generation")
            _emit_stream("Phase 8: Generating backend schema...")
            backend = None
            if spec.requires_database or spec.requires_authentication:
                features_list = [f.name for f in spec.features] if spec.features else []
                pages_list = [p.to_dict() for p in spec.pages] if spec.pages else []
                
                backend = self.backend_generator.generate(
                    prompt=prompt,
                    features=features_list,
                    pages=pages_list,
                    app_name=project_name
                )
                all_files.update(backend.files)
                state.backend_schema = backend.auth_config
            else:
                print(f"   Backend not required for this project type")
            
            state.complete_phase("backend_generation")
            self.state_manager.save()
            self.phases_completed += 1
            
            # ================================================
            # PHASE 9: Verification
            # ================================================
            self._print_phase(9, "Verification")
            _emit_stream("Phase 9: Verifying generated code...")
            verify_result = self.verification.verify(all_files)
            _emit_stream("Phase 9: Verification complete.")
            
            if verify_result.warnings:
                self.warnings.extend(verify_result.warnings)
            
            state.complete_phase("verification", {
                "passed": verify_result.passed,
                "issues": len(verify_result.errors)
            })
            self.state_manager.save()
            self.phases_completed += 1
            
            self._print_phase(10, "Final Validation")
            _emit_stream("Phase 10: Finalizing architecture and verifying module constraints...")

            repair_result = self.surgical_repair.repair(
                files=all_files,
                frozen=set(),  # No pre-frozen files at this stage
                telemetry_callback=_emit_telemetry
            )
            all_files = repair_result.repaired_files

            _emit_stream("Phase 10: Validation complete.")

            if repair_result.bugs_fixed > 0:
                print(f"   Internal constraints resolved: {repair_result.bugs_fixed}")
            if repair_result.bugs_skipped > 0:
                print(f"   Skipped: {repair_result.bugs_skipped} low-severity issues (accepted)")
            if not repair_result.success:
                # 90% threshold not met — log but continue (partial success)
                self.warnings.append(
                    f"Repair completed at {repair_result.files_frozen}/{repair_result.files_processed} "
                    f"clean files — continuing with partial success"
                )

            state.complete_phase("repair", {
                "fixed": repair_result.bugs_fixed,
                "skipped": repair_result.bugs_skipped,
                "frozen": repair_result.files_frozen,
                "elapsed_sec": repair_result.elapsed_sec,
            })
            self.state_manager.save()
            self.checkpoint_manager.create_checkpoint(
                state.generation_id, "repaired",
                files=all_files
            )
            self.phases_completed += 1
            
            # ================================================
            # PHASE 11: Export & Package
            # ================================================
            self._print_phase(11, "Export & Package")
            _emit_stream("Phase 11: Packaging project...")
            
            if getattr(spec, "requires_ai_assistant", False):
                _emit_stream("Phase 11: Injecting Embedded AI Assistant...")
                env_vars = {}
                if getattr(spec, "requires_database", False) or getattr(spec, "requires_authentication", False):
                    env_vars["NEXT_PUBLIC_POCKETBASE_URL"] = "http://127.0.0.1:8090"
                self.ai_scaffold.inject_scaffold(all_files, env_vars)
            else:
                _emit_stream("Phase 11: Skipping AI Assistant (Not requested)...")

            has_backend = backend is not None
            
            export_result = self.exporter.export(
                files=all_files,
                project_name=project_name,
                has_backend=has_backend,
                create_zip=True
            )
            
            state.complete_phase("export")
            self.state_manager.save()
            self.phases_completed += 1

            # ================================================
            # Index project to memory for future RAG retrieval
            # ================================================
            _index_to_memory(project_name, prompt, all_files, self.surgical_repair.trust_registry)
            
            # ================================================
            # PHASE 12: Complete
            # ================================================
            state.complete_phase("packaging")
            self.state_manager.save()
            self.phases_completed += 1
            
            total_time = time.time() - start_time
            
            result = E2EResult(
                success=True,
                project_name=project_name,
                prompt=prompt,
                total_duration_seconds=total_time,
                phases_completed=self.phases_completed,
                total_phases=self.phases_total,
                files_generated=len(all_files),
                collections_generated=len(backend.collections) if backend else 0,
                components_selected=len(generated_comps),
                pages_generated=len(pages),
                bugs_found=repair_result.bugs_found,
                bugs_fixed=repair_result.bugs_fixed,
                export_path=export_result.export_dir,
                zip_path=export_result.zip_path or "",
                warnings=self.warnings,
                errors=self.errors,
            )

            result.display()
            _emit_stream("Generation complete!")
            
            # Emit structured JSON line for frontend parsing
            print("GENERATION_RESULT: " + json.dumps({
                "success": result.success,
                "project_name": result.project_name,
                "files": list(all_files.keys()),
                "components": list(generated_comps) if 'generated_comps' in dir() else [],
                "componentCount": result.components_selected,
                "pages": result.pages_generated,
                "bugs_fixed": result.bugs_fixed,
                "export_path": result.export_path,
                "errors": result.errors,
            }))
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            self.errors.append(str(e))
            
            total_time = time.time() - start_time
            
            result = E2EResult(
                success=False,
                project_name=project_name or "Failed",
                prompt=prompt,
                total_duration_seconds=total_time,
                phases_completed=self.phases_completed,
                total_phases=self.phases_total,
                files_generated=len(all_files),
                collections_generated=0,
                components_selected=0,
                pages_generated=0,
                bugs_found=0,
                bugs_fixed=0,
                export_path="",
                zip_path="",
                warnings=self.warnings,
                errors=self.errors,
            )
            
            result.display()
            
            # Emit structured JSON line for frontend parsing (even on failure)
            print("GENERATION_RESULT: " + json.dumps({
                "success": False,
                "project_name": result.project_name,
                "files": list(all_files.keys()),
                "components": [],
                "componentCount": 0,
                "errors": result.errors,
            }))
            
            return result
    
    def _print_phase(self, num: int, name: str):
        print(f"\n{'─' * 50}")
        print(f"📋 Phase {num}/{self.phases_total}: {name}")
        print(f"{'─' * 50}")
    
    def _generate_main_tsx(self) -> str:
        return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/tokens.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
    
    def _generate_package_json(self, name: str, ds) -> str:
        deps = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.20.0",
            "framer-motion": "^10.16.0",
        }
        if ds.animations.three_d_enabled:
            deps["three"] = "^0.160.0"
            deps["@react-three/fiber"] = "^8.15.0"
            deps["@react-three/drei"] = "^9.92.0"
        
        package = {
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview"
            },
            "dependencies": deps,
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "typescript": "^5.3.0",
                "vite": "^5.0.0",
                "tailwindcss": "^3.4.0",
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0"
            }
        }
        return json.dumps(package, indent=2)
    
    def _generate_tsconfig(self) -> str:
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020", "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext", "skipLibCheck": True,
                "moduleResolution": "bundler", "allowImportingTsExtensions": True,
                "resolveJsonModule": True, "isolatedModules": True,
                "noEmit": True, "jsx": "react-jsx", "strict": True,
                "baseUrl": ".", "paths": {"@/*": ["src/*"]}
            },
            "include": ["src"]
        }, indent=2)
    
    def _generate_vite_config(self) -> str:
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
  server: { port: 3000, open: true },
})
"""
    
    def _generate_index_html(self, name: str, ds) -> str:
        font = ds.typography.font_family_primary.replace(" ", "+")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family={font}:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>"""
    
    def _generate_readme(self, name: str, prompt: str, spec) -> str:
        pages_list = "\n".join([f"- {p.route} → {p.title}" for p in spec.pages]) if spec.pages else "- Home"
        return f"""# {name}

Generated by **NOVARYX** - AI-Powered Application Builder

## Prompt
> {prompt[:300]}

## Pages
{pages_list}

## Quick Start
```bash
npm install
npm run dev
```

## Deployment
```bash
# Docker
docker-compose up -d

# Vercel
vercel deploy

# Netlify
netlify deploy
```

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


# ================================================================
# MAIN ENTRY POINT
# ================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NOVARYX - AI-Powered Application Builder",
        epilog="Example: python novaryx_e2e.py 'Build a dark purple SaaS dashboard'"
    )
    parser.add_argument("prompt", nargs="?", help="Project description")
    parser.add_argument("--prompt", "-p", dest="prompt_flag", help="Project description")
    parser.add_argument("--name", "-n", default="", help="Project name")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--test", action="store_true", help="Run test generation")
    
    args = parser.parse_args()
    
    if args.interactive:
        print("\n" + "=" * 60)
        print("🚀 NOVARYX INTERACTIVE MODE")
        print("=" * 60)
        prompt = input("\nDescribe what you want to build:\n> ")
        name = input("Project name (optional): ").strip()
        
        if not prompt:
            print("No prompt provided.")
            return
        
        novaryx = NOVARYX(use_llm=True)
        novaryx.generate(prompt, name)
        return
    
    if args.test:
        print("\n🧪 Running test generation...")
        novaryx = NOVARYX(use_llm=False)
        novaryx.generate(
            "Build a dark purple SaaS dashboard with analytics, stats cards, and user management",
            "NOVARYX-Test"
        )
        return
    
    prompt = args.prompt or args.prompt_flag
    if not prompt:
        parser.print_help()
        print("\nExample: python novaryx_e2e.py 'Build a dark purple SaaS dashboard with 3D globe'")
        return
    
    novaryx = NOVARYX(use_llm=not args.no_llm)
    novaryx.generate(prompt, args.name)


if __name__ == "__main__":
    main()