"""
NOVARYX - Component Inspector
Inspects and displays component properties, code, and relationships.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("novaryx.component_inspector")


class ComponentInspector:
    """Inspects components for properties and code"""
    
    def __init__(self):
        self._registry = None
    
    def _get_registry(self):
        if self._registry is None:
            try:
                from system.templates.dynamic.components.component_registry import ComponentRegistry
                self._registry = ComponentRegistry
            except Exception:
                pass
        return self._registry
    
    def inspect(self, component_id: str) -> Dict[str, Any]:
        """Get full component inspection"""
        registry = self._get_registry()
        if not registry:
            return {"error": "Registry not available"}
        
        comp = registry.get_component(component_id)
        if not comp:
            return {"error": f"Component not found: {component_id}"}
        
        code = registry.get_component_tsx(component_id)
        
        # Extract properties from code
        props = self._extract_props(code or "")
        
        # Find related components
        related = self._find_related(component_id)
        
        return {
            "id": comp.component_id,
            "name": comp.name,
            "type": comp.component_type,
            "description": comp.description,
            "keywords": comp.keywords,
            "layouts": comp.allowed_layouts,
            "slots": comp.allowed_slots,
            "props": props,
            "code": code[:5000] if code else "",
            "code_length": len(code) if code else 0,
            "has_3d": comp.has_3d,
            "complexity": comp.complexity,
            "dependencies": comp.required_deps,
            "related_components": related,
        }
    
    def _extract_props(self, code: str) -> List[Dict]:
        """Extract props interface from component code"""
        props = []
        lines = code.split("\n")
        in_interface = False
        
        for line in lines:
            line = line.strip()
            if "interface" in line and "Props" in line:
                in_interface = True
                continue
            if in_interface:
                if line == "}" or line == "};":
                    break
                if ":" in line and not line.startswith("//"):
                    parts = line.split(":")
                    if len(parts) >= 2:
                        prop_name = parts[0].strip().replace("?", "")
                        prop_type = parts[1].strip().replace(";", "").strip()
                        props.append({
                            "name": prop_name,
                            "type": prop_type,
                            "optional": "?" in parts[0],
                        })
        
        return props
    
    def _find_related(self, component_id: str) -> List[str]:
        """Find related components"""
        try:
            from system.templates.dynamic.template_intelligence import TemplateIntelligence
            ti = TemplateIntelligence(use_llm=False, use_rag=False)
            return ti.component_relationships.get(component_id, [])[:5]
        except Exception:
            return []
    
    def get_all_props_summary(self) -> Dict[str, List]:
        """Get props summary for all components"""
        registry = self._get_registry()
        if not registry:
            return {}
        
        summary = {}
        for comp_id in registry.COMPONENTS:
            inspection = self.inspect(comp_id)
            summary[comp_id] = {
                "name": inspection.get("name", comp_id),
                "props_count": len(inspection.get("props", [])),
                "props": inspection.get("props", []),
            }
        
        return summary