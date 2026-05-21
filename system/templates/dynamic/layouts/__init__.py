"""
NOVARYX - Dynamic Layout System
Responsive layout shells with named slots for component assembly.

Each layout is a skeleton that components plug into dynamically.
The AI selects which layout and which components based on the prompt.
"""
"""
NOVARYX - Dynamic Template System
Complete prompt-driven application generation.

Modules:
  1.1 Design Token Engine     - Generates complete design system from prompt
  1.2 Base Layout System      - 5 responsive layouts with named slots
  1.3-1.4 Component Library   - 16 production components
  1.5 3D Component Systems    - 5 pre-built Three.js scenes
  1.6 Animation System        - 17 animation presets
  1.7 Assembly Engine         - Orchestrates all subsystems
  1.8 Theme Adaptation Engine - Deep theme injection
  1.9 Template Intelligence   - LLM + RAG smart selection
  1.10 End-to-End Generation  - Prompt → Complete Project
"""

from .base_layout import BaseLayout, LayoutSlot, LayoutType
from .dashboard_layout import DashboardLayout
from .landing_layout import LandingLayout
from .ecommerce_layout import EcommerceLayout
from .admin_layout import AdminLayout
from .portfolio_layout import PortfolioLayout
from .layout_registry import LayoutRegistry, get_layout_for_project
__all__ = [
    "BaseLayout",
    "LayoutSlot",
    "LayoutType",
    "DashboardLayout",
    "LandingLayout",
    "EcommerceLayout",
    "AdminLayout",
    "PortfolioLayout",
    "LayoutRegistry",
    "get_layout_for_project",
]

