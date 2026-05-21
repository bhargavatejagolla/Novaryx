"""
NOVARYX - Template Adapter
Defines rules for how AI can adapt templates during generation.

This is CRITICAL - it prevents the AI from breaking template structure.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("novaryx.template_adapter")


class ModificationLevel(Enum):
    """How much AI can modify"""
    NONE = "none"           # Read-only, cannot modify
    CONTENT_ONLY = "content"  # Only text/content changes
    STYLE_ONLY = "style"      # Only visual changes
    STRUCTURE = "structure"   # Can modify layout
    FULL = "full"            # Can modify anything


@dataclass
class AdaptationRule:
    """A single rule for what AI can/cannot modify"""
    target: str  # File path or component name
    level: ModificationLevel
    allowed_changes: List[str] = field(default_factory=list)
    forbidden_changes: List[str] = field(default_factory=list)
    preserve_sections: List[str] = field(default_factory=list)
    notes: str = ""


class TemplateAdapter:
    """
    Manages adaptation rules for template customization.
    
    This defines the "contract" between templates and AI:
    - What CAN be changed (colors, content, features)
    - What CANNOT be changed (core structure, imports, types)
    
    This prevents the AI from hallucinating and breaking templates.
    """
    
    # Default adaptation rules by file type
    DEFAULT_RULES = {
        "page": AdaptationRule(
            target="*.page.tsx",
            level=ModificationLevel.CONTENT_ONLY,
            allowed_changes=[
                "text_content",
                "page_title",
                "meta_description",
                "data_displayed"
            ],
            forbidden_changes=[
                "import_statements",
                "component_structure",
                "export_signature",
                "route_configuration",
                "type_definitions"
            ],
            preserve_sections=[
                "imports",
                "type_definitions",
                "component_signature",
                "return_statement_structure"
            ],
            notes="Pages: Change content, preserve structure"
        ),
        "component": AdaptationRule(
            target="*.component.tsx",
            level=ModificationLevel.CONTENT_ONLY,
            allowed_changes=[
                "text_labels",
                "data_props",
                "conditional_rendering",
                "list_items"
            ],
            forbidden_changes=[
                "import_statements",
                "component_name",
                "prop_types",
                "core_logic_flow"
            ],
            preserve_sections=[
                "imports",
                "typescript_interfaces",
                "component_declaration",
                "main_jsx_structure"
            ],
            notes="Components: Change data, preserve logic"
        ),
        "style": AdaptationRule(
            target="*.css",
            level=ModificationLevel.STYLE_ONLY,
            allowed_changes=[
                "colors",
                "font_families",
                "spacing_values",
                "border_radius",
                "shadow_values"
            ],
            forbidden_changes=[
                "layout_properties",
                "display_modes",
                "positioning",
                "responsive_breakpoints"
            ],
            preserve_sections=[
                "responsive_queries",
                "layout_grids",
                "flexbox_settings"
            ],
            notes="Styles: Change aesthetics, preserve layout"
        ),
        "config": AdaptationRule(
            target="*.config.*",
            level=ModificationLevel.CONTENT_ONLY,
            allowed_changes=[
                "site_name",
                "environment_variables",
                "feature_flags"
            ],
            forbidden_changes=[
                "build_configuration",
                "dependency_versions",
                "plugin_settings"
            ],
            preserve_sections=[
                "build_settings",
                "plugin_configs",
                "compiler_options"
            ],
            notes="Config: Change values, preserve settings"
        ),
        "hook": AdaptationRule(
            target="*.hook.ts",
            level=ModificationLevel.STRUCTURE,
            allowed_changes=[
                "api_endpoints",
                "data_transformations",
                "error_handling"
            ],
            forbidden_changes=[
                "hook_signature",
                "return_type",
                "core_state_management"
            ],
            preserve_sections=[
                "hook_declaration",
                "return_statement"
            ],
            notes="Hooks: Can modify logic, preserve interface"
        ),
        "layout": AdaptationRule(
            target="*layout*",
            level=ModificationLevel.STRUCTURE,
            allowed_changes=[
                "navigation_items",
                "footer_content",
                "sidebar_configuration"
            ],
            forbidden_changes=[
                "layout_grid",
                "responsive_behavior",
                "core_containers"
            ],
            preserve_sections=[
                "main_layout_grid",
                "responsive_breakpoints"
            ],
            notes="Layout: Can restructure within grid"
        )
    }
    
    # Project-type specific rules
    PROJECT_RULES = {
        "saas_dashboard": [
            AdaptationRule(
                target="src/pages/dashboard",
                level=ModificationLevel.CONTENT_ONLY,
                allowed_changes=["widgets", "data_sources", "chart_configs"],
                forbidden_changes=["dashboard_grid", "sidebar_structure"],
                notes="Dashboard: Change widgets, keep layout"
            )
        ],
        "saas_landing": [
            AdaptationRule(
                target="src/pages/hero",
                level=ModificationLevel.STRUCTURE,
                allowed_changes=["hero_content", "cta_text", "3d_parameters"],
                forbidden_changes=["3d_core_engine", "animation_system"],
                notes="Landing: Full hero customization allowed"
            )
        ]
    }
    
    def __init__(self):
        self.custom_rules: Dict[str, List[AdaptationRule]] = {}
    
    def get_rules_for_file(
        self,
        file_path: str,
        project_type: str = None
    ) -> AdaptationRule:
        """
        Get the adaptation rules for a specific file.
        
        Args:
            file_path: Relative path to the file
            project_type: Optional project type for specific rules
        
        Returns:
            AdaptationRule for the file
        """
        file_path_lower = file_path.lower()
        
        # Check custom rules first
        if project_type and project_type in self.custom_rules:
            for rule in self.custom_rules[project_type]:
                if self._match_target(file_path_lower, rule.target):
                    return rule
        
        # Check project-type specific rules
        if project_type and project_type in self.PROJECT_RULES:
            for rule in self.PROJECT_RULES[project_type]:
                if self._match_target(file_path_lower, rule.target):
                    return rule
        
        # Use default rules
        for file_type, rule in self.DEFAULT_RULES.items():
            if self._match_target(file_path_lower, rule.target):
                return rule
        
        # Default: content only, be safe
        return AdaptationRule(
            target=file_path,
            level=ModificationLevel.CONTENT_ONLY,
            allowed_changes=["text_content"],
            forbidden_changes=["structure", "imports", "types"],
            notes="Unknown file type - restricted to content only"
        )
    
    def _match_target(self, file_path: str, target: str) -> bool:
        """Check if file path matches a target pattern"""
        target_lower = target.lower()
        
        if target_lower.startswith("*."):
            # Extension match
            ext = target_lower[1:]
            return file_path.endswith(ext)
        elif "*" in target_lower:
            # Contains match
            pattern = target_lower.replace("*", "")
            return pattern in file_path
        else:
            # Exact match
            return target_lower in file_path
    
    def can_modify(
        self,
        file_path: str,
        change_type: str,
        project_type: str = None
    ) -> bool:
        """
        Check if a specific change is allowed for a file.
        
        Args:
            file_path: Relative file path
            change_type: Type of change requested
            project_type: Optional project type
        
        Returns:
            True if change is allowed
        """
        rule = self.get_rules_for_file(file_path, project_type)
        
        if change_type in rule.forbidden_changes:
            logger.warning(f"FORBIDDEN: {change_type} in {file_path}")
            return False
        
        if rule.level == ModificationLevel.NONE:
            return False
        
        if rule.level == ModificationLevel.FULL:
            return True
        
        if change_type in rule.allowed_changes:
            return True
        
        logger.debug(f"UNKNOWN change type: {change_type} in {file_path} - denying")
        return False
    
    def get_adaptation_prompt(
        self,
        file_path: str,
        file_content: str,
        project_type: str = None
    ) -> str:
        """
        Generate a prompt for AI that includes adaptation rules.
        
        This ensures the AI knows exactly what it can and cannot modify.
        """
        rule = self.get_rules_for_file(file_path, project_type)
        
        prompt = f"""You are adapting a template file. Follow these rules EXACTLY:

FILE: {file_path}
MODIFICATION LEVEL: {rule.level.value}

ALLOWED CHANGES:
{chr(10).join(f'  ✅ {c}' for c in rule.allowed_changes)}

FORBIDDEN CHANGES:
{chr(10).join(f'  ❌ {c}' for c in rule.forbidden_changes)}

PRESERVE EXACTLY:
{chr(10).join(f'  🔒 {s}' for s in rule.preserve_sections)}

{rule.notes}

ORIGINAL FILE:
```{file_path.split('.')[-1]}
{file_content}
Output the COMPLETE modified file. Keep ALL preserved sections IDENTICAL.
"""
        return prompt
    
    def add_custom_rule(
        self,
        project_type: str,
        rule: AdaptationRule
    ):
        """Add a custom adaptation rule for a project type"""
        if project_type not in self.custom_rules:
            self.custom_rules[project_type] = []
        self.custom_rules[project_type].append(rule)
        logger.info(f"Added custom rule for {project_type}: {rule.target}")
    
    def get_rules_summary(self, project_type: str = None) -> str:
        """Get a summary of all applicable rules"""
        summary_lines = ["Adaptation Rules Summary:", "-" * 40]
        
        for file_type, rule in self.DEFAULT_RULES.items():
            summary_lines.append(
                f" {file_type}: {rule.level.value} "
                f"(allow: {len(rule.allowed_changes)}, "
                f"forbid: {len(rule.forbidden_changes)})"
            )
        
        if project_type and project_type in self.PROJECT_RULES:
            summary_lines.append(f"\n {project_type} specific rules:")
            for rule in self.PROJECT_RULES[project_type]:
                summary_lines.append(f" - {rule.target}: {rule.level.value}")
        
        return "\n".join(summary_lines)
