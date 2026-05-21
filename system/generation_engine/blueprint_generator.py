"""
NOVARYX - System Blueprint Generator (Phase 3)
Architecture-first generation. Plans the system before writing any code.
Generates the sitemap, backend architecture map, API architecture, DB schema, and state management plan.
"""

import logging
from typing import Dict, Any, Optional
from system.intelligence.intent_schema import ProjectSpec

logger = logging.getLogger("novaryx.blueprint_generator")

class BlueprintGenerator:
    """
    Generates a complete system blueprint prior to any file generation.
    Connects to the Lead Architect Agent eventually.
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self._inference = None

    def _get_inference(self):
        if self._inference is None:
            try:
                from system.inference.provider_factory import get_provider
                self._inference = get_provider()
            except Exception as e:
                logger.warning(f"Inference unavailable in blueprint generator: {e}")
        return self._inference

    def generate_blueprint(self, spec: ProjectSpec, project_graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the system blueprint based on the parsed project spec and current graph.
        """
        logger.info(f"Generating Blueprint for Project: {spec.project_name}")
        
        blueprint = {
            "sitemap": self._generate_sitemap(spec),
            "database_schema": self._generate_db_schema(spec),
            "api_architecture": self._generate_api_architecture(spec),
            "state_management": self._plan_state_management(spec),
            "smart_defaults": self._inject_smart_defaults(spec)
        }
        
        logger.info("Blueprint generation complete.")
        return blueprint

    def _generate_sitemap(self, spec: ProjectSpec) -> Dict[str, Any]:
        """Map out the complete route hierarchy."""
        sitemap = {"routes": []}
        for page in spec.pages:
            sitemap["routes"].append({
                "path": page.route,
                "components": page.components,
                "requires_auth": page.requires_auth,
                "layout": "dashboard" if not page.is_landing else "landing"
            })
        return sitemap

    def _generate_db_schema(self, spec: ProjectSpec) -> Dict[str, Any]:
        """Plan the database schema based on features requested."""
        schema = {"collections": []}
        
        if spec.requires_authentication:
            schema["collections"].append({
                "name": "users",
                "fields": ["email", "passwordHash", "role", "avatarUrl"]
            })
            
        for model in spec.data_models:
            schema["collections"].append({
                "name": model.name,
                "fields": model.fields,
                "relationships": model.relationships
            })
            
        return schema

    def _generate_api_architecture(self, spec: ProjectSpec) -> Dict[str, Any]:
        """Define required API endpoints."""
        apis = {"endpoints": []}
        if spec.requires_authentication:
            apis["endpoints"].extend([
                {"method": "POST", "route": "/api/auth/login", "purpose": "Authenticate user"},
                {"method": "POST", "route": "/api/auth/register", "purpose": "Create new user"}
            ])
            
        # Add CRUD endpoints for data models
        for model in spec.data_models:
            resource = model.name.lower()
            apis["endpoints"].extend([
                {"method": "GET", "route": f"/api/{resource}", "purpose": f"List {resource}"},
                {"method": "POST", "route": f"/api/{resource}", "purpose": f"Create {resource}"}
            ])
            
        return apis

    def _plan_state_management(self, spec: ProjectSpec) -> str:
        """Decide on state management (Zustand, React Context, Redux)."""
        if spec.complexity in ["complex", "enterprise"]:
            return "zustand"
        return "react-context"

    def _inject_smart_defaults(self, spec: ProjectSpec) -> Dict[str, Any]:
        """Phase 11: Inject smart defaults automatically."""
        return {
            "seo_basics": True,
            "dark_mode_toggle": spec.design.color_mode in ["dark", "auto"],
            "toast_notifications": True,
            "error_boundaries": True,
            "skeleton_loaders": True
        }
