"""
NOVARYX - Portfolio Layout
Full-bleed creative layout with 3D canvas support.

Structure:
┌──────────────────────────────────────┐
│              NAVBAR                  │
├──────────────────────────────────────┤
│              HERO                    │
│          (3D Canvas BG)              │
├──────────────────────────────────────┤
│           PROJECTS                   │
│         (Masonry Grid)               │
├──────────────────────────────────────┤
│            ABOUT                     │
├──────────────────────────────────────┤
│           SKILLS                     │
├──────────────────────────────────────┤
│           CONTACT                    │
├──────────────────────────────────────┤
│           FOOTER                     │
└──────────────────────────────────────┘
"""

from .base_layout import BaseLayout, LayoutSlot, LayoutConfig, LayoutType


class PortfolioLayout(BaseLayout):
    """Creative portfolio layout with 3D support"""
    
    @property
    def layout_type(self) -> LayoutType:
        return LayoutType.PORTFOLIO
    
    @property
    def layout_name(self) -> str:
        return "Portfolio Layout"
    
    @property
    def description(self) -> str:
        return "Creative portfolio with 3D hero, project showcase, smooth scrolling, and contact form."
    
    def _define_slots(self):
        
        self.add_slot(LayoutSlot(
            name="navbar",
            description="Floating navigation bar",
            allowed_component_types=["navbar", "logo", "nav_links"],
            required=True,
            max_components=3
        ))
        
        self.add_slot(LayoutSlot(
            name="hero",
            description="Hero section with name, title, and optional 3D scene",
            allowed_component_types=["hero", "hero_3d", "hero_canvas", "particle_system"],
            required=True,
            max_components=3,
            default_component="hero_3d"
        ))
        
        self.add_slot(LayoutSlot(
            name="projects",
            description="Project showcase grid",
            allowed_component_types=["project_grid", "project_card", "masonry_grid", "carousel"],
            required=True,
            max_components=20
        ))
        
        self.add_slot(LayoutSlot(
            name="about",
            description="About section with bio and skills",
            allowed_component_types=["about_section", "skill_bars", "timeline", "stats"],
            required=False,
            max_components=4
        ))
        
        self.add_slot(LayoutSlot(
            name="contact",
            description="Contact form section",
            allowed_component_types=["contact_form", "social_links", "map"],
            required=False,
            max_components=3
        ))
        
        self.add_slot(LayoutSlot(
            name="footer",
            description="Minimal footer",
            allowed_component_types=["footer", "social_links"],
            required=True,
            max_components=2
        ))