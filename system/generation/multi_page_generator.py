"""
NOVARYX - Multi-Page Generator
Complete multi-page app generation orchestrator.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .route_generator import RouteGenerator
from .page_generator import PageGenerator
from .navigation_generator import NavigationGenerator
from .auth_guard_generator import AuthGuardGenerator
try:
    from .llm_page_generator import get_page_generator
    _LLM_PAGE_GEN_AVAILABLE = True
except ImportError:
    _LLM_PAGE_GEN_AVAILABLE = False

logger = logging.getLogger("novaryx.multi_page")


@dataclass
class GeneratedApp:
    """Complete generated application"""
    app_name: str
    pages: List[Dict]
    files: Dict[str, str]
    routes: List[Dict]
    has_auth: bool
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MultiPageGenerator:
    """
    Generates complete multi-page React applications.
    
    Takes parsed page specs → produces all files needed.
    """
    
    def __init__(self):
        self.route_gen = RouteGenerator()
        self.page_gen = PageGenerator()
        self.nav_gen = NavigationGenerator()
        self.auth_gen = AuthGuardGenerator()
        self.repair_orchestrator = None  # Will be injected by e2e
    
    def set_repair_orchestrator(self, orchestrator):
        self.repair_orchestrator = orchestrator
        
    def set_contract_engine(self, engine):
        self.contract_engine = engine

    def _emit_telemetry(self, module_id: str, status: str, trust: float = 1.0):
        """Internal helper to emit telemetry via e2e callback if available."""
        if hasattr(self, 'telemetry_callback') and self.telemetry_callback:
            self.telemetry_callback(module_id, status, trust)
    
    def generate(self, project_spec, telemetry_callback: Optional[callable] = None, use_sandbox: bool = True, contract_engine: Optional[Any] = None) -> GeneratedApp:
        """
        Generate complete multi-page app from project spec.
        
        Args:
            project_spec: ProjectSpec from Intent Parser
            telemetry_callback: Optional function(module_id, status, trust)
            use_sandbox: If True, generates into a sandbox context first
            contract_engine: Optional ContractEngine for type injection
        
        Returns:
            GeneratedApp with all files
        """
        self.telemetry_callback = telemetry_callback
        self.use_sandbox = use_sandbox
        self.contract_engine = contract_engine
        self.sandbox_files: Dict[str, str] = {}
        
        pages = [p.to_dict() if hasattr(p, 'to_dict') else p for p in project_spec.pages]
        
        # Enforce PascalCase for component names to prevent React/Vite syntax errors
        for p in pages:
            if 'name' in p:
                raw_name = str(p['name'])
                if 'title' not in p or not p['title']:
                    p['title'] = raw_name
                # "User Management" -> "UserManagement"
                p['name'] = "".join(w.capitalize() for w in raw_name.replace("-", " ").replace("_", " ").split())
                
        app_name = project_spec.project_name if hasattr(project_spec, 'project_name') else project_spec.get('project_name', 'App')
        has_auth = project_spec.requires_authentication if hasattr(project_spec, 'requires_authentication') else project_spec.get('requires_authentication', False)
        
        print("\n" + "=" * 60)
        print("📄 MULTI-PAGE GENERATOR")
        print("=" * 60)
        print(f"   App: {app_name}")
        print(f"   Pages: {len(pages)}")
        print(f"   Auth: {'Yes' if has_auth else 'No'}")
        
        files: Dict[str, str] = {}
        
        # Step 1: Generate pages (LLM-powered if available)
        print(f"\n   Generating {len(pages)} pages...")

        # Get design tokens from spec for LLM generation
        design_tokens = {}
        if hasattr(project_spec, 'design') and project_spec.design:
            ds = project_spec.design
            design_tokens = {
                "color_mode": getattr(ds, 'color_mode', 'dark'),
                "primary_color": getattr(ds, 'primary_color', '#6366f1'),
                "style": getattr(ds, 'style', 'glassmorphism'),
                "font": getattr(ds, 'font_family_primary', 'Inter'),
            }

        if _LLM_PAGE_GEN_AVAILABLE:
            llm_gen = get_page_generator()
            domain_tag = getattr(project_spec, 'industry', '') or getattr(project_spec, 'project_type', '')
            # Phase 4: Granular Incremental Generation
            # NEVER execute multiple pages in parallel on local hardware.
            # Generate one-by-one to prevent Context Overload and Timeouts.
            
            def _generate_single_page(page):
                p_name  = page.get('name', 'Page')
                p_route = page.get('route', '/')
                p_title = page.get('title', p_name)
                p_desc  = page.get('description', '')
                p_comps = page.get('components', [])
                p_auth  = page.get('requires_auth', False)

                # Get injected contracts for this page if available
                page_contracts = ""
                if self.contract_engine:
                    # Heuristic: Pages usually depend on Core Layout and Schema
                    page_contracts = self.contract_engine.get_injected_context(["core_layout", "db_schema"])

                tsx = llm_gen.generate_page(
                    page_name=p_name, route=p_route, title=p_title,
                    description=p_desc, components=p_comps,
                    requires_auth=p_auth, design_tokens=design_tokens,
                    domain=domain_tag, contracts=page_contracts
                )
                fpath = f"src/pages/{p_name}.tsx"
                return fpath, tsx

            for idx, page in enumerate(pages):
                p_name = page.get('name', 'Page')
                print(f"\n      -> Generating page {idx+1}/{len(pages)}: {p_name}")
                self._emit_telemetry(p_name, "generating")
                
                try:
                    fpath, tsx = _generate_single_page(page)
                    
                    # PROGRESSIVE VALIDATION (Surgical repair per-module)
                    if self.repair_orchestrator:
                        self._emit_telemetry(p_name, "validating")
                        tsx, fixed = self.repair_orchestrator.repair_file(fpath, tsx)
                        if fixed > 0:
                            print(f"      [Repair] Surgically fixed {fixed} bugs in {fpath}")
                    
                    if self.use_sandbox:
                        self.sandbox_files[fpath] = tsx
                        print(f"      [Sandbox] Prepared {fpath} for promotion")
                    else:
                        files[fpath] = tsx
                        print(f"      [LLM] Generated & Locked {fpath}")
                    
                    self._emit_telemetry(p_name, "frozen")
                    # Simulate small pause to cool down GPU/Memory
                    import time; time.sleep(2)
                except Exception as e:
                    print(f"      [LLM Error] Failed to generate page: {e}")
                    self._emit_telemetry(p_name, "error", 0.0)

        # Final Promotion from Sandbox
        if self.use_sandbox:
            print(f"\n   Promoting {len(self.sandbox_files)} files from sandbox to project...")
            files.update(self.sandbox_files)
        else:
            page_files = self.page_gen.generate_pages_from_spec(pages)
            files.update(page_files)
            for f in page_files:
                print(f"      [template] {f}")
        
        # Step 2: Generate App.tsx with routing
        print(f"\n   Generating App.tsx with routing...")
        layout = project_spec.project_type if hasattr(project_spec, 'project_type') else project_spec.get('project_type', 'saas_dashboard')
        layout_map = {
            "saas_dashboard": "DashboardLayout",
            "landing_page": "LandingLayout",
            "ecommerce": "EcommerceLayout",
            "admin_panel": "AdminLayout",
            "portfolio": "PortfolioLayout",
        }
        layout_component = layout_map.get(layout, "DashboardLayout")
        
        files["src/App.tsx"] = self.route_gen.generate_app_tsx(
            pages=pages,
            has_auth=has_auth,
            layout_component=layout_component
        )
        print(f"      src/App.tsx")
        
        # Step 3: Generate auth files if needed
        if has_auth:
            print(f"\n   Generating auth system...")
            files["src/components/ProtectedRoute.tsx"] = self.auth_gen.generate_protected_route()
            files["src/hooks/useAuth.tsx"] = self.auth_gen.generate_use_auth_hook()
            files["src/pages/Login.tsx"] = self.auth_gen.generate_login_page()
            files["src/pages/Register.tsx"] = self.auth_gen.generate_login_page() # Placeholder, you can upgrade auth_gen later
            print(f"      src/components/ProtectedRoute.tsx")
            print(f"      src/hooks/useAuth.tsx")
            print(f"      src/pages/Login.tsx")
            print(f"      src/pages/Register.tsx")
        
        # Step 4: Generate utility pages
        files["src/pages/Loading.tsx"] = self.page_gen.generate_loading_page()
        files["src/pages/Error.tsx"] = self.page_gen.generate_error_page()
        print(f"      src/pages/Loading.tsx")
        print(f"      src/pages/Error.tsx")
        
        # Step 5: Generate route types
        files["src/types/routes.ts"] = self.route_gen.generate_route_types(pages)
        print(f"      src/types/routes.ts")
        
        total_files = len(files)
        print(f"\n   ✅ Generated {total_files} files")
        print("=" * 60)
        
        return GeneratedApp(
            app_name=app_name,
            pages=pages,
            files=files,
            routes=pages,
            has_auth=has_auth
        )
    
    def merge_with_existing(self, generated: GeneratedApp, existing_files: Dict[str, str]) -> Dict[str, str]:
        """Merge generated pages with existing project files"""
        merged = dict(existing_files)
        
        # Add only files that don't already exist
        for filepath, content in generated.files.items():
            if filepath not in merged:
                merged[filepath] = content
            elif filepath == "src/App.tsx":
                # Always update App.tsx with routing
                merged[filepath] = content
        
        return merged


# ---- Quick generate ----

def generate_multi_page_app(project_spec) -> GeneratedApp:
    """Quick multi-page generation"""
    generator = MultiPageGenerator()
    return generator.generate(project_spec)


# ---- Test ----

def test_multi_page_generator():
    """Test multi-page generation"""
    from system.intelligence.intent_schema import ProjectSpec, PageSpec, DesignSpec
    
    print("\n" + "=" * 60)
    print("🧪 MULTI-PAGE GENERATOR TEST")
    print("=" * 60)
    
    # Create test spec
    spec = ProjectSpec(
        project_name="TestApp",
        project_type="saas_dashboard",
        requires_authentication=True,
        pages=[
            PageSpec(name="Dashboard", route="/", title="Dashboard", description="Main overview", components=["StatsCard", "ChartWidget"], requires_auth=True),
            PageSpec(name="Analytics", route="/analytics", title="Analytics", description="Detailed analytics", components=["ChartWidget", "DataTable"], requires_auth=True),
            PageSpec(name="Users", route="/users", title="User Management", description="Manage users", components=["DataTable"], requires_auth=True),
            PageSpec(name="Settings", route="/settings", title="Settings", description="App settings", components=["SettingsPanel"], requires_auth=True),
        ]
    )
    
    generator = MultiPageGenerator()
    app = generator.generate(spec)
    
    print(f"\n   Files generated: {len(app.files)}")
    for f in sorted(app.files.keys()):
        print(f"      {f}")
    
    # Show sample
    if "src/App.tsx" in app.files:
        print(f"\n   Sample App.tsx (first 400 chars):")
        print(f"   {app.files['src/App.tsx'][:400]}...")
    
    print("\n✅ Multi-Page Generator test complete")
    
    return app


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_multi_page_generator()