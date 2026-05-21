"""
NOVARYX - Theme Adaptation Engine
Deeply applies design tokens to every component, layout, and 3D scene.

Flow:
  DesignSystem -> ThemeAdapter -> Themed Components -> Themed Layouts -> Themed 3D

This ensures visual consistency across the entire generated project.
Colors, fonts, spacing, effects, and animations all flow from the prompt.
"""

import sys
import json
import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from system.templates.dynamic.token_definitions import (
    DesignSystem, ColorTokens, TypographyTokens,
    SpacingTokens, EffectTokens, AnimationTokens
)

logger = logging.getLogger("novaryx.theme_adapter")


class ThemeAdapter:
    """
    Adapts all project files to use the generated design system.
    
    Takes raw component code and injects:
    - CSS variable references for colors
    - Font family applications
    - Glassmorphism effects
    - Animation token values
    - Dark/light mode support
    """
    
    def __init__(self, design_system: DesignSystem):
        self.ds = design_system
        self.color_map = self._build_color_map()
        self.token_map = self._build_token_map()
    
    def _build_color_map(self) -> Dict[str, str]:
        """Build mapping from semantic names to CSS variables"""
        colors = self.ds.colors
        return {
            "primary": f"var(--primary, {colors.primary})",
            "primary_light": f"var(--primary-light, {colors.primary_light})",
            "primary_dark": f"var(--primary-dark, {colors.primary_dark})",
            "accent": f"var(--accent, {colors.accent})",
            "background": f"var(--background, {colors.background})",
            "background_secondary": f"var(--background-secondary, {colors.background_secondary})",
            "surface": f"var(--surface, {colors.surface})",
            "surface_glass": f"var(--surface-glass, {colors.surface_glass})",
            "surface_raised": f"var(--surface-raised, {colors.surface_raised})",
            "text_primary": f"var(--text-primary, {colors.text_primary})",
            "text_secondary": f"var(--text-secondary, {colors.text_secondary})",
            "text_tertiary": f"var(--text-tertiary, {colors.text_tertiary})",
            "success": f"var(--success, {colors.success})",
            "warning": f"var(--warning, {colors.warning})",
            "error": f"var(--error, {colors.error})",
            "info": f"var(--info, {colors.info})",
            "border": f"var(--border, {colors.border})",
            "border_focus": f"var(--border-focus, {colors.border_focus})",
            "shadow_glow": f"var(--shadow-glow, {self.ds.effects.shadow_glow})",
        }
    
    def _build_token_map(self) -> Dict[str, str]:
        """Build mapping for all design tokens to CSS variable references"""
        tokens = {}
        
        # Typography
        tokens["font_primary"] = f"var(--font-primary, '{self.ds.typography.font_family_primary}')"
        tokens["font_mono"] = f"var(--font-mono, '{self.ds.typography.font_family_mono}')"
        
        # Spacing
        for field_name in self.ds.spacing.__dataclass_fields__:
            value = getattr(self.ds.spacing, field_name)
            css_name = f"--{field_name.replace('_', '-')}"
            tokens[field_name] = f"var({css_name}, {value})"
        
        # Effects
        for field_name in self.ds.effects.__dataclass_fields__:
            value = getattr(self.ds.effects, field_name)
            css_name = f"--{field_name.replace('_', '-')}"
            tokens[field_name] = f"var({css_name}, {value})"
        
        return tokens
    
    def generate_root_css(self) -> str:
        """Generate complete :root CSS with all design tokens"""
        ds = self.ds
        
        css_lines = [
            "/* NOVARYX Generated Design System */",
            f"/* Project: {ds.project_name} */",
            f"/* Mode: {ds.mode} */",
            f"/* Generated: {datetime.now().isoformat()} */",
            "",
            "@tailwind base;",
            "@tailwind components;",
            "@tailwind utilities;",
            "",
            ":root {",
            "",
            "  /* ===== COLOR SYSTEM ===== */",
            f"  --primary: {ds.colors.primary};",
            f"  --primary-light: {ds.colors.primary_light};",
            f"  --primary-dark: {ds.colors.primary_dark};",
            f"  --primary-contrast: {ds.colors.primary_contrast};",
            f"  --accent: {ds.colors.accent};",
            f"  --accent-light: {ds.colors.accent_light};",
            "",
            f"  --background: {ds.colors.background};",
            f"  --background-secondary: {ds.colors.background_secondary};",
            f"  --surface: {ds.colors.surface};",
            f"  --surface-glass: {ds.colors.surface_glass};",
            f"  --surface-raised: {ds.colors.surface_raised};",
            "",
            f"  --text-primary: {ds.colors.text_primary};",
            f"  --text-secondary: {ds.colors.text_secondary};",
            f"  --text-tertiary: {ds.colors.text_tertiary};",
            f"  --text-on-primary: {ds.colors.text_on_primary};",
            "",
            f"  --success: {ds.colors.success};",
            f"  --success-light: {ds.colors.success_light};",
            f"  --warning: {ds.colors.warning};",
            f"  --warning-light: {ds.colors.warning_light};",
            f"  --error: {ds.colors.error};",
            f"  --error-light: {ds.colors.error_light};",
            f"  --info: {ds.colors.info};",
            f"  --info-light: {ds.colors.info_light};",
            "",
            f"  --border: {ds.colors.border};",
            f"  --border-focus: {ds.colors.border_focus};",
            f"  --divider: {ds.colors.divider};",
            "",
            f"  --chart-1: {ds.colors.chart_1};",
            f"  --chart-2: {ds.colors.chart_2};",
            f"  --chart-3: {ds.colors.chart_3};",
            f"  --chart-4: {ds.colors.chart_4};",
            f"  --chart-5: {ds.colors.chart_5};",
            f"  --chart-6: {ds.colors.chart_6};",
            "",
            "  /* ===== TYPOGRAPHY ===== */",
            f"  --font-primary: '{ds.typography.font_family_primary}', system-ui, sans-serif;",
            f"  --font-secondary: '{ds.typography.font_family_secondary}', system-ui, sans-serif;",
            f"  --font-mono: '{ds.typography.font_family_mono}', monospace;",
            "",
            f"  --font-size-xs: {ds.typography.size_xs};",
            f"  --font-size-sm: {ds.typography.size_sm};",
            f"  --font-size-base: {ds.typography.size_base};",
            f"  --font-size-lg: {ds.typography.size_lg};",
            f"  --font-size-xl: {ds.typography.size_xl};",
            f"  --font-size-2xl: {ds.typography.size_2xl};",
            f"  --font-size-3xl: {ds.typography.size_3xl};",
            f"  --font-size-4xl: {ds.typography.size_4xl};",
            "",
            f"  --font-weight-light: {ds.typography.weight_light};",
            f"  --font-weight-normal: {ds.typography.weight_normal};",
            f"  --font-weight-medium: {ds.typography.weight_medium};",
            f"  --font-weight-semibold: {ds.typography.weight_semibold};",
            f"  --font-weight-bold: {ds.typography.weight_bold};",
            "",
            f"  --line-height-tight: {ds.typography.line_height_tight};",
            f"  --line-height-normal: {ds.typography.line_height_normal};",
            f"  --line-height-relaxed: {ds.typography.line_height_relaxed};",
            "",
            "  /* ===== SPACING ===== */",
            f"  --space-unit: {ds.spacing.unit}px;",
            f"  --space-1: {ds.spacing.space_1};",
            f"  --space-2: {ds.spacing.space_2};",
            f"  --space-3: {ds.spacing.space_3};",
            f"  --space-4: {ds.spacing.space_4};",
            f"  --space-6: {ds.spacing.space_6};",
            f"  --space-8: {ds.spacing.space_8};",
            f"  --space-12: {ds.spacing.space_12};",
            f"  --space-16: {ds.spacing.space_16};",
            f"  --section-padding-y: {ds.spacing.section_padding_y};",
            f"  --section-padding-x: {ds.spacing.section_padding_x};",
            f"  --container-max-width: {ds.spacing.container_max_width};",
            f"  --card-padding: {ds.spacing.card_padding};",
            f"  --button-padding-x: {ds.spacing.button_padding_x};",
            f"  --button-padding-y: {ds.spacing.button_padding_y};",
            "",
            "  /* ===== EFFECTS ===== */",
            f"  --glass-blur: {ds.effects.glass_blur};",
            f"  --glass-opacity: {ds.effects.glass_opacity};",
            f"  --glass-border: {ds.effects.glass_border};",
            f"  --radius-sm: {ds.effects.radius_sm};",
            f"  --radius-md: {ds.effects.radius_md};",
            f"  --radius-lg: {ds.effects.radius_lg};",
            f"  --radius-xl: {ds.effects.radius_xl};",
            f"  --radius-full: {ds.effects.radius_full};",
            f"  --shadow-sm: {ds.effects.shadow_sm};",
            f"  --shadow-md: {ds.effects.shadow_md};",
            f"  --shadow-lg: {ds.effects.shadow_lg};",
            f"  --shadow-xl: {ds.effects.shadow_xl};",
            f"  --shadow-glow: {ds.effects.shadow_glow};",
            f"  --transition-fast: {ds.effects.transition_fast};",
            f"  --transition-normal: {ds.effects.transition_normal};",
            f"  --transition-slow: {ds.effects.transition_slow};",
            f"  --z-dropdown: {ds.effects.z_dropdown};",
            f"  --z-sticky: {ds.effects.z_sticky};",
            f"  --z-modal: {ds.effects.z_modal};",
            f"  --z-tooltip: {ds.effects.z_tooltip};",
            "",
            "  /* ===== ANIMATIONS ===== */",
            f"  --page-transition: {ds.animations.page_transition};",
            f"  --page-duration: {ds.animations.page_duration};",
            f"  --page-easing: {ds.animations.page_easing};",
            f"  --hover-scale: {ds.animations.hover_scale};",
            f"  --hover-duration: {ds.animations.hover_duration};",
            f"  --tap-scale: {ds.animations.tap_scale};",
            f"  --scroll-distance: {ds.animations.scroll_distance};",
            f"  --scroll-duration: {ds.animations.scroll_duration};",
            f"  --stagger-delay: {ds.animations.stagger_delay};",
            f"  --skeleton-duration: {ds.animations.skeleton_duration};",
            f"  --3d-perspective: {ds.animations.three_d_perspective};",
            "}",
            "",
        ]
        
        # Dark mode specific overrides
        if ds.mode == "dark":
            css_lines.extend([
                "/* Dark mode is default */",
                "[data-theme='light'] {",
                f"  --background: #f8fafc;",
                f"  --background-secondary: #f1f5f9;",
                f"  --surface: #ffffff;",
                f"  --surface-glass: rgba(255, 255, 255, 0.7);",
                f"  --surface-raised: #f8fafc;",
                f"  --text-primary: #0f172a;",
                f"  --text-secondary: #475569;",
                f"  --text-tertiary: #94a3b8;",
                f"  --border: rgba(0, 0, 0, 0.08);",
                f"  --divider: rgba(0, 0, 0, 0.06);",
                f"  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);",
                f"  --shadow-md: 0 4px 12px rgba(0,0,0,0.1);",
                f"  --shadow-lg: 0 8px 30px rgba(0,0,0,0.12);",
                f"  --shadow-xl: 0 20px 60px rgba(0,0,0,0.15);",
                "}",
                "",
            ])
        else:
            css_lines.extend([
                "/* Light mode is default */",
                "[data-theme='dark'] {",
                f"  --background: {ds.colors.background};",
                f"  --text-primary: {ds.colors.text_primary};",
                "}",
                "",
            ])
        
        # Glassmorphism utility classes
        if ds.effects.glass_enabled:
            css_lines.extend([
                "/* ===== GLASSMORPHISM UTILITIES ===== */",
                ".glass {",
                f"  background: var(--surface-glass);",
                f"  backdrop-filter: blur(var(--glass-blur));",
                f"  -webkit-backdrop-filter: blur(var(--glass-blur));",
                f"  border: var(--glass-border);",
                f"  border-radius: var(--radius-lg);",
                "}",
                "",
                ".glass-card {",
                f"  background: var(--surface-glass);",
                f"  backdrop-filter: blur(var(--glass-blur));",
                f"  -webkit-backdrop-filter: blur(var(--glass-blur));",
                f"  border: var(--glass-border);",
                f"  border-radius: var(--radius-xl);",
                f"  padding: var(--card-padding);",
                f"  transition: all var(--transition-normal);",
                "}",
                "",
                ".glass-card:hover {",
                f"  box-shadow: var(--shadow-lg);",
                f"  border-color: var(--border-focus);",
                "}",
                "",
            ])
        
        # 3D utilities
        if ds.animations.three_d_enabled:
            css_lines.extend([
                "/* ===== 3D UTILITIES ===== */",
                ".perspective-3d {",
                f"  perspective: var(--3d-perspective);",
                "}",
                "",
                ".preserve-3d {",
                "  transform-style: preserve-3d;",
                "}",
                "",
            ])
        
        # Premium utilities
        css_lines.extend([
            "/* ===== PREMIUM UTILITIES ===== */",
            ".text-gradient {",
            "  background: linear-gradient(135deg, var(--primary), var(--accent));",
            "  -webkit-background-clip: text;",
            "  -webkit-text-fill-color: transparent;",
            "  background-clip: text;",
            "}",
            "",
            ".bg-gradient-premium {",
            "  background: linear-gradient(135deg, var(--primary), var(--accent));",
            "  color: var(--text-on-primary, #ffffff);",
            "}",
            "",
            ".text-shimmer {",
            "  background: linear-gradient(90deg, var(--text-primary) 0%, var(--text-secondary) 50%, var(--text-primary) 100%);",
            "  background-size: 200% auto;",
            "  -webkit-background-clip: text;",
            "  -webkit-text-fill-color: transparent;",
            "  animation: shimmer 3s linear infinite;",
            "}",
            "",
            ".glass-panel {",
            "  background: var(--surface-glass);",
            "  backdrop-filter: blur(16px);",
            "  -webkit-backdrop-filter: blur(16px);",
            "  border: 1px solid rgba(255, 255, 255, 0.05);",
            "  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);",
            "}",
            "",
            ".border-glow {",
            "  position: relative;",
            "}",
            ".border-glow::before {",
            "  content: '';",
            "  position: absolute;",
            "  inset: -1px;",
            "  border-radius: inherit;",
            "  background: linear-gradient(to right, var(--primary), var(--accent));",
            "  z-index: -1;",
            "  opacity: 0;",
            "  transition: opacity 0.3s ease;",
            "}",
            ".border-glow:hover::before {",
            "  opacity: 1;",
            "}",
            "",
        ])
        
        # Base styles
        css_lines.extend([
            "/* ===== BASE STYLES ===== */",
            "*, *::before, *::after {",
            "  box-sizing: border-box;",
            "  margin: 0;",
            "  padding: 0;",
            "}",
            "",
            "html {",
            "  font-family: var(--font-primary);",
            "  font-size: var(--font-size-base);",
            "  line-height: var(--line-height-normal);",
            "  -webkit-font-smoothing: antialiased;",
            "  -moz-osx-font-smoothing: grayscale;",
            "  scroll-behavior: smooth;",
            "}",
            "",
            "body {",
            "  background-color: var(--background);",
            "  color: var(--text-primary);",
            "  min-height: 100vh;",
            "  transition: background-color var(--transition-normal), color var(--transition-normal);",
            "}",
            "",
            "a {",
            "  color: var(--primary);",
            "  text-decoration: none;",
            "  transition: color var(--transition-fast);",
            "}",
            "",
            "a:hover {",
            "  color: var(--primary-light);",
            "}",
            "",
            "::-webkit-scrollbar {",
            "  width: 8px;",
            "  height: 8px;",
            "}",
            "",
            "::-webkit-scrollbar-track {",
            "  background: var(--background);",
            "}",
            "",
            "::-webkit-scrollbar-thumb {",
            "  background: var(--border);",
            "  border-radius: var(--radius-full);",
            "}",
            "",
            "::-webkit-scrollbar-thumb:hover {",
            "  background: var(--text-tertiary);",
            "}",
        ])
        
        return "\n".join(css_lines)
    
    def generate_theme_context(self) -> Dict[str, Any]:
        """Generate React context for theme (dark/light toggle)"""
        return {
            "defaultTheme": self.ds.mode,
            "themes": ["dark", "light"],
            "storageKey": "novaryx-theme",
            "attribute": "data-theme",
        }
    
    def generate_theme_provider_tsx(self) -> str:
        """Generate ThemeProvider component with dark/light support"""
        return f'''import React, {{ createContext, useContext, useEffect, useState }} from "react";

type Theme = "dark" | "light";

interface ThemeContextType {{
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}}

const ThemeContext = createContext<ThemeContextType>({{
  theme: "{self.ds.mode}",
  setTheme: () => {{}},
  toggleTheme: () => {{}},
}});

export function useTheme() {{
  return useContext(ThemeContext);
}}

export function ThemeProvider({{ children }}: {{ children: React.ReactNode }}) {{
  const [theme, setThemeState] = useState<Theme>(() => {{
    if (typeof window !== "undefined") {{
      const stored = localStorage.getItem("novaryx-theme") as Theme | null;
      return stored || "{self.ds.mode}";
    }}
    return "{self.ds.mode}";
  }});

  useEffect(() => {{
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("novaryx-theme", theme);
  }}, [theme]);

  const setTheme = (newTheme: Theme) => setThemeState(newTheme);
  const toggleTheme = () => setThemeState(theme === "dark" ? "light" : "dark");

  return (
    <ThemeContext.Provider value={{{{ theme, setTheme, toggleTheme }}}}>
      {{children}}
    </ThemeContext.Provider>
  );
}}
'''
    
    def apply_to_component_tsx(self, component_tsx: str, component_id: str) -> str:
        """Apply theme tokens to a specific component's TSX code"""
        themed = component_tsx
        
        # Replace hardcoded color references with CSS variables where appropriate
        # This is a smart pass that ensures theme tokens flow into components
        
        replacements = {
            # Tailwind-style token references
            "[var(--primary)]": "var(--primary)",
            "[var(--surface)]": "var(--surface)",
            "[var(--background)]": "var(--background)",
            "[var(--text-primary)]": "var(--text-primary)",
            "[var(--text-secondary)]": "var(--text-secondary)",
            "[var(--text-tertiary)]": "var(--text-tertiary)",
            "[var(--border)]": "var(--border)",
            "[var(--surface-raised)]": "var(--surface-raised)",
            "[var(--surface-glass)]": "var(--surface-glass)",
            "[var(--border-focus)]": "var(--border-focus)",
            "[var(--success)]": "var(--success)",
            "[var(--error)]": "var(--error)",
            "[var(--warning)]": "var(--warning)",
            "[var(--info)]": "var(--info)",
            "[var(--divider)]": "var(--divider)",
            "[var(--shadow-glow)]": "var(--shadow-glow)",
        }
        
        for old, new in replacements.items():
            themed = themed.replace(old, new)
        
        return themed
    
    def get_3d_theme_config(self) -> Dict[str, str]:
        """Get theme configuration for 3D scenes"""
        return {
            "primary_color": self.ds.colors.primary,
            "accent_color": self.ds.colors.accent,
            "background_color": self.ds.colors.background,
            "mode": self.ds.mode,
            "emissive_intensity": "0.3" if self.ds.mode == "dark" else "0.1",
            "fog_color": self.ds.colors.background,
            "grid_color": self.ds.colors.primary,
        }
    
    def generate_tailwind_config_js(self) -> str:
        """Generate complete tailwind.config.js with all theme tokens"""
        return f'''/** @type {{import('tailwindcss').Config}} */
export default {{
  content: [
    "./index.html",
    "./src/**/*.{{js,ts,jsx,tsx}}",
  ],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {{
    extend: {{
      colors: {{
        primary: {{
          DEFAULT: "var(--primary)",
          light: "var(--primary-light)",
          dark: "var(--primary-dark)",
          contrast: "var(--primary-contrast)",
        }},
        surface: {{
          DEFAULT: "var(--surface)",
          glass: "var(--surface-glass)",
          raised: "var(--surface-raised)",
        }},
        accent: "var(--accent)",
        success: "var(--success)",
        warning: "var(--warning)",
        error: "var(--error)",
        info: "var(--info)",
      }},
      fontFamily: {{
        primary: ["var(--font-primary)", "system-ui", "sans-serif"],
        secondary: ["var(--font-secondary)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      }},
      fontSize: {{
        xs: "var(--font-size-xs)",
        sm: "var(--font-size-sm)",
        base: "var(--font-size-base)",
        lg: "var(--font-size-lg)",
        xl: "var(--font-size-xl)",
        "2xl": "var(--font-size-2xl)",
        "3xl": "var(--font-size-3xl)",
        "4xl": "var(--font-size-4xl)",
      }},
      borderRadius: {{
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        full: "var(--radius-full)",
      }},
      boxShadow: {{
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        xl: "var(--shadow-xl)",
        glow: "var(--shadow-glow)",
      }},
      transitionDuration: {{
        fast: "150ms",
        normal: "250ms",
        slow: "400ms",
      }},
      zIndex: {{
        dropdown: "var(--z-dropdown)",
        sticky: "var(--z-sticky)",
        modal: "var(--z-modal)",
        tooltip: "var(--z-tooltip)",
      }},
    }},
  }},
  plugins: [],
}};
'''
    
    def generate_all_theme_files(self) -> Dict[str, str]:
        """Generate all theme-related files"""
        return {
            "src/styles/tokens.css": self.generate_root_css(),
            "src/styles/animations.css": self.generate_animations_css(),
            "tailwind.config.js": self.generate_tailwind_config_js(),
            "src/components/ThemeProvider.tsx": self.generate_theme_provider_tsx(),
        }
    
    def generate_animations_css(self) -> str:
        """Generate CSS animations file based on tokens"""
        return """/* NOVARYX Animations */

@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes shimmer {
  to { background-position: 200% center; }
}

.animate-fade-up {
  animation: fade-up 0.6s ease-out forwards;
}

.animate-fade-in {
  animation: fade-in 0.4s ease-out forwards;
}

.hover-lift {
  transition: transform 0.2s ease-out;
}

.hover-lift:hover {
  transform: translateY(-4px);
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 15px var(--primary-light); }
  50% { box-shadow: 0 0 30px var(--primary); }
}

.animate-pulse-glow {
  animation: pulse-glow 2s infinite;
}
"""
    
    def display_theme_summary(self):
        """Display the current theme configuration"""
        ds = self.ds
        
        print("\n" + "=" * 60)
        print(f"THEME: {ds.project_name}")
        print("=" * 60)
        print(f"   Mode: {ds.mode.upper()}")
        print(f"   Primary: {ds.colors.primary}")
        print(f"   Accent: {ds.colors.accent}")
        print(f"   Background: {ds.colors.background}")
        print(f"   Surface: {ds.colors.surface}")
        print(f"   Text: {ds.colors.text_primary}")
        print(f"   Font: {ds.typography.font_family_primary}")
        print(f"   Glassmorphism: {'ON' if ds.effects.glass_enabled else 'OFF'}")
        print(f"   3D: {'ON' if ds.animations.three_d_enabled else 'OFF'}")
        print(f"   Border Radius: {ds.effects.radius_md}")
        print(f"   Transition: {ds.effects.transition_normal}")
        print("=" * 60)


# ---- Quick Adapter ----

def adapt_plan_theme(plan) -> Dict[str, str]:
    """Apply theme adaptation to an assembly plan, return themed files"""
    adapter = ThemeAdapter(plan.design_system)
    adapter.display_theme_summary()
    return adapter.generate_all_theme_files()


# ---- Test ----

def test_theme_adapter():
    """Test the theme adaptation engine"""
    from system.templates.dynamic.assembly_engine import quick_assemble
    
    print("\n" + "=" * 60)
    print("THEME ADAPTATION ENGINE TEST")
    print("=" * 60)
    
    prompts = [
        "Build a dark purple SaaS dashboard with glassmorphism",
        "Create a light blue e-commerce store",
        "Make a portfolio with orange accent and 3D effects",
    ]
    
    for prompt in prompts:
        plan = quick_assemble(prompt)
        adapter = ThemeAdapter(plan.design_system)
        adapter.display_theme_summary()
        
        files = adapter.generate_all_theme_files()
        print(f"   Generated {len(files)} theme files:")
        for name, content in files.items():
            print(f"      {name} ({len(content)} bytes)")
        
        # Show sample of generated CSS
        css = files.get("src/styles/tokens.css", "")
        first_vars = [l for l in css.split("\n") if l.strip().startswith("--")][:5]
        print(f"   Sample CSS variables:")
        for var in first_vars:
            print(f"      {var.strip()}")
        print()
    
    print("DONE: Theme Adaptation Engine test complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_theme_adapter()