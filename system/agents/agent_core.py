"""
NOVARYX - Agent Core
Base agent class, message protocol, and capability definitions.
"""

import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger("novaryx.agents")


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


class MessageType(Enum):
    TASK = "task"
    RESULT = "result"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"
    STATUS = "status"
    CANCEL = "cancel"


@dataclass
class AgentCapability:
    """What an agent can do"""
    name: str
    description: str
    skills: List[str]
    model_role: str  # Which LLM model to use
    priority: int = 1
    max_parallel_tasks: int = 1


@dataclass
class AgentMessage:
    """Message passed between agents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    from_agent: str = ""
    to_agent: str = ""
    type: MessageType = MessageType.TASK
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 1
    requires_response: bool = False
    response_to: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "priority": self.priority,
        }


@dataclass
class AgentTask:
    """A task assigned to an agent"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_id: str = ""
    task_type: str = ""
    prompt: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    deadline: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    assigned_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 2


class Agent(ABC):
    """
    Base agent class. All specialized agents extend this.
    
    Every agent has:
    - A specific capability (what it does)
    - A message inbox/outbox
    - Status tracking
    - Performance metrics
    """
    
    def __init__(self, agent_id: str, capability: AgentCapability):
        self.agent_id = agent_id
        self.capability = capability
        self.status = AgentStatus.IDLE
        self.inbox: List[AgentMessage] = []
        self.outbox: List[AgentMessage] = []
        self.current_task: Optional[AgentTask] = None
        self.completed_tasks: List[AgentTask] = []
        self.failed_tasks: List[AgentTask] = []
        self.started_at = datetime.now()
        
        # Performance
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_time_ms = 0.0
        self.tokens_used = 0
        
        self._inference = None
    
    def _get_inference(self):
        """Get LLM inference provider"""
        if self._inference is None:
            try:
                from system.inference.provider_factory import get_provider
                self._inference = get_provider()
            except Exception as e:
                logger.error(f"Agent {self.agent_id}: Inference unavailable: {e}")
        return self._inference
    
    def receive_message(self, message: AgentMessage):
        """Receive a message from another agent"""
        self.inbox.append(message)
        logger.debug(f"Agent {self.agent_id} received: {message.type.value} from {message.from_agent}")
    
    def send_message(self, to_agent: str, msg_type: MessageType, content: Dict, priority: int = 1) -> AgentMessage:
        """Send a message to another agent"""
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            type=msg_type,
            content=content,
            priority=priority
        )
        self.outbox.append(message)
        return message
    
    def assign_task(self, task: AgentTask) -> bool:
        """Assign a task to this agent"""
        if self.status == AgentStatus.BUSY:
            return False
        
        self.current_task = task
        task.agent_id = self.agent_id
        task.assigned_at = datetime.now().isoformat()
        task.status = "assigned"
        self.status = AgentStatus.BUSY
        return True
    
    @abstractmethod
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        """Execute the assigned task. Must be implemented by each agent."""
        pass
    
    def run_task(self, task: AgentTask) -> Dict[str, Any]:
        """Run a task with timing and error handling"""
        start_time = time.time()
        task.started_at = datetime.now().isoformat()
        
        try:
            result = self.execute(task)
            
            elapsed = (time.time() - start_time) * 1000
            task.completed_at = datetime.now().isoformat()
            task.result = result
            task.status = "completed"
            
            self.tasks_completed += 1
            self.total_time_ms += elapsed
            self.status = AgentStatus.IDLE
            self.completed_tasks.append(task)
            
            logger.info(f"Agent {self.agent_id}: Task {task.task_id} completed in {elapsed:.0f}ms")
            
            return result
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            task.status = "failed"
            
            self.tasks_failed += 1
            self.status = AgentStatus.ERROR
            self.failed_tasks.append(task)
            
            logger.error(f"Agent {self.agent_id}: Task {task.task_id} failed: {e}")
            
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                logger.info(f"Agent {self.agent_id}: Retrying task {task.task_id} ({task.retry_count}/{task.max_retries})")
                return self.run_task(task)
            
            return {"error": str(e), "status": "failed"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        avg_time = self.total_time_ms / max(self.tasks_completed, 1)
        return {
            "agent_id": self.agent_id,
            "type": self.capability.name,
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "success_rate": f"{(self.tasks_completed / max(self.tasks_completed + self.tasks_failed, 1)) * 100:.0f}%",
            "avg_time_ms": f"{avg_time:.0f}",
            "total_tokens": self.tokens_used,
            "uptime_minutes": f"{(datetime.now() - self.started_at).total_seconds() / 60:.0f}",
        }
    
    def __repr__(self):
        return f"Agent({self.agent_id}, {self.capability.name}, {self.status.value})"