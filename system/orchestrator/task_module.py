from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class ModuleType(Enum):
    FRONTEND_LAYOUT = "frontend_layout"
    FRONTEND_PAGE = "frontend_page"
    FRONTEND_COMPONENT = "frontend_component"
    BACKEND_SCHEMA = "backend_schema"
    BACKEND_API = "backend_api"
    AUTH = "auth"
    CONFIG = "config"
    FULLSTACK = "fullstack"

@dataclass
class Submodule:
    """Represents a discrete, independently generatable chunk of the project."""
    module_id: str
    name: str
    type: ModuleType
    description: str
    dependencies: List[str] = field(default_factory=list)
    files_expected: List[str] = field(default_factory=list)
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # State tracking
    status: str = "pending"  # pending, generating, validating, repaired, complete, failed
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "dependencies": self.dependencies,
            "files_expected": self.files_expected,
            "status": self.status
        }

@dataclass
class ProjectArchitecture:
    """The master DAG (Directed Acyclic Graph) of submodules for a project."""
    project_name: str
    modules: Dict[str, Submodule] = field(default_factory=dict)
    generation_order: List[str] = field(default_factory=list)
    
    def add_module(self, module: Submodule):
        self.modules[module.module_id] = module
        
    def resolve_order(self):
        """Topological sort to determine the optimal generation order based on dependencies."""
        visited = set()
        temp_mark = set()
        order = []
        
        def visit(node_id):
            if node_id in temp_mark:
                raise ValueError(f"Circular dependency detected involving module: {node_id}")
            if node_id not in visited:
                temp_mark.add(node_id)
                module = self.modules.get(node_id)
                if module:
                    for dep in module.dependencies:
                        if dep in self.modules:
                            visit(dep)
                temp_mark.remove(node_id)
                visited.add(node_id)
                order.append(node_id)
                
        for m_id in self.modules:
            if m_id not in visited:
                visit(m_id)
                
        self.generation_order = order
        return order
