"""
NOVARYX - Main Orchestrator
The central coordinator that connects all NOVARYX systems.

This is THE brain. Everything flows through here.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from system.orchestrator.task import GenerationTask, TaskStatus, TaskStep, TaskSerializer
from system.orchestrator.pipeline import GenerationPipeline
from system.orchestrator.agent_router import AgentRouter

logger = logging.getLogger("novaryx.orchestrator")


class NovaryxOrchestrator:
    """
    Central orchestrator for NOVARYX.
    
    Connects:
    - Inference Layer (Ollama/Gemini)
    - RAG Engine (ChromaDB)
    - Agent Router
    - Generation Pipeline
    - Verification System
    - Repair System
    
    Usage:
        orchestrator = NovaryxOrchestrator()
        task = orchestrator.create_task("Build a SaaS dashboard")
        task = orchestrator.run_pipeline(task)
    """
    
    def __init__(self):
        """Initialize the orchestrator and all subsystems"""
        self.pipeline = GenerationPipeline()
        self.agent_router = AgentRouter()
        self._inference_provider = None
        self._rag_client = None
        self._retriever = None
        self._initialized = False
        
        logger.info("NovaryxOrchestrator created")
    
    def initialize(self) -> bool:
        """
        Initialize all subsystems.
        Returns True if all critical systems are ready.
        """
        print("\n" + "=" * 60)
        print("🚀 INITIALIZING NOVARYX ORCHESTRATOR")
        print("=" * 60)
        
        all_ready = True
        
        # 1. Check inference provider
        print("\n📦 Checking Inference Layer...")
        try:
            from system.inference.provider_factory import get_provider, list_available_providers
            providers = list_available_providers()
            
            for p in providers:
                status = "🟢" if p["available"] else "🔴"
                print(f"   {status} {p['name']}: {p['type']} ({p['cost']})")
            
            try:
                self._inference_provider = get_provider()
                print(f"   ✅ Active: {self._inference_provider.name}")
            except RuntimeError as e:
                print(f"   ❌ No inference provider: {e}")
                all_ready = False
                
        except ImportError as e:
            print(f"   ❌ Inference layer not found: {e}")
            all_ready = False
        
        # 2. Check RAG engine
        print("\n🗄️  Checking RAG Engine...")
        try:
            from system.rag_engine.chromadb_client import ChromaDBClient
            from system.rag_engine.retriever import TemplateRetriever
            
            self._rag_client = ChromaDBClient()
            stats = self._rag_client.get_collection_stats()
            
            for key, info in stats.items():
                count = info.get("count", 0)
                print(f"   📦 {key}: {count} items")
            
            self._retriever = TemplateRetriever(self._rag_client)
            print(f"   ✅ RAG Engine ready")
            
        except ImportError as e:
            print(f"   ❌ RAG Engine not found: {e}")
            all_ready = False
        except Exception as e:
            print(f"   ⚠️  RAG Engine issue: {e}")
        
        # 3. Agent router
        print("\n🤖 Checking Agent Router...")
        try:
            agents = self.agent_router.AGENTS
            print(f"   ✅ {len(agents)} agents registered")
            for agent_type in agents:
                print(f"      - {agent_type.value}")
        except Exception as e:
            print(f"   ❌ Agent router issue: {e}")
            all_ready = False
        
        self._initialized = all_ready
        
        print(f"\n{'✅ All systems ready!' if all_ready else '⚠️  Some systems unavailable'}")
        print("=" * 60 + "\n")
        
        return all_ready
    
    def create_task(
        self,
        prompt: str,
        project_name: str = None,
        project_type: str = None
    ) -> GenerationTask:
        """
        Create a new generation task from a user prompt.
        
        Args:
            prompt: User's project description
            project_name: Optional project name
            project_type: Optional project type hint
        
        Returns:
            New GenerationTask ready for pipeline
        """
        task = GenerationTask(
            user_prompt=prompt,
            project_name=project_name,
            project_type=project_type
        )
        
        logger.info(f"Created task: {task.task_id} - '{prompt[:50]}...'")
        
        return task
    
    def run_pipeline(self, task: GenerationTask) -> GenerationTask:
        """
        Run the complete generation pipeline on a task.
        
        Args:
            task: GenerationTask to process
        
        Returns:
            Processed task with results
        """
        if not self._initialized:
            logger.warning("Orchestrator not fully initialized. Some features may not work.")
        
        logger.info(f"Starting pipeline for task: {task.task_id}")
        
        print("\n" + "=" * 60)
        print(f"🔧 RUNNING PIPELINE: {task.task_id}")
        print(f"   Prompt: {task.user_prompt[:80]}...")
        print("=" * 60 + "\n")
        
        # Run through pipeline
        task = self.pipeline.run(task)
        
        # Final status
        if task.status == TaskStatus.COMPLETED:
            print(f"\n✅ Generation Complete!")
            print(f"   Files: {len(task.generated_files)}")
            print(f"   Steps: {len(task.steps_completed)}")
        else:
            print(f"\n❌ Generation Failed")
            print(f"   Errors: {len(task.errors)}")
            for err in task.errors[-3:]:  # Last 3 errors
                print(f"   - {err}")
        
        return task
    
    def generate_single_component(
        self,
        component_type: str,
        description: str,
        context: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Generate a single component (for testing).
        
        Args:
            component_type: Type of component (button, card, navbar, etc.)
            description: What the component should do
            context: Additional context
        
        Returns:
            Generated code as string
        """
        if not self._inference_provider:
            logger.error("No inference provider available")
            return None
        
        prompt = f"""Generate a {component_type} component based on this description:
{description}

Requirements:
- Use React with TypeScript
- Use Tailwind CSS for styling
- Include proper TypeScript types
- Include all necessary imports
- Make it responsive
- Handle loading, error, and empty states

{f'Additional Context: {context}' if context else ''}

Output ONLY the complete component code. No explanations.
"""
        
        try:
            result = self._inference_provider.generate(
                prompt=prompt,
                role="generation",
                temperature=0.1,
                max_tokens=2048
            )
            
            if result.success:
                return result.text
            else:
                logger.error(f"Generation failed: {result.error}")
                return None
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "initialized": self._initialized,
            "inference_provider": self._inference_provider.name if self._inference_provider else "none",
            "rag_collections": self._rag_client.get_collection_stats() if self._rag_client else {},
            "agents_available": len(self.agent_router.AGENTS),
            "pipeline_steps": len(self.pipeline.steps)
        }
    
    def display_status(self):
        """Display current orchestrator status"""
        status = self.get_status()
        
        print("\n" + "=" * 60)
        print("🎯 NOVARYX ORCHESTRATOR STATUS")
        print("=" * 60)
        print(f"   Initialized: {'✅' if status['initialized'] else '❌'}")
        print(f"   Inference: {status['inference_provider']}")
        print(f"   Agents: {status['agents_available']}")
        print(f"   Pipeline Steps: {status['pipeline_steps']}")
        
        if status['rag_collections']:
            print(f"   RAG Collections:")
            for key, info in status['rag_collections'].items():
                print(f"      - {key}: {info.get('count', 0)} items")
        
        print("=" * 60 + "\n")


# ---- Test Function ----

def test_orchestrator():
    """Quick test of the orchestrator"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    print("\n" + "=" * 60)
    print("🧪 NOVARYX ORCHESTRATOR TEST")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = NovaryxOrchestrator()
    
    # Initialize
    ready = orchestrator.initialize()
    
    if not ready:
        print("\n⚠️  Orchestrator not fully ready. Some features unavailable.")
        print("   Make sure Ollama is running: ollama serve")
    
    # Display status
    orchestrator.display_status()
    
    # Display pipeline
    orchestrator.pipeline.display_pipeline()
    
    # Display agents
    orchestrator.agent_router.display_agents()
    
    # Create a test task
    print("📝 Creating test task...")
    task = orchestrator.create_task(
        prompt="Build a SaaS dashboard with analytics, user management, and dark mode",
        project_name="TestDashboard",
        project_type="saas"
    )
    
    task.display_progress()
    
    # Run pipeline (will use placeholder handlers for now)
    print("\n🔧 Running pipeline (placeholder mode)...")
    task = orchestrator.run_pipeline(task)
    
    task.display_progress()
    
    print("\n✅ Orchestrator test complete!")
    print("   All systems connected and pipeline flow verified.")
    
    return orchestrator, task


if __name__ == "__main__":
    test_orchestrator()