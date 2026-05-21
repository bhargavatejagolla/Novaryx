"""
NOVARYX - Template Retriever
Intelligent template and component retrieval for generation.
"""

import json
import logging
from typing import List, Dict, Optional, Any
from .chromadb_client import ChromaDBClient
from .embedding_manager import EmbeddingManager

logger = logging.getLogger("novaryx.retriever")


class TemplateRetriever:
    """
    Retrieves templates and components based on user requirements.
    
    Uses semantic search to find the best matching templates,
    components, and architecture patterns.
    """
    
    def __init__(self, chromadb_client: ChromaDBClient = None):
        self.chromadb = chromadb_client or ChromaDBClient()
        self.embedding_manager = EmbeddingManager()
    
    def find_best_template(
        self,
        project_type: str,
        requirements: List[str] = None,
        features: List[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find the best matching template for a project.
        
        Args:
            project_type: Type of project (saas, ecommerce, portfolio, etc.)
            requirements: List of specific requirements
            features: List of desired features
            top_k: Number of results to return
        
        Returns:
            Ranked list of matching templates
        """
        # Build search query
        query_parts = [project_type]
        
        if requirements:
            query_parts.extend(requirements)
        if features:
            query_parts.append("Features: " + ", ".join(features))
        
        query = " ".join(query_parts)
        
        logger.info(f"Searching templates for: {query[:100]}...")
        
        results = self.chromadb.query_templates(
            query=query,
            n_results=top_k
        )
        
        if not results:
            logger.warning("No matching templates found")
            # Return empty with note
            return [{
                "id": "fallback",
                "name": "Generic Template",
                "metadata": {"type": "generic"},
                "distance": 1.0
            }]
        
        return results
    
    def find_components(
        self,
        description: str,
        component_type: str = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find matching UI components.
        
        Args:
            description: What the component should do/look like
            component_type: Optional type filter (button, card, navbar, etc.)
            top_k: Number of results
        
        Returns:
            List of matching components with code
        """
        results = self.chromadb.query_components(
            query=description,
            component_type=component_type,
            n_results=top_k
        )
        
        return results
    
    def find_architecture(
        self,
        project_description: str,
        scale: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Find matching architecture patterns.
        
        Args:
            project_description: Description of the project
            scale: Project scale (small, medium, large)
        
        Returns:
            Matching architecture patterns
        """
        query = f"{project_description} scale:{scale}"
        
        results = self.chromadb.query_architectures(
            query=query,
            n_results=3
        )
        
        return results
    
    def get_context_for_generation(
        self,
        project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build complete context for generation.
        
        This is the main method called by the orchestrator.
        It gathers templates, components, and architecture patterns
        relevant to the project specification.
        
        Args:
            project_spec: Project specification dictionary
        
        Returns:
            Complete context with all retrieved information
        """
        project_type = project_spec.get("type", "website")
        requirements = project_spec.get("requirements", [])
        features = project_spec.get("features", [])
        pages = project_spec.get("pages", [])
        
        context = {
            "project_type": project_type,
            "best_template": None,
            "alternative_templates": [],
            "components": {},
            "architecture": None,
            "retrieval_quality": 0.0
        }
        
        # Find templates
        templates = self.find_best_template(
            project_type=project_type,
            requirements=requirements,
            features=features,
            top_k=3
        )
        
        if templates:
            context["best_template"] = templates[0]
            context["alternative_templates"] = templates[1:] if len(templates) > 1 else []
            # Quality score based on similarity distance (lower = better)
            if "distance" in templates[0]:
                context["retrieval_quality"] = max(0, 1.0 - templates[0]["distance"])
        
        # Find components for each page type
        for page in pages:
            page_type = page if isinstance(page, str) else page.get("type", "page")
            components = self.find_components(
                description=f"{page_type} page components",
                top_k=3
            )
            context["components"][page_type] = components
        
        # Find architecture
        arch_results = self.find_architecture(
            project_description=project_type + " " + " ".join(requirements),
            scale=project_spec.get("scale", "medium")
        )
        
        if arch_results:
            context["architecture"] = arch_results[0]
        
        logger.info(
            f"Context built: template={context['best_template'].get('metadata', {}).get('name', 'none') if context['best_template'] else 'none'}, "
            f"components={sum(len(v) for v in context['components'].values())}, "
            f"quality={context['retrieval_quality']:.2f}"
        )
        
        return context
    
    def display_context(self, context: Dict[str, Any]):
        """Display retrieved context in readable format"""
        print("\n" + "=" * 60)
        print("📋 RETRIEVED GENERATION CONTEXT")
        print("=" * 60)
        
        print(f"\n📁 Project Type: {context['project_type']}")
        print(f"⭐ Quality Score: {context['retrieval_quality']:.2%}")
        
        print(f"\n📄 Best Template:")
        if context["best_template"]:
            t = context["best_template"]
            print(f"   Name: {t.get('metadata', {}).get('name', t.get('id', 'unknown'))}")
            print(f"   ID: {t.get('id', 'unknown')}")
        
        print(f"\n🧩 Components Found:")
        for page_type, components in context["components"].items():
            print(f"   {page_type}: {len(components)} components")
            for comp in components:
                name = comp.get("name", "unknown")
                print(f"      - {name}")
        
        print(f"\n🏗️  Architecture:")
        if context["architecture"]:
            a = context["architecture"]
            print(f"   Pattern: {a.get('name', 'unknown')}")
        
        print("=" * 60 + "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test retrieval system
    retriever = TemplateRetriever()
    
    # Test with a sample spec
    test_spec = {
        "type": "saas_dashboard",
        "requirements": ["user authentication", "dark mode", "responsive"],
        "features": ["charts", "data tables", "user management"],
        "pages": ["dashboard", "settings", "profile", "analytics"],
        "scale": "medium"
    }
    
    print("Testing retrieval with spec:")
    print(json.dumps(test_spec, indent=2))
    
    context = retriever.get_context_for_generation(test_spec)
    retriever.display_context(context)