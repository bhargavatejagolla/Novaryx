"""
NOVARYX - Real LLM Page Generator
Generates complete TSX pages using LLM + RAG context.
Falls back to high-quality templates if LLM fails.
"""
import logging
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from system.memory.context_optimizer import ContextOptimizer, TokenBudget

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
logger = logging.getLogger("novaryx.page_generator")


class LLMPageGenerator:
    """Generates complete TSX pages via LLM with RAG injection"""

    def __init__(self):
        self._provider = None
        self._rag = None

    def _get_provider(self):
        if self._provider is None:
            try:
                from system.inference.provider_factory import get_provider_for_role
                self._provider = get_provider_for_role("generation")
            except Exception as e:
                logger.warning(f"Provider unavailable: {e}")
        return self._provider

    def _get_rag_context(self, query: str, component_type: str = "", domain: str = "") -> str:
        """Retrieve relevant component examples from ChromaDB"""
        try:
            import chromadb
            import os
            persist_dir = os.environ.get(
                "CHROMA_PERSIST_DIR",
                str(Path(__file__).parent.parent / "rag_engine" / "chromadb")
            )
            client = chromadb.PersistentClient(path=persist_dir)
            collection = client.get_collection("novaryx_components")

            where = {}
            if component_type and domain:
                where = {"$and": [
                    {"component_type": {"$eq": component_type}},
                    {"tags": {"$contains": domain}}
                ]}
            elif component_type:
                where = {"component_type": {"$eq": component_type}}
            elif domain:
                where = {"tags": {"$contains": domain}}

            results = collection.query(
                query_texts=[query],
                n_results=2,
                where=where if where else None
            )
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                formatted_lessons = []
                for idx, doc in enumerate(docs[:2]):
                    formatted_lessons.append(
                        f"LESSON {idx+1} (Architectural Pattern):\n"
                        f"STRICTLY follow this implementation pattern for similar components:\n"
                        f"{doc}\n"
                    )
                return "\n\n======================================\n\n".join(formatted_lessons)
        except Exception as e:
            logger.debug(f"RAG unavailable: {e}")
        return ""

    def generate_page(
        self,
        page_name: str,
        route: str,
        title: str,
        description: str,
        components: List[str],
        requires_auth: bool,
        design_tokens: Dict[str, Any],
        domain: str = "",
        contracts: str = ""
    ) -> str:
        """
        Generate a complete TSX page. Returns TSX code string.
        Falls back to a high-quality template if LLM fails.
        """
        provider = self._get_provider()

        # Get RAG context for the primary component type and domain
        component_type = self._infer_component_type(components)
        rag_raw = self._get_rag_context(f"{page_name} {description}", component_type, domain)

        if provider:
            from system.intelligence.prompt_engine import get_prompt_engine
            engine = get_prompt_engine()
            
            # Context Budgeting
            optimizer = ContextOptimizer(model="qwen2.5-coder:7b") # default fallback limit
            if rag_raw:
                optimizer.add_chunk(rag_raw, "rag_examples", priority=5, can_prune=True)
            
            # Auto-tune parameters based on expected complexity and creativity needs
            target_temp = 0.4
            if component_type in ["stats", "table", "settings"]:
                target_temp = 0.2  # Needs strict structure
            elif component_type in ["hero", "landing"]:
                target_temp = 0.6  # Needs high creativity and aesthetic flair

            error_feedback = ""
            current_rag_budget = 4000 # initial token budget for RAG
            
            for attempt in range(3):
                try:
                    optimized_rag = optimizer.optimize(max_tokens=current_rag_budget)
                    
                    base_system_prompt, base_user_prompt = engine.build_page_prompt(
                        page_name=page_name, route=route, title=title,
                        description=description, components=components,
                        requires_auth=requires_auth, design_tokens=design_tokens,
                        rag_context=optimized_rag, contracts=contracts
                    )
                    
                    user_prompt = base_user_prompt
                    if error_feedback:
                        user_prompt += f"\n\nPREVIOUS GENERATION ERROR:\n{error_feedback}\nFIX THIS AND DO NOT USE STATIC TEMPLATES."
                    
                    # Completeness marker
                    user_prompt += "\n\nCRITICAL: Output MUST end with a complete closing brace '}'."

                    result = provider.generate(
                        prompt=user_prompt,
                        system_prompt=base_system_prompt,
                        role="generation",
                        temperature=target_temp,
                        max_tokens=4096,
                    )

                    if result.success and result.text and len(result.text.strip()) > 200:
                        code = self._clean_llm_output(result.text)
                        
                        # Truncation check (unbalanced braces)
                        open_braces = code.count('{')
                        close_braces = code.count('}')
                        if open_braces > close_braces + 2: # minor leniency for string braces
                            error_feedback = "The generated code was truncated due to token limits. It has unbalanced braces. Output a shorter version or omit non-essential parts."
                            logger.warning(f"LLM output truncated (unbalanced braces) for {page_name}, attempt {attempt+1}")
                            current_rag_budget = int(current_rag_budget * 0.5) # Auto-retry with 50% shorter context
                            continue

                        if self._validate_tsx(code):
                            logger.info(f"LLM generated page: {page_name} ({len(code)} chars)")
                            return code
                        else:
                            error_feedback = "The generated code was invalid TSX. Ensure you export default function, and use valid JSX tags."
                            logger.warning(f"LLM output invalid TSX for {page_name}, attempt {attempt+1}")
                            if attempt == 2:
                                return code # Return broken code, let repair engine fix it
                    else:
                        error_feedback = "Output was empty or failed."
                except Exception as e:
                    logger.error(f"LLM page generation failed for {page_name}: {e}")
                    error_feedback = str(e)

        raise RuntimeError(f"Failed to generate page {page_name} dynamically. Static template fallback disabled.")

    def _infer_component_type(self, components: List[str]) -> str:
        if not components:
            return ""
        comp_str = " ".join(components).lower()
        if any(k in comp_str for k in ["hero", "landing"]):
            return "hero"
        if any(k in comp_str for k in ["auth", "login", "signin"]):
            return "auth"
        if any(k in comp_str for k in ["dashboard", "analytics", "stats"]):
            return "stats"
        if any(k in comp_str for k in ["settings", "profile"]):
            return "settings"
        if any(k in comp_str for k in ["pricing", "plans"]):
            return "pricing"
        if any(k in comp_str for k in ["table", "list", "users"]):
            return "table"
        return ""

    def _clean_llm_output(self, text: str) -> str:
        """
        Multi-pass scrubber for LLM output.
        Removes fences, hallucinated trailing XML/JSX tags, extra comment
        blocks the model sometimes appends, and duplicate module blocks.
        """
        text = text.strip()

        # Pass 1: Extract code block if CoT reasoning is present
        # If there's a ```tsx block, grab everything inside it and discard the rest.
        fence_match = re.search(r'```(?:tsx|typescript|jsx|js|ts)?\n(.*?)\n```', text, flags=re.DOTALL | re.IGNORECASE)
        if fence_match:
            text = fence_match.group(1)
        else:
            # Fallback: just strip leading/trailing fences if they exist but don't close properly
            text = re.sub(r'^```(?:tsx|typescript|jsx|js|ts)?\n?', '', text, flags=re.MULTILINE)
            text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
            
        text = text.strip()

        # Pass 2: Remove everything after a second 'export default' block
        # (LLM sometimes appends an entire second file / helper snippet)
        matches = list(re.finditer(r'^export default ', text, re.MULTILINE))
        if len(matches) >= 2:
            text = text[:matches[1].start()].strip()

        # Pass 3: Aggressively strip hallucinated trailing XML/JSX tags at EOF
        text = re.sub(r'(?:</?[A-Za-z0-9_.\-]+[^>]*>?\s*)+$', '', text)
        # Pass 4: Strip lone comment lines appended after closing brace
        text = re.sub(r'(\}\s*)(\/\/[^\n]*\n?)+$', r'\1', text)

        # Pass 5: Strip Next.js-specific 'use client' directive (we're in Vite)
        text = re.sub(r"^['\"]use client['\"];?\s*\n", '', text)

        # Pass 6: Force PascalCase on local import paths with spaces
        # e.g., from './User Management' -> from './UserManagement'
        # Only matches paths starting with ./ or ../
        def fix_import_path(match):
            prefix = match.group(1) # e.g. "from '"
            path_dots = match.group(2) # "./" or "../"
            path_body = match.group(3) # "User Management"
            suffix = match.group(4) # "'"
            # Strip spaces and dashes from the local path body
            clean_body = re.sub(r'[\s\-]', '', path_body)
            # If they used camelCase, we can't easily fix it here, but spaces are the main killer
            return f"{prefix}{path_dots}{clean_body}{suffix}"
        
        text = re.sub(r"(from\s+['\"])([.]{1,2}/)([^'\"]+)(['\"])", fix_import_path, text)

        # Pass 7: Force PascalCase on function names that have spaces
        # e.g. 'export default function User Management()' -> 'export default function UserManagement()'
        def fix_func_name(match):
            prefix = match.group(1) # 'export default function '
            name = match.group(2) # 'User Management'
            suffix = match.group(3) # '(...)'
            clean_name = "".join(w.capitalize() for w in re.sub(r'[^a-zA-Z0-9\s]', '', name).split())
            return f"{prefix}{clean_name}{suffix}"
            
        text = re.sub(r"(export\s+default\s+function\s+)([^\(]+)(\()", fix_func_name, text)

        # Pass 8: Auto-correct invalid Framer Motion prop strings
        def fix_framer_props(match):
            prop = match.group(1)
            val = match.group(2)
            if ":" in val or "," in val:
                return f"{prop}={{{{{val}}}}}"
            return match.group(0)

        text = re.sub(r'\b(initial|animate|whileHover|whileInView|transition|viewport|exit|value)="([^"]*)"', fix_framer_props, text)

        # Pass 9: Fix lucide-react imports to avoid slow LLM repairs
        def fix_lucide(match):
            imports = match.group(1)
            imports = re.sub(r'\bIcon\b,?\s*', '', imports)
            imports = re.sub(r'\b(?:Fi|Fa)([A-Z][a-zA-Z0-9]*)\b', r'\1', imports)
            if not imports.strip().strip(','):
                return ""
            return f"import {{{imports}}} from 'lucide-react'"
        text = re.sub(r"import\s+\{([^}]+)\}\s+from\s+['\"]lucide-react['\"]", fix_lucide, text)

        # Pass 10: Void Element Sanitizer
        # E.g., <input></input> -> <input />
        void_elements = ['input', 'img', 'br', 'hr', 'textarea', 'meta', 'link']
        for tag in void_elements:
            # Fix <tag></tag>
            text = re.sub(rf'<{tag}([^>]*)>\s*</{tag}>', rf'<{tag}\1 />', text)
            # Remove stray </tag> that have no opening tag
            text = re.sub(rf'</{tag}>', '', text)

        # Pass 11: Context Consolidation (Remove local createContext)
        # Prevents Duplicate ThemeContext bugs by stripping local declarations
        text = re.sub(r'const\s+\w*Context\s*=\s*createContext[^;]*;', '', text)
        
        # Pass 12: Import Validation (Ensure ThemeProvider/ThemeContext is imported if used)
        if 'ThemeContext' in text and 'import { ThemeContext }' not in text:
            # Auto-inject import at top
            text = "import { ThemeContext } from '@/components/ThemeProvider';\n" + text
        if '<ThemeProvider' in text and 'import { ThemeProvider }' not in text:
            text = "import { ThemeProvider } from '@/components/ThemeProvider';\n" + text

        # Pass 13: Unescaped Apostrophe/Quote Sanitizer
        def sanitize_quotes(match):
            prop = match.group(1)
            content = match.group(2)
            comma = match.group(3) or ""
            if "'" in content:
                # Escape any unescaped single quotes: team's -> team\'s
                escaped = re.sub(r"(?<!\\)'", r"\'", content)
                return f"{prop}: '{escaped}'{comma}"
            return match.group(0)

        text = re.sub(r'\b(\w+):\s*\'(.*?)\'\s*(,)?\s*$', sanitize_quotes, text, flags=re.MULTILINE)

        def sanitize_jsx_quotes(match):
            prop = match.group(1)
            content = match.group(2)
            if "'" in content:
                # JSX standard prefers double quotes, which naturally fixes apostrophes
                return f'{prop}="{content}"'
            return match.group(0)

        text = re.sub(r'\b(\w+)=\'(.*?)\'(?=\s|/|>)', sanitize_jsx_quotes, text)

        return text.strip()

    def _validate_tsx(self, code: str) -> bool:
        """Basic TSX validation"""
        if len(code) < 100:
            return False
        if "export default" not in code and "export function" not in code:
            return False
        if "<" not in code or ">" not in code:
            return False
        return True

    def _template_fallback(
        self, page_name: str, route: str, title: str, description: str,
        components: List[str], requires_auth: bool, design_tokens: Dict[str, Any]
    ) -> str:
        """
        High-quality Vite/React Router template fallback.
        Uses react-router-dom (not Next.js). Never returns empty or invalid TSX.
        """
        color_mode = design_tokens.get("color_mode", "dark")
        bg = "bg-gray-950" if color_mode == "dark" else "bg-gray-50"
        text_color = "text-white" if color_mode == "dark" else "text-gray-900"
        card_bg = "bg-gray-900 border-white/5" if color_mode == "dark" else "bg-white border-gray-200"
        sub_text = "text-gray-400" if color_mode == "dark" else "text-gray-600"

        auth_guard = ""
        auth_import = ""
        if requires_auth:
            auth_import = "import { useAuth } from '../hooks/useAuth'\nimport { Navigate } from 'react-router-dom'"
            auth_guard = (
                "  const { isAuthenticated, loading } = useAuth()\n"
                "  if (loading) return <div className=\"min-h-screen flex items-center justify-center\"><div className=\"animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full\" /></div>\n"
                "  if (!isAuthenticated) return <Navigate to=\"/login\" replace />\n"
            )

        comps_list = "\n".join([
            f"            <div className=\"p-6 {card_bg} border rounded-2xl\">\n"
            f"              <h3 className=\"text-lg font-semibold {text_color} mb-2\">{c}</h3>\n"
            f"              <p className=\"{sub_text} text-sm\">{c} is ready.</p>\n"
            f"            </div>"
            for c in (components if components else ["Main Content"])
        ])

        return f"""import React from 'react'
import {{ motion }} from 'framer-motion'
import {{ Link }} from 'react-router-dom'
{auth_import}

export default function {page_name}() {{
{auth_guard}
  return (
    <div className="min-h-screen {bg}">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <motion.div
          initial={{{{ opacity: 0, y: 20 }}}}
          animate={{{{ opacity: 1, y: 0 }}}}
          transition={{{{ duration: 0.4 }}}}
        >
          <h1 className="text-3xl font-bold {text_color} mb-2">{title}</h1>
          <p className="{sub_text} mb-8">{description}</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
{comps_list}
          </div>
        </motion.div>
      </div>
    </div>
  )
}}
"""


# Singleton
_generator: Optional[LLMPageGenerator] = None


def get_page_generator() -> LLMPageGenerator:
    global _generator
    if _generator is None:
        _generator = LLMPageGenerator()
    return _generator
