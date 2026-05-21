
"""
NOVARYX - Template Seeder
Creates sample template files on disk and syncs with ChromaDB.

Run this to initialize the template system with working samples.
"""

import sys
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from system.templates.template_registry import TemplateRegistry
from system.templates.template_validator import TemplateValidator
from system.templates.template_adapter import TemplateAdapter

logger = logging.getLogger("novaryx.seed_templates")


def create_sample_template_files(registry: TemplateRegistry):
    """Create actual template files on disk for registered templates"""
    
    templates_data = [
        {
            "template_id": "modern_saas_dash",
            "files": {
                "package.json": json.dumps({
                    "name": "saas-dashboard",
                    "version": "1.0.0",
                    "scripts": {
                        "dev": "vite",
                        "build": "tsc && vite build",
                        "preview": "vite preview"
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "recharts": "^2.10.0",
                        "framer-motion": "^10.16.0"
                    },
                    "devDependencies": {
                        "@types/react": "^18.2.0",
                        "@types/react-dom": "^18.2.0",
                        "typescript": "^5.3.0",
                        "vite": "^5.0.0",
                        "tailwindcss": "^3.4.0",
                        "autoprefixer": "^10.4.0",
                        "postcss": "^8.4.0"
                    }
                }, indent=2),
                
                "tsconfig.json": json.dumps({
                    "compilerOptions": {
                        "target": "ES2020",
                        "lib": ["ES2020", "DOM", "DOM.Iterable"],
                        "module": "ESNext",
                        "skipLibCheck": True,
                        "moduleResolution": "bundler",
                        "allowImportingTsExtensions": True,
                        "resolveJsonModule": True,
                        "isolatedModules": True,
                        "noEmit": True,
                        "jsx": "react-jsx",
                        "strict": True,
                        "noUnusedLocals": True,
                        "noUnusedParameters": True,
                        "noFallthroughCasesInSwitch": True
                    },
                    "include": ["src"]
                }, indent=2),
                
                "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{PROJECT_NAME}} - Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>""",
                
                "src/main.tsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/globals.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
                
                "src/App.tsx": """import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Analytics from './pages/Analytics'
import Users from './pages/Users'
import Settings from './pages/Settings'
import Layout from './components/Layout'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/users" element={<Users />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}""",
                
                "src/pages/Dashboard.tsx": """import { StatsCard, ChartWidget, DataTable } from '../components'

export default function Dashboard() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Dashboard Overview</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard title="Total Users" value="12,345" change="+12%" />
        <StatsCard title="Revenue" value="$45,678" change="+8%" />
        <StatsCard title="Active Projects" value="89" change="+3%" />
        <StatsCard title="Conversion" value="3.2%" change="-1%" />
      </div>
      <ChartWidget title="Revenue Overview" type="line" />
      <DataTable title="Recent Activity" />
    </div>
  )
}""",
                
                "src/styles/globals.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --primary: {{PRIMARY_COLOR}};
  --background: {{BACKGROUND_COLOR}};
  --text: {{TEXT_COLOR}};
}

body {
  font-family: 'Inter', sans-serif;
}
"""
            }
        },
        {
            "template_id": "startup_landing_pro",
            "files": {
                "package.json": json.dumps({
                    "name": "startup-landing",
                    "version": "1.0.0",
                    "scripts": {
                        "dev": "vite",
                        "build": "tsc && vite build"
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "three": "^0.160.0",
                        "@react-three/fiber": "^8.15.0",
                        "@react-three/drei": "^9.92.0",
                        "framer-motion": "^10.16.0"
                    }
                }, indent=2),
                
                "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{PROJECT_NAME}}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>""",
                
                "src/pages/Hero.tsx": """import { Canvas } from '@react-three/fiber'
import { motion } from 'framer-motion'

export default function Hero() {
  return (
    <section className="relative h-screen flex items-center justify-center">
      <div className="absolute inset-0 z-0">
        <Canvas>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} />
          {/* 3D scene here */}
        </Canvas>
      </div>
      <motion.div 
        className="relative z-10 text-center"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-6xl font-bold mb-6">{{HEADLINE}}</h1>
        <p className="text-xl mb-8">{{SUBHEADLINE}}</p>
        <button className="px-8 py-4 rounded-full bg-primary text-white">
          {{CTA_TEXT}}
        </button>
      </motion.div>
    </section>
  )
}"""
            }
        },
        {
            "template_id": "admin_panel_lite",
            "files": {
                "package.json": json.dumps({
                    "name": "admin-panel",
                    "version": "1.0.0",
                    "scripts": {
                        "dev": "vite",
                        "build": "tsc && vite build"
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "@tanstack/react-table": "^8.11.0"
                    }
                }, indent=2),
                
                "src/pages/Users.tsx": """import { useState } from 'react'
import { DataTable } from '../components/DataTable'

export default function Users() {
  const [users] = useState([])
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">User Management</h1>
      <DataTable data={users} />
    </div>
  )
}"""
            }
        }
    ]
    
    print("\n📝 Creating template files on disk...")
    created_count = 0
    
    for template_data in templates_data:
        template_id = template_data["template_id"]
        template = registry.get_template(template_id)
        
        if not template:
            print(f"   ⚠️  Template not registered: {template_id}")
            continue
        
        for file_path, content in template_data["files"].items():
            registry.write_template_file(template_id, file_path, content)
            created_count += 1
        
        print(f"   ✅ {template_id}: {len(template_data['files'])} files created")
    
    print(f"\n   Total: {created_count} files created across {len(templates_data)} templates")
    return created_count


def main():
    """Seed templates and sync to ChromaDB"""
    
    print("\n" + "=" * 60)
    print("🌱 NOVARYX TEMPLATE SEEDER")
    print("=" * 60)
    
    # Initialize registry
    print("\n📁 Initializing Template Registry...")
    registry = TemplateRegistry()
    
    # Register templates
    print("\n📝 Registering templates...")
    
    registry.register_template(
        template_id="modern_saas_dash",
        name="Modern SaaS Dashboard",
        description="Complete SaaS dashboard with analytics, dark mode, and glassmorphism UI",
        project_type="saas_dashboard",
        version="1.0.0",
        pages=["dashboard", "analytics", "users", "settings", "billing", "profile"],
        components=["StatsCard", "ChartWidget", "DataTable", "Sidebar", "Navbar"],
        features=["authentication", "charts", "dark_mode", "responsive", "notifications"],
        tech_stack=["react", "typescript", "tailwind", "recharts", "framer_motion"]
    )
    
    registry.register_template(
        template_id="startup_landing_pro",
        name="Startup Landing Pro",
        description="High-conversion landing page with 3D hero and smooth animations",
        project_type="saas_landing",
        version="1.0.0",
        pages=["hero", "features", "pricing", "testimonials", "cta"],
        components=["Hero3D", "FeatureCard", "PricingTable", "TestimonialCarousel"],
        features=["3d_hero", "animations", "pricing", "newsletter"],
        tech_stack=["react", "typescript", "tailwind", "three_js", "framer_motion"]
    )
    
    registry.register_template(
        template_id="admin_panel_lite",
        name="Admin Panel Lite",
        description="Lightweight admin panel with CRUD operations and data tables",
        project_type="admin_panel",
        version="1.0.0",
        pages=["dashboard", "users", "roles", "settings", "audit_log"],
        components=["DataTable", "CrudForm", "RoleManager", "ActivityLog"],
        features=["crud_operations", "role_management", "data_tables"],
        tech_stack=["react", "typescript", "tailwind", "tanstack_table"]
    )
    
    # Create sample files
    file_count = create_sample_template_files(registry)
    
    # Validate templates
    print("\n🔍 Validating templates...")
    validator = TemplateValidator()
    for template_id in registry.templates:
        template = registry.get_template(template_id)
        result = validator.validate_template(
            template.path,
            template_id=template_id,
            template_name=template.name
        )
        result.display()
    
    # Display adapter rules
    print("\n📋 Template Adapter Rules:")
    adapter = TemplateAdapter()
    print(adapter.get_rules_summary())
    
    # Sync to ChromaDB
    print("\n🔄 Syncing to ChromaDB...")
    try:
        from system.rag_engine.chromadb_client import ChromaDBClient
        chromadb_client = ChromaDBClient()
        synced = registry.sync_to_chromadb(chromadb_client)
        print(f"   ✅ {synced} templates synced to ChromaDB")
    except Exception as e:
        print(f"   ⚠️  ChromaDB sync skipped: {e}")
    
    # Display final registry
    registry.display_registry()
    
    print("\n✅ Template system ready!")
    print(f"   Templates: {len(registry.templates)}")
    print(f"   Files on disk: {file_count}")
    print(f"   Location: {registry.templates_dir}")
    print("\nNext: Phase 0.7 - Logging & Error Handling")
    print("Waiting for your command...\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    main()