"""
NOVARYX - Agent Router
Routes tasks to the right specialized agent based on task type.
"""

import logging
from typing import Dict, List, Optional
from .agent_core import Agent, AgentCapability, AgentTask, AgentMessage
from .specialized_agents import (
    ArchitectAgent, FrontendAgent, BackendAgent,
    DesignAgent, ContentAgent, RepairAgent, ReviewAgent
)

logger = logging.getLogger("novaryx.agent_router")


class AgentRouter:
    """
    Routes tasks to the most capable agent.
    
    Task type mapping:
      architecture → ArchitectAgent
      frontend → FrontendAgent
      backend → BackendAgent
      design → DesignAgent
      content → ContentAgent
      repair → RepairAgent
      review → ReviewAgent
    """
    
    TASK_ROUTING = {
        "architecture": "architect",
        "plan_architecture": "architect",
        "design_routes": "architect",
        "design_schema": "architect",
        "design_data_model": "architect",
        
        "frontend": "frontend",
        "generate_component": "frontend",
        "generate_page": "frontend",
        "generate_hook": "frontend",
        "generate_style": "frontend",
        
        "backend": "backend",
        "generate_collection": "backend",
        "generate_migration": "backend",
        "generate_api": "backend",
        "generate_auth": "backend",
        
        "design": "design",
        "generate_theme": "design",
        "generate_tokens": "design",
        "generate_animation": "design",
        "generate_3d": "design",
        
        "content": "content",
        "generate_copy": "content",
        "generate_seo": "content",
        
        "repair": "repair",
        "fix_bug": "repair",
        "fix_syntax": "repair",
        "fix_import": "repair",
        "fix_type": "repair",
        
        "review": "review",
        "review_code": "review",
        "quality_check": "review",
        "security_check": "review",
    }
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._init_agents()
    
    def _init_agents(self):
        """Initialize all specialized agents"""
        self.agents["architect"] = ArchitectAgent()
        self.agents["frontend"] = FrontendAgent()
        self.agents["backend"] = BackendAgent()
        self.agents["design"] = DesignAgent()
        self.agents["content"] = ContentAgent()
        self.agents["repair"] = RepairAgent()
        self.agents["review"] = ReviewAgent()
        
        logger.info(f"AgentRouter initialized with {len(self.agents)} agents")
    
    def route_task(self, task: AgentTask) -> Optional[Agent]:
        """Route a task to the best agent"""
        
        # Direct routing by task type
        agent_id = self.TASK_ROUTING.get(task.task_type)
        
        if agent_id and agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent.status.value != "busy":
                if agent.assign_task(task):
                    logger.info(f"Task {task.task_id} → {agent_id}")
                    return agent
        
        # Find best available agent by skill match
        best_agent = None
        best_score = 0
        
        for agent_id, agent in self.agents.items():
            if agent.status.value == "busy":
                continue
            
            score = self._match_score(task, agent)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if best_agent and best_agent.assign_task(task):
            logger.info(f"Task {task.task_id} → {best_agent.agent_id} (score: {best_score})")
            return best_agent
        
        logger.warning(f"No available agent for task: {task.task_type}")
        return None
    
    def _match_score(self, task: AgentTask, agent: Agent) -> int:
        """Score how well an agent matches a task"""
        score = 0
        task_lower = task.task_type.lower()
        
        for skill in agent.capability.skills:
            if skill in task_lower:
                score += 3
            if skill in task.prompt.lower():
                score += 1
        
        return score
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        return list(self.agents.values())
    
    def get_available_agents(self) -> List[Agent]:
        return [a for a in self.agents.values() if a.status.value != "busy"]
    
    def get_agent_stats(self) -> List[Dict]:
        return [a.get_stats() for a in self.agents.values()]
    
    def broadcast_message(self, message: AgentMessage, exclude: List[str] = None):
        """Send a message to all agents"""
        exclude = exclude or []
        for agent_id, agent in self.agents.items():
            if agent_id not in exclude:
                agent.receive_message(message)