"""
NOVARYX - Trust Scoring
Tracks the reliability of generated modules to apply dynamic validation depth.
Autonomous software engineering requires prioritizing review on unstable artifacts.
"""

import logging
from typing import Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger("novaryx.trust_scoring")

@dataclass
class ModuleTrustProfile:
    file_path: str
    stability_score: float = 1.0  # 1.0 = perfect, 0.0 = completely unstable
    repair_count: int = 0
    confidence_score: float = 1.0
    history: list = field(default_factory=list)
    
    def record_repair(self, bugs_fixed: int, severity_weight: float = 0.1):
        """Records a repair event and docks trust score accordingly."""
        self.repair_count += bugs_fixed
        self.stability_score = max(0.0, self.stability_score - (bugs_fixed * severity_weight))
        self.history.append(f"Fixed {bugs_fixed} bugs. Score docked to {self.stability_score:.2f}")

    @property
    def requires_deep_validation(self) -> bool:
        """If trust is below 0.7, trigger multi-stage deep validation."""
        return self.stability_score < 0.7


class TrustRegistry:
    """Central registry tracking all module trust profiles during a generation run."""
    
    def __init__(self):
        self.profiles: Dict[str, ModuleTrustProfile] = {}
        
    def get_profile(self, file_path: str) -> ModuleTrustProfile:
        if file_path not in self.profiles:
            self.profiles[file_path] = ModuleTrustProfile(file_path=file_path)
        return self.profiles[file_path]
        
    def get_trust_score(self, file_path: str) -> float:
        """Returns the stability score for a module, defaults to 1.0."""
        if file_path not in self.profiles:
            return 1.0
        return self.profiles[file_path].stability_score
        
    def record_validation_pass(self, file_path: str):
        """Boosts trust score for passing a validation stage cleanly."""
        prof = self.get_profile(file_path)
        prof.stability_score = min(1.0, prof.stability_score + 0.05)
        
    def record_repair(self, file_path: str, bugs_fixed: int):
        prof = self.get_profile(file_path)
        prof.record_repair(bugs_fixed)
        
    def get_unstable_modules(self) -> list:
        """Returns all modules heavily flagged by the repair orchestrator."""
        return [p for p in self.profiles.values() if p.requires_deep_validation]
    
    def summarize(self) -> Dict[str, Any]:
        unstable = len(self.get_unstable_modules())
        total = len(self.profiles)
        avg = sum(p.stability_score for p in self.profiles.values()) / max(1, total)
        return {
            "total_modules_tracked": total,
            "unstable_modules": unstable,
            "average_system_trust": avg
        }
