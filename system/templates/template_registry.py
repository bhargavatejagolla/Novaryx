"""
NOVARYX - Template Registry
Central registry for all templates. Syncs disk files with ChromaDB.
"""

import os
import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger("novaryx.template_registry")


@dataclass
class TemplateFile:
    """Represents a single file within a template"""
    relative_path: str
    file_type: str  # "page", "component", "style", "config", "hook", "util"
    description: str
    is_required: bool = True
    can_be_modified: bool = True
    modification_rules: List[str] = field(default_factory=list)


@dataclass
class Template:
    """Complete template definition"""
    template_id: str
    name: str
    description: str
    version: str
    project_type: str
    path: str
    pages: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    tech_stack: List[str] = field(default_factory=list)
    files: List[TemplateFile] = field(default_factory=list)
    file_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "project_type": self.project_type,
            "path": self.path,
            "pages": self.pages,
            "components": self.components,
            "features": self.features,
            "tech_stack": self.tech_stack,
            "file_count": len(self.files),
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class TemplateRegistry:
    """
    Manages all templates in the NOVARYX system.
    
    Responsibilities:
    1. Discover templates on disk
    2. Validate template structure
    3. Index into ChromaDB for RAG
    4. Provide templates for generation
    5. Track versions and updates
    """
    
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            novaryx_root = Path.home() / "novaryx"
            templates_dir = str(novaryx_root / "system" / "templates")
        
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Template type directories
        self.template_types = [
            "saas_dashboard",
            "saas_landing",
            "ecommerce",
            "portfolio",
            "blog",
            "admin_panel",
            "social_app",
            "documentation",
            "auth_system",
            "marketing_site"
        ]
        
        # Create type directories
        for ttype in self.template_types:
            (self.templates_dir / ttype).mkdir(exist_ok=True)
        
        # Registry file
        self.registry_file = self.templates_dir / "template_registry.json"
        
        # Loaded templates
        self.templates: Dict[str, Template] = {}
        
        # Load registry
        self._load_registry()
        
        logger.info(f"TemplateRegistry initialized at: {self.templates_dir}")
    
    def _load_registry(self):
        """Load template registry from disk"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r") as f:
                    data = json.load(f)
                
                for template_data in data.get("templates", []):
                    template = Template(**template_data)
                    self.templates[template.template_id] = template
                
                logger.info(f"Loaded {len(self.templates)} templates from registry")
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")
                self.templates = {}
        else:
            logger.info("No existing registry found, starting fresh")
            self._save_registry()
    
    def _save_registry(self):
        """Save template registry to disk"""
        try:
            data = {
                "version": "1.0.0",
                "updated_at": datetime.now().isoformat(),
                "template_count": len(self.templates),
                "templates": [t.to_dict() for t in self.templates.values()]
            }
            
            with open(self.registry_file, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Registry saved: {len(self.templates)} templates")
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def register_template(
        self,
        template_id: str,
        name: str,
        description: str,
        project_type: str,
        version: str = "1.0.0",
        pages: List[str] = None,
        components: List[str] = None,
        features: List[str] = None,
        tech_stack: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Template:
        """
        Register a new template or update existing one.
        
        Args:
            template_id: Unique template identifier
            name: Human-readable name
            description: What this template is for
            project_type: Type of project (saas, ecommerce, etc.)
            version: Template version
            pages: List of page names
            components: List of component names
            features: List of features
            tech_stack: Technology stack used
            metadata: Additional metadata
        
        Returns:
            Registered Template object
        """
        # Template path
        template_path = self.templates_dir / project_type / template_id
        template_path.mkdir(parents=True, exist_ok=True)
        
        # Create or update template
        if template_id in self.templates:
            template = self.templates[template_id]
            template.name = name
            template.description = description
            template.version = version
            template.updated_at = datetime.now().isoformat()
        else:
            template = Template(
                template_id=template_id,
                name=name,
                description=description,
                version=version,
                project_type=project_type,
                path=str(template_path),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        
        template.pages = pages or template.pages
        template.components = components or template.components
        template.features = features or template.features
        template.tech_stack = tech_stack or template.tech_stack
        template.metadata = metadata or template.metadata
        
        # Scan for files
        template.files = self._scan_template_files(template_path)
        
        # Store
        self.templates[template_id] = template
        
        # Save registry
        self._save_registry()
        
        logger.info(f"Registered template: {name} ({template_id}) - {len(template.files)} files")
        
        return template
    
    def _scan_template_files(self, template_path: Path) -> List[TemplateFile]:
        """Scan template directory for files"""
        files = []
        
        if not template_path.exists():
            return files
        
        for file_path in template_path.rglob("*"):
            if file_path.is_file():
                # Skip hidden files and config
                if file_path.name.startswith("."):
                    continue
                if file_path.name in ["template_config.json", "registry.json"]:
                    continue
                
                rel_path = file_path.relative_to(template_path)
                
                # Determine file type
                file_type = self._classify_file(file_path)
                
                template_file = TemplateFile(
                    relative_path=str(rel_path),
                    file_type=file_type,
                    description=f"{file_type} file: {rel_path.name}",
                    is_required=file_type in ["page", "component", "config"],
                    can_be_modified=True,
                    modification_rules=self._get_modification_rules(file_type)
                )
                
                files.append(template_file)
        
        return files
    
    def _classify_file(self, file_path: Path) -> str:
        """Classify a file by its path and extension"""
        path_str = str(file_path).lower()
        
        if "page" in path_str or path_str.endswith("page.tsx"):
            return "page"
        elif "component" in path_str:
            return "component"
        elif path_str.endswith(".css") or "style" in path_str:
            return "style"
        elif "config" in path_str or path_str.endswith("config.ts"):
            return "config"
        elif "hook" in path_str or path_str.endswith("hook.ts"):
            return "hook"
        elif "util" in path_str or "helper" in path_str:
            return "util"
        elif path_str.endswith(".json"):
            return "config"
        elif path_str.endswith(".ts") or path_str.endswith(".tsx"):
            return "component"
        else:
            return "other"
    
    def _get_modification_rules(self, file_type: str) -> List[str]:
        """Get rules for what can be modified in a file type"""
        rules = {
            "page": ["can_change_content", "can_change_layout", "cannot_remove_imports"],
            "component": ["can_change_props", "can_change_styling", "can_add_variants"],
            "style": ["can_change_colors", "can_change_spacing", "can_change_fonts"],
            "config": ["can_change_values", "cannot_change_structure"],
            "hook": ["can_change_logic", "must_keep_signature"],
            "util": ["can_modify_freely"]
        }
        return rules.get(file_type, ["can_modify_freely"])
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def get_template_path(self, template_id: str) -> Optional[Path]:
        """Get the disk path for a template"""
        template = self.get_template(template_id)
        if template:
            return Path(template.path)
        return None
    
    def get_template_files(self, template_id: str) -> List[str]:
        """Get list of all file paths in a template"""
        template = self.get_template(template_id)
        if not template:
            return []
        
        template_path = Path(template.path)
        if not template_path.exists():
            return []
        
        files = []
        for file_path in template_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                files.append(str(file_path.relative_to(template_path)))
        
        return files
    
    def read_template_file(self, template_id: str, file_path: str) -> Optional[str]:
        """Read a specific file from a template"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        full_path = Path(template.path) / file_path
        if not full_path.exists():
            return None
        
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read template file: {e}")
            return None
    
    def write_template_file(
        self,
        template_id: str,
        file_path: str,
        content: str
    ) -> bool:
        """Write content to a template file"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        full_path = Path(template.path) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Written: {file_path} in template {template_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to write template file: {e}")
            return False
    
    def list_templates(self, project_type: str = None) -> List[Dict[str, Any]]:
        """List all templates, optionally filtered by type"""
        templates = []
        for template in self.templates.values():
            if project_type and template.project_type != project_type:
                continue
            templates.append(template.to_dict())
        
        return sorted(templates, key=lambda t: t["name"])
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Simple text search across template names and descriptions"""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            score = 0
            if query_lower in template.name.lower():
                score += 10
            if query_lower in template.description.lower():
                score += 5
            if query_lower in " ".join(template.features).lower():
                score += 3
            if query_lower in template.project_type.lower():
                score += 2
            
            if score > 0:
                result = template.to_dict()
                result["relevance_score"] = score
                results.append(result)
        
        return sorted(results, key=lambda r: r["relevance_score"], reverse=True)
    
    def sync_to_chromadb(self, chromadb_client) -> int:
        """
        Sync all templates to ChromaDB for RAG retrieval.
        
        Args:
            chromadb_client: ChromaDBClient instance
        
        Returns:
            Number of templates synced
        """
        synced = 0
        for template in self.templates.values():
            try:
                chromadb_client.add_template(
                    template_id=template.template_id,
                    name=template.name,
                    description=template.description,
                    metadata={
                        "type": template.project_type,
                        "pages": template.pages,
                        "features": template.features,
                        "tech_stack": template.tech_stack,
                        "version": template.version,
                        "file_count": len(template.files)
                    }
                )
                synced += 1
            except Exception as e:
                logger.error(f"Failed to sync template {template.template_id}: {e}")
        
        logger.info(f"Synced {synced} templates to ChromaDB")
        return synced
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template from registry and disk"""
        template = self.get_template(template_id)
        if not template:
            return False
        
        # Remove from disk
        template_path = Path(template.path)
        if template_path.exists():
            shutil.rmtree(template_path, ignore_errors=True)
        
        # Remove from registry
        del self.templates[template_id]
        self._save_registry()
        
        logger.info(f"Deleted template: {template_id}")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get template statistics"""
        stats = {
            "total_templates": len(self.templates),
            "by_type": {},
            "total_files": 0,
            "total_pages": 0,
            "total_components": 0
        }
        
        for template in self.templates.values():
            ptype = template.project_type
            if ptype not in stats["by_type"]:
                stats["by_type"][ptype] = 0
            stats["by_type"][ptype] += 1
            stats["total_files"] += len(template.files)
            stats["total_pages"] += len(template.pages)
            stats["total_components"] += len(template.components)
        
        return stats
    
    def display_registry(self):
        """Display template registry overview"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("📁 TEMPLATE REGISTRY")
        print("=" * 60)
        print(f"   Templates: {stats['total_templates']}")
        print(f"   Total Files: {stats['total_files']}")
        print(f"   Total Pages: {stats['total_pages']}")
        print(f"   Total Components: {stats['total_components']}")
        
        print(f"\n   By Type:")
        for ptype, count in stats["by_type"].items():
            print(f"      - {ptype}: {count}")
        
        print(f"\n   Registered Templates:")
        for template in self.templates.values():
            status = "🟢" if len(template.files) > 0 else "🟡"
            print(f"      {status} {template.name} ({template.template_id})")
            print(f"         Type: {template.project_type} | v{template.version}")
            print(f"         Files: {len(template.files)} | Pages: {len(template.pages)}")
        
        print("=" * 60 + "\n")


# ---- Test ----

def test_registry():
    """Test the template registry"""
    
    print("\n" + "=" * 60)
    print("🧪 TEMPLATE REGISTRY TEST")
    print("=" * 60)
    
    registry = TemplateRegistry()
    
    # Register sample templates
    print("\n📝 Registering sample templates...")
    
    registry.register_template(
        template_id="modern_saas_dash",
        name="Modern SaaS Dashboard",
        description="Complete SaaS dashboard with analytics, dark mode, and glassmorphism UI",
        project_type="saas_dashboard",
        version="1.0.0",
        pages=["dashboard", "analytics", "users", "settings", "billing", "profile"],
        components=["sidebar", "navbar", "charts", "data_table", "stats_card"],
        features=["authentication", "charts", "dark_mode", "responsive", "notifications"],
        tech_stack=["react", "typescript", "tailwind", "recharts", "framer_motion"]
    )
    
    registry.register_template(
        template_id="startup_landing_pro",
        name="Startup Landing Pro",
        description="High-conversion landing page with 3D hero, animations, and pricing",
        project_type="saas_landing",
        version="1.0.0",
        pages=["hero", "features", "pricing", "testimonials", "cta"],
        components=["3d_hero", "feature_card", "pricing_table", "testimonial_carousel"],
        features=["3d_hero", "animations", "pricing", "newsletter", "contact_form"],
        tech_stack=["react", "typescript", "tailwind", "three_js", "framer_motion"]
    )
    
    registry.register_template(
        template_id="admin_panel_lite",
        name="Admin Panel Lite",
        description="Lightweight admin panel with CRUD, tables, and role management",
        project_type="admin_panel",
        version="1.0.0",
        pages=["dashboard", "users", "roles", "settings", "audit_log"],
        components=["data_table", "crud_form", "role_manager", "activity_log"],
        features=["crud_operations", "role_management", "data_tables", "file_upload"],
        tech_stack=["react", "typescript", "tailwind", "tanstack_table"]
    )
    
    # Display registry
    registry.display_registry()
    
    # Test search
    print("🔍 Search: 'dashboard':")
    results = registry.search_templates("dashboard")
    for r in results:
        print(f"   - {r['name']} (score: {r['relevance_score']})")
    
    # Test listing
    print(f"\n📋 All templates: {len(registry.list_templates())}")
    print(f"📋 SaaS templates: {len(registry.list_templates('saas_dashboard'))}")
    
    print("\n✅ Template Registry test complete")
    
    return registry


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_registry()