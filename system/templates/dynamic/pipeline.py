"""
NOVARYX - Complete Generation Pipeline
THE unified pipeline. Every subsystem connected end-to-end.

Flow:
  Prompt -> Intent -> Design -> Layout -> Components -> Theme -> Files -> Output
"""

import sys
import json
import logging
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from system.templates.dynamic.design_token_engine import DesignTokenEngine
from system.templates.dynamic.layouts.layout_registry import LayoutRegistry, get_layout_for_project
from system.templates.dynamic.layouts.base_layout import BaseLayout
from system.templates.dynamic.components.component_registry import ComponentRegistry
from system.templates.dynamic.components.three_d.three_registry import ThreeRegistry
from system.templates.dynamic.animations.animation_registry import AnimationRegistry
from system.templates.dynamic.animations.animation_config import AnimationConfigGenerator
from system.templates.dynamic.theme_adaptation_engine import ThemeAdapter
from system.templates.dynamic.template_intelligence import TemplateIntelligence, SelectionResult
from system.templates.dynamic.token_definitions import DesignSystem

logger = logging.getLogger("novaryx.pipeline")

# In-memory semantic cache for zero-latency component deduplication
_semantic_cache: Dict[str, dict] = {}


class GenerationPipeline:
    """
    THE complete NOVARYX generation pipeline.
    
    All 10 phases connected in one unified flow.
    """
    
    def __init__(self, use_llm: bool = True, use_rag: bool = True):
        self.use_llm = use_llm
        self.use_rag = use_rag
        
        # Initialize all engines
        self.token_engine = DesignTokenEngine(use_llm_refinement=use_llm)
        self.intelligence = TemplateIntelligence(use_llm=use_llm, use_rag=use_rag)
        
        # Pipeline state
        self.design_system: Optional[DesignSystem] = None
        self.layout: Optional[BaseLayout] = None
        self.selections: Dict[str, List[SelectionResult]] = {}
        self.animation_config: Dict[str, Any] = {}
        self.generated_files: Dict[str, str] = {}
        
        # Stats
        self.stats = {
            "start_time": None,
            "end_time": None,
            "phases_completed": [],
            "components_selected": 0,
            "files_generated": 0,
            "warnings": [],
            "errors": []
        }
    
    def generate(self, prompt: str, project_name: str = "") -> Dict[str, Any]:
        """
        MAIN ENTRY POINT.
        
        Takes a prompt, produces a complete project.
        
        Args:
            prompt: User's project description
            project_name: Optional project name
        
        Returns:
            Complete generation result with all files and metadata
        """
        
        self.stats["start_time"] = datetime.now()
        
        print("=" * 80)
        print("NOVARYX GENERATION PIPELINE")
        print("=" * 80)
        print(f"   Prompt: {prompt[:100]}...")
        print(f"   Time: {self.stats['start_time'].strftime('%H:%M:%S')}")
        print("=" * 80)
        
        try:
            # ================================================
            # PHASE 1: DESIGN SYSTEM GENERATION
            # ================================================
            self._phase_design_system(prompt, project_name)
            
            # ================================================
            # PHASE 2: INTENT ANALYSIS
            # ================================================
            intent = self._phase_intent_analysis(prompt)
            
            # ================================================
            # PHASE 3: LAYOUT SELECTION
            # ================================================
            self._phase_layout_selection(prompt, intent)
            
            # ================================================
            # PHASE 4: COMPONENT SELECTION
            # ================================================
            self._phase_component_selection(prompt, intent)
            
            # ================================================
            # PHASE 5: 3D COMPONENT SELECTION
            # ================================================
            self._phase_3d_selection(prompt)
            
            # ================================================
            # PHASE 6: ANIMATION CONFIGURATION
            # ================================================
            self._phase_animation_config(prompt)
            
            # ================================================
            # PHASE 7: FILE GENERATION
            # ================================================
            self._phase_file_generation(prompt)
            
            # ================================================
            # PHASE 8: THEME ADAPTATION
            # ================================================
            self._phase_theme_adaptation()
            
            # ================================================
            # PHASE 9: VERIFICATION
            # ================================================
            self._phase_verification()
            
            # ================================================
            # PHASE 10: PACKAGING
            # ================================================
            result = self._phase_packaging(prompt, project_name)
            
            self.stats["end_time"] = datetime.now()
            
            self._print_success(result)
            
            return result
            
        except Exception as e:
            self.stats["errors"].append(str(e))
            self.stats["end_time"] = datetime.now()
            logger.error(f"Pipeline failed: {e}")
            self._print_failure(e)
            raise
    
    # ================================================================
    # PHASE IMPLEMENTATIONS
    # ================================================================
    
    def _phase_design_system(self, prompt: str, project_name: str):
        """Phase 1: Generate complete design system from prompt"""
        print("\n" + "-" * 60)
        print("PHASE 1: Design System Generation")
        print("-" * 60)
        
        self.design_system = self.token_engine.generate(prompt, project_name)
        
        print(f"   Primary: {self.design_system.colors.primary}")
        print(f"   Mode: {self.design_system.mode}")
        print(f"   Font: {self.design_system.typography.font_family_primary}")
        print(f"   Glassmorphism: {'ON' if self.design_system.effects.glass_enabled else 'OFF'}")
        print(f"   3D: {'ON' if self.design_system.animations.three_d_enabled else 'OFF'}")
        
        self.stats["phases_completed"].append("design_system")
    
    def _phase_intent_analysis(self, prompt: str):
        """Phase 2: Analyze user intent with LLM + keywords"""
        print("\n" + "-" * 60)
        print("PHASE 2: Intent Analysis")
        print("-" * 60)
        
        intent = self.intelligence.analyze_intent(prompt)
        
        print(f"   Type: {intent.project_type} ({intent.project_type_confidence:.0%})")
        print(f"   Features: {', '.join(intent.features_requested[:8])}")
        print(f"   Complexity: {intent.complexity_level}")
        print(f"   Style: {intent.visual_style.get('color_preference', 'unknown')}")
        
        self.stats["phases_completed"].append("intent_analysis")
        return intent
    
    def _phase_layout_selection(self, prompt: str, intent):
        """Phase 3: Select best layout for project type"""
        print("\n" + "-" * 60)
        print("PHASE 3: Layout Selection")
        print("-" * 60)
        
        self.layout = get_layout_for_project(intent.project_type)
        
        print(f"   Layout: {self.layout.layout_name}")
        print(f"   Type: {self.layout.layout_type.value}")
        print(f"   Slots: {len(self.layout.get_all_slots())}")
        print(f"   Required: {len(self.layout.get_required_slots())}")
        
        self.stats["phases_completed"].append("layout_selection")
    
    def _phase_component_selection(self, prompt: str, intent):
        """Phase 4: Intelligently select components for each slot"""
        print("\n" + "-" * 60)
        print("PHASE 4: Component Selection")
        print("-" * 60)
        
        self.selections = self.intelligence.select_components_intelligently(
            prompt=prompt,
            layout=self.layout,
            intent=intent
        )
        
        total = 0
        for slot_name, results in self.selections.items():
            slot = self.layout.get_slot(slot_name)
            required = "REQ" if slot and slot.required else "OPT"
            names = [r.component_name for r in results]
            avg_conf = sum(r.confidence for r in results) / max(len(results), 1)
            print(f"   [{required}] {slot_name}: {', '.join(names[:3])} ({avg_conf:.0%})")
            total += len(results)
            
            # Assign to layout
            for r in results:
                self.layout.assign_component(slot_name, r.component_id)
        
        self.stats["components_selected"] = total
        self.stats["phases_completed"].append("component_selection")
    
    def _phase_3d_selection(self, prompt: str):
        """Phase 5: Select 3D components if needed"""
        print("\n" + "-" * 60)
        print("PHASE 5: 3D Component Selection")
        print("-" * 60)
        
        if self.design_system.animations.three_d_enabled:
            matches = ThreeRegistry.find_by_prompt(prompt)
            if matches:
                best = matches[0]
                print(f"   Selected: {best.name}")
                print(f"   Performance: {best.performance_tier}")
                
                # Assign to appropriate slot
                for slot_name in best.allowed_slots:
                    if self.layout.get_slot(slot_name):
                        self.layout.assign_component(slot_name, f"3d_{best.component_id}")
                        break
            else:
                print(f"   No matching 3D component found")
        else:
            print(f"   3D not requested in prompt")
        
        self.stats["phases_completed"].append("3d_selection")
    
    def _phase_animation_config(self, prompt: str):
        """Phase 6: Generate animation configuration"""
        print("\n" + "-" * 60)
        print("PHASE 6: Animation Configuration")
        print("-" * 60)
        
        component_ids = []
        for results in self.selections.values():
            for r in results:
                component_ids.append(r.component_id)
        
        self.animation_config = AnimationConfigGenerator.generate(
            prompt=prompt,
            design_system=self.design_system,
            component_list=component_ids,
            layout_type=self.layout.layout_type.value
        )
        
        print(f"   Page Transition: {self.animation_config['page_transition']['name']}")
        print(f"   Scroll Reveal: {self.animation_config['scroll_reveal']['name']}")
        print(f"   Micro: {self.animation_config['micro_interaction']['name']}")
        
        self.stats["phases_completed"].append("animation_config")
    
    def _phase_file_generation(self, prompt: str):
        """Phase 7: Generate all project files"""
        print("\n" + "-" * 60)
        print("PHASE 7: File Generation")
        print("-" * 60)
        
        files = {}
        
        # 1. Design tokens CSS
        adapter = ThemeAdapter(self.design_system)
        files.update(adapter.generate_all_theme_files())
        
        # 2. Layout TSX
        layout_name = self.layout.layout_type.value
        layout_tsx = self.layout.generate_layout_tsx(self.design_system)
        files[f"src/layouts/{layout_name}Layout.tsx"] = layout_tsx
        
        # 3. Component TSX files
        generated_comps = set()
        for slot_name, results in self.selections.items():
            for r in results:
                if r.component_id in generated_comps:
                    continue
                generated_comps.add(r.component_id)
                
                tsx = ComponentRegistry.get_component_tsx(r.component_id)
                if tsx:
                    comp_name = r.component_name.replace(" ", "")
                    themed_tsx = adapter.apply_to_component_tsx(tsx, r.component_id)
                    files[f"src/components/{comp_name}.tsx"] = themed_tsx
        
        # 4. App.tsx
        files["src/App.tsx"] = self._generate_app_tsx(prompt)
        
        # 5. main.tsx
        files["src/main.tsx"] = self._generate_main_tsx()
        
        # 6. index.html
        files["index.html"] = self._generate_index_html()
        
        # 7. Config files
        files["package.json"] = self._generate_package_json()
        files["tsconfig.json"] = self._generate_tsconfig()
        files["vite.config.js"] = self._generate_vite_config()
        files["postcss.config.js"] = self._generate_postcss_config()
        files[".env"] = self._generate_env()
        files["README.md"] = self._generate_readme(prompt)
        
        self.generated_files = files
        self.stats["files_generated"] = len(files)
        
        print(f"   Generated: {len(files)} files")
        for f in sorted(files.keys())[:10]:
            print(f"      {f}")
        if len(files) > 10:
            print(f"      ... and {len(files) - 10} more")
        
        self.stats["phases_completed"].append("file_generation")
    
    def _phase_theme_adaptation(self):
        """Phase 8: Deep theme injection into all files"""
        print("\n" + "-" * 60)
        print("PHASE 8: Theme Adaptation")
        print("-" * 60)
        
        adapter = ThemeAdapter(self.design_system)
        
        # Apply theme to all generated TSX files
        themed_count = 0
        for filepath, content in self.generated_files.items():
            if filepath.endswith('.tsx'):
                themed = adapter.apply_to_component_tsx(content, filepath)
                if themed != content:
                    self.generated_files[filepath] = themed
                    themed_count += 1
        
        print(f"   Files themed: {themed_count}")
        print(f"   Theme: {self.design_system.colors.primary} / {self.design_system.mode}")
        
        self.stats["phases_completed"].append("theme_adaptation")
    
    def _phase_verification(self):
        """Phase 9: Verify all required files exist and slots are filled"""
        print("\n" + "-" * 60)
        print("PHASE 9: Verification")
        print("-" * 60)
        
        checks = []
        
        # Check required slots filled
        missing = self.layout.get_missing_components()
        if not missing:
            checks.append("[OK] All required slots filled")
        else:
            self.stats["warnings"].append(f"Missing components in slots: {missing}")
            checks.append(f"[!] Missing: {', '.join(missing)}")
        
        # Check essential files
        essential = ["src/App.tsx", "src/main.tsx", "index.html", "package.json"]
        for f in essential:
            if f in self.generated_files:
                checks.append(f"[OK] {f}")
            else:
                checks.append(f"[ERROR] Missing: {f}")
                self.stats["errors"].append(f"Missing essential file: {f}")
        
        # Check component files
        comp_files = [f for f in self.generated_files if f.startswith("src/components/")]
        checks.append(f"[OK] {len(comp_files)} component files")
        
        for check in checks:
            print(f"   {check}")
        
        self.stats["phases_completed"].append("verification")
    
    def _phase_packaging(self, prompt: str, project_name: str) -> Dict[str, Any]:
        """Phase 10: Package everything into final output"""
        print("\n" + "-" * 60)
        print("PHASE 10: Packaging")
        print("-" * 60)
        
        project = project_name or self.design_system.project_name
        project_slug = project.lower().replace(" ", "-")
        
        result = {
            "project_name": project,
            "project_slug": project_slug,
            "prompt": prompt,
            "generated_at": datetime.now().isoformat(),
            "design_system": self.design_system.to_dict(),
            "layout_type": self.layout.layout_type.value,
            "components_count": self.stats["components_selected"],
            "files_count": self.stats["files_generated"],
            "files": self.generated_files,
            "slot_assignments": {
                slot: [r.component_id for r in results]
                for slot, results in self.selections.items()
            },
            "stats": {
                "phases": self.stats["phases_completed"],
                "warnings": self.stats["warnings"],
                "errors": self.stats["errors"],
                "duration_seconds": (
                    self.stats["end_time"] - self.stats["start_time"]
                ).total_seconds() if self.stats["end_time"] else 0
            }
        }
        
        print(f"   Project: {project}")
        print(f"   Files: {len(self.generated_files)}")
        print(f"   Phases: {len(self.stats['phases_completed'])}/10")
        print(f"   Duration: {result['stats']['duration_seconds']:.1f}s")
        
        self.stats["phases_completed"].append("packaging")
        
        return result
    
    # ================================================================
    # FILE GENERATORS
    # ================================================================
    
    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Convert any string to valid TypeScript identifier"""
        import re
        words = re.findall(r'[a-zA-Z0-9]+', name)
        return ''.join(word.capitalize() for word in words) if words else "Component"

    def _generate_dynamic_content(self, prompt: str) -> str:
        """Prompt LLM to generate context-aware JSON string content for components using Parallel Models & Auto-Healing"""
        if not self.use_llm or not hasattr(self, 'intelligence'): return "{}"
        
        # get all component names in use
        comp_names = []
        for slot_name, results in self.selections.items():
            if results: comp_names.extend([self._sanitize_name(r.component_name) for r in results])
            
        if not comp_names: return "{}"
            
        # Hard limit chunk size to 3 to absolutely prevent timeouts on massive prompts
        chunk_size = 3
        chunks = [comp_names[i:i + chunk_size] for i in range(0, len(comp_names), chunk_size)]
        
        from system.inference.provider_factory import get_provider_for_role
        
        def _fetch_chunk(chunk: List[str], chunk_id: int) -> dict:
            if not chunk: return {}
            # Use alternating roles to force using two different models parallelly
            role = "planning" if chunk_id % 2 == 0 else "generation"
            
            try:
                provider = get_provider_for_role(role)
            except Exception:
                provider = self.intelligence._get_inference() # fallback
                
            if not provider: return {}
            
            target_description = self.design_system.project_name if self.design_system else "AI Saas platform"
            
            # Context Injection: Read actual TSX interfaces to force exact schema adherence
            interface_context = []
            try:
                reg = ComponentRegistry()
                for comp in chunk:
                    info = reg.get_component(comp)
                    if info and "template" in info:
                        import re
                        # Extract the interface definition
                        match = re.search(r'(interface\s+\w+Props\s*\{[^}]+\})', info["template"])
                        if match:
                            interface_context.append(f"Component: {comp}\\n{match.group(1)}")
            except Exception:
                pass
                
            interfaces_str = "\\n\\n".join(interface_context)
            
            system_prompt = f"""Generate a contextual UI content JSON object for a web project targeting: "{target_description}"
User Prompt: "{prompt}"

You MUST return ONLY a valid JSON object. NO MARKDOWN, NO ```json.
The keys MUST be the exact component names: {', '.join(chunk)}. 
The values MUST be objects containing deep logical layout data tailored to the User Prompt.

CRITICAL: Adhere perfectly to the following TypeScript interfaces for each component. Your JSON keys inside the objects must perfectly match these Props:
{interfaces_str}

Be extremely CREATIVE, PROFESSIONAL, and PREMIUM in your copywriting. Make it high-converting and professional.
"""
            # Semantic Caching
            import hashlib
            prompt_hash = hashlib.md5(system_prompt.encode('utf-8')).hexdigest()
            if prompt_hash in _semantic_cache:
                logger.info(f"Chunk {chunk_id} loaded from Semantic Cache (0ms latency)")
                return _semantic_cache[prompt_hash]

            # Auto-healing loop
            max_retries = 3 # Increased retries
            for attempt in range(max_retries):
                text = ""
                try:
                    # Native JSON Mode + Increased creativity
                    result = provider.generate(
                        prompt=system_prompt, 
                        role=role, 
                        temperature=0.85, 
                        max_tokens=1500,
                        response_format="json" # Native Grammar Constraint
                    )
                    if result.success and result.text:
                        text = result.text.strip()
                        import re
                        json_match = re.search(r'\{.*\}', text, re.DOTALL)
                        if json_match:
                            try:
                                parsed = json.loads(json_match.group(0))
                                _semantic_cache[prompt_hash] = parsed
                                return parsed
                            except json.JSONDecodeError:
                                pass # let it fall through to auto-repair
                except Exception as e:
                    logger.warning(f"Chunk {chunk_id} attempt {attempt+1} failed: {e}")
                    if attempt == max_retries - 1 and text:
                        # Auto-repair via repair model on last failure
                        try:
                            repair_provider = get_provider_for_role("repair")
                            repair_prompt = f"Fix this JSON. Return ONLY valid JSON. It is broken:\\n{text}"
                            repair_result = repair_provider.generate(prompt=repair_prompt, role="repair")
                            rt = repair_result.text.strip()
                            import re
                            r_match = re.search(r'\{.*\}', rt, re.DOTALL)
                            if r_match:
                                try:
                                    return json.loads(r_match.group(0))
                                except json.JSONDecodeError:
                                    pass
                        except Exception as re_err:
                            logger.error(f"Auto-repair failed: {re_err}")
            return {}

        merged_data = {}
        print(f"   [Parallel] Generating dynamic content in {len(chunks)} steps across models (chunk size: {chunk_size})...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor: # Increased workers
            futures = [executor.submit(_fetch_chunk, chunk, i) for i, chunk in enumerate(chunks)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    # 160s is safely higher than the 120s API limit in provider_factory
                    data = future.result(timeout=160)  
                    merged_data.update(data)
                except concurrent.futures.TimeoutError:
                    logger.error("Thread execution timed out violently. Gracefully continuing.")
                except Exception as e:
                    logger.error(f"Thread execution failed: {e}")
                    
        return json.dumps(merged_data, indent=2)

    def _generate_app_tsx(self, prompt: str) -> str:
        layout_type = self.layout.layout_type.value
        layout_component = f"{self._sanitize_name(layout_type)}Layout"
        
        dynamic_json_str = self._generate_dynamic_content(prompt)
        
        slot_props_lines = []
        import_lines = set()
        for slot_name, results in self.selections.items():
            if not results:
                continue
            comp_names = [self._sanitize_name(r.component_name) for r in results]
            if comp_names:
                components_jsx = " ".join(f"<{n} {{...(dynamicProps.{n} || {{}})}} />" for n in comp_names)
                slot_props_lines.append(f"        {slot_name}Content={{<>{components_jsx}</>}}")
                for n in comp_names:
                    import_lines.add(f"import {{ {n} }} from './components/{n}';")
        
        slot_props = "\n".join(slot_props_lines)
        imports_str = "\n".join(sorted(import_lines))
        
        return f"""import React from 'react';
import {{ ThemeProvider }} from './components/ThemeProvider';
import {layout_component} from './layouts/{layout_type}Layout';
{imports_str}

const dynamicProps: any = {dynamic_json_str};

export default function App() {{
  return (
    <ThemeProvider>
      <{layout_component}
{slot_props}
      />
    </ThemeProvider>
  );
}}
"""
    
    def _generate_main_tsx(self) -> str:
        return """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/tokens.css';
import './styles/animations.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    
    def _generate_index_html(self) -> str:
        ds = self.design_system
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{ds.project_name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family={ds.typography.font_family_primary.replace(' ', '+')}:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>"""
    
    def _generate_package_json(self) -> str:
        deps = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "framer-motion": "^10.16.0",
        }
        
        if self.design_system.animations.three_d_enabled:
            deps["three"] = "^0.160.0"
            deps["@react-three/fiber"] = "^8.15.0"
            deps["@react-three/drei"] = "^9.92.0"
        
        package = {
            "name": self.design_system.project_name.lower().replace(" ", "-"),
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
                "@vitejs/plugin-react": "^4.2.0",
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
    
    def _generate_postcss_config(self) -> str:
        return """export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
}
"""
    
    def _generate_env(self) -> str:
        return f"""VITE_APP_NAME={self.design_system.project_name}
VITE_APP_VERSION=1.0.0
"""
    
    def _generate_readme(self, prompt: str) -> str:
        ds = self.design_system
        return f"""# {ds.project_name}

Generated by **NOVARYX** - AI-Powered Application Builder

## Prompt
> {prompt[:200]}

## Design System
| Token | Value |
|-------|-------|
| Primary | {ds.colors.primary} |
| Mode | {ds.mode} |
| Font | {ds.typography.font_family_primary} |
| Glassmorphism | {'Yes' if ds.effects.glass_enabled else 'No'} |
| 3D | {'Yes' if ds.animations.three_d_enabled else 'No'} |

## Project Structure
- Layout: {self.layout.layout_type.value}
- Components: {self.stats['components_selected']}
- Files: {self.stats['files_generated']}

## Getting Started
```bash
npm install
npm run dev
```

## Generated
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Pipeline: Phase 1.10
"""
    
    # ================================================================
    # DISPLAY
    # ================================================================
    
    def _print_success(self, result: Dict[str, Any]):
        duration = result["stats"]["duration_seconds"]
        
        print("\n" + "=" * 80)
        print("GENERATION COMPLETE")
        print("=" * 80)
        print(f"   Project: {result['project_name']}")
        print(f"   Files: {result['files_count']}")
        print(f"   Components: {result['components_count']}")
        print(f"   Duration: {duration:.1f}s")
        if result["stats"]["warnings"]:
            print(f"   Warnings: {len(result['stats']['warnings'])}")
        print("=" * 80)
        print(f"\n   Ready for: npm install && npm run dev")
        print()
    
    def _print_failure(self, error: Exception):
        print("\n" + "=" * 80)
        print("GENERATION FAILED")
        print("=" * 80)
        print(f"   Error: {error}")
        print(f"   Phases completed: {len(self.stats['phases_completed'])}/10")
        print("=" * 80 + "\n")


# ================================================================
# MAIN ENTRY FUNCTION
# ================================================================

def novaryx_generate(
    prompt: str,
    project_name: str = "",
    use_llm: bool = True,
    use_rag: bool = True
) -> Dict[str, Any]:
    """
    THE main function. Prompt → Complete Project.
    
    Args:
        prompt: Describe what you want to build
        project_name: Optional project name
        use_llm: Enable LLM for intelligent selection
        use_rag: Enable RAG for similar project retrieval
    
    Returns:
        Complete generation result with all files
    """
    pipeline = GenerationPipeline(use_llm=use_llm, use_rag=use_rag)
    return pipeline.generate(prompt, project_name)


def write_project_to_disk(result: Dict[str, Any], output_dir: str = None) -> str:
    """Write generated project files to disk"""
    if output_dir is None:
        novaryx_root = Path.home() / "novaryx"
        output_dir = str(novaryx_root / "projects" / "active" / result["project_slug"])
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    written = 0
    for filepath, content in result["files"].items():
        full_path = output_path / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        written += 1
    
    print(f"\nProject written to: {output_path}")
    print(f"   {written} files")
    print(f"\n   cd {output_path}")
    print(f"   npm install")
    print(f"   npm run dev")
    
    return str(output_path)


# ================================================================
# TEST
# ================================================================

def test_pipeline():
    """Test the complete generation pipeline"""
    
    print("\n" + "=" * 80)
    print("END-TO-END PIPELINE TEST")
    print("=" * 80)
    
    test_prompts = [
        "Build a dark purple SaaS dashboard with analytics, stats cards, and user management",
        "Create a modern landing page for an AI startup with 3D hero and pricing",
    ]
    
    for prompt in test_prompts:
        try:
            result = novaryx_generate(prompt, use_llm=False, use_rag=False)
            
            # Write to disk
            write_project_to_disk(result)
            
        except Exception as e:
            print(f"\nTest failed: {e}")
    
    print("\nPipeline test complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_pipeline()