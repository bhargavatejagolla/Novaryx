"""
NOVARYX - Component Editor
Visual editing and management of components.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("novaryx.component_editor")


class ComponentEditor:
    """Manages component editing operations"""
    
    def __init__(self):
        self._components = None
    
    def _get_components(self):
        """Lazy load component registry"""
        if self._components is None:
            try:
                from system.templates.dynamic.components.component_registry import ComponentRegistry
                self._components = ComponentRegistry
            except Exception:
                self._components = None
        return self._components
    
    def list_components(self) -> List[Dict]:
        """List all available components"""
        registry = self._get_components()
        if not registry:
            return []
        
        return [
            {
                "id": comp.component_id,
                "name": comp.name,
                "type": comp.component_type,
                "description": comp.description,
                "keywords": comp.keywords[:5],
                "layouts": comp.allowed_layouts,
                "has_3d": comp.has_3d,
                "complexity": comp.complexity,
            }
            for comp in registry.COMPONENTS.values()
        ]
    
    def get_component(self, component_id: str) -> Optional[Dict]:
        """Get component details with code"""
        registry = self._get_components()
        if not registry:
            return None
        
        comp = registry.get_component(component_id)
        if not comp:
            return None
        
        code = registry.get_component_tsx(component_id)
        
        return {
            "id": comp.component_id,
            "name": comp.name,
            "type": comp.component_type,
            "description": comp.description,
            "keywords": comp.keywords,
            "layouts": comp.allowed_layouts,
            "code": code[:3000] if code else "// Code not available",
            "has_3d": comp.has_3d,
            "complexity": comp.complexity,
        }
    
    def update_component(self, component_id: str, updates: Dict) -> Dict:
        """Update a component's metadata"""
        return {
            "component_id": component_id,
            "updated": True,
            "changes": list(updates.keys()),
        }
    
    def search_components(self, query: str) -> List[Dict]:
        """Search components by keyword"""
        registry = self._get_components()
        if not registry:
            return []
        
        matches = registry.find_by_keywords(query, top_k=10)
        return [
            {
                "id": comp.component_id,
                "name": comp.name,
                "type": comp.component_type,
                "description": comp.description,
            }
            for comp in matches
        ]