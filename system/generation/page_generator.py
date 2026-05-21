"""
NOVARYX - Page Generator
Generates individual page components with proper structure.
"""

from typing import Dict, List, Optional


class PageGenerator:
    """Generates page components"""
    
    @staticmethod
    def generate_page(
        page_name: str,
        route: str,
        title: str,
        description: str,
        components: List[str],
        requires_auth: bool = False,
        is_landing: bool = False
    ) -> str:
        """Generate a single page component"""
        
        # Build component imports
        comp_imports = []
        comp_usage = []
        for comp in components:
            comp_name = comp.replace(" ", "").replace("-", "")
            comp_imports.append(f"import {{ {comp_name} }} from '../components/{comp_name}'")
            comp_usage.append(f"          <{comp_name} />")
        
        imports_block = "\n".join(comp_imports) if comp_imports else "// No specific components"
        usage_block = "\n".join(comp_usage) if comp_usage else "          <p className='text-[var(--text-secondary)]'>Content coming soon</p>"
        
        return f"""import React from 'react'
import {{ motion }} from 'framer-motion'
{imports_block}

export default function {page_name}() {{
  return (
    <motion.div
      initial={{{{ opacity: 0, y: 20 }}}}
      animate={{{{ opacity: 1, y: 0 }}}}
      transition={{{{ duration: 0.4 }}}}
      className="p-6 space-y-6"
    >
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">{title}</h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">{description}</p>
      </div>
      
      <div className="space-y-6">
{usage_block}
      </div>
    </motion.div>
  )
}}
"""
    
    @staticmethod
    def generate_pages_from_spec(pages: List[Dict]) -> Dict[str, str]:
        """Generate all pages from a page spec list"""
        generated = {}
        
        for page in pages:
            name = page.get("name", "Page")
            content = PageGenerator.generate_page(
                page_name=name,
                route=page.get("route", "/"),
                title=page.get("title", name),
                description=page.get("description", ""),
                components=page.get("components", []),
                requires_auth=page.get("requires_auth", False),
                is_landing=page.get("is_landing", False)
            )
            generated[f"src/pages/{name}.tsx"] = content
        
        return generated
    
    @staticmethod
    def generate_loading_page() -> str:
        """Generate a loading/splash page"""
        return """import React from 'react'
import { motion } from 'framer-motion'

export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-[var(--background)]">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
        className="w-12 h-12 border-2 border-[var(--border)] border-t-[var(--primary)] rounded-full"
      />
    </div>
  )
}
"""
    
    @staticmethod
    def generate_error_page() -> str:
        """Generate a 404/error page"""
        return """import React from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'

export default function Error() {
  const navigate = useNavigate()
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-[var(--background)]">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center p-8"
      >
        <div className="text-8xl mb-6">404</div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-4">
          Page Not Found
        </h1>
        <p className="text-[var(--text-secondary)] mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-3 bg-[var(--primary)] text-white rounded-full hover:shadow-[var(--shadow-glow)] transition-shadow"
        >
          Go Home
        </button>
      </motion.div>
    </div>
  )
}
"""