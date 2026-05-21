"""
NOVARYX - Parallel Executor
Executes multiple agent tasks simultaneously for faster generation.
"""

import logging
import concurrent.futures
from typing import Dict, List, Callable, Any
from datetime import datetime

logger = logging.getLogger("novaryx.parallel_executor")


class ParallelExecutor:
    """
    Executes agent tasks in parallel using thread pools.
    
    Enables:
    - Multiple pages generated simultaneously
    - Multiple components generated at once
    - Backend + Frontend in parallel
    """
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.results: Dict[str, Any] = {}
        self.active_tasks: Dict[str, concurrent.futures.Future] = {}
    
    def execute_parallel(
        self,
        tasks: List[Dict],
        agent_router
    ) -> Dict[str, Any]:
        """
        Execute multiple tasks in parallel.
        
        Args:
            tasks: List of {task_type, prompt, context}
            agent_router: AgentRouter instance
        
        Returns:
            Dict of task_id → result
        """
        
        from .agent_core import AgentTask
        
        results = {}
        futures = {}
        
        # Create and submit all tasks
        for i, task_data in enumerate(tasks):
            task = AgentTask(
                task_type=task_data.get("task_type", "generate"),
                prompt=task_data.get("prompt", ""),
                context=task_data.get("context", {}),
                priority=task_data.get("priority", 1)
            )
            
            agent = agent_router.route_task(task)
            
            if agent:
                future = self.executor.submit(agent.run_task, task)
                futures[task.task_id] = (future, agent, task)
                logger.info(f"Submitted parallel task: {task.task_id} → {agent.agent_id}")
            else:
                results[task.task_id] = {"error": "No available agent"}
        
        # Collect results
        for task_id, (future, agent, task) in futures.items():
            try:
                result = future.result(timeout=300)  # 5 min timeout
                results[task_id] = result
                logger.info(f"Parallel task {task_id} completed")
            except Exception as e:
                results[task_id] = {"error": str(e)}
                logger.error(f"Parallel task {task_id} failed: {e}")
        
        return results
    
    def execute_batch(
        self,
        task_type: str,
        items: List[Dict],
        agent_router,
        context: Dict = None
    ) -> List[Dict]:
        """
        Execute the same task type on multiple items in parallel.
        
        Example: Generate 5 pages simultaneously.
        """
        
        tasks = []
        for item in items:
            tasks.append({
                "task_type": task_type,
                "prompt": item.get("prompt", item.get("name", "")),
                "context": {**(context or {}), **(item.get("context", {}))},
                "priority": item.get("priority", 1)
            })
        
        return self.execute_parallel(tasks, agent_router)
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)
        logger.info("Parallel executor shut down")
    
    def get_active_count(self) -> int:
        return len(self.active_tasks)


# ---- Test ----

def test_parallel_executor():
    """Test parallel execution"""
    from .agent_router import AgentRouter
    
    print("\n" + "=" * 60)
    print("🧪 PARALLEL EXECUTOR TEST")
    print("=" * 60)
    
    router = AgentRouter()
    executor = ParallelExecutor(max_workers=2)
    
    tasks = [
        {
            "task_type": "generate_component",
            "prompt": "Create a dashboard stats card component with purple theme",
            "context": {"component_type": "stats_card"}
        },
        {
            "task_type": "generate_component",
            "prompt": "Create a sidebar navigation component with icons",
            "context": {"component_type": "sidebar"}
        },
    ]
    
    print(f"\n   Executing {len(tasks)} tasks in parallel...")
    results = executor.execute_parallel(tasks, router)
    
    print(f"\n   Results: {len(results)} tasks")
    for task_id, result in results.items():
        status = "✅" if "error" not in result else "❌"
        print(f"      {status} {task_id}: {list(result.keys())}")
    
    executor.shutdown()
    
    print("\n✅ Parallel Executor test complete")
    
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s', datefmt='%H:%M:%S')
    test_parallel_executor()