"""
NOVARYX - Generation Pipeline
Defines the complete generation pipeline with all steps.
"""

from typing import List, Optional, Callable, Dict, Any
from .task import GenerationTask, TaskStep, TaskStatus, StepResult
from datetime import datetime
import logging
import concurrent.futures

logger = logging.getLogger("novaryx.pipeline")


class PipelineStep:
    """A single step in the generation pipeline"""
    
    def __init__(
        self,
        step: TaskStep,
        name: str,
        description: str,
        handler: Callable,
        required: bool = True,
        max_retries: int = 1
    ):
        self.step = step
        self.name = name
        self.description = description
        self.handler = handler  # Function that takes GenerationTask, returns GenerationTask
        self.required = required
        self.max_retries = max_retries
    
    def execute(self, task: GenerationTask) -> GenerationTask:
        """Execute this pipeline step"""
        result = StepResult(
            step=self.step,
            status="success",
            started_at=datetime.now()
        )
        
        logger.info(f"Executing: {self.name} ({self.step.value})")
        
        try:
            # Phase 2: Watchdog Timer (300s TTL)
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self.handler, task)
                try:
                    task = future.result(timeout=300)
                    result.status = "success"
                    result.completed_at = datetime.now()
                except concurrent.futures.TimeoutError:
                    logger.error(f"Step {self.step.value} timed out after 300s!")
                    raise TimeoutError(f"Generation step {self.step.value} exceeded 300s limit.")
                    
        except Exception as e:
            logger.error(f"Step {self.step.value} failed: {e}")
            result.status = "failed"
            result.error = str(e)
            result.completed_at = datetime.now()
            
            if self.required:
                task.errors.append(f"{self.name}: {str(e)}")
        
        task.add_step_result(result)
        return task


class GenerationPipeline:
    """
    Complete generation pipeline.
    
    Flow:
    PARSE → PLAN → RETRIEVE → GENERATE → VERIFY → REPAIR → PACKAGE
    """
    
    def __init__(self):
        self.steps: List[PipelineStep] = []
        self._build_pipeline()
    
    def _build_pipeline(self):
        """Define all pipeline steps in order"""
        
        # Phase 1: Understanding
        self.steps.append(PipelineStep(
            step=TaskStep.PARSE_PROMPT,
            name="Parse User Prompt",
            description="Extract requirements from user prompt",
            handler=self._parse_prompt,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.DOMAIN_UNDERSTANDING,
            name="Domain Understanding",
            description="Determine software domain (SaaS, AI, ML, CV, etc)",
            handler=self._domain_understanding,
            required=True
        ))
        
        # Phase 2: Planning & Blueprint
        self.steps.append(PipelineStep(
            step=TaskStep.PLAN_ARCHITECTURE,
            name="Plan Architecture",
            description="Analyze existing project graph",
            handler=self._plan_architecture,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.GENERATE_BLUEPRINT,
            name="Generate System Blueprint",
            description="Generate comprehensive architecture blueprint",
            handler=self._generate_blueprint,
            required=True
        ))
        
        # Phase 3: Retrieval
        self.steps.append(PipelineStep(
            step=TaskStep.RETRIEVE_TEMPLATES,
            name="Retrieve Templates",
            description="Find best matching templates from RAG",
            handler=self._retrieve_templates,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.RETRIEVE_COMPONENTS,
            name="Retrieve Components",
            description="Find matching components for each page",
            handler=self._retrieve_components,
            required=False
        ))
        
        # Phase 4: Modular Generation
        self.steps.append(PipelineStep(
            step=TaskStep.GENERATE_BACKEND,
            name="Generate Backend Schema",
            description="Generate database schema and auth logic",
            handler=self._generate_backend,
            required=False
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.GENERATE_ROUTES,
            name="Generate Routing Hierarchy",
            description="Setup directory structure and Next.js routes",
            handler=self._generate_routes,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.GENERATE_LAYOUT,
            name="Generate Layouts",
            description="Generate global and nested layouts",
            handler=self._generate_layout,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.GENERATE_SHARED_COMPONENTS,
            name="Generate Shared Components",
            description="Generate reusable UI components based on tokens",
            handler=self._generate_shared_components,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.GENERATE_PAGES,
            name="Generate Pages",
            description="Generate all frontend pages",
            handler=self._generate_pages,
            required=True,
            max_retries=2
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.GENERATE_API,
            name="Generate API Endpoints",
            description="Generate Next.js API route handlers",
            handler=self._generate_api,
            required=False
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.ASSEMBLE_PROJECT,
            name="Assemble Project",
            description="Combine all generated files into project structure",
            handler=self._assemble_project,
            required=True
        ))
        
        # Phase 5: Verification
        self.steps.append(PipelineStep(
            step=TaskStep.VERIFY_SYNTAX,
            name="Verify Syntax",
            description="Check all files for syntax errors",
            handler=self._verify_syntax,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.VERIFY_IMPORTS,
            name="Verify Imports",
            description="Ensure all imports resolve correctly",
            handler=self._verify_imports,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.VERIFY_ROUTES,
            name="Verify Routes",
            description="Validate all routes are connected",
            handler=self._verify_routes,
            required=True
        ))
        
        # Phase 6: Repair (if needed)
        self.steps.append(PipelineStep(
            step=TaskStep.REPAIR_ISSUES,
            name="Repair Issues",
            description="Fix any verification failures",
            handler=self._repair_issues,
            required=False,
            max_retries=3
        ))
        
        # Phase 7: Package
        self.steps.append(PipelineStep(
            step=TaskStep.PACKAGE_OUTPUT,
            name="Package Output",
            description="Create final project package",
            handler=self._package_output,
            required=True
        ))
        
        self.steps.append(PipelineStep(
            step=TaskStep.GENERATE_DOCS,
            name="Generate Documentation",
            description="Create README and API docs",
            handler=self._generate_docs,
            required=False
        ))
    
    # ---- Pipeline Step Handlers (Placeholders - Implemented in later phases) ----
    
    def _parse_prompt(self, task: GenerationTask) -> GenerationTask:
        """Parse user prompt to extract requirements"""
        task.status = TaskStatus.PARSING
        task.current_step = TaskStep.PARSE_PROMPT
        
        # TODO: Implement with LLM in Phase 2
        logger.info(f"Parsing prompt: {task.user_prompt[:100]}...")
        
        task.project_spec = {
            "raw_prompt": task.user_prompt,
            "parsed": False  # Will be filled by intent parser
        }
        
        return task
    
    def _domain_understanding(self, task: GenerationTask) -> GenerationTask:
        """Domain Understanding Phase"""
        task.current_step = TaskStep.DOMAIN_UNDERSTANDING
        task.context["domain"] = task.project_type or "general"
        return task
    
    def _plan_architecture(self, task: GenerationTask) -> GenerationTask:
        """Analyze existing project graph"""
        task.status = TaskStatus.PLANNING
        task.current_step = TaskStep.PLAN_ARCHITECTURE
        
        try:
            from system.intelligence.project_graph import ProjectGraphAnalyzer
            analyzer = ProjectGraphAnalyzer("../../novaryx-web")
            task.context["project_graph"] = analyzer.analyze()
        except Exception as e:
            logger.warning(f"Could not build project graph: {e}")
            task.context["project_graph"] = {}
            
        return task

    def _generate_blueprint(self, task: GenerationTask) -> GenerationTask:
        """Generate full system blueprint"""
        task.current_step = TaskStep.GENERATE_BLUEPRINT
        try:
            from system.generation_engine.blueprint_generator import BlueprintGenerator
            blueprint_gen = BlueprintGenerator()
            task.context["blueprint"] = blueprint_gen.generate_blueprint(
                task.project_spec, 
                task.context.get("project_graph", {})
            )
        except Exception as e:
            logger.error(f"Failed to generate blueprint: {e}")
        return task
    
    def _retrieve_templates(self, task: GenerationTask) -> GenerationTask:
        """Retrieve matching templates from RAG"""
        task.status = TaskStatus.RETRIEVING
        task.current_step = TaskStep.RETRIEVE_TEMPLATES
        
        # TODO: Connect to ChromaDB retriever
        task.context["retrieved_templates"] = []
        task.context["best_template"] = None
        
        return task
    
    def _retrieve_components(self, task: GenerationTask) -> GenerationTask:
        """Retrieve matching components"""
        task.current_step = TaskStep.RETRIEVE_COMPONENTS
        
        task.context["retrieved_components"] = {}
        
        return task
    
    def _generate_pages(self, task: GenerationTask) -> GenerationTask:
        """Generate frontend pages"""
        task.status = TaskStatus.GENERATING
        task.current_step = TaskStep.GENERATE_PAGES
        task.generated_files = getattr(task, 'generated_files', [])
        return task
        
    def _generate_routes(self, task: GenerationTask) -> GenerationTask:
        """Generate routing hierarchy"""
        task.current_step = TaskStep.GENERATE_ROUTES
        return task
        
    def _generate_layout(self, task: GenerationTask) -> GenerationTask:
        """Generate global and nested layouts"""
        task.current_step = TaskStep.GENERATE_LAYOUT
        return task
        
    def _generate_shared_components(self, task: GenerationTask) -> GenerationTask:
        """Generate reusable UI components"""
        task.current_step = TaskStep.GENERATE_SHARED_COMPONENTS
        return task
        
    def _generate_api(self, task: GenerationTask) -> GenerationTask:
        """Generate Next.js API endpoints"""
        task.current_step = TaskStep.GENERATE_API
        return task
    
    def _generate_backend(self, task: GenerationTask) -> GenerationTask:
        """Generate backend schema"""
        task.current_step = TaskStep.GENERATE_BACKEND
        
        task.context["backend_schema"] = {}
        
        return task
    
    def _assemble_project(self, task: GenerationTask) -> GenerationTask:
        """Assemble all generated files"""
        task.current_step = TaskStep.ASSEMBLE_PROJECT
        
        # TODO: Create project directory with all files
        
        return task
    
    def _verify_syntax(self, task: GenerationTask) -> GenerationTask:
        """Verify syntax of all generated files"""
        task.status = TaskStatus.VERIFYING
        task.current_step = TaskStep.VERIFY_SYNTAX
        
        return task
    
    def _verify_imports(self, task: GenerationTask) -> GenerationTask:
        """Verify imports resolve"""
        task.current_step = TaskStep.VERIFY_IMPORTS
        
        return task
    
    def _verify_routes(self, task: GenerationTask) -> GenerationTask:
        """Verify all routes"""
        task.current_step = TaskStep.VERIFY_ROUTES
        
        return task
    
    def _repair_issues(self, task: GenerationTask) -> GenerationTask:
        """Repair any issues found during verification"""
        task.status = TaskStatus.REPAIRING
        task.current_step = TaskStep.REPAIR_ISSUES
        task.repair_attempts += 1
        
        # TODO: Connect to repair agent (DeepSeek)
        
        return task
    
    def _package_output(self, task: GenerationTask) -> GenerationTask:
        """Package final output"""
        task.status = TaskStatus.PACKAGING
        task.current_step = TaskStep.PACKAGE_OUTPUT
        
        return task
    
    def _generate_docs(self, task: GenerationTask) -> GenerationTask:
        """Generate documentation"""
        task.current_step = TaskStep.GENERATE_DOCS
        
        return task
    
    # ---- Pipeline Execution ----
    
    def run(self, task: GenerationTask) -> GenerationTask:
        """
        Execute the complete pipeline on a task.
        
        Args:
            task: GenerationTask to process
        
        Returns:
            Processed GenerationTask with results
        """
        logger.info(f"Starting pipeline for task: {task.task_id}")
        
        # Set up remaining steps
        task.steps_remaining = [s.step for s in self.steps]
        
        for pipeline_step in self.steps:
            if task.is_complete():
                logger.info("Task marked as complete, stopping pipeline")
                break
            
            # Execute step
            task.current_step = pipeline_step.step
            task = pipeline_step.execute(task)
            
            # Update remaining
            if pipeline_step.step in task.steps_remaining:
                task.steps_remaining.remove(pipeline_step.step)
            
            # Check for failure
            last_result = task.steps_completed[-1] if task.steps_completed else None
            
            if last_result and last_result.status == "failed":
                if pipeline_step.required:
                    # Try repair if allowed
                    if task.can_repair():
                        logger.warning(f"Step failed, attempting repair ({task.repair_attempts + 1}/{task.max_repair_attempts})")
                        task = self._repair_issues(task)
                        
                        # Retry the failed step
                        if task.errors and task.repair_attempts <= task.max_repair_attempts:
                            task = pipeline_step.execute(task)
                        else:
                            logger.error(f"Step {pipeline_step.step.value} failed after repair")
                            task.status = TaskStatus.FAILED
                            break
                    else:
                        logger.error(f"Max repairs reached for {pipeline_step.step.value}")
                        task.status = TaskStatus.FAILED
                        break
                else:
                    logger.warning(f"Optional step {pipeline_step.step.value} failed, continuing")
        
        # Mark complete if not failed
        if task.status != TaskStatus.FAILED:
            task.status = TaskStatus.COMPLETED
            task.current_step = TaskStep.COMPLETE
            logger.info(f"Pipeline complete for task: {task.task_id}")
        
        return task
    
    def run_step(self, task: GenerationTask, step: TaskStep) -> GenerationTask:
        """Run a single pipeline step"""
        for pipeline_step in self.steps:
            if pipeline_step.step == step:
                return pipeline_step.execute(task)
        
        logger.error(f"Step not found: {step.value}")
        return task
    
    def get_step_names(self) -> List[str]:
        """Get all step names"""
        return [s.name for s in self.steps]
    
    def display_pipeline(self):
        """Display pipeline structure"""
        print("\n" + "=" * 60)
        print("🔧 NOVARYX GENERATION PIPELINE")
        print("=" * 60)
        
        for i, step in enumerate(self.steps, 1):
            icon = "🔴" if step.required else "🟡"
            retry = f" (max {step.max_retries} retries)" if step.max_retries > 1 else ""
            print(f"  {i:2d}. {icon} {step.name}{retry}")
            print(f"      {step.description}")
        
        print("=" * 60 + "\n")