"""
NOVARYX - 3D Component Systems
Pre-built, parameterized Three.js components for React Three Fiber.

The AI NEVER generates raw Three.js code.
It selects a pre-built system and configures its parameters.

Each component:
  - Uses React Three Fiber + Drei
  - Auto-detects GPU capability
  - Falls back to CSS if WebGL unavailable
  - Has mobile-friendly polygon counts
  - Accepts theme colors from Design Token Engine
"""

from .three_registry import ThreeRegistry, ThreeComponentMeta
from .globe_scene import generate_globe_tsx, generate_globe_config
from .particle_field import generate_particle_field_tsx, generate_particle_config
from .card_3d import generate_card_3d_tsx
from .hero_scene import generate_hero_scene_tsx
from .wave_background import generate_wave_background_tsx

__all__ = [
    "ThreeRegistry",
    "ThreeComponentMeta",
    "generate_globe_tsx",
    "generate_globe_config",
    "generate_particle_field_tsx",
    "generate_particle_config",
    "generate_card_3d_tsx",
    "generate_hero_scene_tsx",
    "generate_wave_background_tsx",
]
