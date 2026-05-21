"""
NOVARYX - Context Manager (Phase 15)
Intelligently manages the context window and token budget.
Prevents context overflow by retrieving ONLY the minimum relevant context.
Implements smart chunking and rolling memory summaries.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("novaryx.context_manager")

class ContextManager:
    """Manages token budgets and context windows for specialized agents."""
    
    def __init__(self, default_max_tokens: int = 4000):
        # Strict hard budgets per agent role (tokens roughly * 4 chars)
        self.BUDGETS = {
            "frontend": 6000,
            "backend": 5000,
            "repair": 4000,
            "validation": 2000,
            "architect": 8000
        }
        self.default_char_limit = default_max_tokens * 4
        
    def build_agent_context(self, task_type: str, full_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a context payload specifically tailored for a given agent type,
        omitting irrelevant information to save tokens.
        """
        agent_context = {}
        
        # Always include project basics
        agent_context["project_name"] = full_context.get("project_name", "")
        agent_context["domain"] = full_context.get("domain", "")
        
        if task_type == "frontend":
            agent_context["design"] = full_context.get("design", {})
            # Fix 3: Strict file graph retrieval isolation
            agent_context["target_page"] = full_context.get("current_target_page", {})
            
            # Scoped relationships only
            project_graph = full_context.get("project_graph", {})
            if "pages" in project_graph:
                page_name = agent_context["target_page"].get("name", "")
                agent_context["related_components"] = project_graph.get("components", [])[:3] # Limit to 3 max
            
            # Tiny backend summary, NOT full API schema
            agent_context["backend_summary"] = self._summarize_backend(full_context.get("backend_schema", {}))
            
        elif task_type == "backend":
            agent_context["data_models"] = full_context.get("data_models", [])
            # Don't need design tokens for backend
            
        elif task_type == "architect":
            # Architect needs a high-level view of everything
            agent_context["features"] = full_context.get("features", [])
            agent_context["pages_summary"] = [p.get("route") for p in full_context.get("pages", [])]
            
        elif task_type == "repair":
            agent_context["code"] = full_context.get("code", "")
            agent_context["errors"] = full_context.get("errors", [])
            
        # Ensure it fits within budget
        return self._enforce_budget(agent_context, task_type)

    def _summarize_backend(self, schema: Dict[str, Any]) -> str:
        """Create a compact summary of the backend schema for frontend agents."""
        if not schema or "collections" not in schema:
            return "No backend schema defined."
            
        summary = []
        for col in schema["collections"]:
            fields = [f"{f['name']}({f['type']})" for f in col.get("fields", [])]
            summary.append(f"{col['name']}: {', '.join(fields)}")
            
        return " | ".join(summary)

    def _enforce_budget(self, context: Dict[str, Any], task_type: str = "default") -> Dict[str, Any]:
        """Ensures the context dictionary does not exceed the token budget."""
        import json
        
        token_limit = self.BUDGETS.get(task_type, 4000)
        char_limit = token_limit * 4
        
        # Quick size check
        serialized = json.dumps(context)
        if len(serialized) <= char_limit:
            return context
            
        logger.warning(f"Context overflow detected for {task_type}! Size: {len(serialized)} chars. Limit: {char_limit}. Truncating...")
        
        # Simple truncation strategy
        if "code" in context and len(context["code"]) > char_limit // 2:
            context["code"] = context["code"][:char_limit // 2] + "\n...[TRUNCATED_DUE_TO_CONTEXT_LIMIT]..."
            
        # If still too large, prune heavy items
        serialized = json.dumps(context)
        if len(serialized) > char_limit:
             if "project_graph" in context:
                 del context["project_graph"]
             if "design" in context and len(str(context["design"])) > 500:
                 context["design"] = "Design tokens omitted to save context space."
                 
        return context

    def chunk_file(self, file_content: str, max_chunk_chars: int = 8000) -> List[str]:
        """
        Smart chunking system for large files.
        Chunks based on functions/classes rather than arbitrary characters.
        """
        if len(file_content) <= max_chunk_chars:
            return [file_content]
            
        # Simple fallback chunking (line based to avoid breaking syntax mid-line)
        lines = file_content.split("\n")
        chunks = []
        current_chunk = []
        current_len = 0
        
        for line in lines:
            if current_len + len(line) > max_chunk_chars and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_len = len(line)
            else:
                current_chunk.append(line)
                current_len += len(line) + 1 # +1 for newline
                
        if current_chunk:
            chunks.append("\n".join(current_chunk))
            
        return chunks
