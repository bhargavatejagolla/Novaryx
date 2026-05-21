"""
NOVARYX - Framework Intelligence (Phase 10)
Understands how technologies work together (e.g. Next.js App Router + Tailwind + Zustand).
Provides wiring logic and compatibility matrices.
"""

from typing import Dict, List, Any

class FrameworkIntel:
    """Knowledge graph of framework combinations and wiring instructions."""
    
    COMPATIBILITY_MATRIX = {
        "frontend": {
            "react": ["nextjs", "vite", "create-react-app"],
            "vue": ["nuxt", "vite"]
        },
        "styling": {
            "nextjs": ["tailwind", "css-modules", "styled-components"],
            "vite": ["tailwind", "css", "sass"]
        },
        "state": {
            "react": ["zustand", "redux-toolkit", "context", "jotai"],
            "nextjs": ["zustand", "redux-toolkit", "context"]
        },
        "backend": {
            "nextjs": ["pocketbase", "supabase", "firebase", "prisma", "custom-api"]
        },
        "database": {
            "prisma": ["postgresql", "mysql", "sqlite", "mongodb"]
        }
    }

    @staticmethod
    def get_recommended_stack(project_type: str, complexity: str) -> Dict[str, str]:
        """Returns the recommended technology stack for a given project."""
        
        stack = {
            "frontend": "nextjs",
            "styling": "tailwind",
            "language": "typescript"
        }
        
        if complexity in ["complex", "enterprise"]:
            stack["state"] = "zustand"
            stack["backend"] = "supabase" if project_type == "saas_dashboard" else "custom-api"
            stack["database"] = "postgresql"
        else:
            stack["state"] = "context"
            stack["backend"] = "pocketbase"
            stack["database"] = "sqlite"
            
        return stack
        
    @staticmethod
    def get_wiring_instructions(stack: Dict[str, str]) -> List[str]:
        """Returns specific instructions on how to wire the selected stack together."""
        instructions = []
        
        if stack.get("frontend") == "nextjs" and stack.get("styling") == "tailwind":
            instructions.append("Configure postcss.config.js and tailwind.config.ts.")
            instructions.append("Import tailwind directives in globals.css.")
            
        if stack.get("frontend") == "nextjs" and stack.get("state") == "zustand":
            instructions.append("Create a store/ directory for Zustand stores.")
            instructions.append("Ensure stores use create() and handle hydration issues in SSR (Next.js).")
            
        if stack.get("backend") == "pocketbase":
            instructions.append("Initialize PocketBase client in a lib/pocketbase.ts singleton.")
            
        return instructions
