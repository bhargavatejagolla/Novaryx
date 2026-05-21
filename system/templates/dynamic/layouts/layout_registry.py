"""
NOVARYX - Layout Registry
Selects the right layout based on project type and prompt.
"""

import logging
from typing import Optional, Dict, Any
from .base_layout import BaseLayout, LayoutConfig, LayoutType
from .dashboard_layout import DashboardLayout
from .landing_layout import LandingLayout
from .ecommerce_layout import EcommerceLayout
from .admin_layout import AdminLayout
from .portfolio_layout import PortfolioLayout
from .ai_startup_layout import AiStartupLayout

logger = logging.getLogger("novaryx.layout_registry")


class LayoutRegistry:
    """
    Registry of all available layouts.
    Selects the best layout for a given project type.
    """
    
    LAYOUTS = {
        LayoutType.DASHBOARD: DashboardLayout,
        LayoutType.LANDING: LandingLayout,
        LayoutType.ECOMMERCE: EcommerceLayout,
        LayoutType.ADMIN: AdminLayout,
        LayoutType.PORTFOLIO: PortfolioLayout,
        LayoutType.AI_STARTUP: AiStartupLayout,
    }
    
    # Project type to layout mapping
    PROJECT_TYPE_MAP = {
        "saas_dashboard": LayoutType.DASHBOARD,
        "dashboard": LayoutType.DASHBOARD,
        "analytics": LayoutType.DASHBOARD,
        "admin_panel": LayoutType.ADMIN,
        "admin": LayoutType.ADMIN,
        "saas_landing": LayoutType.LANDING,
        "landing": LayoutType.LANDING,
        "landing_page": LayoutType.LANDING,
        "marketing": LayoutType.LANDING,
        "ecommerce": LayoutType.ECOMMERCE,
        "store": LayoutType.ECOMMERCE,
        "shop": LayoutType.ECOMMERCE,
        "portfolio": LayoutType.PORTFOLIO,
        "creative": LayoutType.PORTFOLIO,
        "showcase": LayoutType.PORTFOLIO,
        "ai_startup": LayoutType.AI_STARTUP,
        "startup": LayoutType.AI_STARTUP,
        "ai": LayoutType.AI_STARTUP,
    }
    
    @classmethod
    def get_layout(cls, layout_type: LayoutType, config: LayoutConfig = None) -> BaseLayout:
        """Get a layout instance by type"""
        layout_class = cls.LAYOUTS.get(layout_type, DashboardLayout)
        layout_config = config or LayoutConfig(layout_type=layout_type)
        return layout_class(layout_config)
    
    @classmethod
    def get_layout_for_project(
        cls,
        project_type: str,
        config: LayoutConfig = None
    ) -> BaseLayout:
        """Get the best layout for a project type"""
        layout_type = cls.PROJECT_TYPE_MAP.get(
            project_type.lower(), LayoutType.DASHBOARD
        )
        
        logger.info(f"Layout selected: {layout_type.value} for project type '{project_type}'")
        
        return cls.get_layout(layout_type, config)
    
    @classmethod
    def get_layout_for_prompt(cls, prompt: str) -> BaseLayout:
        """Detect project type from prompt and return layout"""
        prompt_lower = prompt.lower()
        
        # Check keywords
        for keyword, layout_type in cls.PROJECT_TYPE_MAP.items():
            if keyword.replace("_", " ") in prompt_lower or keyword in prompt_lower:
                return cls.get_layout(layout_type)
        
        # Default to landing page
        return cls.get_layout(LayoutType.LANDING)
    
    @classmethod
    def list_all_layouts(cls) -> list:
        """List all available layouts"""
        layouts = []
        for layout_type, layout_class in cls.LAYOUTS.items():
            instance = layout_class()
            layouts.append({
                "type": layout_type.value,
                "name": instance.layout_name,
                "description": instance.description,
                "slots": len(instance.get_all_slots()),
                "required_slots": len(instance.get_required_slots())
            })
        return layouts
    
    @classmethod
    def display_registry(cls):
        """Display all layouts"""
        print("\n" + "=" * 60)
        print("LAYOUT REGISTRY")
        print("=" * 60)
        
        for layout_info in cls.list_all_layouts():
            print(f"\n  {layout_info['type'].upper()}")
            print(f"  Name: {layout_info['name']}")
            print(f"  Slots: {layout_info['slots']} ({layout_info['required_slots']} required)")
            print(f"  Description: {layout_info['description'][:80]}...")
        
        print("\n" + "=" * 60 + "\n")


def get_layout_for_project(project_type: str, config: LayoutConfig = None) -> BaseLayout:
    """Convenience function"""
    return LayoutRegistry.get_layout_for_project(project_type, config)


# ---- Test ----

def test_layout_system():
    """Test the layout system"""
    
    print("\n" + "=" * 60)
    print("LAYOUT SYSTEM TEST")
    print("=" * 60)
    
    # Display registry
    LayoutRegistry.display_registry()
    
    # Test layout selection
    test_cases = [
        ("saas_dashboard", "purple dashboard with analytics"),
        ("landing_page", "startup landing with 3D hero"),
        ("ecommerce", "online store with cart"),
        ("admin_panel", "admin panel with user management"),
        ("portfolio", "creative portfolio showcase"),
    ]
    
    for project_type, prompt in test_cases:
        print(f"\n{'-' * 50}")
        print(f"Project: {project_type}")
        
        layout = LayoutRegistry.get_layout_for_project(project_type)
        layout.display_layout()
        
        # Check slots
        print(f"   Required slots: {[s.name for s in layout.get_required_slots()]}")
        print(f"   Optional slots: {[s.name for s in layout.get_all_slots() if not s.required]}")
    
    print("Layout system test complete")
    
    return LayoutRegistry


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_layout_system()