"""
NOVARYX - Component Assembly Engine
THE central engine that builds complete pages from prompts.

Flow:
  Prompt -> Layout Selection -> Component Selection -> Slot Filling -> 
  Theme Application -> Animation Application -> Complete Project

Connected to ALL subsystems:
  - Design Token Engine (1.1)
  - Layout System (1.2)
  - Component Registry (1.3, 1.4)
  - 3D Registry (1.5)
  - Animation System (1.6)
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from system.templates.dynamic.token_definitions import DesignSystem
from system.templates.dynamic.design_token_engine import DesignTokenEngine
from system.templates.dynamic.layouts.layout_registry import LayoutRegistry, get_layout_for_project
from system.templates.dynamic.layouts.base_layout import BaseLayout, LayoutSlot
from system.templates.dynamic.components.component_registry import ComponentRegistry, ComponentMeta
from system.templates.dynamic.components.three_d.three_registry import ThreeRegistry
from system.templates.dynamic.animations.animation_config import AnimationConfigGenerator
from system.templates.dynamic.theme_adaptation_engine import ThemeAdapter

logger = logging.getLogger("novaryx.assembly_engine")


class AssemblyPlan:
    """Complete assembly plan for a project"""
    
    def __init__(self):
        self.project_name: str = ""
        self.prompt: str = ""
        self.project_type: str = ""
        self.layout = None  # BaseLayout
        self.design_system: Optional[DesignSystem] = None
        self.animation_config: Dict[str, Any] = {}
        self.slot_assignments: Dict[str, List[str]] = {}  # slot_name → [component_ids]
        self.components_used: List[str] = []
        self.components_3d: List[str] = []
        self.pages_to_generate: List[str] = []
        self.tsx_files: Dict[str, str] = {}  # filename → tsx content
        self.css_files: Dict[str, str] = {}
        self.config_files: Dict[str, str] = {}
        self.missing_components: List[str] = []
        self.generation_log: List[str] = []
    
    def log(self, message: str):
        """Add to generation log"""
        self.generation_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        logger.info(message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "project_type": self.project_type,
            "layout": self.layout.layout_type.value if self.layout else "none",
            "components_count": len(self.components_used),
            "3d_components": self.components_3d,
            "slots_filled": {
                slot: len(comps) 
                for slot, comps in self.slot_assignments.items()
            },
            "files_generated": len(self.tsx_files),
            "missing_components": self.missing_components
        }


class AssemblyEngine:
    """
    THE assembly engine. Takes a prompt, produces a complete project plan.
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.token_engine = DesignTokenEngine(use_llm_refinement=use_llm)
        self._inference = None
    
    def _get_inference(self):
        """Lazy load inference provider"""
        if self._inference is None:
            try:
                from system.inference.provider_factory import get_provider
                self._inference = get_provider()
            except Exception as e:
                logger.warning(f"Inference not available: {e}")
        return self._inference
    
    def assemble(self, prompt: str, project_name: str = "") -> AssemblyPlan:
        """
        Main entry point. Takes a prompt, returns complete assembly plan.
        
        Args:
            prompt: User's project description
            project_name: Optional project name
        
        Returns:
            Complete AssemblyPlan ready for file generation
        """
        plan = AssemblyPlan()
        plan.prompt = prompt
        
        print("\n" + "=" * 70)
        print("NOVARYX ASSEMBLY ENGINE")
        print("=" * 70)
        print(f"   Prompt: {prompt[:80]}...")
        print("=" * 70)
        
        # ---- STEP 1: Generate Design System ----
        print("\nStep 1: Generating Design System...")
        plan.log("Starting design token generation")
        plan.design_system = self.token_engine.generate(prompt, project_name)
        plan.project_name = plan.design_system.project_name
        plan.log(f"Design system ready: {plan.design_system.colors.primary} / {plan.design_system.mode}")
        print(f"   Primary: {plan.design_system.colors.primary}")
        print(f"   Mode: {plan.design_system.mode}")
        print(f"   Font: {plan.design_system.typography.font_family_primary}")
        print(f"   Glass: {'Yes' if plan.design_system.effects.glass_enabled else 'No'}")
        print(f"   3D: {'Yes' if plan.design_system.animations.three_d_enabled else 'No'}")
        
        # ---- STEP 2: Select Layout ----
        print("\nStep 2: Selecting Layout...")
        plan.log("Selecting layout")
        plan.project_type = self._detect_project_type(prompt)
        plan.layout = get_layout_for_project(plan.project_type)
        plan.log(f"Layout selected: {plan.layout.layout_name}")
        print(f"   Type: {plan.layout.layout_type.value}")
        print(f"   Slots: {len(plan.layout.get_all_slots())}")
        
        # ---- STEP 3: Select Components ----
        print("\nStep 3: Selecting Components...")
        plan.log("Starting component selection")
        plan.slot_assignments = self._select_components_for_slots(
            prompt, plan.layout, plan.design_system
        )
        
        total_assigned = sum(len(comps) for comps in plan.slot_assignments.values())
        plan.components_used = []
        for comps in plan.slot_assignments.values():
            plan.components_used.extend(comps)
        plan.log(f"Components selected: {len(plan.components_used)} total")
        
        for slot_name, comps in plan.slot_assignments.items():
            slot = plan.layout.get_slot(slot_name)
            required = "[REQ]" if slot and slot.required else "[OPT]"
            print(f"   {required} {slot_name}: {len(comps)} components -> {', '.join(comps[:3])}")
        
        # ---- STEP 4: Select 3D Components ----
        print("\nStep 4: Selecting 3D Components...")
        plan.log("Checking for 3D requirements")
        plan.components_3d = self._select_3d_components(prompt, plan.layout)
        if plan.components_3d:
            print(f"   3D Components: {', '.join(plan.components_3d)}")
        else:
            print(f"   No 3D components needed")
        
        # ---- STEP 5: Generate Animation Config ----
        print("\nStep 5: Generating Animation Config...")
        plan.log("Generating animation configuration")
        plan.animation_config = AnimationConfigGenerator.generate(
            prompt=prompt,
            design_system=plan.design_system,
            component_list=plan.components_used,
            layout_type=plan.layout.layout_type.value
        )
        print(f"   Page Transition: {plan.animation_config['page_transition']['name']}")
        print(f"   Scroll Reveal: {plan.animation_config['scroll_reveal']['name']}")
        print(f"   Micro: {plan.animation_config['micro_interaction']['name']}")
        
        # ---- STEP 6: Check for missing components ----
        print("\nStep 6: Checking completeness...")
        plan.missing_components = plan.layout.get_missing_components()
        if plan.missing_components:
            plan.log(f"Missing components: {plan.missing_components}")
            print(f"   Missing: {', '.join(plan.missing_components)}")
            print(f"   These will be generated by LLM in Step 1.9-1.10")
        else:
            print(f"   All required slots filled!")
        
        # ---- Summary ----
        print("\n" + "=" * 70)
        print("ASSEMBLY COMPLETE")
        print("=" * 70)
        print(f"   Project: {plan.project_name}")
        print(f"   Layout: {plan.layout.layout_type.value}")
        print(f"   Components: {len(plan.components_used)}")
        print(f"   3D: {len(plan.components_3d)}")
        print(f"   Files ready to generate: {len(plan.layout.get_all_slots())} pages")
        print("=" * 70 + "\n")
        
        return plan
    
    def _detect_project_type(self, prompt: str) -> str:
        """Detect project type from prompt"""
        prompt_lower = prompt.lower()
        
        type_keywords = {
            "saas_dashboard": ["dashboard", "saas", "analytics", "admin panel", "metrics", "kpi"],
            "landing_page": ["landing", "landing page", "hero", "pricing", "cta", "marketing"],
            "ecommerce": ["store", "shop", "ecommerce", "product", "cart", "checkout"],
            "admin_panel": ["admin", "management", "crud", "users table", "role"],
            "portfolio": ["portfolio", "showcase", "creative", "projects", "gallery"],
        }
        
        scores = {}
        for ptype, keywords in type_keywords.items():
            scores[ptype] = sum(1 for kw in keywords if kw in prompt_lower)
        
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "saas_dashboard"
    
    def _select_components_for_slots(
        self,
        prompt: str,
        layout: BaseLayout,
        design_system: DesignSystem
    ) -> Dict[str, List[str]]:
        """Select components for each slot based on prompt"""
        
        assignments: Dict[str, List[str]] = {}
        
        for slot in layout.get_all_slots():
            # Find matching components for this slot
            matches = ComponentRegistry.find_for_slot(
                slot_name=slot.name,
                slot_allowed_types=slot.allowed_component_types,
                prompt=prompt
            )
            
            if matches:
                # Take the best match
                best_match = matches[0]
                assignments[slot.name] = [best_match.component_id]
                
                # If slot allows multiple, add more if relevant
                if slot.max_components > 1 and len(matches) > 1:
                    for extra in matches[1:slot.max_components]:
                        assignments[slot.name].append(extra.component_id)
                
                # Assign to layout
                for comp_id in assignments[slot.name]:
                    layout.assign_component(slot.name, comp_id)
            
            elif slot.required and slot.default_component:
                # Use default if required
                assignments[slot.name] = [slot.default_component]
                layout.assign_component(slot.name, slot.default_component)
            
            elif slot.required:
                # Mark as missing - will be generated later
                assignments[slot.name] = []
        
        return assignments
    
    def _select_3d_components(self, prompt: str, layout: BaseLayout) -> List[str]:
        """Select 3D components if prompt wants them"""
        
        # Check if design system has 3D enabled
        has_3d_prompt = any(
            kw in prompt.lower() 
            for kw in ["3d", "three", "globe", "particle", "dimensional", "webgl"]
        )
        
        if not has_3d_prompt:
            return []
        
        # Find 3D components matching prompt
        matches = ThreeRegistry.find_by_prompt(prompt)
        
        selected = []
        for match in matches[:2]:  # Max 2 3D components
            # Check if any slot in layout can accept 3D
            for slot_name in match.allowed_slots:
                slot = layout.get_slot(slot_name)
                if slot and slot_name not in [c for comps in selected for c in []]:
                    selected.append(match.component_id)
                    layout.assign_component(slot_name, f"3d_{match.component_id}")
                    break
        
        return selected
    
    def generate_project_files(self, plan: AssemblyPlan) -> Dict[str, str]:
        """Generate all project files from assembly plan"""
        
        print("\nGenerating project files...")
        files: Dict[str, str] = {}
        
        # 1. Theme files (CSS, Tailwind, Provider)
        adapter = ThemeAdapter(plan.design_system)
        theme_files = adapter.generate_all_theme_files()
        files.update(theme_files)
        plan.log("Generated theme files via ThemeAdapter")
        
        # 3. Animation config
        anim_css = AnimationConfigGenerator.get_tailwind_animation_config()
        files["src/styles/animations.css"] = anim_css
        plan.log("Generated animations.css")
        
        # 4. Layout component
        layout_tsx = plan.layout.generate_layout_tsx(plan.design_system)
        themed_layout_tsx = adapter.apply_to_component_tsx(layout_tsx, "layout")
        layout_name = plan.layout.layout_type.value
        files[f"src/layouts/{layout_name}Layout.tsx"] = themed_layout_tsx
        plan.log(f"Generated {layout_name}Layout.tsx")
        
        # 5. Page components for each slot
        for slot_name, comp_ids in plan.slot_assignments.items():
            slot = plan.layout.get_slot(slot_name)
            if not slot or not comp_ids:
                continue
            
            for comp_id in comp_ids:
                tsx = ComponentRegistry.get_component_tsx(comp_id)
                if tsx:
                    themed_tsx = adapter.apply_to_component_tsx(tsx, comp_id)
                    comp_meta = ComponentRegistry.get_component(comp_id)
                    comp_name = comp_meta.name.replace(" ", "") if comp_meta else comp_id.title()
                    files[f"src/components/{comp_name}.tsx"] = themed_tsx
                    plan.log(f"Generated {comp_name}.tsx")
        
        # 6. 3D components
        for comp_id in plan.components_3d:
            meta = ThreeRegistry.get_component(comp_id)
            if meta:
                files[f"src/components/three/{meta.name.replace(' ', '')}.tsx"] = f"// 3D Component: {meta.name}\n// Configured for: {plan.project_name}"
        
        # 7. Package.json
        files["package.json"] = self._generate_package_json(plan)
        
        # 8. Index.html
        files["index.html"] = self._generate_index_html(plan)
        
        # 9. Main entry
        files["src/main.tsx"] = self._generate_main_tsx(plan)
        
        # 10. App component
        files["src/App.tsx"] = self._generate_app_tsx(plan)
        
        plan.tsx_files = {k: v for k, v in files.items() if k.endswith('.tsx')}
        plan.css_files = {k: v for k, v in files.items() if k.endswith('.css')}
        plan.config_files = {k: v for k, v in files.items() if k.endswith('.json') or k.endswith('.js')}
        
        plan.log(f"Generated {len(files)} files total")
        
        return files
    
    def _generate_package_json(self, plan: AssemblyPlan) -> str:
        """Generate package.json"""
        deps = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "framer-motion": "^10.16.0",
            "tailwindcss": "^3.4.0",
        }
        
        # Add component-specific deps
        for comp_id in plan.components_used:
            meta = ComponentRegistry.get_component(comp_id)
            if meta:
                for dep in meta.required_deps:
                    deps[dep] = "*"
        
        # Add 3D deps
        if plan.components_3d:
            deps["three"] = "^0.160.0"
            deps["@react-three/fiber"] = "^8.15.0"
            deps["@react-three/drei"] = "^9.92.0"
        
        package = {
            "name": plan.project_name.lower().replace(" ", "-"),
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
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0"
            }
        }
        
        return json.dumps(package, indent=2)
    
    def _generate_index_html(self, plan: AssemblyPlan) -> str:
        """Generate index.html"""
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{plan.project_name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family={plan.design_system.typography.font_family_primary.replace(' ', '+')}:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  </head>
  <body style="background: {plan.design_system.colors.background}; color: {plan.design_system.colors.text_primary};">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>"""
    
    def _generate_main_tsx(self, plan: AssemblyPlan) -> str:
        """Generate main.tsx entry point"""
        return f"""import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/tokens.css'
import './styles/animations.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

    def _generate_dynamic_content(self, plan: AssemblyPlan) -> str:
        """Prompt LLM to generate context-aware JSON string content for components"""
        provider = self._get_inference()
        if not provider or not plan.use_llm:
            return "{}"

        comp_names = [ComponentRegistry.get_component(c).name.replace(" ", "") for c in plan.components_used if ComponentRegistry.get_component(c)]
        
        system_prompt = f"""Generate a contextual UI content JSON object for a web project targeting: "{plan.prompt}"
        
You must return ONLY a valid JSON object. Do NOT wrap it in Markdown or ```json blocks.
The keys MUST be the exact component names: {', '.join(comp_names)}. 
The values MUST be objects containing deep logical layout data:
- For NavigationBars/Sidebars, use "items": [{{label, href, icon}}] arrays.
- For Hero sections, use "headline", "subheadline", "ctaText".
- For FeatureGrids or BentoBoxes, use "features": [{{title, description, icon}}] arrays.
- For Pricing, use "tiers".
Ensure the exact copywriting perfectly caters to the user's prompt! It must be high-converting and professional.
"""
        try:
            result = provider.generate(prompt=system_prompt, role="planning", temperature=0.7, max_tokens=1500)
            if result.success and result.text:
                text = result.text.strip()
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0 and end > start:
                    return text[start:end]
        except Exception as e:
            logger.warning(f"Failed to generate dynamic UI content: {e}")
            
        return "{}"
    
    def _generate_app_tsx(self, plan: AssemblyPlan) -> str:
        """Generate App.tsx with layout and components"""
        
        layout_type = plan.layout.layout_type.value
        layout_component = f"{layout_type.capitalize()}Layout"
        
        # Hydrate dynamic JSON properties
        dynamic_json_str = self._generate_dynamic_content(plan)
        
        # Build slot props
        slot_props = []
        import_lines = set()
        for slot_name, comp_ids in plan.slot_assignments.items():
            if not comp_ids:
                continue
            comp_names = []
            for comp_id in comp_ids:
                meta = ComponentRegistry.get_component(comp_id)
                if meta:
                    comp_names.append(meta.name.replace(" ", ""))
            if comp_names:
                # Spread the generated contextual JSON properties explicitly bypassing internal tsx lint bounds
                slot_props.append(f"            {slot_name}Content={{<>{' '.join(f'<{n} {{...(dynamicProps.{n} || {{}})}} />' for n in comp_names)}</>}}")
                for n in comp_names:
                    import_lines.add(f"import {{ {n} }} from './components/{n}'")
        
        slot_props_str = "\n".join(slot_props) if slot_props else ""
        imports_str = "\n".join(sorted(import_lines))
        
        return f"""import React from 'react'
import {layout_component} from './layouts/{layout_type}Layout'
import {{ ThemeProvider }} from './components/ThemeProvider'
import './styles/tokens.css'
import './styles/animations.css'
{imports_str}

// Auto-generated by NOVARYX Assembly Engine
// Project: {plan.project_name}
// Generated: {datetime.now().isoformat()}

const dynamicProps: any = {dynamic_json_str};

export default function App() {{
  return (
    <ThemeProvider>
      <{layout_component}
{slot_props_str}
      />
    </ThemeProvider>
  )
}}
"""
    
    def display_plan(self, plan: AssemblyPlan):
        """Display complete assembly plan"""
        print("\n" + "=" * 70)
        print(f"ASSEMBLY PLAN: {plan.project_name}")
        print("=" * 70)
        print(f"   Prompt: {plan.prompt[:100]}...")
        print(f"   Type: {plan.project_type}")
        print(f"   Layout: {plan.layout.layout_name}")
        print(f"   Theme: {plan.design_system.colors.primary} / {plan.design_system.mode}")
        print(f"   Animation: {plan.animation_config['page_transition']['name']}")
        
        print(f"\n   Slot Assignments:")
        for slot_name, comp_ids in plan.slot_assignments.items():
            slot = plan.layout.get_slot(slot_name)
            required = "REQ" if slot and slot.required else "OPT"
            print(f"      [{required}] {slot_name}: {', '.join(comp_ids) if comp_ids else 'EMPTY'}")
        
        print(f"\n   3D Components: {plan.components_3d if plan.components_3d else 'None'}")
        print(f"   Missing: {plan.missing_components if plan.missing_components else 'None'}")
        print(f"   Total Components: {len(plan.components_used)}")
        print("=" * 70 + "\n")


# ---- Quick assemble function ----

def quick_assemble(prompt: str) -> AssemblyPlan:
    """Quick assembly without LLM (for testing)"""
    engine = AssemblyEngine(use_llm=False)
    return engine.assemble(prompt)


# ---- Test ----

def test_assembly_engine():
    """Test the complete assembly engine"""
    
    print("\n" + "=" * 70)
    print("ASSEMBLY ENGINE TEST")
    print("=" * 70)
    
    engine = AssemblyEngine(use_llm=False)
    
    test_prompts = [
        "Build a dark purple SaaS dashboard with analytics, user management, and glassmorphism",
        "Create a modern landing page for an AI startup with 3D hero and pricing",
    ]
    
    for prompt in test_prompts:
        plan = engine.assemble(prompt)
        engine.display_plan(plan)
        
        # Generate files
        files = engine.generate_project_files(plan)
        print(f"\nGenerated {len(files)} files:")
        for filepath in sorted(files.keys()):
            size = len(files[filepath])
            print(f"   {filepath} ({size} bytes)")
    
    print("\nDONE: Assembly Engine test complete")
    
    return engine


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_assembly_engine()