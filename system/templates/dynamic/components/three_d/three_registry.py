"""
NOVARYX - 3D Component Registry
Registers all 3D components with metadata for AI selection and configuration.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ThreeComponentMeta:
    """Metadata for a 3D component"""
    component_id: str
    name: str
    description: str
    keywords: List[str]
    allowed_layouts: List[str]
    allowed_slots: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    performance_tier: str = "medium"  # low, medium, high
    has_gpu_fallback: bool = True
    min_polygons: int = 1000
    max_polygons: int = 50000
    
    def matches_prompt(self, prompt: str) -> bool:
        prompt_lower = prompt.lower()
        for kw in self.keywords:
            if kw.lower() in prompt_lower:
                return True
        return False
    
    def get_config(self, theme_colors: Dict[str, str] = None) -> Dict[str, Any]:
        """Generate configuration with theme colors applied"""
        config = dict(self.parameters)
        if theme_colors:
            config["primary_color"] = theme_colors.get("primary", "#6366f1")
            config["accent_color"] = theme_colors.get("accent", "#06b6d4")
            config["background_color"] = theme_colors.get("background", "#0f0f1a")
        return config


class ThreeRegistry:
    """Registry of all 3D components the AI can select from"""
    
    COMPONENTS: Dict[str, ThreeComponentMeta] = {
        "globe": ThreeComponentMeta(
            component_id="globe",
            name="3D Globe",
            description="Rotating Earth globe with customizable markers, arcs, and atmosphere glow. Perfect for showing global user locations or data points.",
            keywords=["globe", "earth", "world", "global", "planet", "sphere", "map", "3d globe"],
            allowed_layouts=["dashboard", "landing", "portfolio"],
            allowed_slots=["hero", "main", "content"],
            parameters={
                "rotation_speed": 0.3,
                "marker_count": 20,
                "arc_count": 5,
                "atmosphere_enabled": True,
                "auto_rotate": True,
                "globe_scale": 1.0,
            },
            performance_tier="medium",
            max_polygons=30000
        ),
        "particles": ThreeComponentMeta(
            component_id="particles",
            name="Particle Field",
            description="Interactive 3D particle network with mouse interaction. Particles connect with lines when near each other. Great for hero backgrounds and tech-focused designs.",
            keywords=["particle", "particles", "network", "mesh", "dots", "nodes", "connections", "web"],
            allowed_layouts=["dashboard", "landing", "portfolio"],
            allowed_slots=["hero", "main"],
            parameters={
                "particle_count": 500,
                "connection_distance": 2.0,
                "particle_size": 0.05,
                "speed": 0.2,
                "mouse_interaction": True,
                "color_mode": "gradient",
            },
            performance_tier="low",
            max_polygons=5000
        ),
        "card_3d": ThreeComponentMeta(
            component_id="card_3d",
            name="3D Tilt Card",
            description="Card with 3D perspective tilt effect following mouse movement. Multiple layers create parallax depth. Use for pricing cards, feature showcases, or product displays.",
            keywords=["3d card", "tilt", "perspective", "parallax card", "depth card", "floating card"],
            allowed_layouts=["landing", "portfolio", "ecommerce"],
            allowed_slots=["features", "pricing", "projects", "products"],
            parameters={
                "tilt_amount": 15,
                "glare_enabled": True,
                "glare_opacity": 0.15,
                "scale_on_hover": 1.03,
                "layers": 3,
                "border_glow": True,
            },
            performance_tier="low",
            max_polygons=2000
        ),
        "hero_scene": ThreeComponentMeta(
            component_id="hero_scene",
            name="3D Hero Scene",
            description="Full-screen 3D hero background with animated geometry, lighting, and post-processing. Creates immersive first impressions for landing pages and portfolios.",
            keywords=["3d hero", "hero 3d", "3d background", "animated background", "scene", "immersive"],
            allowed_layouts=["landing", "portfolio"],
            allowed_slots=["hero"],
            parameters={
                "geometry_type": "torus",
                "rotation_speed": 0.5,
                "lighting_mode": "studio",
                "post_processing": True,
                "fog_enabled": True,
                "camera_auto_rotate": True,
            },
            performance_tier="high",
            max_polygons=40000
        ),
        "waves": ThreeComponentMeta(
            component_id="waves",
            name="Wave Background",
            description="Animated 3D wave mesh with flowing movement. Subtle background effect that adds depth without distracting. Ideal for section backgrounds and page transitions.",
            keywords=["wave", "waves", "ocean", "flow", "liquid", "sine wave", "animated wave"],
            allowed_layouts=["dashboard", "landing", "portfolio", "admin"],
            allowed_slots=["hero", "main", "stats"],
            parameters={
                "wave_count": 5,
                "amplitude": 1.0,
                "frequency": 0.5,
                "speed": 0.3,
                "color_mode": "solid",
                "wireframe": False,
            },
            performance_tier="low",
            max_polygons=8000
        ),
    }
    
    @classmethod
    def get_component(cls, component_id: str) -> Optional[ThreeComponentMeta]:
        return cls.COMPONENTS.get(component_id)
    
    @classmethod
    def find_by_prompt(cls, prompt: str) -> List[ThreeComponentMeta]:
        """Find 3D components matching prompt keywords"""
        scored = []
        for comp in cls.COMPONENTS.values():
            score = sum(1 for kw in comp.keywords if kw.lower() in prompt.lower())
            if score > 0:
                scored.append((score, comp))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [comp for _, comp in scored]
    
    @classmethod
    def find_for_slot(cls, slot_name: str) -> List[ThreeComponentMeta]:
        """Find 3D components compatible with a slot"""
        return [c for c in cls.COMPONENTS.values() if slot_name in c.allowed_slots]
    
    @classmethod
    def detect_3d_in_prompt(cls, prompt: str) -> Optional[ThreeComponentMeta]:
        """Detect if prompt wants 3D and return best component"""
        matches = cls.find_by_prompt(prompt)
        return matches[0] if matches else None
    
    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": c.component_id,
                "name": c.name,
                "keywords": c.keywords[:4],
                "performance": c.performance_tier,
                "layouts": c.allowed_layouts,
            }
            for c in cls.COMPONENTS.values()
        ]
    
    @classmethod
    def display_registry(cls):
        """Display all 3D components"""
        print("\n" + "=" * 60)
        print("3D COMPONENT REGISTRY")
        print("=" * 60)
        for comp in cls.COMPONENTS.values():

            print(f"\n  [PERF: {comp.performance_tier}] {comp.name}")
            print(f"     ID: {comp.component_id}")
            print(f"     Perf: {comp.performance_tier} | Polygons: <={comp.max_polygons:,}")
            print(f"     Keywords: {', '.join(comp.keywords[:5])}")
            print(f"     Layouts: {', '.join(comp.allowed_layouts)}")
            print(f"     Slots: {', '.join(comp.allowed_slots)}")
        print("\n" + "=" * 60 + "\n")


# ---- Test ----

def test_three_registry():
    """Test 3D component registry"""
    print("\n" + "=" * 60)
    print("3D REGISTRY TEST")
    print("=" * 60)
    
    ThreeRegistry.display_registry()
    
    test_prompts = [
        "dashboard with 3D globe showing user locations",
        "landing page with particle animation background",
        "portfolio with 3D hero scene and tilt cards",
        "saas dashboard with animated wave background",
        "create a pricing page with 3d card effects",
    ]
    
    for prompt in test_prompts:
        matches = ThreeRegistry.find_by_prompt(prompt)
        best = matches[0] if matches else None
        print(f"\nPROMPT: '{prompt[:60]}...'")
        if best:
            print(f"   - Selects: {best.name}")
            print(f"   - Performance: {best.performance_tier}")
        else:
            print(f"   - No 3D component detected")
    
    print("\nDONE: 3D Registry test complete")


if __name__ == "__main__":
    test_three_registry()