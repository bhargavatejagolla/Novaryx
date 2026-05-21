"""
NOVARYX - Agent Router
Routes tasks to appropriate agents based on task type and requirements.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger("novaryx.agent_router")


class AgentType(Enum):
    """Types of agents in the system"""
    ARCHITECT = "architect"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DESIGN = "design"
    CONTENT = "content"
    SEO = "seo"
    SECURITY = "security"
    REPAIR = "repair"
    VERIFICATION = "verification"


class AgentCapability:
    """What an agent can do"""
    
    def __init__(
        self,
        agent_type: AgentType,
        model_role: str,
        description: str,
        tasks: List[str]
    ):
        self.agent_type = agent_type
        self.model_role = model_role  # Maps to inference provider role
        self.description = description
        self.tasks = tasks


class AgentRouter:
    """
    Routes generation tasks to the correct agents.
    
    Knows which agent handles which part of generation,
    and which model to use for each agent.
    """
    
    # Agent registry with capabilities and model mapping
    AGENTS = {
        AgentType.ARCHITECT: AgentCapability(
            agent_type=AgentType.ARCHITECT,
            model_role="planning",
            description="Architecture planning and system design",
            tasks=["plan_architecture", "design_routes", "design_schema", "design_components"]
        ),
        AgentType.FRONTEND: AgentCapability(
            agent_type=AgentType.FRONTEND,
            model_role="generation",
            description="Frontend page and component generation",
            tasks=["generate_pages", "generate_components", "generate_styles", "generate_hooks"]
        ),
        AgentType.BACKEND: AgentCapability(
            agent_type=AgentType.BACKEND,
            model_role="generation",
            description="Backend schema and API generation",
            tasks=["generate_schema", "generate_api", "generate_migrations", "generate_auth"]
        ),
        AgentType.DESIGN: AgentCapability(
            agent_type=AgentType.DESIGN,
            model_role="generation",
            description="UI/UX design and styling",
            tasks=["generate_styles", "generate_animations", "generate_3d", "generate_theme"]
        ),
        AgentType.REPAIR: AgentCapability(
            agent_type=AgentType.REPAIR,
            model_role="repair",
            description="Bug fixing and code repair",
            tasks=["fix_syntax", "fix_imports", "fix_types", "fix_routes", "fix_build"]
        ),
        AgentType.VERIFICATION: AgentCapability(
            agent_type=AgentType.VERIFICATION,
            model_role="repair",
            description="Code verification and validation",
            tasks=["verify_syntax", "verify_imports", "verify_types", "verify_routes", "verify_build"]
        )
    }
    
    def __init__(self):
        self.agent_instances: Dict[AgentType, Any] = {}
    
    def get_agent_for_task(self, task_name: str) -> Optional[AgentCapability]:
        """Find the right agent for a specific task"""
        for agent_type, capability in self.AGENTS.items():
            if task_name in capability.tasks:
                return capability
        
        logger.warning(f"No agent found for task: {task_name}")
        return None
    
    def get_model_role_for_task(self, task_name: str) -> str:
        """Get which model role to use for a task"""
        agent = self.get_agent_for_task(task_name)
        if agent:
            return agent.model_role
        
        # Default to generation model
        return "generation"
    
    def get_agent_for_phase(self, phase: str) -> List[AgentCapability]:
        """
        Get all agents needed for a generation phase.
        
        Phases: planning, generation, verification, repair
        """
        phase_agents = {
            "planning": [AgentType.ARCHITECT],
            "generation": [AgentType.FRONTEND, AgentType.BACKEND, AgentType.DESIGN],
            "verification": [AgentType.VERIFICATION],
            "repair": [AgentType.REPAIR],
            "all": list(AgentType)
        }
        
        agent_types = phase_agents.get(phase, [AgentType.FRONTEND])
        return [self.AGENTS[at] for at in agent_types if at in self.AGENTS]
    
    def route_generation(
        self,
        task_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route a generation request to the appropriate agent.
        
        Args:
            task_type: Type of generation needed
            context: Generation context
        
        Returns:
            Routing information including which agent and model to use
        """
        agent = self.get_agent_for_task(task_type)
        
        if not agent:
            return {
                "agent": "default",
                "model_role": "generation",
                "task_type": task_type,
                "error": f"No agent for task: {task_type}"
            }
        
        return {
            "agent": agent.agent_type.value,
            "model_role": agent.model_role,
            "task_type": task_type,
            "description": agent.description,
            "context": context
        }
    
    def get_generation_order(self, project_type: str) -> List[Dict[str, Any]]:
        """
        Get the ordered list of generation tasks for a project type.
        
        This defines WHAT gets generated and in WHAT ORDER.
        """
        
        # Standard generation order for any project
        generation_order = [
            {
                "phase": "planning",
                "tasks": [
                    {"task": "plan_architecture", "agent": "architect", "model": "planning"},
                    {"task": "design_routes", "agent": "architect", "model": "planning"},
                    {"task": "design_schema", "agent": "architect", "model": "planning"}
                ]
            },
            {
                "phase": "generation",
                "tasks": [
                    {"task": "generate_theme", "agent": "design", "model": "generation"},
                    {"task": "generate_styles", "agent": "design", "model": "generation"},
                    {"task": "generate_pages", "agent": "frontend", "model": "generation"},
                    {"task": "generate_components", "agent": "frontend", "model": "generation"},
                    {"task": "generate_hooks", "agent": "frontend", "model": "generation"},
                    {"task": "generate_schema", "agent": "backend", "model": "generation"},
                    {"task": "generate_api", "agent": "backend", "model": "generation"}
                ]
            },
            {
                "phase": "verification",
                "tasks": [
                    {"task": "verify_syntax", "agent": "verification", "model": "repair"},
                    {"task": "verify_imports", "agent": "verification", "model": "repair"},
                    {"task": "verify_types", "agent": "verification", "model": "repair"},
                    {"task": "verify_routes", "agent": "verification", "model": "repair"}
                ]
            },
            {
                "phase": "repair",
                "tasks": [
                    {"task": "fix_syntax", "agent": "repair", "model": "repair"},
                    {"task": "fix_imports", "agent": "repair", "model": "repair"},
                    {"task": "fix_types", "agent": "repair", "model": "repair"}
                ]
            }
        ]
        
        return generation_order
    
    def display_agents(self):
        """Display all registered agents"""
        print("\n" + "=" * 60)
        print("🤖 NOVARYX AGENT REGISTRY")
        print("=" * 60)
        
        for agent_type, capability in self.AGENTS.items():
            print(f"\n  📌 {agent_type.value.upper()} Agent")
            print(f"     Model: {capability.model_role}")
            print(f"     Description: {capability.description}")
            print(f"     Tasks: {', '.join(capability.tasks)}")
        
        print("\n" + "=" * 60 + "\n")