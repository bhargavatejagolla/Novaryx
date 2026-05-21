"""
NOVARYX - Admin Panel Layout
Sidebar + Header + Content Area + Drawer

Grid Structure:
┌──────────┬──────────────────────────────┐
│          │                              │
│  SIDEBAR │       HEADER                 │
│          ├──────────────────────────────┤
│          │                              │
│          │       CONTENT                │
│          │                              │
└──────────┴──────────────────────────────┘
           ┌──────────────────────────────┐
           │       DRAWER (slide-in)      │
           └──────────────────────────────┘
"""

from .base_layout import BaseLayout, LayoutSlot, LayoutConfig, LayoutType


class AdminLayout(BaseLayout):
    """Admin panel layout for management interfaces"""
    
    @property
    def layout_type(self) -> LayoutType:
        return LayoutType.ADMIN
    
    @property
    def layout_name(self) -> str:
        return "Admin Panel Layout"
    
    @property
    def description(self) -> str:
        return "Admin dashboard with sidebar navigation, data tables, CRUD forms, and slide-in drawers."
    
    def _define_slots(self):
        
        self.add_slot(LayoutSlot(
            name="sidebar",
            description="Admin navigation sidebar",
            allowed_component_types=["sidebar", "navigation", "admin_menu"],
            required=True,
            max_components=5
        ))
        
        self.add_slot(LayoutSlot(
            name="header",
            description="Admin header with breadcrumbs and actions",
            allowed_component_types=["header", "breadcrumbs", "action_buttons", "search_bar"],
            required=True,
            max_components=5
        ))
        
        self.add_slot(LayoutSlot(
            name="content",
            description="Main content area for tables, forms, dashboards",
            allowed_component_types=["data_table", "crud_form", "stats_grid", "chart", "audit_log"],
            required=True,
            max_components=3
        ))
        
        self.add_slot(LayoutSlot(
            name="drawer",
            description="Slide-in drawer for forms and details",
            allowed_component_types=["crud_form", "detail_panel", "settings_form", "upload_form"],
            required=False,
            max_components=2
        ))
        
        self.add_slot(LayoutSlot(
            name="footer",
            description="Admin footer with status info",
            allowed_component_types=["footer", "status_bar", "version_info"],
            required=False,
            max_components=3
        ))