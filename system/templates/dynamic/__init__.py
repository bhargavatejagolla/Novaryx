"""
NOVARYX - Dynamic Template System
Prompt-driven design token generation and component assembly.

Flow:
  User Prompt → DesignTokenEngine → Complete Design System
  Design System → Component Assembly → Themed Pages
  Themed Pages → Verification → Production Output

No static templates. Everything adapts to the prompt.
"""

from .design_token_engine import DesignTokenEngine
from .token_definitions import (
    ColorTokens,
    TypographyTokens,
    SpacingTokens,
    EffectTokens,
    AnimationTokens,
    DesignSystem
)
from .theme_presets import ThemePresets, get_smart_defaults

__all__ = [
    "DesignTokenEngine",
    "ColorTokens",
    "TypographyTokens",
    "SpacingTokens",
    "EffectTokens",
    "AnimationTokens",
    "DesignSystem",
    "ThemePresets",
    "get_smart_defaults"
]