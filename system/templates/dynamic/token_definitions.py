"""
NOVARYX - Token Definitions
Complete design token types for the dynamic template system.

Every visual property is a token that can be generated from a prompt.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json


@dataclass
class ColorTokens:
    """Complete color system generated from a single primary color"""
    
    # Core
    primary: str = "#6366f1"          # Indigo
    primary_light: str = "#a5b4fc"
    primary_dark: str = "#4338ca"
    primary_contrast: str = "#ffffff"
    
    # Surfaces
    background: str = "#0f0f1a"       # Dark default
    background_secondary: str = "#1a1a2e"
    surface: str = "#1e1e32"
    surface_glass: str = "rgba(30, 30, 50, 0.7)"
    surface_raised: str = "#2a2a40"
    
    # Text
    text_primary: str = "#f1f1f6"
    text_secondary: str = "#a0a0b8"
    text_tertiary: str = "#6b6b80"
    text_on_primary: str = "#ffffff"
    
    # Semantic
    accent: str = "#06b6d4"           # Cyan
    accent_light: str = "#22d3ee"
    success: str = "#10b981"
    success_light: str = "#34d399"
    warning: str = "#f59e0b"
    warning_light: str = "#fbbf24"
    error: str = "#ef4444"
    error_light: str = "#f87171"
    info: str = "#3b82f6"
    info_light: str = "#60a5fa"
    
    # Borders & Dividers
    border: str = "rgba(255, 255, 255, 0.08)"
    border_focus: str = "#6366f1"
    divider: str = "rgba(255, 255, 255, 0.06)"
    
    # Chart colors
    chart_1: str = "#6366f1"
    chart_2: str = "#06b6d4"
    chart_3: str = "#10b981"
    chart_4: str = "#f59e0b"
    chart_5: str = "#ef4444"
    chart_6: str = "#8b5cf6"
    
    def to_css_variables(self) -> str:
        """Generate CSS custom properties"""
        css = ":root {\n"
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            css_name = f"--{field_name.replace('_', '-')}"
            css += f"  {css_name}: {value};\n"
        css += "}"
        return css
    
    def to_tailwind_config(self) -> Dict[str, Any]:
        """Generate Tailwind CSS config extension"""
        return {
            "colors": {
                "primary": {
                    "DEFAULT": self.primary,
                    "light": self.primary_light,
                    "dark": self.primary_dark,
                },
                "surface": {
                    "DEFAULT": self.surface,
                    "glass": self.surface_glass,
                    "raised": self.surface_raised,
                },
                "accent": self.accent,
                "success": self.success,
                "warning": self.warning,
                "error": self.error,
                "info": self.info,
            }
        }
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dictionary"""
        result = {}
        for field_name in self.__dataclass_fields__:
            result[field_name] = getattr(self, field_name)
        return result


@dataclass
class TypographyTokens:
    """Typography system"""
    
    font_family_primary: str = "Inter"
    font_family_secondary: str = "Inter"
    font_family_mono: str = "JetBrains Mono"
    
    # Font sizes (rem-based)
    size_xs: str = "0.75rem"     # 12px
    size_sm: str = "0.875rem"    # 14px
    size_base: str = "1rem"      # 16px
    size_lg: str = "1.125rem"    # 18px
    size_xl: str = "1.25rem"     # 20px
    size_2xl: str = "1.5rem"     # 24px
    size_3xl: str = "1.875rem"   # 30px
    size_4xl: str = "2.25rem"    # 36px
    size_5xl: str = "3rem"       # 48px
    size_6xl: str = "3.75rem"    # 60px
    size_7xl: str = "4.5rem"     # 72px
    
    # Font weights
    weight_light: int = 300
    weight_normal: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700
    weight_extrabold: int = 800
    
    # Line heights
    line_height_tight: float = 1.25
    line_height_normal: float = 1.5
    line_height_relaxed: float = 1.75
    
    # Letter spacing
    letter_spacing_tight: str = "-0.025em"
    letter_spacing_normal: str = "0em"
    letter_spacing_wide: str = "0.025em"
    
    def to_css_variables(self) -> str:
        css = ":root {\n"
        css += f"  --font-primary: '{self.font_family_primary}', sans-serif;\n"
        css += f"  --font-secondary: '{self.font_family_secondary}', sans-serif;\n"
        css += f"  --font-mono: '{self.font_family_mono}', monospace;\n"
        for field_name in self.__dataclass_fields__:
            if field_name.startswith("size_"):
                value = getattr(self, field_name)
                css_name = f"--{field_name.replace('_', '-')}"
                css += f"  {css_name}: {value};\n"
        css += "}"
        return css
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for field_name in self.__dataclass_fields__:
            result[field_name] = getattr(self, field_name)
        return result


@dataclass
class SpacingTokens:
    """Spacing system based on 4px grid"""
    
    unit: int = 4  # Base unit in pixels
    
    # Spacing scale
    space_0: str = "0px"
    space_1: str = "4px"
    space_2: str = "8px"
    space_3: str = "12px"
    space_4: str = "16px"
    space_5: str = "20px"
    space_6: str = "24px"
    space_8: str = "32px"
    space_10: str = "40px"
    space_12: str = "48px"
    space_16: str = "64px"
    space_20: str = "80px"
    space_24: str = "96px"
    space_32: str = "128px"
    
    # Component-specific
    section_padding_y: str = "80px"
    section_padding_x: str = "24px"
    container_max_width: str = "1280px"
    container_padding: str = "24px"
    card_padding: str = "24px"
    button_padding_x: str = "20px"
    button_padding_y: str = "10px"
    input_padding_x: str = "16px"
    input_padding_y: str = "10px"
    
    def to_dict(self) -> Dict[str, str]:
        result = {}
        for field_name in self.__dataclass_fields__:
            result[field_name] = str(getattr(self, field_name))
        return result


@dataclass
class EffectTokens:
    """Visual effects system"""
    
    # Glassmorphism
    glass_enabled: bool = True
    glass_blur: str = "12px"
    glass_opacity: float = 0.7
    glass_border: str = "1px solid rgba(255,255,255,0.1)"
    
    # Border radius
    radius_sm: str = "6px"
    radius_md: str = "12px"
    radius_lg: str = "16px"
    radius_xl: str = "24px"
    radius_full: str = "9999px"
    
    # Shadows
    shadow_sm: str = "0 1px 3px rgba(0,0,0,0.3)"
    shadow_md: str = "0 4px 12px rgba(0,0,0,0.4)"
    shadow_lg: str = "0 8px 30px rgba(0,0,0,0.5)"
    shadow_xl: str = "0 20px 60px rgba(0,0,0,0.6)"
    shadow_glow: str = "0 0 30px rgba(99,102,241,0.3)"
    
    # Transitions
    transition_fast: str = "150ms ease"
    transition_normal: str = "250ms ease"
    transition_slow: str = "400ms ease"
    
    # Z-index scale
    z_dropdown: int = 100
    z_sticky: int = 200
    z_modal: int = 300
    z_tooltip: int = 400
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for field_name in self.__dataclass_fields__:
            result[field_name] = getattr(self, field_name)
        return result


@dataclass
class AnimationTokens:
    """Animation and motion design tokens"""
    
    # Page transitions
    page_transition: str = "fade_slide"  # fade, fade_slide, scale, none
    page_duration: str = "0.3s"
    page_easing: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    
    # Micro-interactions
    micro_enabled: bool = True
    hover_scale: float = 1.02
    hover_duration: str = "200ms"
    tap_scale: float = 0.98
    
    # Scroll animations
    scroll_reveal: bool = True
    scroll_distance: str = "30px"
    scroll_duration: str = "0.6s"
    
    # Stagger
    stagger_children: bool = True
    stagger_delay: str = "0.1s"
    
    # Loading
    skeleton_enabled: bool = True
    skeleton_duration: str = "1.5s"
    
    # 3D
    three_d_enabled: bool = False
    three_d_perspective: str = "1000px"
    parallax_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for field_name in self.__dataclass_fields__:
            result[field_name] = getattr(self, field_name)
        return result


@dataclass
class DesignSystem:
    """Complete design system combining all token types"""
    
    project_name: str = ""
    mode: str = "dark"  # dark | light
    colors: ColorTokens = field(default_factory=ColorTokens)
    typography: TypographyTokens = field(default_factory=TypographyTokens)
    spacing: SpacingTokens = field(default_factory=SpacingTokens)
    effects: EffectTokens = field(default_factory=EffectTokens)
    animations: AnimationTokens = field(default_factory=AnimationTokens)
    
    # Metadata
    generated_from_prompt: str = ""
    generated_at: str = ""
    version: str = "1.0.0"
    
    def to_full_css(self) -> str:
        """Generate complete CSS with all variables"""
        css_sections = [
            "/* NOVARYX Generated Design System */",
            "/* Generated from prompt */",
            "",
            self.colors.to_css_variables(),
            "",
            self.typography.to_css_variables(),
            "",
            "/* Base Styles */",
            "*, *::before, *::after {",
            "  box-sizing: border-box;",
            "  margin: 0;",
            "  padding: 0;",
            "}",
            "",
            "html {",
            "  font-family: var(--font-primary);",
            "  font-size: var(--size-base);",
            "  line-height: 1.5;",
            "  -webkit-font-smoothing: antialiased;",
            "  -moz-osx-font-smoothing: grayscale;",
            "}",
            "",
            f"body {{",
            f"  background-color: {self.colors.background};",
            f"  color: {self.colors.text_primary};",
            "  min-height: 100vh;",
            "}",
        ]
        return "\n".join(css_sections)
    
    def to_tailwind_config(self) -> Dict[str, Any]:
        """Generate complete Tailwind config extension"""
        return {
            "theme": {
                "extend": {
                    **self.colors.to_tailwind_config(),
                    "fontFamily": {
                        "primary": [self.typography.font_family_primary, "sans-serif"],
                        "secondary": [self.typography.font_family_secondary, "sans-serif"],
                        "mono": [self.typography.font_family_mono, "monospace"],
                    },
                    "borderRadius": {
                        "sm": self.effects.radius_sm,
                        "md": self.effects.radius_md,
                        "lg": self.effects.radius_lg,
                        "xl": self.effects.radius_xl,
                    },
                    "boxShadow": {
                        "glow": self.effects.shadow_glow,
                    }
                }
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Full serialization"""
        return {
            "project_name": self.project_name,
            "mode": self.mode,
            "colors": self.colors.to_dict(),
            "typography": self.typography.to_dict(),
            "spacing": self.spacing.to_dict(),
            "effects": self.effects.to_dict(),
            "animations": self.animations.to_dict(),
            "generated_from_prompt": self.generated_from_prompt,
            "generated_at": self.generated_at,
            "version": self.version
        }
    
    def to_json(self) -> str:
        """Export as JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def save(self, filepath: str):
        """Save design system to file"""
        with open(filepath, "w") as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, filepath: str) -> "DesignSystem":
        """Load design system from file"""
        with open(filepath, "r") as f:
            data = json.load(f)
        
        ds = cls()
        ds.project_name = data.get("project_name", "")
        ds.mode = data.get("mode", "dark")
        ds.colors = ColorTokens(**data.get("colors", {}))
        ds.typography = TypographyTokens(**data.get("typography", {}))
        ds.spacing = SpacingTokens(**data.get("spacing", {}))
        ds.effects = EffectTokens(**data.get("effects", {}))
        ds.animations = AnimationTokens(**data.get("animations", {}))
        ds.generated_from_prompt = data.get("generated_from_prompt", "")
        ds.generated_at = data.get("generated_at", "")
        ds.version = data.get("version", "1.0.0")
        return ds