"""
NOVARYX - Animation Registry
Central registry of all animation presets. AI selects based on prompt and design tokens.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class AnimationCategory(Enum):
    PAGE_TRANSITION = "page_transition"
    SCROLL_REVEAL = "scroll_reveal"
    MICRO_INTERACTION = "micro_interaction"
    LOADING = "loading"
    STAGGER = "stagger"
    HERO = "hero"
    THREE_D = "three_d"


@dataclass
class AnimationPreset:
    """A single animation preset that the AI can select"""
    preset_id: str
    name: str
    category: AnimationCategory
    description: str
    framer_motion_props: Dict[str, Any] = field(default_factory=dict)
    css_class: str = ""
    keywords: List[str] = field(default_factory=list)
    performance_tier: str = "low"  # low, medium, high
    duration_seconds: float = 0.4
    easing: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    
    def to_framer_motion(self, custom: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate Framer Motion props with optional overrides"""
        props = dict(self.framer_motion_props)
        if custom:
            props.update(custom)
        return props
    
    def to_tailwind(self) -> str:
        """Generate Tailwind CSS classes"""
        return self.css_class


class AnimationRegistry:
    """Complete animation system registry"""
    
    # ---- Page Transitions ----
    PAGE_TRANSITIONS = {
        "fade": AnimationPreset(
            preset_id="page_fade",
            name="Fade Transition",
            category=AnimationCategory.PAGE_TRANSITION,
            description="Smooth fade in/out between pages",
            framer_motion_props={
                "initial": {"opacity": 0},
                "animate": {"opacity": 1},
                "exit": {"opacity": 0},
                "transition": {"duration": 0.3}
            },
            keywords=["fade", "smooth", "gentle", "simple transition"],
            duration_seconds=0.3
        ),
        "fade_slide": AnimationPreset(
            preset_id="page_fade_slide",
            name="Fade + Slide",
            category=AnimationCategory.PAGE_TRANSITION,
            description="Fade combined with vertical slide for depth",
            framer_motion_props={
                "initial": {"opacity": 0, "y": 20},
                "animate": {"opacity": 1, "y": 0},
                "exit": {"opacity": 0, "y": -20},
                "transition": {"duration": 0.35, "ease": "easeInOut"}
            },
            keywords=["slide", "fade slide", "smooth slide", "modern transition"],
            duration_seconds=0.35
        ),
        "scale": AnimationPreset(
            preset_id="page_scale",
            name="Scale Transition",
            category=AnimationCategory.PAGE_TRANSITION,
            description="Scale up with fade for dramatic effect",
            framer_motion_props={
                "initial": {"opacity": 0, "scale": 0.95},
                "animate": {"opacity": 1, "scale": 1},
                "exit": {"opacity": 0, "scale": 0.95},
                "transition": {"duration": 0.4, "ease": "easeOut"}
            },
            keywords=["scale", "zoom", "dramatic", "bold transition"],
            duration_seconds=0.4
        ),
        "none": AnimationPreset(
            preset_id="page_none",
            name="No Transition",
            category=AnimationCategory.PAGE_TRANSITION,
            description="Instant page changes, no animation",
            framer_motion_props={
                "initial": {},
                "animate": {},
                "exit": {}
            },
            keywords=["none", "instant", "no animation", "static"],
            duration_seconds=0
        ),
    }
    
    # ---- Scroll Reveals ----
    SCROLL_REVEALS = {
        "fade_up": AnimationPreset(
            preset_id="scroll_fade_up",
            name="Fade Up",
            category=AnimationCategory.SCROLL_REVEAL,
            description="Elements fade in and slide up as they enter viewport",
            framer_motion_props={
                "initial": {"opacity": 0, "y": 40},
                "whileInView": {"opacity": 1, "y": 0},
                "viewport": {"once": True, "margin": "-80px"},
                "transition": {"duration": 0.6, "ease": "easeOut"}
            },
            keywords=["fade up", "reveal", "scroll reveal", "appear"],
            duration_seconds=0.6
        ),
        "fade_in": AnimationPreset(
            preset_id="scroll_fade_in",
            name="Fade In",
            category=AnimationCategory.SCROLL_REVEAL,
            description="Pure fade in without movement",
            framer_motion_props={
                "initial": {"opacity": 0},
                "whileInView": {"opacity": 1},
                "viewport": {"once": True, "margin": "-60px"},
                "transition": {"duration": 0.5}
            },
            keywords=["fade in", "simple reveal", "subtle"],
            duration_seconds=0.5
        ),
        "slide_left": AnimationPreset(
            preset_id="scroll_slide_left",
            name="Slide from Left",
            category=AnimationCategory.SCROLL_REVEAL,
            description="Elements slide in from the left",
            framer_motion_props={
                "initial": {"opacity": 0, "x": -60},
                "whileInView": {"opacity": 1, "x": 0},
                "viewport": {"once": True, "margin": "-80px"},
                "transition": {"duration": 0.6, "ease": "easeOut"}
            },
            keywords=["slide left", "from left", "enter left"],
            duration_seconds=0.6
        ),
        "slide_right": AnimationPreset(
            preset_id="scroll_slide_right",
            name="Slide from Right",
            category=AnimationCategory.SCROLL_REVEAL,
            description="Elements slide in from the right",
            framer_motion_props={
                "initial": {"opacity": 0, "x": 60},
                "whileInView": {"opacity": 1, "x": 0},
                "viewport": {"once": True, "margin": "-80px"},
                "transition": {"duration": 0.6, "ease": "easeOut"}
            },
            keywords=["slide right", "from right", "enter right"],
            duration_seconds=0.6
        ),
        "scale_in": AnimationPreset(
            preset_id="scroll_scale_in",
            name="Scale In",
            category=AnimationCategory.SCROLL_REVEAL,
            description="Elements scale up from smaller size",
            framer_motion_props={
                "initial": {"opacity": 0, "scale": 0.8},
                "whileInView": {"opacity": 1, "scale": 1},
                "viewport": {"once": True, "margin": "-60px"},
                "transition": {"duration": 0.5, "ease": "easeOut"}
            },
            keywords=["scale in", "grow", "pop in", "bounce in"],
            duration_seconds=0.5
        ),
    }
    
    # ---- Micro Interactions ----
    MICRO_INTERACTIONS = {
        "hover_lift": AnimationPreset(
            preset_id="micro_hover_lift",
            name="Hover Lift",
            category=AnimationCategory.MICRO_INTERACTION,
            description="Element lifts slightly on hover with shadow",
            framer_motion_props={
                "whileHover": {"y": -4, "boxShadow": "0 12px 40px rgba(0,0,0,0.3)"},
                "whileTap": {"y": 0, "scale": 0.98},
                "transition": {"type": "spring", "stiffness": 400, "damping": 25}
            },
            css_class="hover-lift",
            keywords=["hover lift", "elevate", "raise", "float"],
            duration_seconds=0.2
        ),
        "hover_glow": AnimationPreset(
            preset_id="micro_hover_glow",
            name="Hover Glow",
            category=AnimationCategory.MICRO_INTERACTION,
            description="Element glows on hover",
            framer_motion_props={
                "whileHover": {"boxShadow": "0 0 25px var(--primary)"},
                "transition": {"duration": 0.25}
            },
            css_class="hover-glow",
            keywords=["glow", "shine", "illuminate", "highlight"],
            duration_seconds=0.25
        ),
        "hover_scale": AnimationPreset(
            preset_id="micro_hover_scale",
            name="Hover Scale",
            category=AnimationCategory.MICRO_INTERACTION,
            description="Element scales up slightly on hover",
            framer_motion_props={
                "whileHover": {"scale": 1.05},
                "whileTap": {"scale": 0.97},
                "transition": {"type": "spring", "stiffness": 400, "damping": 17}
            },
            keywords=["scale hover", "grow hover", "enlarge"],
            duration_seconds=0.2
        ),
        "tap_bounce": AnimationPreset(
            preset_id="micro_tap_bounce",
            name="Tap Bounce",
            category=AnimationCategory.MICRO_INTERACTION,
            description="Button bounces on click",
            framer_motion_props={
                "whileTap": {"scale": 0.93},
                "transition": {"type": "spring", "stiffness": 500, "damping": 15}
            },
            keywords=["tap", "click", "bounce", "press"],
            duration_seconds=0.15
        ),
    }
    
    # ---- Stagger Animations ----
    STAGGERS = {
        "list_stagger": AnimationPreset(
            preset_id="stagger_list",
            name="List Stagger",
            category=AnimationCategory.STAGGER,
            description="Children animate in sequence with delay",
            framer_motion_props={
                "initial": "hidden",
                "animate": "visible",
                "variants": {
                    "hidden": {},
                    "visible": {"transition": {"staggerChildren": 0.08}}
                }
            },
            keywords=["stagger", "list", "sequence", "one by one", "cascade"],
            duration_seconds=0.5
        ),
        "grid_stagger": AnimationPreset(
            preset_id="stagger_grid",
            name="Grid Stagger",
            category=AnimationCategory.STAGGER,
            description="Grid items animate row by row",
            framer_motion_props={
                "initial": "hidden",
                "animate": "visible",
                "variants": {
                    "hidden": {},
                    "visible": {"transition": {"staggerChildren": 0.05, "delayChildren": 0.1}}
                }
            },
            keywords=["grid stagger", "cards stagger", "gallery"],
            duration_seconds=0.6
        ),
    }
    
    # ---- Loading Animations ----
    LOADERS = {
        "skeleton_pulse": AnimationPreset(
            preset_id="loader_skeleton_pulse",
            name="Skeleton Pulse",
            category=AnimationCategory.LOADING,
            description="Pulsing skeleton placeholder",
            framer_motion_props={},
            css_class="animate-pulse bg-[var(--surface-raised)] rounded",
            keywords=["skeleton", "pulse", "shimmer", "loading placeholder"],
            duration_seconds=1.5
        ),
        "spinner": AnimationPreset(
            preset_id="loader_spinner",
            name="Loading Spinner",
            category=AnimationCategory.LOADING,
            description="Spinning circle loader",
            framer_motion_props={
                "animate": {"rotate": 360},
                "transition": {"repeat": float("inf"), "duration": 1, "ease": "linear"}
            },
            css_class="spinner",
            keywords=["spinner", "loading circle", "wheel", "rotating"],
            duration_seconds=1.0
        ),
    }
    
    @classmethod
    def get_page_transition(cls, name: str) -> AnimationPreset:
        """Get page transition by name or keyword"""
        if name in cls.PAGE_TRANSITIONS:
            return cls.PAGE_TRANSITIONS[name]
        for preset in cls.PAGE_TRANSITIONS.values():
            if name.lower() in [k.lower() for k in preset.keywords]:
                return preset
        return cls.PAGE_TRANSITIONS["fade_slide"]  # Default
    
    @classmethod
    def get_scroll_reveal(cls, name: str) -> AnimationPreset:
        """Get scroll reveal by name or keyword"""
        if name in cls.SCROLL_REVEALS:
            return cls.SCROLL_REVEALS[name]
        for preset in cls.SCROLL_REVEALS.values():
            if name.lower() in [k.lower() for k in preset.keywords]:
                return preset
        return cls.SCROLL_REVEALS["fade_up"]
    
    @classmethod
    def get_micro_interaction(cls, name: str) -> AnimationPreset:
        """Get micro interaction by name or keyword"""
        if name in cls.MICRO_INTERACTIONS:
            return cls.MICRO_INTERACTIONS[name]
        for preset in cls.MICRO_INTERACTIONS.values():
            if name.lower() in [k.lower() for k in preset.keywords]:
                return preset
        return cls.MICRO_INTERACTIONS["hover_lift"]
    
    @classmethod
    def get_stagger(cls, name: str) -> AnimationPreset:
        """Get stagger animation"""
        return cls.STAGGERS.get(name, cls.STAGGERS["list_stagger"])
    
    @classmethod
    def get_loader(cls, name: str) -> AnimationPreset:
        """Get loading animation"""
        return cls.LOADERS.get(name, cls.LOADERS["skeleton_pulse"])
    
    @classmethod
    def detect_from_prompt(cls, prompt: str) -> Dict[str, str]:
        """
        Detect animation preferences from prompt.
        Returns animation names for each category.
        """
        prompt_lower = prompt.lower()
        
        result = {
            "page_transition": "fade_slide",
            "scroll_reveal": "fade_up",
            "micro_interaction": "hover_lift",
            "stagger": "list_stagger",
            "loader": "skeleton_pulse",
        }
        
        # Page transitions
        if any(w in prompt_lower for w in ["fade", "smooth"]):
            result["page_transition"] = "fade"
        if any(w in prompt_lower for w in ["slide", "modern"]):
            result["page_transition"] = "fade_slide"
        if any(w in prompt_lower for w in ["scale", "zoom", "dramatic"]):
            result["page_transition"] = "scale"
        if any(w in prompt_lower for w in ["no animation", "instant", "static"]):
            result["page_transition"] = "none"
        
        # Scroll reveals
        if any(w in prompt_lower for w in ["slide left", "from left"]):
            result["scroll_reveal"] = "slide_left"
        if any(w in prompt_lower for w in ["slide right", "from right"]):
            result["scroll_reveal"] = "slide_right"
        if any(w in prompt_lower for w in ["pop", "scale in", "bounce"]):
            result["scroll_reveal"] = "scale_in"
        
        # Micro interactions
        if any(w in prompt_lower for w in ["glow", "shine"]):
            result["micro_interaction"] = "hover_glow"
        if any(w in prompt_lower for w in ["scale hover", "grow"]):
            result["micro_interaction"] = "hover_scale"
        if any(w in prompt_lower for w in ["bounce", "spring"]):
            result["micro_interaction"] = "tap_bounce"
        
        return result
    
    @classmethod
    def generate_animation_config(cls, prompt: str, design_tokens: Any = None) -> Dict[str, Any]:
        """
        Generate complete animation configuration from prompt and design tokens.
        This is the main entry point for the AI.
        """
        detected = cls.detect_from_prompt(prompt)
        
        page_transition = cls.get_page_transition(detected["page_transition"])
        scroll_reveal = cls.get_scroll_reveal(detected["scroll_reveal"])
        micro = cls.get_micro_interaction(detected["micro_interaction"])
        stagger = cls.get_stagger(detected["stagger"])
        loader = cls.get_loader(detected["loader"])
        
        config = {
            "page_transition": {
                "name": page_transition.name,
                "props": page_transition.to_framer_motion(),
            },
            "scroll_reveal": {
                "name": scroll_reveal.name,
                "props": scroll_reveal.to_framer_motion(),
            },
            "micro_interaction": {
                "name": micro.name,
                "props": micro.to_framer_motion(),
            },
            "stagger": {
                "name": stagger.name,
                "props": stagger.to_framer_motion(),
            },
            "loader": {
                "name": loader.name,
                "css": loader.css_class,
            },
            "duration_scale": 1.0,  # Can be adjusted by design tokens
        }
        
        # Apply design token overrides if available
        if design_tokens and hasattr(design_tokens, 'animations'):
            anim_tokens = design_tokens.animations
            if hasattr(anim_tokens, 'page_duration'):
                try:
                    config["duration_scale"] = float(anim_tokens.page_duration.replace("s", "")) / 0.3
                except:
                    pass
        
        return config
    
    @classmethod
    def display_registry(cls):
        """Display all animation presets"""
        print("\n" + "=" * 60)
        print("ANIMATION REGISTRY")
        print("=" * 60)
        
        categories = {
            "Page Transitions": cls.PAGE_TRANSITIONS,
            "Scroll Reveals": cls.SCROLL_REVEALS,
            "Micro Interactions": cls.MICRO_INTERACTIONS,
            "Stagger Animations": cls.STAGGERS,
            "Loading Animations": cls.LOADERS,
        }
        
        for cat_name, presets in categories.items():
            print(f"\n  [{cat_name}]")
            for preset in presets.values():
                print(f"    - {preset.name}")
                print(f"       {preset.description[:70]}...")
                print(f"       Keywords: {', '.join(preset.keywords[:4])}")
        
        print("\n" + "=" * 60)
        total = sum(len(c) for c in [cls.PAGE_TRANSITIONS, cls.SCROLL_REVEALS, cls.MICRO_INTERACTIONS, cls.STAGGERS, cls.LOADERS])
        print(f"  Total: {total} animation presets")
        print("=" * 60 + "\n")


# ---- Test ----

def test_animation_registry():
    """Test the animation system"""
    print("\n" + "=" * 60)
    print("ANIMATION SYSTEM TEST")
    print("=" * 60)
    
    AnimationRegistry.display_registry()
    
    # Test prompt detection
    test_prompts = [
        "modern landing page with smooth fade transitions",
        "dashboard with slide-in panels and hover glow effects",
        "portfolio with dramatic scale animations and stagger reveals",
        "simple admin panel with no animations",
    ]
    
    for prompt in test_prompts:
        print(f"\nPROMPT: '{prompt[:60]}...'")
        config = AnimationRegistry.detect_from_prompt(prompt)
        print(f"   Page: {config['page_transition']}")
        print(f"   Scroll: {config['scroll_reveal']}")
        print(f"   Micro: {config['micro_interaction']}")
        print(f"   Stagger: {config['stagger']}")
    
    print("\nDONE: Animation System test complete")
    
    return AnimationRegistry


if __name__ == "__main__":
    test_animation_registry()