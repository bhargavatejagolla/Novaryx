"""
NOVARYX - Agent Orchestrator
THE central coordinator for all agents.

Manages:
- Task distribution across agents
- Parallel execution
- Agent communication
- Performance monitoring
- Result aggregation
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .agent_core import Agent, AgentTask, AgentMessage, MessageType, AgentStatus
from .agent_router import AgentRouter
from .parallel_executor import ParallelExecutor
from .performance_monitor import PerformanceMonitor

logger = logging.getLogger("novaryx.agent_orchestrator")


class AgentOrchestrator:
    """
    Central orchestrator for the multi-agent system.
    
    Coordinates all specialized agents to work together.
    """
    
    def __init__(self, max_parallel: int = 3):
        self.router = AgentRouter()
        self.executor = ParallelExecutor(max_workers=max_parallel)
        self.monitor = PerformanceMonitor()
        self.generation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"AgentOrchestrator initialized (max_parallel={max_parallel})")
    
    def run_pipeline(self, prompt: str, context: Dict = None) -> Dict[str, Any]:
        """
        Run the complete agent pipeline for a generation.
        
        Pipeline:
          Architect → [Frontend + Backend + Design in parallel] → 
          Content → [Review + Repair in parallel] → Complete
        """
        
        context = context or {}
        
        print("\n" + "=" * 70)
        print("🤖 AGENT ORCHESTRATOR")
        print("=" * 70)
        print(f"   Pipeline: Architect → Agents → Review → Complete")
        print(f"   Agents: {len(self.router.agents)} ready")
        print("=" * 70)
        
        results = {}
        
        # ================================================
        # STAGE 1: Architect plans everything
        # ================================================
        print(f"\n📐 Stage 1: Architect Planning...")
        arch_task = AgentTask(
            task_type="plan_architecture",
            prompt=prompt,
            context=context,
            priority=10
        )
        
        arch_agent = self.router.route_task(arch_task)
        if arch_agent:
            arch_result = arch_agent.run_task(arch_task)
            results["architecture"] = arch_result
            
            # Update context with architecture
            context.update(arch_result)
            print(f"   ✅ Architecture planned")
            
            self.monitor.record_task(
                arch_agent.agent_id, arch_agent.capability.name,
                "error" not in arch_result, 0
            )
        
        # ================================================
        # STAGE 2: Parallel generation
        # ================================================
        print(f"\n⚡ Stage 2: Parallel Generation...")
        
        parallel_tasks = []
        
        # Frontend tasks
        pages = context.get("routes", [])
        if pages:
            for page in pages[:3]:  # Generate up to 3 pages in parallel
                parallel_tasks.append({
                    "task_type": "generate_page",
                    "prompt": f"Generate page: {page.get('path', '/')} - {page.get('component', 'Page')}",
                    "context": {**context, "page": page}
                })
        else:
            parallel_tasks.append({
                "task_type": "generate_page",
                "prompt": f"Generate main dashboard page for: {prompt}",
                "context": context
            })
        
        # Backend task
        parallel_tasks.append({
            "task_type": "generate_collection",
            "prompt": f"Generate database schema for: {prompt}",
            "context": context,
            "priority": 8
        })
        
        # Design task
        parallel_tasks.append({
            "task_type": "generate_theme",
            "prompt": f"Generate design system for: {prompt}",
            "context": context,
            "priority": 6
        })
        
        parallel_results = self.executor.execute_parallel(parallel_tasks, self.router)
        results["parallel"] = parallel_results
        
        success_count = sum(1 for r in parallel_results.values() if "error" not in r)
        print(f"   ✅ {success_count}/{len(parallel_tasks)} parallel tasks completed")
        
        # ================================================
        # STAGE 3: Content generation
        # ================================================
        print(f"\n📝 Stage 3: Content Generation...")
        content_task = AgentTask(
            task_type="generate_copy",
            prompt=prompt,
            context=context,
            priority=5
        )
        
        content_agent = self.router.route_task(content_task)
        if content_agent:
            content_result = content_agent.run_task(content_task)
            results["content"] = content_result
            print(f"   ✅ Content generated")
        
        # ================================================
        # STAGE 4: Review & Repair
        # ================================================
        print(f"\n🔍 Stage 4: Review & Repair...")
        
        review_tasks = []
        for task_id, result in parallel_results.items():
            if "code" in result:
                review_tasks.append({
                    "task_type": "review_code",
                    "prompt": "Review generated code for quality",
                    "context": {"code": result.get("code", ""), "task_id": task_id}
                })
        
        if review_tasks:
            review_results = self.executor.execute_parallel(review_tasks, self.router)
            results["reviews"] = review_results
            
            # Repair any failed reviews
            for task_id, review in review_results.items():
                if not review.get("approved", True):
                    repair_task = AgentTask(
                        task_type="fix_bug",
                        prompt="Fix issues found in review",
                        context={"review": review, "code": parallel_results.get(task_id, {}).get("code", "")},
                        priority=9
                    )
                    repair_agent = self.router.route_task(repair_task)
                    if repair_agent:
                        repair_result = repair_agent.run_task(repair_task)
                        results[f"repair_{task_id}"] = repair_result
            
            print(f"   ✅ Review complete")
        
        # ================================================
        # FINAL: Aggregate results
        # ================================================
        print(f"\n" + "=" * 70)
        print("✅ AGENT PIPELINE COMPLETE")
        print("=" * 70)
        
        # Display performance
        self.monitor.display_report()
        
        return {
            "generation_id": self.generation_id,
            "prompt": prompt,
            "results": results,
            "agents_used": len(self.router.agents),
            "completed_at": datetime.now().isoformat(),
        }
    
    def shutdown(self):
        """Shutdown the orchestrator"""
        self.executor.shutdown()
        logger.info("Agent orchestrator shut down")


# ---- Test ----

def test_agent_orchestrator():
    """Test the complete agent orchestration system"""
    
    print("\n" + "=" * 70)
    print("🧪 AGENT ORCHESTRATOR TEST")
    print("=" * 70)
    
    orchestrator = AgentOrchestrator(max_parallel=2)
    
    result = orchestrator.run_pipeline(
        prompt="Build a dark purple SaaS dashboard with analytics and user management",
        context={"project_type": "saas_dashboard"}
    )
    
    print(f"\n   Pipeline completed: {result['generation_id']}")
    print(f"   Results: {list(result['results'].keys())}")
    
    orchestrator.shutdown()
    
    print("\n✅ Agent Orchestrator test complete")
    
    return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_agent_orchestrator()