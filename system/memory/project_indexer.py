"""
NOVARYX - Project Indexer
Auto-indexes new generations into memory with rich metadata.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .memory_store import MemoryStore, ProjectMemory

logger = logging.getLogger("novaryx.project_indexer")


class ProjectIndexer:
    """Automatically indexes generated projects into long-term memory"""
    
    def __init__(self, memory_store: MemoryStore = None):
        self.memory_store = memory_store or MemoryStore()
    
    def index_generation(
        self,
        prompt: str,
        project_name: str,
        project_type: str,
        design_system: Dict = None,
        layout_type: str = "",
        pages: list = None,
        components: list = None,
        components_3d: list = None,
        success: bool = True,
        quality_score: float = 0.0,
        bugs_found: int = 0,
        bugs_fixed: int = 0,
        generation_time: float = 0.0,
        tags: list = None,
    ) -> str:
        """Index a completed generation into memory"""
        
        design = design_system or {}
        
        # Extract design tokens
        colors = design.get("colors", {}) if isinstance(design, dict) else {}
        if hasattr(design_system, 'colors'):
            colors = {
                "primary": design_system.colors.primary,
                "mode": getattr(design_system, 'mode', 'dark'),
                "font": getattr(design_system.typography, 'font_family_primary', 'Inter')
            }
        
        # Auto-generate tags
        auto_tags = list(set(
            [project_type] +
            ([c.replace("_", " ") for c in components[:5]] if components else []) +
            ([colors.get("primary", "")] if colors.get("primary") else []) +
            (["3d"] if components_3d else []) +
            (["success"] if success else ["failed"])
        ))
        
        # Build full description for embeddings
        full_desc = f"""
Project: {project_name}
Type: {project_type}
Prompt: {prompt}
Design: {colors.get('primary', 'unknown')} primary, {colors.get('mode', 'dark')} mode
Layout: {layout_type}
Components: {', '.join(components[:15]) if components else 'none'}
Pages: {', '.join([p.get('name', '') for p in pages]) if pages else 'none'}
Quality: {quality_score:.0%}
Success: {success}
"""
        
        memory = ProjectMemory(
            project_name=project_name,
            prompt=prompt,
            project_type=project_type,
            design_tokens=colors if isinstance(colors, dict) else {},
            primary_color=colors.get("primary", "") if isinstance(colors, dict) else "",
            mode=colors.get("mode", "dark") if isinstance(colors, dict) else "dark",
            font=colors.get("font", "Inter") if isinstance(colors, dict) else "Inter",
            layout_type=layout_type,
            pages=pages or [],
            components_used=components or [],
            components_3d=components_3d or [],
            success=success,
            quality_score=quality_score,
            bugs_found=bugs_found,
            bugs_fixed=bugs_fixed,
            generation_time_seconds=generation_time,
            tags=tags or auto_tags,
            full_description=full_desc,
        )
        
        memory_id = self.memory_store.store(memory)
        
        logger.info(f"Indexed generation: {project_name} ({memory_id})")
        
        return memory_id
    
    def index_from_e2e_result(self, result) -> str:
        """Index from an E2E result object"""
        
        return self.index_generation(
            prompt=result.prompt if hasattr(result, 'prompt') else "",
            project_name=result.project_name if hasattr(result, 'project_name') else "",
            project_type=getattr(result, 'project_type', 'unknown'),
            components=getattr(result, 'components_used', []),
            success=result.success if hasattr(result, 'success') else True,
            quality_score=getattr(result, 'quality_score', 0.7),
            bugs_found=result.bugs_found if hasattr(result, 'bugs_found') else 0,
            bugs_fixed=result.bugs_fixed if hasattr(result, 'bugs_fixed') else 0,
            generation_time=result.total_duration_seconds if hasattr(result, 'total_duration_seconds') else 0,
        )