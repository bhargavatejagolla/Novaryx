"""
NOVARYX - Design Token Engine
Generates a complete DesignSystem from a user prompt.

Uses:
  1. Smart defaults (keyword matching) - fast, offline
  2. LLM refinement (optional) - for complex/unusual requests
  3. Color science (automatic palette generation)

This is THE engine. Everything visual starts here.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from system.templates.dynamic.token_definitions import (
    DesignSystem,
    ColorTokens,
    TypographyTokens,
    SpacingTokens,
    EffectTokens,
    AnimationTokens
)
from system.templates.dynamic.theme_presets import ThemePresets, get_smart_defaults

logger = logging.getLogger("novaryx.design_tokens")


class DesignTokenEngine:
    """
    Generates complete design systems from prompts.
    
    Flow:
      Prompt → Smart Defaults → Color Generation → Token Assembly → DesignSystem
    """
    
    def __init__(self, use_llm_refinement: bool = True):
        self.use_llm_refinement = use_llm_refinement
        self._inference = None
    
    def _get_inference(self):
        """Lazy load inference provider"""
        if self._inference is None:
            try:
                from system.inference.provider_factory import get_provider
                self._inference = get_provider()
            except Exception as e:
                logger.warning(f"Inference not available: {e}")
                self._inference = None
        return self._inference
    
    def generate(self, prompt: str, project_name: str = "") -> DesignSystem:
        """
        Generate a complete design system from a prompt.
        
        Args:
            prompt: User's project description
            project_name: Optional project name
        
        Returns:
            Complete DesignSystem ready for component theming
        """
        logger.info(f"Generating design system from prompt: '{prompt[:80]}...'")
        
        # Step 1: Extract smart defaults
        defaults = get_smart_defaults(prompt)
        
        # Step 2: Build color tokens
        colors = self._build_colors(defaults)
        
        # Step 3: Refine with LLM if available
        if self.use_llm_refinement:
            colors = self._llm_refine_colors(prompt, colors, defaults)
        
        # Step 4: Build typography
        typography = self._build_typography(defaults)
        
        # Step 5: Build spacing
        spacing = SpacingTokens()
        
        # Step 6: Build effects
        effects = self._build_effects(defaults)
        
        # Step 7: Build animations
        animations = self._build_animations(defaults)
        
        # Step 8: Assemble complete system
        design_system = DesignSystem(
            project_name=project_name or self._extract_project_name(prompt),
            mode=defaults["mode"],
            colors=colors,
            typography=typography,
            spacing=spacing,
            effects=effects,
            animations=animations,
            generated_from_prompt=prompt,
            generated_at=datetime.now().isoformat(),
            version="1.0.0"
        )
        
        logger.info(f"Design system generated: {design_system.colors.primary}")
        
        return design_system
    
    def _build_colors(self, defaults: Dict[str, Any]) -> ColorTokens:
        """Build color tokens from smart defaults"""
        preset = defaults["color_preset"]
        mode_config = defaults["mode_config"]
        
        return ColorTokens(
            primary=preset.primary,
            primary_light=preset.primary_light,
            primary_dark=preset.primary_dark,
            accent=preset.accent,
            background=mode_config["background"],
            background_secondary=mode_config["background_secondary"],
            surface=mode_config["surface"],
            text_primary=mode_config["text_primary"],
            text_secondary=mode_config["text_secondary"],
            border_focus=preset.primary,
            chart_1=preset.primary,
            chart_2=preset.accent,
        )
    
    def _llm_refine_colors(
        self,
        prompt: str,
        colors: ColorTokens,
        defaults: Dict[str, Any]
    ) -> ColorTokens:
        """Use LLM to refine colors for unusual requests"""
        provider = self._get_inference()
        
        if provider is None:
            return colors
        
        try:
            refinement_prompt = f"""Given this project description: "{prompt[:200]}"
Current primary color: {colors.primary}
Current accent color: {colors.accent}
Mode: {defaults['mode']}

CRITICAL INSTRUCTION: You are a world-class UI/UX designer. Suggest ONLY a hex color for primary and accent that perfectly matches the description and feels EXTREMELY PREMIUM, modern, and high-converting (like Linear, Vercel, or Stripe). If dark mode, lean towards vibrant saturated colors.

Respond in JSON format ONLY:
{{"primary": "#hex", "accent": "#hex"}}
"""
            # Auto-healing loop
            for attempt in range(2):
                try:
                    result = provider.generate(
                        prompt=refinement_prompt,
                        role="planning",
                        temperature=0.8,
                        max_tokens=150
                    )
                    
                    if result.success and result.text:
                        import json
                        text = result.text.strip()
                        if "{" in text and "}" in text:
                            start = text.index("{")
                            end = text.rindex("}") + 1
                            data = json.loads(text[start:end])
                            
                            if "primary" in data:
                                colors.primary = data["primary"]
                            if "accent" in data:
                                colors.accent = data["accent"]
                            
                            logger.info(f"LLM refined colors: {colors.primary}, {colors.accent}")
                            return colors
                except Exception as loop_e:
                    logger.warning(f"Color refinement attempt {attempt+1} failed: {loop_e}")
                    
        except Exception as e:
            logger.debug(f"LLM refinement skipped: {e}")
        
        return colors
    
    def _build_typography(self, defaults: Dict[str, Any]) -> TypographyTokens:
        """Build typography tokens"""
        # Force premium fonts if generic
        primary_font = defaults.get("font_primary", "Inter")
        if primary_font.lower() in ["sans-serif", "arial", "helvetica", "system-ui"]:
            primary_font = "Inter"
            
        return TypographyTokens(
            font_family_primary=primary_font,
            font_family_secondary=defaults.get("font_secondary", "Outfit"),
        )
    
    def _build_effects(self, defaults: Dict[str, Any]) -> EffectTokens:
        """Build effect tokens based on style preferences"""
        glass_enabled = defaults.get("glassmorphism", True)
        
        preset = defaults["color_preset"]
        effects = EffectTokens(
            glass_enabled=glass_enabled,
            shadow_glow=f"0 0 30px {preset.primary}40",
        )
        
        if glass_enabled:
            effects.shadow_sm = "0 1px 3px rgba(0,0,0,0.2)"
            effects.shadow_md = "0 4px 12px rgba(0,0,0,0.3)"
            effects.shadow_lg = "0 8px 30px rgba(0,0,0,0.4)"
            effects.shadow_xl = "0 20px 60px rgba(0,0,0,0.5)"
        
        return effects
    
    def _build_animations(self, defaults: Dict[str, Any]) -> AnimationTokens:
        """Build animation tokens"""
        animations = AnimationTokens(
            micro_enabled=True,
            scroll_reveal=True,
            stagger_children=True,
            skeleton_enabled=True,
            three_d_enabled=defaults.get("three_d_enabled", False),
        )
        
        return animations
    
    def _extract_project_name(self, prompt: str) -> str:
        """Extract a project name from the prompt"""
        # Simple extraction
        words = prompt.split()
        
        # Look for "called", "named", "title"
        for i, word in enumerate(words):
            if word.lower() in ["called", "named"] and i + 1 < len(words):
                return words[i + 1].strip('"\'.,')
        
        # Use first 3 meaningful words
        meaningful = [w for w in words[:8] if len(w) > 3 and w.lower() not in 
                      ["build", "create", "make", "generate", "with", "that", "this", "have", "like"]]
        
        if len(meaningful) >= 2:
            name = " ".join(meaningful[:3]).title()
            return name[:40]
        
        return "NOVARYX Project"
    
    def quick_generate(self, prompt: str) -> DesignSystem:
        """Fast generation without LLM refinement"""
        self.use_llm_refinement = False
        return self.generate(prompt)
    
    def generate_to_file(self, prompt: str, output_path: str) -> DesignSystem:
        """Generate and save to file"""
        ds = self.generate(prompt)
        ds.save(output_path)
        return ds
    
    def display_design_system(self, ds: DesignSystem):
        """Display design system in readable format"""
        print("\n" + "=" * 60)
        print(f"DESIGN SYSTEM: {ds.project_name}")
        print("=" * 60)
        
        print(f"\n  Mode: {ds.mode.upper()}")
        print(f"  Primary: {ds.colors.primary}")
        print(f"  Accent: {ds.colors.accent}")
        print(f"  Background: {ds.colors.background}")
        print(f"  Text: {ds.colors.text_primary}")
        
        print(f"\n  Font: {ds.typography.font_family_primary}")
        print(f"  Glassmorphism: {'YES' if ds.effects.glass_enabled else 'NO'}")
        print(f"  3D: {'YES' if ds.animations.three_d_enabled else 'NO'}")
        print(f"  Animations: {'YES' if ds.animations.micro_enabled else 'NO'}")
        print(f"  Scroll Reveal: {'YES' if ds.animations.scroll_reveal else 'NO'}")
        
        print("\n" + "=" * 60 + "\n")


# ---- Test ----

def test_design_token_engine():
    """Test the design token engine"""
    
    print("\n" + "=" * 60)
    print("DESIGN TOKEN ENGINE TEST")
    print("=" * 60)
    
    engine = DesignTokenEngine(use_llm_refinement=False)
    
    test_prompts = [
        "Build a dark purple SaaS dashboard with glassmorphism and Inter font",
        "Create a light blue e-commerce store with minimal design",
        "Make a modern portfolio with orange accent and 3D animations",
        "Build a corporate admin panel with slate colors and clean design",
    ]
    
    for prompt in test_prompts:
        print(f"\n{'-' * 50}")
        print(f"Prompt: '{prompt[:60]}...'")
        
        ds = engine.generate(prompt)
        engine.display_design_system(ds)
        
        # Show generated CSS sample
        print("  CSS Variables (sample):")
        css = ds.to_full_css()
        for line in css.split("\n")[:8]:
            print(f"    {line}")
        print("    ...")
    
    print("\nDesign Token Engine test complete")
    
    return engine


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_design_token_engine()