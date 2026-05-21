"""
NOVARYX - Performance Monitor
Tracks agent performance, success rates, and bottlenecks.
"""

import time
import logging
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger("novaryx.perf_monitor")


@dataclass
class AgentMetrics:
    """Performance metrics for a single agent"""
    agent_id: str
    agent_type: str
    tasks_total: int = 0
    tasks_succeeded: int = 0
    tasks_failed: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    tokens_used: int = 0
    last_active: str = ""
    errors: List[str] = field(default_factory=list)


class PerformanceMonitor:
    """
    Monitors and reports on agent performance.
    
    Tracks:
    - Success/failure rates per agent
    - Average execution time
    - Token usage
    - Bottleneck detection
    """
    
    def __init__(self):
        self.metrics: Dict[str, AgentMetrics] = {}
        self.session_start = datetime.now()
        self.total_tasks = 0
        self.total_success = 0
        self.total_failure = 0
    
    def record_task(self, agent_id: str, agent_type: str, success: bool, duration_ms: float, tokens: int = 0, error: str = None):
        """Record a completed task"""
        
        if agent_id not in self.metrics:
            self.metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_type=agent_type
            )
        
        metrics = self.metrics[agent_id]
        metrics.tasks_total += 1
        metrics.total_time_ms += duration_ms
        metrics.avg_time_ms = metrics.total_time_ms / metrics.tasks_total
        metrics.tokens_used += tokens
        metrics.last_active = datetime.now().isoformat()
        
        if success:
            metrics.tasks_succeeded += 1
            self.total_success += 1
        else:
            metrics.tasks_failed += 1
            self.total_failure += 1
            if error:
                metrics.errors.append(error)
        
        self.total_tasks += 1
    
    def get_agent_report(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed report for a specific agent"""
        metrics = self.metrics.get(agent_id)
        if not metrics:
            return {}
        
        success_rate = (metrics.tasks_succeeded / max(metrics.tasks_total, 1)) * 100
        
        return {
            "agent_id": metrics.agent_id,
            "type": metrics.agent_type,
            "tasks": metrics.tasks_total,
            "success_rate": f"{success_rate:.1f}%",
            "avg_time": f"{metrics.avg_time_ms:.0f}ms",
            "total_tokens": metrics.tokens_used,
            "recent_errors": metrics.errors[-3:] if metrics.errors else [],
            "last_active": metrics.last_active,
        }
    
    def get_overall_report(self) -> Dict[str, Any]:
        """Get overall system performance report"""
        
        overall_success = (self.total_success / max(self.total_tasks, 1)) * 100
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        # Find bottlenecks (agents with lowest success rate)
        bottlenecks = []
        for agent_id, metrics in self.metrics.items():
            rate = (metrics.tasks_succeeded / max(metrics.tasks_total, 1)) * 100
            if rate < 80 and metrics.tasks_total > 2:
                bottlenecks.append({
                    "agent": agent_id,
                    "success_rate": f"{rate:.0f}%",
                    "avg_time": f"{metrics.avg_time_ms:.0f}ms"
                })
        
        return {
            "session_duration": f"{session_duration:.0f}s",
            "total_tasks": self.total_tasks,
            "total_success": self.total_success,
            "total_failure": self.total_failure,
            "overall_success_rate": f"{overall_success:.1f}%",
            "active_agents": len(self.metrics),
            "bottlenecks": bottlenecks,
            "agents": {aid: self.get_agent_report(aid) for aid in self.metrics}
        }
    
    def display_report(self):
        """Display performance report"""
        report = self.get_overall_report()
        
        print("\n" + "=" * 60)
        print("📊 AGENT PERFORMANCE REPORT")
        print("=" * 60)
        print(f"   Session: {report['session_duration']}")
        print(f"   Tasks: {report['total_tasks']} total")
        print(f"   Success: {report['total_success']} ({report['overall_success_rate']})")
        print(f"   Failed: {report['total_failure']}")
        print(f"   Active Agents: {report['active_agents']}")
        
        if report['bottlenecks']:
            print(f"\n   ⚠️  Bottlenecks:")
            for b in report['bottlenecks']:
                print(f"      - {b['agent']}: {b['success_rate']} success, {b['avg_time']} avg")
        
        print(f"\n   Agent Details:")
        for aid, agent_report in report['agents'].items():
            print(f"      {agent_report['type']}: {agent_report['tasks']} tasks, {agent_report['success_rate']}, {agent_report['avg_time']}")
        
        print("=" * 60)