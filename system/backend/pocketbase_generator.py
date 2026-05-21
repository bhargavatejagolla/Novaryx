"""
NOVARYX - PocketBase Backend Generator
Dynamic backend generation from prompt intent.

Produces complete PocketBase backend:
  - Collection schemas (generated from features)
  - Migration files
  - Auth configuration
  - API documentation
  - Environment configuration
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .schema_generator import SchemaGenerator
from .migration_generator import MigrationGenerator
from .auth_config_generator import AuthConfigGenerator
from .api_generator import APIGenerator

logger = logging.getLogger("novaryx.backend")


@dataclass
class GeneratedBackend:
    """Complete generated backend"""
    app_name: str
    collections: List[Dict]
    files: Dict[str, str]
    auth_config: Dict
    api_endpoints: List[Dict]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PocketBaseGenerator:
    """
    Complete PocketBase backend generator.
    
    Takes project spec → produces complete backend files.
    Everything dynamic. Nothing hardcoded.
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.schema_gen = SchemaGenerator()
        self.migration_gen = MigrationGenerator()
        self.auth_gen = AuthConfigGenerator()
        self.api_gen = APIGenerator()
    
    def generate(self, prompt: str, features: List[str] = None, pages: List[Dict] = None, app_name: str = "") -> GeneratedBackend:
        """
        Generate complete backend from prompt.
        
        Args:
            prompt: User's project description
            features: Extracted features
            pages: Page specifications
            app_name: Application name
        
        Returns:
            GeneratedBackend with all files
        """
        
        print("\n" + "=" * 60)
        print("🗄️  POCKETBASE BACKEND GENERATOR")
        print("=" * 60)
        print(f"   App: {app_name or 'Unnamed'}")
        print(f"   Features: {', '.join(features) if features else 'auto-detect'}")
        
        # Step 1: Generate schema from prompt
        print(f"\n   Analyzing requirements...")
        schema = self.schema_gen.generate_from_prompt(
            prompt=prompt,
            features=features,
            pages=pages
        )
        
        collections = schema.get("collections", [])
        auth_config = schema.get("auth_config", {})
        
        print(f"   Generated {len(collections)} collections:")
        for col in collections:
            print(f"      📦 {col['name']} ({col['type']}) - {len(col['schema'])} fields")
        
        # Step 2: Generate files
        files = {}
        
        # PocketBase schema JSON
        files["backend/pb_schema.json"] = json.dumps(schema, indent=2)
        
        # Migration file
        files["backend/pb_migrations/001_initial_schema.js"] = self.migration_gen.generate_initial_migration(collections)
        
        # Auth config
        files["backend/pb_auth.json"] = self.auth_gen.generate_auth_config(auth_config)
        
        # API documentation
        files["backend/API.md"] = self.api_gen.generate_api_docs(collections, app_name)
        
        # Environment config
        files["backend/.env"] = self._generate_env(app_name, auth_config)
        
        # Docker compose
        files["docker-compose.yml"] = self._generate_docker_compose(app_name)
        
        # Seed data
        files["backend/pb_seed.json"] = self._generate_seed_data(collections, app_name)
        
        print(f"\n   Generated {len(files)} backend files:")
        for f in sorted(files.keys()):
            print(f"      {f}")
        
        print("=" * 60)
        
        return GeneratedBackend(
            app_name=app_name,
            collections=collections,
            files=files,
            auth_config=auth_config,
            api_endpoints=self.api_gen.extract_endpoints(collections)
        )
    
    def _generate_env(self, app_name: str, auth_config: Dict) -> str:
        return f"""# PocketBase Environment
PB_DATABASE_URL=pb_data/data.db
PB_PORT=8090
PB_ADMIN_EMAIL=admin@{app_name.lower().replace(' ', '')}.local
PB_ADMIN_PASSWORD=admin123change
PB_ENCRYPTION_KEY=auto-generated-on-first-run
PB_LOG_LEVEL=info
PB_ORIGINS=http://localhost:3000,http://localhost:5173
"""

    def _generate_docker_compose(self, app_name: str) -> str:
        slug = app_name.lower().replace(" ", "-")
        return f"""version: '3.8'
services:
  pocketbase:
    image: ghcr.io/muchobien/pocketbase:latest
    container_name: {slug}-pocketbase
    restart: unless-stopped
    ports:
      - "8090:8090"
    volumes:
      - ./backend/pb_data:/pb_data
      - ./backend/pb_migrations:/pb_migrations
    environment:
      - PB_ENCRYPTION_KEY=${{PB_ENCRYPTION_KEY}}
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8090/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: .
    container_name: {slug}-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      pocketbase:
        condition: service_healthy
    environment:
      - VITE_POCKETBASE_URL=http://localhost:8090
"""

    def _generate_seed_data(self, collections: List[Dict], app_name: str) -> str:
        """Generate seed data for demo purposes"""
        seed = {"collections": {}}
        
        for col in collections:
            if col["name"] == "users":
                seed["collections"]["users"] = [
                    {
                        "email": f"admin@{app_name.lower().replace(' ', '')}.com",
                        "password": "admin123",
                        "passwordConfirm": "admin123",
                        "name": "Admin User",
                        "role": "admin",
                    },
                    {
                        "email": "demo@example.com",
                        "password": "demo1234",
                        "passwordConfirm": "demo1234",
                        "name": "Demo User",
                        "role": "user",
                    }
                ]
            elif col["name"] == "tasks":
                seed["collections"]["tasks"] = [
                    {"title": "Set up project", "status": "done", "priority": "high"},
                    {"title": "Design system", "status": "in_progress", "priority": "high"},
                    {"title": "Implement features", "status": "todo", "priority": "medium"},
                    {"title": "Write tests", "status": "todo", "priority": "medium"},
                    {"title": "Deploy to production", "status": "todo", "priority": "low"},
                ]
            elif col["name"] == "projects":
                seed["collections"]["projects"] = [
                    {"name": "Website Redesign", "status": "active", "color": "#6366f1"},
                    {"name": "Mobile App", "status": "active", "color": "#06b6d4"},
                    {"name": "API Development", "status": "completed", "color": "#10b981"},
                ]
        
        return json.dumps(seed, indent=2)


# ---- Test ----

def test_backend_generator():
    """Test the backend generator"""
    
    print("\n" + "=" * 60)
    print("🧪 BACKEND GENERATOR TEST")
    print("=" * 60)
    
    generator = PocketBaseGenerator(use_llm=False)
    
    test_cases = [
        {
            "prompt": "Build a project management SaaS with kanban boards, team collaboration, file sharing, and analytics",
            "features": ["kanban", "file_upload", "analytics", "messaging"],
        },
        {
            "prompt": "Create an e-commerce store with products, cart, checkout, and order management",
            "features": ["ecommerce", "payments", "user_management"],
        },
    ]
    
    for case in test_cases:
        backend = generator.generate(
            prompt=case["prompt"],
            features=case["features"],
            app_name=case["prompt"].split(" ")[-2].title()
        )
        
        print(f"\n   Collections: {[c['name'] for c in backend.collections]}")
        print(f"   Files: {len(backend.files)}")
        print(f"   API Endpoints: {len(backend.api_endpoints)}")
    
    print("\n✅ Backend Generator test complete")
    
    return generator


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_backend_generator()