"""
NOVARYX - Intelligence Layer
LLM-powered intent understanding and structured extraction.

Replaces keyword matching with semantic AI analysis.
The LLM reads natural language and outputs structured project specs.
"""

from .intent_parser import IntentParser
from .intent_schema import ProjectSpec, PageSpec, FeatureSpec, DesignSpec
from .intent_validator import IntentValidator
from .prompt_templates import PromptTemplates

__all__ = [
    "IntentParser",
    "ProjectSpec",
    "PageSpec",
    "FeatureSpec",
    "DesignSpec",
    "IntentValidator",
    "PromptTemplates",
]