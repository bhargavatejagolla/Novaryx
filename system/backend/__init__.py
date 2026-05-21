"""
NOVARYX - Dynamic Backend Generator
Generates complete PocketBase backends from prompt intent.

Fully dynamic - no static templates. The LLM analyzes:
  - What data models are needed
  - What fields each collection needs
  - What auth rules to apply
  - What API endpoints to expose

Connected to:
  - Intent Parser (reads features → determines data needs)
  - LLM (generates schema from semantic understanding)
  - Project Builder (writes backend files)
"""

from .pocketbase_generator import PocketBaseGenerator, GeneratedBackend
from .schema_generator import SchemaGenerator
from .migration_generator import MigrationGenerator
from .auth_config_generator import AuthConfigGenerator
from .api_generator import APIGenerator

__all__ = [
    "PocketBaseGenerator",
    "GeneratedBackend",
    "SchemaGenerator",
    "MigrationGenerator",
    "AuthConfigGenerator",
    "APIGenerator",
]