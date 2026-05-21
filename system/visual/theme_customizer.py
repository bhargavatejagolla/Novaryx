"""
NOVARYX - Theme Customizer
Real-time theme customization and preview.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("novaryx.theme_customizer")


class ThemeCustomizer:
    """Manages theme customization"""
    
    def __init__(self):
        self.current_theme = {
            "primary": "#6366f1",
            "accent": "#06b6d4",
            "mode": "dark",
            "font": "Inter",
            "border_radius": "12px",
            "glassmorphism": False,
            "animation_level": "moderate",
        }
        self._design_engine = None
    
    def _get_engine(self):
        if self._design_engine is None:
            try:
                from system.templates.dynamic.design_token_engine import DesignTokenEngine
                self._design_engine = DesignTokenEngine(use_llm_refinement=False)
            except Exception:
                pass
        return self._design_engine
    
    def get_current_theme(self) -> Dict:
        """Get current theme"""
        return dict(self.current_theme)
    
    def apply_theme(self, updates: Dict) -> Dict:
        """Apply theme updates and return generated CSS"""
        self.current_theme.update(updates)
        
        # Generate design system from theme
        engine = self._get_engine()
        if engine:
            prompt = f"{self.current_theme['mode']} mode with {self.current_theme['primary']} primary"
            ds = engine.quick_generate(prompt)
            
            return {
                "theme": self.current_theme,
                "css_variables": {
                    "--primary": ds.colors.primary if ds else self.current_theme["primary"],
                    "--accent": self.current_theme["accent"],
                    "--background": ds.colors.background if ds else "#0f0f1a",
                    "--surface": ds.colors.surface if ds else "#1e1e32",
                    "--text-primary": ds.colors.text_primary if ds else "#f1f1f6",
                    "--text-secondary": ds.colors.text_secondary if ds else "#a0a0b8",
                },
                "design_system": ds.to_dict() if ds else {},
            }
        
        return {"theme": self.current_theme, "css_variables": {}}
    
    def get_preset_themes(self) -> Dict[str, Dict]:
        """Get predefined theme presets"""
        return {
            "purple_dark": {
                "primary": "#7c3aed", "accent": "#06b6d4",
                "mode": "dark", "font": "Inter"
            },
            "ocean_blue": {
                "primary": "#3b82f6", "accent": "#f97316",
                "mode": "dark", "font": "Inter"
            },
            "emerald_light": {
                "primary": "#10b981", "accent": "#8b5cf6",
                "mode": "light", "font": "Poppins"
            },
            "sunset_orange": {
                "primary": "#f97316", "accent": "#6366f1",
                "mode": "dark", "font": "Inter"
            },
            "minimal_slate": {
                "primary": "#64748b", "accent": "#f59e0b",
                "mode": "light", "font": "Roboto"
            },
        }