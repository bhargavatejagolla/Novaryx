"""
NOVARYX - Project Learning Engine
Learns from every generation - what works, what fails, what improves quality.

Combined with User Preference Learning for personalized output.
"""

import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter
from datetime import datetime

from .memory_store import MemoryStore, ProjectMemory

logger = logging.getLogger("novaryx.learning")


class LearningEngine:
    """
    Learns patterns from past generations to improve future ones.
    
    Tracks:
    - Which components produce the best results
    - Which color combinations users prefer
    - Which layouts work best for which project types
    - Common failure patterns to avoid
    - Success patterns to replicate
    """
    
    def __init__(self, memory_store: MemoryStore = None):
        self.memory_store = memory_store or MemoryStore()
        self.learning_data = self._load_learning_data()
    
    def _load_learning_data(self) -> Dict:
        """Load accumulated learning data"""
        return {
            "component_scores": {},       # component → avg quality
            "color_scores": {},           # color → avg quality
            "layout_scores": {},          # layout → avg quality by project type
            "success_patterns": [],       # patterns from successful projects
            "failure_patterns": [],       # patterns from failed projects
            "component_combos": {},       # component pairs that work well
            "style_preferences": {        # learned user preferences
                "preferred_colors": Counter(),
                "preferred_modes": Counter(),
                "preferred_fonts": Counter(),
                "preferred_layouts": Counter(),
                "preferred_animations": Counter(),
            },
            "last_updated": datetime.now().isoformat(),
        }
    
    def analyze_all(self) -> Dict[str, Any]:
        """Analyze all stored memories and extract patterns"""
        
        memories = list(self.memory_store.memories.values())
        
        if not memories:
            return {"message": "No memories to analyze", "ready": False}
        
        # Reset learning data
        self.learning_data = self._load_learning_data()
        
        successful = [m for m in memories if m.success]
        failed = [m for m in memories if not m.success]
        
        print(f"\n📊 Analyzing {len(memories)} projects...")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        
        # ---- Component Scoring ----
        print(f"\n   Scoring components...")
        comp_qualities = {}
        for mem in successful:
            for comp in mem.components_used:
                if comp not in comp_qualities:
                    comp_qualities[comp] = []
                comp_qualities[comp].append(mem.quality_score)
        
        for comp, scores in comp_qualities.items():
            self.learning_data["component_scores"][comp] = {
                "avg_quality": sum(scores) / len(scores),
                "usage_count": len(scores),
                "effectiveness": "high" if sum(scores) / len(scores) > 0.8 else "medium" if sum(scores) / len(scores) > 0.6 else "low"
            }
        
        # ---- Color Scoring ----
        print(f"   Scoring colors...")
        for mem in successful:
            if mem.primary_color:
                if mem.primary_color not in self.learning_data["color_scores"]:
                    self.learning_data["color_scores"][mem.primary_color] = []
                self.learning_data["color_scores"][mem.primary_color].append(mem.quality_score)
        
        for color, scores in self.learning_data["color_scores"].items():
            self.learning_data["color_scores"][color] = {
                "avg_quality": sum(scores) / len(scores),
                "usage_count": len(scores),
            }
        
        # ---- Layout Scoring by Project Type ----
        print(f"   Scoring layouts...")
        for mem in successful:
            key = f"{mem.project_type}_{mem.layout_type}"
            if key not in self.learning_data["layout_scores"]:
                self.learning_data["layout_scores"][key] = []
            self.learning_data["layout_scores"][key].append(mem.quality_score)
        
        # ---- Component Combinations ----
        print(f"   Finding component combinations...")
        combo_scores = {}
        for mem in successful:
            comps = sorted(mem.components_used)
            for i in range(len(comps)):
                for j in range(i + 1, len(comps)):
                    pair = f"{comps[i]}+{comps[j]}"
                    if pair not in combo_scores:
                        combo_scores[pair] = []
                    combo_scores[pair].append(mem.quality_score)
        
        # Keep top combos
        for pair, scores in combo_scores.items():
            if len(scores) >= 2:
                avg = sum(scores) / len(scores)
                if avg > 0.7:
                    self.learning_data["component_combos"][pair] = {
                        "avg_quality": avg,
                        "count": len(scores)
                    }
        
        # ---- Success Patterns ----
        print(f"   Extracting success patterns...")
        if successful:
            # Most common components in successful projects
            all_success_comps = []
            for mem in successful:
                all_success_comps.extend(mem.components_used)
            top_comps = Counter(all_success_comps).most_common(10)
            
            self.learning_data["success_patterns"] = [
                {"pattern": f"Component '{comp}' used in {count} successful projects", "confidence": count / len(successful)}
                for comp, count in top_comps
            ]
        
        # ---- Failure Patterns ----
        print(f"   Extracting failure patterns...")
        if failed:
            failure_reasons = []
            for mem in failed:
                if mem.bugs_found > mem.bugs_fixed:
                    failure_reasons.append(f"Unresolved bugs ({mem.bugs_found - mem.bugs_fixed} remaining)")
                if mem.quality_score < 0.4:
                    failure_reasons.append("Low quality score")
                if len(mem.components_used) > 15:
                    failure_reasons.append("Too many components (complexity)")
            
            self.learning_data["failure_patterns"] = [
                {"pattern": reason, "occurrences": count}
                for reason, count in Counter(failure_reasons).most_common(5)
            ]
        
        # ---- Style Preferences ----
        print(f"   Learning style preferences...")
        prefs = self.learning_data["style_preferences"]
        
        for mem in successful:
            if mem.primary_color:
                prefs["preferred_colors"][mem.primary_color] += 1
            if mem.mode:
                prefs["preferred_modes"][mem.mode] += 1
            if mem.font:
                prefs["preferred_fonts"][mem.font] += 1
            if mem.layout_type:
                prefs["preferred_layouts"][mem.layout_type] += 1
        
        self.learning_data["last_updated"] = datetime.now().isoformat()
        
        print(f"\n   ✅ Analysis complete!")
        
        return self.get_report()
    
    def get_component_score(self, component_id: str) -> float:
        """Get effectiveness score for a component"""
        data = self.learning_data["component_scores"].get(component_id, {})
        return data.get("avg_quality", 0.5)
    
    def get_best_components(self, project_type: str = None, top_k: int = 10) -> List[Tuple[str, float]]:
        """Get highest-scoring components"""
        scored = [
            (comp, data["avg_quality"])
            for comp, data in self.learning_data["component_scores"].items()
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
    
    def get_recommended_color(self) -> Optional[str]:
        """Get the user's most preferred color"""
        prefs = self.learning_data["style_preferences"]
        if prefs["preferred_colors"]:
            return prefs["preferred_colors"].most_common(1)[0][0]
        return None
    
    def get_recommended_mode(self) -> str:
        """Get the user's preferred mode"""
        prefs = self.learning_data["style_preferences"]
        if prefs["preferred_modes"]:
            return prefs["preferred_modes"].most_common(1)[0][0]
        return "dark"
    
    def get_recommended_font(self) -> str:
        """Get the user's preferred font"""
        prefs = self.learning_data["style_preferences"]
        if prefs["preferred_fonts"]:
            return prefs["preferred_fonts"].most_common(1)[0][0]
        return "Inter"
    
    def get_recommended_layout(self, project_type: str) -> Optional[str]:
        """Get best layout for a project type"""
        prefix = f"{project_type}_"
        best_score = 0
        best_layout = None
        
        for key, scores in self.learning_data["layout_scores"].items():
            if key.startswith(prefix):
                avg = sum(scores) / len(scores) if isinstance(scores, list) else scores
                if avg > best_score:
                    best_score = avg
                    best_layout = key[len(prefix):]
        
        return best_layout
    
    def get_personalized_defaults(self) -> Dict[str, Any]:
        """Get personalized default settings based on learned preferences"""
        return {
            "preferred_color": self.get_recommended_color() or "#6366f1",
            "preferred_mode": self.get_recommended_mode(),
            "preferred_font": self.get_recommended_font(),
            "preferred_layout": self.learning_data["style_preferences"]["preferred_layouts"].most_common(1)[0][0] if self.learning_data["style_preferences"]["preferred_layouts"] else "dashboard",
            "learning_ready": len(self.memory_store.memories) >= 3,
        }
    
    def get_report(self) -> Dict[str, Any]:
        """Get complete learning report"""
        prefs = self.learning_data["style_preferences"]
        
        return {
            "ready": len(self.memory_store.memories) >= 2,
            "projects_analyzed": len(self.memory_store.memories),
            "top_components": self.get_best_components(top_k=5),
            "top_color": self.get_recommended_color(),
            "preferred_mode": self.get_recommended_mode(),
            "preferred_font": self.get_recommended_font(),
            "success_patterns": self.learning_data["success_patterns"][:5],
            "failure_warnings": self.learning_data["failure_patterns"][:3],
            "component_combos_found": len(self.learning_data["component_combos"]),
            "style_profile": {
                "colors": dict(prefs["preferred_colors"].most_common(5)),
                "modes": dict(prefs["preferred_modes"].most_common(2)),
                "fonts": dict(prefs["preferred_fonts"].most_common(3)),
                "layouts": dict(prefs["preferred_layouts"].most_common(3)),
            },
            "last_updated": self.learning_data["last_updated"],
        }
    
    def display_report(self):
        """Display learning report"""
        report = self.get_report()
        
        print("\n" + "=" * 60)
        print("🧠 LEARNING ENGINE REPORT")
        print("=" * 60)
        
        if not report["ready"]:
            print("   Not enough data yet. Generate more projects.")
            return
        
        print(f"   Projects Analyzed: {report['projects_analyzed']}")
        print(f"\n   🏆 Top Components:")
        for comp, score in report["top_components"]:
            print(f"      - {comp}: {score:.0%} effectiveness")
        
        print(f"\n   🎨 Style Profile:")
        print(f"      Color: {report['top_color']}")
        print(f"      Mode: {report['preferred_mode']}")
        print(f"      Font: {report['preferred_font']}")
        
        if report["success_patterns"]:
            print(f"\n   ✅ Success Patterns:")
            for sp in report["success_patterns"][:3]:
                print(f"      - {sp['pattern']}")
        
        if report["failure_warnings"]:
            print(f"\n   ⚠️  Failure Warnings:")
            for fp in report["failure_warnings"]:
                print(f"      - {fp['pattern']}")
        
        print("=" * 60)


# ---- Test ----

def test_learning_engine():
    """Test the learning engine"""
    
    print("\n" + "=" * 60)
    print("🧪 LEARNING ENGINE TEST")
    print("=" * 60)
    
    from .memory_store import MemoryStore
    from .project_indexer import ProjectIndexer
    
    store = MemoryStore()
    indexer = ProjectIndexer(store)
    
    # Index sample projects
    test_projects = [
        ("PurpleDash", "saas_dashboard", ["sidebar", "stats_card", "chart_widget"], "#7c3aed", "dark", 0.85, True),
        ("BlueAnalytics", "saas_dashboard", ["sidebar", "chart_widget", "data_table"], "#3b82f6", "dark", 0.78, True),
        ("GreenLanding", "landing_page", ["navbar", "hero", "features_grid"], "#10b981", "light", 0.92, True),
        ("RedFail", "saas_dashboard", ["sidebar", "data_table"], "#ef4444", "dark", 0.35, False),
        ("PurpleDash2", "saas_dashboard", ["sidebar", "stats_card", "chart_widget", "data_table"], "#7c3aed", "dark", 0.88, True),
    ]
    
    for name, ptype, comps, color, mode, quality, success in test_projects:
        indexer.index_generation(
            prompt=f"Build a {color} {ptype}",
            project_name=name,
            project_type=ptype,
            design_system={"colors": {"primary": color}, "mode": mode},
            components=comps,
            success=success,
            quality_score=quality,
        )
    
    # Run learning
    engine = LearningEngine(store)
    engine.analyze_all()
    engine.display_report()
    
    # Test personalized defaults
    defaults = engine.get_personalized_defaults()
    print(f"\n   Personalized Defaults:")
    for key, value in defaults.items():
        print(f"      {key}: {value}")
    
    print("\n✅ Learning Engine test complete")
    
    return engine


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_learning_engine()