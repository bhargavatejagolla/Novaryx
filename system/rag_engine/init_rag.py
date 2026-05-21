"""
NOVARYX - RAG Initialization Script
Run this to set up ChromaDB and seed initial data.

Usage:
  python system/rag_engine/init_rag.py
  python system/rag_engine/init_rag.py --reset   (to start fresh)
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from system.rag_engine.chromadb_client import ChromaDBClient
from system.rag_engine.embedding_manager import OllamaEmbeddingFunction, EmbeddingManager
from system.rag_engine.retriever import TemplateRetriever

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("novaryx.rag_init")


def seed_initial_data(client: ChromaDBClient):
    """Seed ChromaDB with initial template and component data"""
    
    print("\n" + "=" * 60)
    print("🌱 SEEDING INITIAL DATA")
    print("=" * 60)
    
    templates = [
        {
            "id": "template_saas_dashboard",
            "name": "SaaS Dashboard",
            "description": "Complete SaaS dashboard with analytics, user management, and dark mode. Premium UI with glassmorphism design.",
            "metadata": {
                "type": "saas",
                "pages": ["dashboard", "analytics", "users", "settings", "billing", "profile"],
                "features": ["authentication", "charts", "data_tables", "dark_mode", "responsive", "notifications"],
                "tech_stack": ["react", "typescript", "tailwind", "recharts"],
                "complexity": "medium",
                "estimated_pages": 6
            }
        },
        {
            "id": "template_saas_landing",
            "name": "SaaS Landing Page",
            "description": "High-conversion SaaS landing page with 3D hero, pricing tables, testimonials, and CTA sections.",
            "metadata": {
                "type": "landing",
                "pages": ["hero", "features", "pricing", "testimonials", "cta", "footer"],
                "features": ["3d_hero", "animations", "pricing_table", "testimonials", "newsletter"],
                "tech_stack": ["react", "typescript", "tailwind", "framer_motion", "three_js"],
                "complexity": "low",
                "estimated_pages": 1
            }
        },
        {
            "id": "template_ecommerce",
            "name": "E-Commerce Store",
            "description": "Full e-commerce template with product listings, cart, checkout flow, and order management.",
            "metadata": {
                "type": "ecommerce",
                "pages": ["products", "product_detail", "cart", "checkout", "orders", "account"],
                "features": ["product_grid", "shopping_cart", "payment_flow", "order_tracking", "reviews"],
                "tech_stack": ["react", "typescript", "tailwind", "stripe"],
                "complexity": "high",
                "estimated_pages": 8
            }
        },
        {
            "id": "template_admin_panel",
            "name": "Admin Panel",
            "description": "Comprehensive admin panel with data tables, CRUD operations, role management, and system monitoring.",
            "metadata": {
                "type": "admin",
                "pages": ["dashboard", "users", "roles", "settings", "logs", "backup"],
                "features": ["data_tables", "crud_forms", "role_management", "activity_logs", "file_upload"],
                "tech_stack": ["react", "typescript", "tailwind", "tanstack_table"],
                "complexity": "medium",
                "estimated_pages": 6
            }
        },
        {
            "id": "template_portfolio",
            "name": "Creative Portfolio",
            "description": "Modern portfolio with 3D animations, project showcase, smooth scrolling, and contact form.",
            "metadata": {
                "type": "portfolio",
                "pages": ["hero", "projects", "about", "skills", "contact"],
                "features": ["3d_showcase", "smooth_scroll", "project_filter", "contact_form", "animations"],
                "tech_stack": ["react", "typescript", "tailwind", "three_js", "framer_motion"],
                "complexity": "low",
                "estimated_pages": 1
            }
        }
    ]
    
    for template in templates:
        client.add_template(
            template_id=template["id"],
            name=template["name"],
            description=template["description"],
            metadata=template["metadata"]
        )
    print(f"   ✅ {len(templates)} templates seeded")
    
    components = [
        {"id": "comp_hero_3d", "name": "3D Hero Section", "type": "hero", "code": "// Three.js animated hero", "metadata": {"description": "Interactive 3D hero with particle effects"}},
        {"id": "comp_dashboard_charts", "name": "Dashboard Charts Grid", "type": "dashboard", "code": "// Recharts-based chart grid", "metadata": {"description": "Responsive chart grid"}},
        {"id": "comp_data_table", "name": "Data Table", "type": "table", "code": "// TanStack table", "metadata": {"description": "Sortable data table with CRUD"}},
        {"id": "comp_auth_form", "name": "Auth Form", "type": "auth", "code": "// Login/Register form", "metadata": {"description": "Email/password auth with validation"}},
        {"id": "comp_navbar", "name": "Responsive Navbar", "type": "navigation", "code": "// Responsive navbar", "metadata": {"description": "Top navigation with dropdown"}},
        {"id": "comp_pricing_table", "name": "Pricing Table", "type": "pricing", "code": "// Pricing table", "metadata": {"description": "Three-tier pricing comparison"}},
        {"id": "comp_settings_panel", "name": "Settings Panel", "type": "settings", "code": "// Settings panel", "metadata": {"description": "Profile and security settings"}},
        {"id": "comp_kanban_board", "name": "Kanban Board", "type": "board", "code": "// Kanban board", "metadata": {"description": "Drag-and-drop project management"}}
    ]
    
    for component in components:
        client.add_component(
            component_id=component["id"],
            name=component["name"],
            component_type=component["type"],
            code=component["code"],
            metadata=component["metadata"]
        )
    print(f"   ✅ {len(components)} components seeded")
    
    architectures = [
        {
            "id": "arch_saas_standard",
            "name": "Standard SaaS Architecture",
            "description": "Frontend + Backend + Database for SaaS apps",
            "pattern": {
                "frontend": "React with TypeScript",
                "backend": "PocketBase",
                "database": "SQLite (via PocketBase)",
                "auth": "JWT with PocketBase",
                "deployment": "Docker + Nginx",
                "folder_structure": ["frontend/src/pages/", "frontend/src/components/", "backend/pb_migrations/", "deployment/"]
            }
        },
        {
            "id": "arch_landing_simple",
            "name": "Landing Page Architecture",
            "description": "Simple single-page architecture",
            "pattern": {
                "frontend": "React with TypeScript",
                "sections": ["Hero", "Features", "Pricing", "Testimonials", "CTA", "Footer"],
                "deployment": "Vercel / Static Export"
            }
        }
    ]
    
    for arch in architectures:
        client.add_architecture(
            arch_id=arch["id"],
            name=arch["name"],
            description=arch["description"],
            pattern=arch["pattern"]
        )
    print(f"   ✅ {len(architectures)} architecture patterns seeded")
    print("=" * 60)


def main():
    """Initialize RAG system"""
    
    # Check for --reset flag
    reset = "--reset" in sys.argv
    
    print("\n" + "=" * 60)
    print("🚀 NOVARYX - RAG SYSTEM INITIALIZATION")
    if reset:
        print("   (RESET MODE: Deleting all existing data)")
    print("=" * 60)
    
    # Step 1: Initialize embedding
    print("\n📊 Step 1/4: Setting up embedding manager...")
    embedding_mgr = EmbeddingManager()
    if embedding_mgr.initialize():
        print("   ✅ Embedding system ready")
    else:
        print("   ⚠️  Embedding not available. Install: pip install sentence-transformers")
    
    # Step 2: Create embedding function
    print("\n🔗 Step 2/4: Creating ChromaDB embedding function...")
    try:
        embedding_fn = OllamaEmbeddingFunction()
        test_result = embedding_fn(["test"])
        if test_result is not None and len(test_result) > 0:
            print(f"   ✅ Ollama embeddings working (dimension: {len(test_result[0])})")
        else:
            raise Exception("Empty embedding returned")
    except Exception as e:
        print(f"   ⚠️  Ollama embeddings failed: {e}")
        embedding_fn = None
    
    # Step 3: Initialize ChromaDB
    print("\n🗄️  Step 3/4: Initializing ChromaDB...")
    try:
        client = ChromaDBClient(embedding_function=embedding_fn, reset=reset)
        print("   ✅ ChromaDB initialized")
    except Exception as e:
        print(f"   ❌ ChromaDB failed: {e}")
        print("   💡 Try running with --reset flag")
        return
    
    # Step 4: Seed data
    print("\n🌱 Step 4/4: Seeding initial data...")
    seed_initial_data(client)
    
    # Display stats
    client.display_stats()
    
    # Quick retrieval test
    print("🔍 Testing retrieval...")
    retriever = TemplateRetriever(client)
    test_spec = {
        "type": "saas",
        "requirements": ["dashboard", "analytics"],
        "features": ["charts", "dark mode"],
        "pages": ["dashboard", "settings"],
        "scale": "medium"
    }
    context = retriever.get_context_for_generation(test_spec)
    
    if context["best_template"]:
        name = context["best_template"].get("metadata", {}).get("name", "unknown")
        print(f"   ✅ Retrieval works! Found: {name}")
    else:
        print("   ⚠️  No results found")
    
    print("\n" + "=" * 60)
    print("✅ RAG SYSTEM INITIALIZATION COMPLETE")
    print("=" * 60)
    print(f"\n📍 ChromaDB location: {client.persist_dir}")
    print(f"📦 Collections: {', '.join(client.COLLECTIONS.keys())}")
    print("\nNext: Step 0.4 - Orchestrator Skeleton")
    print("Waiting for your command...\n")


if __name__ == "__main__":
    main()