"""
NOVARYX - Intent Validator
Validates LLM output against the schema. Fixes common issues automatically.
"""

import json
import logging
from typing import Dict, Any, Tuple, List, Optional
from .intent_schema import (
    ProjectSpec, PageSpec, FeatureSpec, DesignSpec, DataModelSpec
)

logger = logging.getLogger("novaryx.intent_validator")

# Valid values for enum-like fields
VALID_PROJECT_TYPES = [
    "saas_dashboard", "landing_page", "ecommerce", "admin_panel",
    "portfolio", "blog", "social_app", "documentation", "marketing_site"
]

VALID_COMPLEXITIES = ["simple", "medium", "complex", "enterprise"]
VALID_COLOR_MODES = ["dark", "light", "auto"]
VALID_ANIMATION_LEVELS = ["subtle", "moderate", "rich", "none"]
VALID_COLORS = ["purple", "indigo", "blue", "teal", "green", "red", "orange", "pink", "cyan", "amber", "slate"]
VALID_FONTS = ["inter", "poppins", "roboto", "mono", "serif"]
VALID_PRIORITIES = ["high", "medium", "low"]


class IntentValidator:
    """
    Validates and repairs LLM-generated project specs.
    
    Ensures:
    - All required fields present
    - All values within valid ranges
    - Types are correct
    - Defaults applied where missing
    """
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate and repair a project spec dictionary.
        
        Returns:
            (is_valid, warnings, repaired_data)
        """
        warnings = []
        
        # Ensure it's a dict
        if not isinstance(data, dict):
            return False, ["Input is not a dictionary"], {}
        
        # ---- Core fields ----
        data = IntentValidator._validate_core_fields(data, warnings)
        
        # ---- Design ----
        if "design" in data and isinstance(data["design"], dict):
            data["design"] = IntentValidator._validate_design(data["design"], warnings)
        else:
            data["design"] = DesignSpec().to_dict()
            warnings.append("Missing 'design' section, using defaults")
        
        # ---- Pages ----
        if "pages" not in data or not isinstance(data["pages"], list) or len(data["pages"]) == 0:
            data["pages"] = IntentValidator._generate_default_pages(data.get("project_type", "saas_dashboard"))
            warnings.append("No pages specified, generated defaults")
        else:
            data["pages"] = [
                IntentValidator._validate_page(p, warnings) 
                for p in data["pages"]
            ]
        
        # ---- Features ----
        if "features" not in data or not isinstance(data["features"], list):
            data["features"] = []
        else:
            data["features"] = [
                IntentValidator._validate_feature(f, warnings)
                for f in data["features"]
            ]
        
        # ---- Boolean flags ----
        for flag in ["requires_authentication", "requires_database", "requires_payments",
                      "requires_file_upload", "requires_real_time", "requires_search", "requires_email"]:
            if flag not in data:
                data[flag] = False
        
        # ---- Content ----
        if "sample_content" not in data or not isinstance(data["sample_content"], dict):
            data["sample_content"] = {}
        
        # ---- Confidence ----
        if "confidence_score" not in data:
            data["confidence_score"] = 0.5
        
        is_valid = len([w for w in warnings if "CRITICAL" in w]) == 0
        
        return is_valid, warnings, data
    
    @staticmethod
    def _validate_core_fields(data: Dict, warnings: List[str]) -> Dict:
        """Validate core project fields"""
        
        # Project name
        if not data.get("project_name"):
            data["project_name"] = "NOVARYX Project"
            warnings.append("Missing project_name, using default")
        
        # Project type
        if data.get("project_type") not in VALID_PROJECT_TYPES:
            old_type = data.get("project_type", "none")
            data["project_type"] = "saas_dashboard"
            warnings.append(f"Invalid project_type '{old_type}', defaulting to saas_dashboard")
        
        # Complexity
        if data.get("complexity") not in VALID_COMPLEXITIES:
            data["complexity"] = "medium"
        
        # Confidence
        if "project_type_confidence" not in data:
            data["project_type_confidence"] = 0.5
        else:
            try:
                data["project_type_confidence"] = float(data["project_type_confidence"])
                data["project_type_confidence"] = max(0.0, min(1.0, data["project_type_confidence"]))
            except (ValueError, TypeError):
                data["project_type_confidence"] = 0.5
        
        # String defaults
        for field in ["project_description", "target_audience", "industry", "brand_name", "tagline"]:
            if field not in data:
                data[field] = ""
        
        return data
    
    @staticmethod
    def _validate_design(design: Dict, warnings: List[str]) -> Dict:
        """Validate design specification"""
        
        if design.get("color_mode") not in VALID_COLOR_MODES:
            design["color_mode"] = "dark"
        
        if design.get("primary_color_name") not in VALID_COLORS:
            design["primary_color_name"] = "indigo"
        
        if design.get("accent_color_name") not in VALID_COLORS:
            design["accent_color_name"] = "cyan"
        
        if design.get("font_preference") not in VALID_FONTS:
            design["font_preference"] = "inter"
        
        if design.get("animation_level") not in VALID_ANIMATION_LEVELS:
            design["animation_level"] = "moderate"
        
        # Booleans
        for bool_field in ["glassmorphism", "three_d_enabled"]:
            if bool_field not in design:
                design[bool_field] = False
        
        # Lists
        if "three_d_elements" not in design or not isinstance(design.get("three_d_elements"), list):
            design["three_d_elements"] = []
        
        # String defaults
        for str_field in ["font_style", "border_radius", "density", "primary_color_hex", "accent_color_hex"]:
            if str_field not in design:
                design[str_field] = ""
        
        return design
    
    @staticmethod
    def _validate_page(page: Dict, warnings: List[str]) -> Dict:
        """Validate a single page spec"""
        
        if not page.get("name"):
            page["name"] = "Page"
        
        if not page.get("route"):
            page["route"] = f"/{page['name'].lower().replace(' ', '-')}"
        
        if not page["route"].startswith("/"):
            page["route"] = f"/{page['route']}"
        
        if not page.get("title"):
            page["title"] = page["name"]
        
        if not page.get("description"):
            page["description"] = ""
        
        if "components" not in page or not isinstance(page.get("components"), list):
            page["components"] = []
        
        if "requires_auth" not in page:
            page["requires_auth"] = False
        
        if "is_landing" not in page:
            page["is_landing"] = page["route"] == "/"
        
        return page
    
    @staticmethod
    def _validate_feature(feature: Dict, warnings: List[str]) -> Dict:
        """Validate a single feature spec"""
        
        if not feature.get("name"):
            feature["name"] = "Unnamed Feature"
        
        if not feature.get("description"):
            feature["description"] = ""
        
        if feature.get("priority") not in VALID_PRIORITIES:
            feature["priority"] = "medium"
        
        for bool_field in ["requires_auth", "requires_database", "requires_3d"]:
            if bool_field not in feature:
                feature[bool_field] = False
        
        for list_field in ["components_needed", "pages_affected"]:
            if list_field not in feature or not isinstance(feature.get(list_field), list):
                feature[list_field] = []
        
        return feature
    
    @staticmethod
    def _generate_default_pages(project_type: str) -> List[Dict]:
        """Generate sensible default pages based on project type"""
        
        defaults = {
            "saas_dashboard": [
                {"name": "Dashboard", "route": "/", "title": "Dashboard", "description": "Main overview dashboard", "components": ["stats_card", "chart_widget"], "requires_auth": True, "is_landing": False},
                {"name": "Analytics", "route": "/analytics", "title": "Analytics", "description": "Detailed analytics and reports", "components": ["chart_widget", "data_table"], "requires_auth": True},
                {"name": "Settings", "route": "/settings", "title": "Settings", "description": "Account and app settings", "components": ["settings_panel"], "requires_auth": True},
            ],
            "landing_page": [
                {"name": "Home", "route": "/", "title": "Welcome", "description": "Landing page hero", "components": ["hero", "features_grid", "cta_section"], "requires_auth": False, "is_landing": True},
            ],
            "ecommerce": [
                {"name": "Shop", "route": "/", "title": "Shop", "description": "Product listing", "components": ["product_grid"], "requires_auth": False, "is_landing": True},
                {"name": "Cart", "route": "/cart", "title": "Shopping Cart", "description": "View and manage cart", "components": ["cart_sidebar"], "requires_auth": False},
                {"name": "Checkout", "route": "/checkout", "title": "Checkout", "description": "Complete purchase", "components": ["checkout_form"], "requires_auth": True},
            ],
            "admin_panel": [
                {"name": "Dashboard", "route": "/", "title": "Admin Dashboard", "description": "System overview", "components": ["stats_card", "data_table"], "requires_auth": True},
                {"name": "Users", "route": "/users", "title": "User Management", "description": "Manage users", "components": ["data_table", "crud_form"], "requires_auth": True},
                {"name": "Settings", "route": "/settings", "title": "System Settings", "description": "Configure system", "components": ["settings_panel"], "requires_auth": True},
            ],
            "portfolio": [
                {"name": "Home", "route": "/", "title": "Portfolio", "description": "Creative portfolio", "components": ["hero_3d", "project_grid"], "requires_auth": False, "is_landing": True},
                {"name": "Contact", "route": "/contact", "title": "Get in Touch", "description": "Contact form", "components": ["contact_form"], "requires_auth": False},
            ],
        }
        
        return defaults.get(project_type, defaults["landing_page"])
    
    @staticmethod
    def to_project_spec(data: Dict[str, Any]) -> ProjectSpec:
        """Convert validated dict to ProjectSpec dataclass"""
        
        design_data = data.get("design", {})
        design = DesignSpec(
            color_mode=design_data.get("color_mode", "dark"),
            primary_color_name=design_data.get("primary_color_name", "indigo"),
            primary_color_hex=design_data.get("primary_color_hex", "#6366f1"),
            accent_color_name=design_data.get("accent_color_name", "cyan"),
            accent_color_hex=design_data.get("accent_color_hex", "#06b6d4"),
            font_preference=design_data.get("font_preference", "inter"),
            font_style=design_data.get("font_style", "modern"),
            glassmorphism=design_data.get("glassmorphism", False),
            three_d_enabled=design_data.get("three_d_enabled", False),
            three_d_elements=design_data.get("three_d_elements", []),
            animation_level=design_data.get("animation_level", "moderate"),
            border_radius=design_data.get("border_radius", "medium"),
            density=design_data.get("density", "comfortable"),
        )
        
        pages = [
            PageSpec(
                name=p.get("name", "Page"),
                route=p.get("route", "/"),
                title=p.get("title", ""),
                description=p.get("description", ""),
                components=p.get("components", []),
                requires_auth=p.get("requires_auth", False),
                is_landing=p.get("is_landing", False),
            )
            for p in data.get("pages", [])
        ]
        
        features = [
            FeatureSpec(
                name=f.get("name", "Feature"),
                description=f.get("description", ""),
                priority=f.get("priority", "medium"),
                requires_auth=f.get("requires_auth", False),
                requires_database=f.get("requires_database", False),
                requires_3d=f.get("requires_3d", False),
                components_needed=f.get("components_needed", []),
                pages_affected=f.get("pages_affected", []),
            )
            for f in data.get("features", [])
        ]
        
        return ProjectSpec(
            project_name=data.get("project_name", "NOVARYX Project"),
            project_description=data.get("project_description", ""),
            project_type=data.get("project_type", "saas_dashboard"),
            project_type_confidence=data.get("project_type_confidence", 0.5),
            complexity=data.get("complexity", "medium"),
            target_audience=data.get("target_audience", "general"),
            industry=data.get("industry", "technology"),
            design=design,
            pages=pages,
            features=features,
            data_models=[],
            requires_authentication=data.get("requires_authentication", False),
            requires_database=data.get("requires_database", False),
            requires_payments=data.get("requires_payments", False),
            requires_file_upload=data.get("requires_file_upload", False),
            requires_real_time=data.get("requires_real_time", False),
            requires_search=data.get("requires_search", False),
            requires_email=data.get("requires_email", False),
            sample_content=data.get("sample_content", {}),
            brand_name=data.get("brand_name", ""),
            tagline=data.get("tagline", ""),
            raw_prompt=data.get("raw_prompt", ""),
            confidence_score=data.get("confidence_score", 0.5),
        )