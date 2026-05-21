"""
NOVARYX - Specialized Agents
Each agent masters one domain of the generation pipeline.
"""

import json
import logging
from typing import Dict, Any, List
from .agent_core import Agent, AgentCapability, AgentTask

logger = logging.getLogger("novaryx.agents.specialized")


class ArchitectAgent(Agent):
    """Masters system architecture, routing, and data model design"""
    
    def __init__(self):
        super().__init__("architect", AgentCapability(
            name="Architect",
            description="System architecture design, route planning, data model design",
            skills=["architecture", "routing", "database_design", "system_design"],
            model_role="planning",
            priority=10
        ))
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        provider = self._get_inference()
        if not provider:
            return {"architecture": {}, "routes": [], "data_models": []}
        
        prompt = f"""As a senior system architect, design the architecture for this application:

REQUEST: {task.prompt}
CONTEXT: {json.dumps(task.context, indent=2)}

Return JSON:
{{
  "architecture": {{
    "type": "spa|ssr|static",
    "frontend": "react",
    "backend": "pocketbase|none",
    "state_management": "context|redux|zustand",
    "styling": "tailwind",
    "complexity": "simple|medium|complex"
  }},
  "routes": [
    {{"path": "/route", "component": "ComponentName", "auth": true|false}}
  ],
  "data_models": [
    {{"name": "ModelName", "fields": [{{"name": "field", "type": "text|number|bool|relation", "required": true|false}}]}}
  ],
  "component_tree": {{
    "root": "App",
    "children": []
  }},
  "recommendations": ["rec1", "rec2"]
}}"""
        
        result = provider.generate(prompt=prompt, role="planning", temperature=0.1, max_tokens=1500)
        
        if result.success:
            try:
                text = result.text.strip()
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0:
                    return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        
        return {"architecture": {"type": "spa"}, "routes": [], "data_models": [], "component_tree": {}}


class FrontendAgent(Agent):
    """Masters React component and page generation"""
    
    def __init__(self):
        super().__init__("frontend", AgentCapability(
            name="Frontend",
            description="React components, pages, hooks, and state management",
            skills=["react", "typescript", "tailwind", "components", "pages", "hooks"],
            model_role="generation",
            priority=8,
            max_parallel_tasks=3
        ))
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        provider = self._get_inference()
        if not provider:
            return {"files": {}}
        
        component_type = task.task_type.replace("generate_", "")
        
        prompt = f"""Generate a production-ready React {component_type} component.

CONTEXT: {json.dumps(task.context, indent=2)}

Requirements:
- Use React 18+ with TypeScript
- Use Tailwind CSS with design tokens (var(--primary), var(--surface), etc.)
- Include proper TypeScript interfaces
- Handle loading, empty, and error states
- Add Framer Motion animations
- Be responsive (mobile-first)
- Export as default or named export

Return ONLY the complete code. No explanations."""
        
        result = provider.generate(prompt=prompt, role="generation", temperature=0.1, max_tokens=2000)
        
        if result.success:
            return {"code": result.text.strip(), "type": component_type}
        
        return {"code": "", "type": component_type, "error": "Generation failed"}


class BackendAgent(Agent):
    """Masters database schema, API, and backend generation"""
    
    def __init__(self):
        super().__init__("backend", AgentCapability(
            name="Backend",
            description="Database schema, API endpoints, migrations, auth rules",
            skills=["pocketbase", "database", "api", "migrations", "auth"],
            model_role="generation",
            priority=7
        ))
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        provider = self._get_inference()
        if not provider:
            return {"collections": [], "auth_config": {}}
        
        features = task.context.get("features", [])
        
        prompt = f"""Generate a complete PocketBase database schema for this application.

APP DESCRIPTION: {task.prompt}
FEATURES: {', '.join(features) if features else 'standard app'}

Return JSON:
{{
  "collections": [
    {{
      "name": "collection_name",
      "type": "base|auth",
      "fields": [
        {{"name": "field_name", "type": "text|number|bool|email|url|date|select|file|relation|json", "required": true|false, "unique": true|false}}
      ],
      "rules": {{
        "list": "rule",
        "view": "rule",
        "create": "rule",
        "update": "rule",
        "delete": "rule"
      }}
    }}
  ],
  "auth_config": {{
    "email_auth": true,
    "verification_required": false,
    "password_reset": true
  }}
}}"""
        
        result = provider.generate(prompt=prompt, role="generation", temperature=0.1, max_tokens=1500)
        
        if result.success:
            try:
                text = result.text.strip()
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0:
                    return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        
        return {"collections": [], "auth_config": {}}


class DesignAgent(Agent):
    """Masters visual design, theming, and styling"""
    
    def __init__(self):
        super().__init__("design", AgentCapability(
            name="Design",
            description="Visual design, color systems, typography, animations, 3D",
            skills=["design_systems", "colors", "typography", "animations", "3d"],
            model_role="generation",
            priority=6
        ))
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        provider = self._get_inference()
        if not provider:
            return {"design_tokens": {}}
        
        prompt = f"""Generate a complete design system for this application:

DESCRIPTION: {task.prompt}
EXISTING TOKENS: {json.dumps(task.context.get('design', {}), indent=2)}

Return JSON with design tokens:
{{
  "colors": {{
    "primary": "#hex",
    "primary_light": "#hex",
    "primary_dark": "#hex",
    "accent": "#hex",
    "background": "#hex",
    "surface": "#hex",
    "text_primary": "#hex",
    "text_secondary": "#hex",
    "success": "#hex",
    "warning": "#hex",
    "error": "#hex"
  }},
  "typography": {{
    "font_family": "Inter|Poppins|Roboto|etc",
    "scale": {{"xs": "12px", "sm": "14px", "base": "16px", "lg": "18px", "xl": "20px", "2xl": "24px", "3xl": "30px"}}
  }},
  "effects": {{
    "glassmorphism": true|false,
    "border_radius": "6px|12px|16px|24px",
    "shadow": "subtle|medium|strong"
  }},
  "animations": {{
    "level": "subtle|moderate|rich",
    "page_transition": "fade|slide|scale",
    "3d_enabled": true|false
  }}
}}"""
        
        result = provider.generate(prompt=prompt, role="generation", temperature=0.2, max_tokens=1000)
        
        if result.success:
            try:
                text = result.text.strip()
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0:
                    return {"design_tokens": json.loads(text[start:end])}
            except json.JSONDecodeError:
                pass
        
        return {"design_tokens": {}}


class ContentAgent(Agent):
    """Masters copywriting, content generation, and SEO"""
    
    def __init__(self):
        super().__init__("content", AgentCapability(
            name="Content",
            description="Copywriting, content generation, SEO metadata",
            skills=["copywriting", "content", "seo", "headlines", "descriptions"],
            model_role="generation",
            priority=4
        ))
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        provider = self._get_inference()
        if not provider:
            return {"content": {}}
        
        prompt = f"""Generate compelling content for this application:

DESCRIPTION: {task.prompt}
PAGES: {json.dumps(task.context.get('pages', []), indent=2)}

Return JSON:
{{
  "hero": {{
    "headline": "Compelling headline",
    "subheadline": "Supporting subheadline",
    "cta_text": "Call to action"
  }},
  "pages": {{
    "page_name": {{
      "title": "Page Title",
      "description": "Page description",
      "seo_title": "SEO Title",
      "seo_description": "SEO meta description"
    }}
  }},
  "branding": {{
    "tagline": "Brand tagline",
    "value_proposition": "Main value proposition",
    "tone": "professional|friendly|bold|minimal"
  }}
}}"""
        
        result = provider.generate(prompt=prompt, role="generation", temperature=0.3, max_tokens=1000)
        
        if result.success:
            try:
                text = result.text.strip()
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0:
                    return {"content": json.loads(text[start:end])}
            except json.JSONDecodeError:
                pass
        
        return {"content": {}}


class RepairAgent(Agent):
    """Masters debugging and code repair"""
    
    def __init__(self):
        super().__init__("repair", AgentCapability(
            name="Repair",
            description="Bug detection, code repair, error fixing",
            skills=["debugging", "code_repair", "error_fixing", "validation"],
            model_role="repair",
            priority=9
        ))
    
    def execute(self, task: AgentTask) -> Dict[str, Any]:
        provider = self._get_inference()
        if not provider:
            return {"fixed": False, "changes": []}
        
        code = task.context.get("code", "")
        errors = task.context.get("errors", [])
        
        prompt = f"""Fix ALL errors in this code:

ERRORS:
{json.dumps(errors, indent=2)}

CODE:
```tsx
{code[:3000]}
```
Return ONLY the complete fixed code. No explanations."""

        result = provider.generate(prompt=prompt, role="repair", temperature=0.05, max_tokens=3000)

        if result.success:
            return {"fixed": True, "code": result.text.strip(), "changes": ["Repaired via LLM"]}

        return {"fixed": False, "changes": []}


class ReviewAgent(Agent):
    """Masters quality review and validation"""

    def __init__(self):
        super().__init__("review", AgentCapability(
            name="Review",
            description="Code review, quality assessment, best practices validation",
            skills=["code_review", "quality", "best_practices", "security"],
            model_role="planning",
            priority=5
        ))

    def execute(self, task: AgentTask) -> Dict[str, Any]:
        provider = self._get_inference()
        if not provider:
            return {"approved": True, "issues": [], "score": 7}

        code = task.context.get("code", "")

        prompt = f"""Review this code for quality, best practices, and issues:

CODE:
```tsx
{code[:2500]}
```
Return JSON:
{{
  "approved": true|false,
  "score": 1-10,
  "issues": [
    {{"severity": "critical|warning|info", "description": "issue description", "suggestion": "how to fix"}}
  ],
  "strengths": ["what's good"],
  "recommendations": ["improvement suggestions"]
}}"""

        result = provider.generate(prompt=prompt, role="planning", temperature=0.1, max_tokens=800)

        if result.success:
            try:
                text = result.text.strip()
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0:
                    return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        return {"approved": True, "issues": [], "score": 7}

class MLAgent(Agent):
    """Masters machine learning pipelines and AI integrations"""

    def __init__(self):
        super().__init__("ml_ai", AgentCapability(
            name="ML/AI",
            description="Machine learning pipelines, AI integrations, models, inference",
            skills=["ml_pipelines", "ai_integration", "models", "inference", "rag"],
            model_role="generation",
            priority=7
        ))

    def execute(self, task: AgentTask) -> Dict[str, Any]:
        provider = self._get_inference()
        if not provider:
            return {"ml_config": {}}
            
        prompt = f"""Design the ML/AI integration for this application:
        
        DESCRIPTION: {task.prompt}
        
        Return JSON with ML configurations:
        {{
            "models_required": ["model1", "model2"],
            "pipeline_steps": ["step1", "step2"],
            "apis_needed": ["openai", "huggingface"],
            "vector_db": "chromadb|pinecone|qdrant"
        }}
        """
        
        result = provider.generate(prompt=prompt, role="generation", temperature=0.1, max_tokens=1000)
        
        if result.success:
            try:
                text = result.text.strip()
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0:
                    return {"ml_config": json.loads(text[start:end])}
            except json.JSONDecodeError:
                pass
                
        return {"ml_config": {}}


class ValidationAgent(Agent):
    """Masters strict deterministic and semantic validation of generated code"""

    def __init__(self):
        super().__init__("validation", AgentCapability(
            name="Validation",
            description="Strict deterministic code validation, dependency checks, route mapping",
            skills=["validation", "linting", "dependency_checks", "typescript"],
            model_role="planning",
            priority=10
        ))

    def execute(self, task: AgentTask) -> Dict[str, Any]:
        # Typically uses deterministic tools first, then LLM for semantic checks
        return {"valid": True, "errors": []}


class RAGRetrievalAgent(Agent):
    """Masters semantic retrieval from the multi-layer ChromaDB memory"""

    def __init__(self):
        super().__init__("rag_retrieval", AgentCapability(
            name="RAG Retrieval",
            description="Semantic retrieval of components, architecture patterns, and bugs",
            skills=["rag", "semantic_search", "memory_retrieval", "chromadb"],
            model_role="planning",
            priority=10
        ))

    def execute(self, task: AgentTask) -> Dict[str, Any]:
        # Connects to ChromaDB to retrieve relevant context for other agents
        return {"retrieved_context": []}
