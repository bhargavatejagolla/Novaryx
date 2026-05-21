"""
NOVARYX - Agent Orchestration System
Multi-agent coordination for parallel, specialized generation.

Architecture:
  Orchestrator → Agent Router → Specialized Agents → Parallel Execution
  
Agents:
  - Architect Agent: System design & planning
  - Frontend Agent: UI components & pages
  - Backend Agent: Database & API
  - Design Agent: Visual design & theming
  - Content Agent: Copy & content
  - Repair Agent: Debug & fix
  - Review Agent: Quality review
"""

from .agent_core import Agent, AgentStatus, AgentMessage, AgentCapability
from .agent_orchestrator import AgentOrchestrator
from .agent_router import AgentRouter
from .specialized_agents import (
    ArchitectAgent,
    FrontendAgent,
    BackendAgent,
    DesignAgent,
    ContentAgent,
    RepairAgent,
    ReviewAgent,
)
from .parallel_executor import ParallelExecutor
from .performance_monitor import PerformanceMonitor

__all__ = [
    "Agent",
    "AgentStatus",
    "AgentMessage",
    "AgentCapability",
    "AgentOrchestrator",
    "AgentRouter",
    "ArchitectAgent",
    "FrontendAgent",
    "BackendAgent",
    "DesignAgent",
    "ContentAgent",
    "RepairAgent",
    "ReviewAgent",
    "ParallelExecutor",
    "PerformanceMonitor",
]