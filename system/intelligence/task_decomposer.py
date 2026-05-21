import logging
import json
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from system.orchestrator.task_module import Submodule, ModuleType, ProjectArchitecture
from system.intelligence.intent_schema import ProjectSpec
from system.intelligence.prompt_engine import PromptEngine

logger = logging.getLogger("novaryx.decomposer")

class TaskDecomposer:
    """
    Intelligent Task Decomposer.
    Analyzes a Project Blueprint and breaks it down into isolated Submodules (Auth, Dashboard, API)
    with a strict dependency graph for sequential, token-safe generation.
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self._provider = None
        
    def _get_provider(self):
        if self._provider is None and self.use_llm:
            try:
                from system.inference.provider_factory import get_provider_for_role
                self._provider = get_provider_for_role("planning")
            except Exception as e:
                logger.warning(f"Provider unavailable: {e}")
        return self._provider
        
    def decompose(self, spec: ProjectSpec) -> ProjectArchitecture:
        """
        Decomposes a project into a structured architecture DAG.
        Falls back to rule-based heuristic decomposition if LLM fails or is disabled.
        """
        logger.info(f"Decomposing project: {spec.project_name} into submodules...")
        
        arch = ProjectArchitecture(project_name=spec.project_name)
        
        provider = self._get_provider()
        if provider:
            try:
                # We prompt the LLM to provide a JSON breakdown of modules
                engine = PromptEngine()
                system_prompt = (
                    "You are the Core Autonomous Architecture Decomposer. "
                    "Your job is to take a project specification and decompose it into distinct, isolated submodules.\n"
                    "RULES:\n"
                    "1. Respond ONLY with raw, valid JSON.\n"
                    "2. The JSON must be a list of objects, each representing a module.\n"
                    "3. Each object must have: module_id, name, type (frontend_layout, frontend_page, frontend_component, backend_schema, backend_api, auth, config, fullstack), description, dependencies (list of module_ids this depends on).\n"
                    "4. Base components (layout, schema) must have no dependencies. Pages must depend on layouts and schemas."
                )
                
                # Simplified spec for prompt
                spec_dict = {
                    "project_name": spec.project_name,
                    "project_type": spec.project_type,
                    "features": [f.name for f in (spec.features or [])],
                    "pages": [p.name for p in (spec.pages or [])],
                    "auth_required": spec.requires_authentication,
                    "db_required": spec.requires_database
                }
                
                user_prompt = f"Decompose this project into a dependency graph:\n\n{json.dumps(spec_dict, indent=2)}"
                
                result = provider.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    role="planning",
                    temperature=0.1
                )
                
                if result.success and result.text:
                    # Clean up JSON
                    text = result.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.startswith("```"):
                        text = text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    
                    parsed_modules = json.loads(text.strip())
                    for item in parsed_modules:
                        mod = Submodule(
                            module_id=item["module_id"],
                            name=item["name"],
                            type=ModuleType(item["type"]),
                            description=item["description"],
                            dependencies=item.get("dependencies", [])
                        )
                        arch.add_module(mod)
                        
                    arch.resolve_order()
                    logger.info(f"LLM Decomposition successful: {len(arch.modules)} modules identified.")
                    return arch
                    
            except Exception as e:
                logger.error(f"LLM Decomposition failed: {e}. Falling back to heuristics.")
                
        # Heuristic fallback (Rule-based decomposition)
        return self._heuristic_decomposition(spec)
        
    def _heuristic_decomposition(self, spec: ProjectSpec) -> ProjectArchitecture:
        arch = ProjectArchitecture(project_name=spec.project_name)
        
        # 1. Base Layout
        arch.add_module(Submodule(
            module_id="core_layout",
            name="Core Layout & Navigation",
            type=ModuleType.FRONTEND_LAYOUT,
            description="The master shell, sidebar, and navbar.",
            dependencies=[]
        ))
        
        # 2. Database Schema (if needed)
        schema_dep = []
        if getattr(spec, 'requires_database', False) or getattr(spec, 'requires_authentication', False):
            arch.add_module(Submodule(
                module_id="db_schema",
                name="Database Schema",
                type=ModuleType.BACKEND_SCHEMA,
                description="Core database collections and PocketBase schema.",
                dependencies=[]
            ))
            schema_dep.append("db_schema")
            
        # 3. Auth Module (if needed)
        auth_dep = []
        if getattr(spec, 'requires_authentication', False):
            arch.add_module(Submodule(
                module_id="auth_module",
                name="Authentication System",
                type=ModuleType.AUTH,
                description="Login, Register, and Session Guard components.",
                dependencies=["core_layout"] + schema_dep
            ))
            auth_dep.append("auth_module")
            
        # 4. Pages
        if spec.pages:
            for i, page in enumerate(spec.pages):
                safe_name = page.name.lower().replace(" ", "_")
                deps = ["core_layout"] + schema_dep + auth_dep
                arch.add_module(Submodule(
                    module_id=f"page_{safe_name}",
                    name=f"{page.name} Page",
                    type=ModuleType.FRONTEND_PAGE,
                    description=f"Generated UI for {page.name}: {page.description}",
                    dependencies=deps
                ))
                
        arch.resolve_order()
        return arch
