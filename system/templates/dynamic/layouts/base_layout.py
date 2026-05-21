"""
NOVARYX - Base Layout
Abstract layout that all layouts extend.

Defines the slot system for dynamic component injection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import re


class LayoutType(Enum):
    """Types of base layouts available"""
    DASHBOARD = "dashboard"
    LANDING = "landing"
    ECOMMERCE = "ecommerce"
    ADMIN = "admin"
    PORTFOLIO = "portfolio"
    AI_STARTUP = "ai_startup"


@dataclass
class LayoutSlot:
    """
    A named slot in a layout where components can be injected.
    
    The AI selects components for each slot based on the prompt.
    """
    name: str
    description: str
    allowed_component_types: List[str]  # What kinds of components go here
    required: bool = True
    max_components: int = 10
    grid_area: Optional[str] = None  # CSS grid area name
    default_component: Optional[str] = None  # Fallback if nothing assigned
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "allowed_types": self.allowed_component_types,
            "required": self.required,
            "max_components": self.max_components,
            "grid_area": self.grid_area,
            "default": self.default_component
        }


@dataclass
class LayoutConfig:
    """Configuration for a specific layout instance"""
    layout_type: LayoutType
    theme: Any = None  # DesignSystem from token engine
    responsive_breakpoints: Dict[str, int] = field(default_factory=lambda: {
        "sm": 640,
        "md": 768,
        "lg": 1024,
        "xl": 1280,
        "2xl": 1536
    })
    container_max_width: str = "1280px"
    sidebar_width: str = "280px"
    header_height: str = "64px"


class BaseLayout(ABC):
    """
    Abstract base for all layouts.
    
    Every layout defines:
    - Its slots (where components go)
    - Its grid structure (CSS Grid)
    - Responsive behavior
    - Theme integration
    """
    
    def __init__(self, config: LayoutConfig = None):
        self.config = config or LayoutConfig(layout_type=self.layout_type)
        self._slots: Dict[str, LayoutSlot] = {}
        self._assigned_components: Dict[str, List[str]] = {}  # slot_name → [component_ids]
        self._define_slots()
    
    @property
    @abstractmethod
    def layout_type(self) -> LayoutType:
        """Which layout type this is"""
        pass
    
    @property
    @abstractmethod
    def layout_name(self) -> str:
        """Human-readable layout name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """What this layout is used for"""
        pass
    
    @abstractmethod
    def _define_slots(self):
        """Define all slots for this layout"""
        pass
    
    def add_slot(self, slot: LayoutSlot):
        """Add a slot to the layout"""
        self._slots[slot.name] = slot
        self._assigned_components[slot.name] = []
    
    def get_slot(self, name: str) -> Optional[LayoutSlot]:
        """Get a slot by name"""
        return self._slots.get(name)
    
    def get_all_slots(self) -> List[LayoutSlot]:
        """Get all slots"""
        return list(self._slots.values())
    
    def get_required_slots(self) -> List[LayoutSlot]:
        """Get slots that must be filled"""
        return [s for s in self._slots.values() if s.required]
    
    def get_empty_slots(self) -> List[LayoutSlot]:
        """Get slots with no components assigned"""
        return [s for s in self._slots.values() if len(self._assigned_components.get(s.name, [])) == 0]
    
    def assign_component(self, slot_name: str, component_id: str) -> bool:
        """Assign a component to a slot"""
        if slot_name not in self._slots:
            return False
        
        slot = self._slots[slot_name]
        current = self._assigned_components[slot_name]
        
        if len(current) >= slot.max_components:
            return False
        
        current.append(component_id)
        return True
    
    def get_slot_components(self, slot_name: str) -> List[str]:
        """Get components assigned to a slot"""
        return self._assigned_components.get(slot_name, [])
    
    def generate_grid_css(self) -> str:
        """Generate CSS Grid for this layout"""
        return ""
    
    def generate_layout_tsx(self, design_system=None) -> str:
        """Generate the React layout component with slots"""
        return ""
    
    def get_safe_project_name(self, design_system) -> str:
        """Get a safe, camelCased project name for React components"""
        if not design_system or not design_system.project_name:
            return "App"
        
        # Remove non-alphanumeric, split by spaces/dashes
        words = re.split(r'[^a-zA-Z0-9]+', design_system.project_name)
        # Capitalize and join
        return "".join(word.capitalize() for word in words if word)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize layout for storage/RAG"""
        return {
            "type": self.layout_type.value,
            "name": self.layout_name,
            "description": self.description,
            "slots": {name: slot.to_dict() for name, slot in self._slots.items()},
            "assigned_components": self._assigned_components
        }
    
    def is_ready(self) -> bool:
        """Check if all required slots are filled"""
        for slot in self.get_required_slots():
            if len(self._assigned_components.get(slot.name, [])) == 0:
                return False
        return True
    
    def get_missing_components(self) -> List[str]:
        """Get list of required slots that need components"""
        missing = []
        for slot in self.get_required_slots():
            if len(self._assigned_components.get(slot.name, [])) == 0:
                missing.append(slot.name)
        return missing
    
    def display_layout(self):
        """Display layout structure"""
        print(f"\n{'='*50}")
        print(f"LAYOUT: {self.layout_name}")
        print(f"   Type: {self.layout_type.value}")
        print(f"   Description: {self.description}")
        print(f"   Slots: {len(self._slots)}")
        print(f"   Components assigned: {sum(len(v) for v in self._assigned_components.values())}")
        print(f"   Ready: {'YES' if self.is_ready() else 'NO'}")
        
        if not self.is_ready():
            missing = self.get_missing_components()
            print(f"   Missing: {', '.join(missing)}")
        
        print(f"\n   Slots:")
        for name, slot in self._slots.items():
            assigned = len(self._assigned_components.get(name, []))
            required = "(REQ)" if slot.required else "(OPT)"
            print(f"      {required} {name}: {assigned} components")
            print(f"         Allowed: {', '.join(slot.allowed_component_types)}")
        
        print(f"{'='*50}\n")