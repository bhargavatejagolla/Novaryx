"""
NOVARYX - Multi-Page App Generator
Generates complete multi-page React applications with routing.

Connected to:
  - Intent Parser (reads page specs)
  - Design Token Engine (themes all pages)
  - Component Registry (page-specific components)
  - Assembly Engine (file generation)
"""

from .multi_page_generator import MultiPageGenerator, GeneratedApp
from .route_generator import RouteGenerator
from .page_generator import PageGenerator
from .navigation_generator import NavigationGenerator
from .auth_guard_generator import AuthGuardGenerator

__all__ = [
    "MultiPageGenerator",
    "GeneratedApp",
    "RouteGenerator",
    "PageGenerator",
    "NavigationGenerator",
    "AuthGuardGenerator",
]