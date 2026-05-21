"""
NOVARYX - Animation & Motion System
AI-configurable animation presets for the entire application.

Connected to:
  - Design Token Engine (uses animation tokens)
  - Component Registry (components use these presets)
  - Layout System (page transitions)
  
All animations are parameterized. AI selects and configures.
"""

from .animation_registry import AnimationRegistry, AnimationPreset
from .page_transitions import generate_page_transition_wrapper
from .scroll_animations import generate_scroll_reveal_component
from .micro_interactions import generate_micro_interactions_utility

__all__ = [
    "AnimationRegistry",
    "AnimationPreset",
    "generate_page_transition_wrapper",
    "generate_scroll_reveal_component",
    "generate_micro_interactions_utility",
]