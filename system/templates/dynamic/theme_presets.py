"""
NOVARYX - Theme Presets
Smart defaults and color science for design token generation.

Maps prompt keywords to design decisions without needing LLM.
Falls back to LLM for complex/unusual requests.
"""

from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class ColorPreset:
    """Pre-defined color palette"""
    name: str
    primary: str
    primary_light: str
    primary_dark: str
    accent: str


class ThemePresets:
    """Collection of smart defaults and keyword mappings"""
    
    # Pre-built color palettes
    COLOR_PRESETS: Dict[str, ColorPreset] = {
        "purple": ColorPreset(
            name="Purple",
            primary="#7c3aed",
            primary_light="#a78bfa",
            primary_dark="#5b21b6",
            accent="#06b6d4"
        ),
        "indigo": ColorPreset(
            name="Indigo",
            primary="#6366f1",
            primary_light="#818cf8",
            primary_dark="#4338ca",
            accent="#f59e0b"
        ),
        "blue": ColorPreset(
            name="Blue",
            primary="#3b82f6",
            primary_light="#60a5fa",
            primary_dark="#1d4ed8",
            accent="#f97316"
        ),
        "teal": ColorPreset(
            name="Teal",
            primary="#14b8a6",
            primary_light="#2dd4bf",
            primary_dark="#0d9488",
            accent="#f43f5e"
        ),
        "green": ColorPreset(
            name="Green",
            primary="#10b981",
            primary_light="#34d399",
            primary_dark="#047857",
            accent="#8b5cf6"
        ),
        "red": ColorPreset(
            name="Red",
            primary="#ef4444",
            primary_light="#f87171",
            primary_dark="#b91c1c",
            accent="#3b82f6"
        ),
        "orange": ColorPreset(
            name="Orange",
            primary="#f97316",
            primary_light="#fb923c",
            primary_dark="#c2410c",
            accent="#6366f1"
        ),
        "pink": ColorPreset(
            name="Pink",
            primary="#ec4899",
            primary_light="#f472b6",
            primary_dark="#be185d",
            accent="#06b6d4"
        ),
        "cyan": ColorPreset(
            name="Cyan",
            primary="#06b6d4",
            primary_light="#22d3ee",
            primary_dark="#0891b2",
            accent="#f59e0b"
        ),
        "amber": ColorPreset(
            name="Amber",
            primary="#f59e0b",
            primary_light="#fbbf24",
            primary_dark="#b45309",
            accent="#6366f1"
        ),
        "slate": ColorPreset(
            name="Slate",
            primary="#64748b",
            primary_light="#94a3b8",
            primary_dark="#334155",
            accent="#f59e0b"
        ),
        "zinc": ColorPreset(
            name="Zinc",
            primary="#71717a",
            primary_light="#a1a1aa",
            primary_dark="#3f3f46",
            accent="#14b8a6"
        ),
    }
    
    # Mode configurations
    MODE_CONFIGS = {
        "dark": {
            "background": "#09090b",
            "background_secondary": "#18181b",
            "surface": "#09090b",
            "text_primary": "#fafafa",
            "text_secondary": "#a1a1aa",
        },
        "light": {
            "background": "#f8fafc",
            "background_secondary": "#f1f5f9",
            "surface": "#ffffff",
            "text_primary": "#0f172a",
            "text_secondary": "#475569",
        }
    }
    
    # Font pairings
    FONT_PAIRS = {
        "modern": ("Inter", "Inter"),
        "classic": ("Merriweather", "Lato"),
        "tech": ("JetBrains Mono", "Inter"),
        "minimal": ("DM Sans", "DM Sans"),
        "playful": ("Poppins", "Poppins"),
        "elegant": ("Playfair Display", "Lato"),
        "corporate": ("Roboto", "Roboto"),
    }
    
    # Keyword mapping
    KEYWORD_MAP = {
        # Colors
        "purple": "purple", "violet": "purple", "lavender": "purple",
        "indigo": "indigo",
        "blue": "blue", "ocean": "blue", "sky": "blue",
        "teal": "teal", "turquoise": "teal",
        "green": "green", "emerald": "green", "forest": "green",
        "red": "red", "crimson": "red", "rose": "red",
        "orange": "orange", "coral": "orange",
        "pink": "pink", "magenta": "pink",
        "cyan": "cyan",
        "amber": "amber", "gold": "amber", "yellow": "amber",
        "slate": "slate", "gray": "slate", "grey": "slate",
        
        # Modes
        "dark": "dark", "night": "dark", "midnight": "dark",
        "light": "light", "white": "light", "bright": "light",
        
        # Styles
        "glass": "glassmorphism", "glassmorphism": "glassmorphism",
        "frosted": "glassmorphism", "translucent": "glassmorphism",
        "flat": "flat", "minimal": "minimal",
        "gradient": "gradient", "colorful": "gradient",
        "3d": "three_d_enabled", "three": "three_d_enabled", "dimensional": "three_d_enabled",
        
        # Fonts
        "inter": ("modern", "Inter"),
        "poppins": ("playful", "Poppins"),
        "roboto": ("corporate", "Roboto"),
        "mono": ("tech", "JetBrains Mono"),
        "serif": ("classic", "Merriweather"),
    }
    
    @classmethod
    def detect_color(cls, prompt: str) -> str:
        """Detect which color preset to use from prompt"""
        prompt_lower = prompt.lower()
        
        # Check for exact matches
        for keyword, preset_name in cls.KEYWORD_MAP.items():
            if keyword in prompt_lower and preset_name in cls.COLOR_PRESETS:
                return preset_name
        
        return "indigo"  # Default
    
    @classmethod
    def detect_mode(cls, prompt: str) -> str:
        """Detect dark or light mode from prompt"""
        prompt_lower = prompt.lower()
        
        if any(w in prompt_lower for w in ["light", "white", "bright", "day"]):
            return "light"
        
        return "dark"  # Default to dark
    
    @classmethod
    def detect_style(cls, prompt: str) -> list:
        """Detect style preferences from prompt"""
        prompt_lower = prompt.lower()
        styles = []
        
        if any(w in prompt_lower for w in ["glass", "glassmorphism", "frosted", "translucent"]):
            styles.append("glassmorphism")
        
        if any(w in prompt_lower for w in ["3d", "three", "dimensional"]):
            styles.append("three_d_enabled")
        
        if any(w in prompt_lower for w in ["gradient", "colorful"]):
            styles.append("gradient")
        
        if "minimal" in prompt_lower:
            styles.append("minimal")
        
        return styles
    
    @classmethod
    def detect_font(cls, prompt: str) -> Tuple[str, str]:
        """Detect font preference from prompt"""
        prompt_lower = prompt.lower()
        
        if "inter" in prompt_lower:
            return cls.FONT_PAIRS["modern"]
        if "poppins" in prompt_lower:
            return cls.FONT_PAIRS["playful"]
        if "roboto" in prompt_lower:
            return cls.FONT_PAIRS["corporate"]
        if "mono" in prompt_lower or "jetbrain" in prompt_lower:
            return cls.FONT_PAIRS["tech"]
        if "serif" in prompt_lower or "merriweather" in prompt_lower:
            return cls.FONT_PAIRS["classic"]
        if "elegant" in prompt_lower or "playfair" in prompt_lower:
            return cls.FONT_PAIRS["elegant"]
        
        return cls.FONT_PAIRS["modern"]  # Default Inter
    
    @classmethod
    def get_color_preset(cls, name: str) -> ColorPreset:
        """Get a color preset by name"""
        return cls.COLOR_PRESETS.get(name, cls.COLOR_PRESETS["indigo"])
    
    @classmethod
    def get_mode_config(cls, mode: str) -> dict:
        """Get mode configuration"""
        return cls.MODE_CONFIGS.get(mode, cls.MODE_CONFIGS["dark"])


def get_smart_defaults(prompt: str) -> Dict[str, Any]:
    """
    Extract all design preferences from a prompt without using LLM.
    Fast, deterministic, and works offline.
    """
    
    color_name = ThemePresets.detect_color(prompt)
    color_preset = ThemePresets.get_color_preset(color_name)
    mode = ThemePresets.detect_mode(prompt)
    mode_config = ThemePresets.get_mode_config(mode)
    styles = ThemePresets.detect_style(prompt)
    font_primary, font_secondary = ThemePresets.detect_font(prompt)
    
    return {
        "color_name": color_name,
        "color_preset": color_preset,
        "mode": mode,
        "mode_config": mode_config,
        "styles": styles,
        "glassmorphism": "glassmorphism" in styles,
        "three_d_enabled": "three_d_enabled" in styles,
        "font_primary": font_primary,
        "font_secondary": font_secondary,
    }