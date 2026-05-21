"""
NOVARYX - Live Build Graph
Tracks dependencies between modules and manages incremental rebuilds.
"""

import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("novaryx.build_graph")

@dataclass
class ModuleNode:
    id: str
    name: str
    path: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    is_dirty: bool = True
    last_hash: str = ""

class BuildGraph:
    """
    Representation of the project's module dependency graph.
    """
    
    def __init__(self):
        self.nodes: Dict[str, ModuleNode] = {}
        
    def add_module(self, module_id: str, name: str, path: str, dependencies: List[str] = None):
        """Add a module and link its dependencies."""
        if module_id not in self.nodes:
            self.nodes[module_id] = ModuleNode(id=module_id, name=name, path=path)
            
        if dependencies:
            for dep_id in dependencies:
                self.nodes[module_id].dependencies.add(dep_id)
                # Link back for reverse lookup
                if dep_id in self.nodes:
                    self.nodes[dep_id].dependents.add(module_id)
        
    def mark_dirty(self, module_id: str):
        """Recursively mark module and all its dependents as dirty."""
        if module_id not in self.nodes:
            return
            
        node = self.nodes[module_id]
        if not node.is_dirty:
            node.is_dirty = True
            logger.info(f"Marking module dirty: {module_id}")
            for dependent_id in node.dependents:
                self.mark_dirty(dependent_id)
                
    def get_dirty_modules(self) -> List[ModuleNode]:
        """Return all modules that need a rebuild."""
        return [node for node in self.nodes.values() if node.is_dirty]
        
    def get_generation_order(self) -> List[str]:
        """Simple topological sort for generation."""
        visited = set()
        order = []
        
        def visit(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for dep in self.nodes[node_id].dependencies:
                if dep in self.nodes:
                    visit(dep)
            order.append(node_id)
            
        for node_id in self.nodes:
            visit(node_id)
            
        return order
