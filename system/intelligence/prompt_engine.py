"""
NOVARYX - Prompt Engine
Centralized prompt builder with role-specific, model-tuned templates.

All prompts are optimized for:
  - qwen2.5-coder (generation)
  - deepseek-coder (repair)
  - llama-3.1/3.3 on Groq (planning)

Usage:
  from system.intelligence.prompt_engine import PromptEngine
  engine = PromptEngine()
  prompt = engine.build_page_prompt(page_spec, design_tokens, rag_context)
"""

import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("novaryx.prompt_engine")


class PromptEngine:
    """
    Centralized prompt builder with RAG injection support.
    All prompts are tuned for qwen2.5-coder instruction format.
    """

    # ------------------------------------------------------------------
    # Intent Extraction
    # ------------------------------------------------------------------

    INTENT_SYSTEM = """You are NOVARYX Planner. Extract structured project specs from user prompts.
Output ONLY valid JSON. No explanations. No markdown. Just the JSON object."""

    INTENT_TEMPLATE = """Analyze this project request and extract a complete specification.

USER REQUEST:
{prompt}

Output a JSON object with EXACTLY this structure:
{{
  "project_name": "short-kebab-case-name",
  "project_type": "saas|landing|ecommerce|admin|blog|portfolio|startup|dashboard",
  "complexity": "simple|moderate|complex",
  "description": "one sentence description",
  "pages": [
    {{
      "name": "PageName",
      "route": "/route",
      "title": "Page Title",
      "description": "what this page does",
      "components": ["Hero", "Features", "CTA"],
      "requires_auth": false,
      "is_landing": true
    }}
  ],
  "features": [
    {{"name": "feature-name", "description": "what it does", "priority": "high|medium|low"}}
  ],
  "design": {{
    "color_mode": "dark|light",
    "primary_color": "#hex",
    "style": "glassmorphism|minimal|corporate|vibrant",
    "animation_level": "minimal|moderate|rich",
    "three_d_enabled": false
  }},
  "requires_database": true,
  "requires_authentication": true,
  "tech_stack": ["Next.js", "TypeScript", "Tailwind CSS"],
  "confidence_score": 0.95
}}

RULES:
- Include at minimum: home page + 2-3 feature pages relevant to the request
- For SaaS/admin: always include dashboard, settings, auth pages
- For landing pages: hero, features, pricing, contact
- Pages must have realistic routes (/dashboard, /settings, not /page1)
- confidence_score: 0.9+ if clear, 0.6-0.9 if some guessing, <0.6 if very vague"""

    # ------------------------------------------------------------------
    # Page Generation
    # ------------------------------------------------------------------

    PAGE_SYSTEM = """You are NOVARYX, an elite React/TypeScript code generator for Vite projects.
Output ONLY valid TypeScript/TSX source code. No prose, no markdown, no code fences.

ABSOLUTE RULES - violations will break production builds:
1. Use react-router-dom for routing (NOT next/link, NOT next/navigation)
2. Use default exports: `export default function ComponentName()`
3. One single export default per file - NEVER write two
4. End your output with the closing `}` of the component. NOTHING after it.
5. Do NOT write trailing XML tags, closing tags, or any text after the final `}`
6. Do NOT include 'use client' directives
7. All imports must be from: react, react-router-dom, framer-motion, lucide-react, ../hooks/useAuth
8. For framer-motion, ONLY use object syntax for props. Example: initial={{ opacity: 0, y: 20 }} NOT initial="opacity: 0".
9. For lucide-react, import specific icons by their standard names (e.g., import { Mail, ArrowRight } from 'lucide-react'). DO NOT use 'Fi' or 'Fa' prefixes or generic 'Icon' components.
10. DO NOT import missing custom hooks like 'useAuth' unless explicitly provided.
11. NEVER add closing tags for HTML void elements (`input`, `img`, `br`, `hr`, `textarea`). Use self-closing syntax: `<input />` not `<input></input>`.
12. If you need a theme context, ALWAYS `import { ThemeContext } from '@/components/ThemeProvider'` - NEVER create `createContext` yourself.
13. Always close all JSX tags within the component return statement.
14. If you reach the token limit, STOP and close all open braces to ensure compilation.
15. Output ONLY complete, compilable TypeScript.
16. Every `.map()` JSX element MUST include a unique `key` prop.
17. Use ONLY `var(--primary)`, `var(--surface)`, `var(--text-primary)`, etc. for colors. Do NOT hardcode hex colors."""

    PAGE_TEMPLATE = """Generate a complete React Router page component.

PAGE SPEC:
- Name: {page_name}
- Route: {route}
- Title: {title}
- Description: {description}
- Components needed: {components}
- Requires auth: {requires_auth}

DESIGN TOKENS (Apply ruthlessly):
- Color mode: {color_mode}
- Primary color: {primary_color}
- Style: {style}
- Font: {font}

GENERATION CONTRACTS:
- Allowed external imports: React, framer-motion, lucide-react, react-router-dom
- Routing Scope: Use standard React Router 'Link' and 'useNavigate'

{rag_context}

{contracts}

REQUIREMENTS:
1. MAXIMIZE AESTHETICS: The interface must feel incredibly premium, state-of-the-art, and "wow" the user immediately.
2. DYNAMIC & ALIVE: heavily utilize framer-motion for micro-interactions, layout transitions, hover states, and staggering list reveals.
3. PREMIUM SCALING: Use smooth gradients, translucent glassmorphism panels (backdrop-blur), and curated color matching.
4. STRUCTURE: Complete TypeScript file using React and Tailwind CSS.
5. EXPORTS: Strict `export default function {page_name}()`.
6. CONTENT: Write deep, realistic placeholder data that looks like a real production SaaS platform.

Generate the complete {page_name}.tsx file using this EXACT Step-by-Step process:
STEP 1: List all components needed for this page
STEP 2: Define all props interfaces
STEP 3: Write the imports
STEP 4: Write the component skeleton
STEP 5: Fill in the JSX with animations and states
STEP 6: Output the COMPLETE code from all steps combined inside a single ```tsx block.

CRITICAL RULE: DO NOT append any random text, XML, or hallucinated closing tags after the final '}}' of your component block."""

    # ------------------------------------------------------------------
    # Component Generation
    # ------------------------------------------------------------------

    COMPONENT_SYSTEM = """You are NOVARYX Component Generator.
Generate reusable, production-quality React components.
Output ONLY the TypeScript code. No prose, no markdown.

ABSOLUTE RULES:
1. NEVER add closing tags for HTML void elements (`input`, `img`, `br`, `hr`, `textarea`). Use self-closing syntax: `<input />` not `<input></input>`.
2. If you need a theme context, ALWAYS `import { ThemeContext } from '@/components/ThemeProvider'` - NEVER create `createContext` yourself.
3. Always close all JSX tags within the component return statement.
4. If you reach the token limit, STOP and close all open braces to ensure compilation.
5. Output ONLY complete, compilable TypeScript.
6. Every `.map()` JSX element MUST include a unique `key` prop.
7. Use ONLY `var(--primary)`, `var(--surface)`, `var(--text-primary)`, etc. for colors. Do NOT hardcode hex colors."""

    COMPONENT_TEMPLATE = """Generate a reusable React component.

COMPONENT: {component_name}
PURPOSE: {purpose}
PROPS: {props_description}

DESIGN:
- Color mode: {color_mode}
- Primary: {primary_color}
- Style: {style}

{rag_context}

REQUIREMENTS:
- TypeScript with full prop types (interface Props)
- Tailwind CSS styling
- Framer Motion for animations where appropriate
- Accessibility attributes (aria-*)
- Responsive design
- Export as named export AND default export

PERFECT EXAMPLE (StatsCard):
```tsx
import {{ motion }} from 'framer-motion';

export interface StatsCardProps {{
  title: string;
  value: number;
  trend: 'up' | 'down';
}}

export function StatsCard({{ title, value, trend }}: StatsCardProps) {{
  return (
    <motion.div
      whileHover={{{{ y: -2 }}}}
      className="p-6 rounded-xl bg-[var(--surface)] border border-[var(--border)]"
    >
      <h3 className="text-sm text-[var(--text-secondary)]">{{title}}</h3>
      <p className="text-2xl font-bold text-[var(--text-primary)]">{{value}}</p>
      <span className={{trend === 'up' ? 'text-green-500' : 'text-red-500'}}>
        {{trend === 'up' ? '↑' : '↓'}}
      </span>
    </motion.div>
  );
}}
export default StatsCard;
```

Generate {component_name}.tsx using this EXACT Step-by-Step process:
STEP 1: Define the props interface
STEP 2: Write the imports
STEP 3: Write the component skeleton
STEP 4: Fill in the JSX with design tokens and animations
STEP 5: Output the COMPLETE code inside a single ```tsx block."""

    # ------------------------------------------------------------------
    # Backend Schema
    # ------------------------------------------------------------------

    SCHEMA_SYSTEM = """You are NOVARYX Backend Architect.
Generate PocketBase collection schemas from project descriptions.
Output ONLY valid JSON."""

    SCHEMA_TEMPLATE = """Generate PocketBase collection schemas for this project.

PROJECT: {project_name}
TYPE: {project_type}
FEATURES: {features}
PAGES: {pages}

Output a JSON array of collections:
[
  {{
    "name": "collection_name",
    "type": "base|auth",
    "fields": [
      {{
        "name": "field_name",
        "type": "text|number|bool|date|select|relation|file|json",
        "required": true,
        "options": {{}}
      }}
    ],
    "indexes": ["field_name"],
    "rules": {{
      "listRule": "@request.auth.id != ''",
      "viewRule": "@request.auth.id != ''",
      "createRule": "@request.auth.id != ''",
      "updateRule": "@request.auth.id = id",
      "deleteRule": "@request.auth.id = id"
    }}
  }}
]

RULES:
- Always include 'users' collection if auth required
- Use realistic field names
- Add proper access rules
- Include relations between collections
- Add indexes for frequently queried fields

Generate the complete schema:"""

    # ------------------------------------------------------------------
    # Repair
    # ------------------------------------------------------------------

    REPAIR_SYSTEM = """You are NOVARYX Repair. Fix bugs in React/TypeScript files.
Output ONLY the complete fixed file. No explanations. No markdown.

ABSOLUTE RULES:
1. Fix ONLY the listed bugs. Do NOT change working code.
2. For framer-motion, ensure object syntax is used for props: initial={{ opacity: 0 }}.
3. For lucide-react, use standard names (e.g. Mail) and NOT 'FiMail' or 'Icon'.
4. Do NOT import missing custom hooks unless explicitly provided."""

    REPAIR_TEMPLATE = """Fix ALL bugs in this file.

FILE: {file_path}

BUGS TO FIX:
{bug_list}

ORIGINAL CODE:
{code}

RULES:
- Fix ONLY the listed bugs
- Do NOT change working code
- Keep all existing functionality and structure
- Return the COMPLETE fixed file (all lines)
- No markdown fences, no explanations

Fixed {file_path}:"""

    # ------------------------------------------------------------------
    # Builder methods
    # ------------------------------------------------------------------

    def build_intent_prompt(self, user_prompt: str) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) for intent extraction"""
        return (
            self.INTENT_SYSTEM,
            self.INTENT_TEMPLATE.format(prompt=user_prompt)
        )

    def build_page_prompt(
        self,
        page_name: str,
        route: str,
        title: str,
        description: str,
        components: List[str],
        requires_auth: bool,
        design_tokens: Dict[str, Any],
        rag_context: str = "",
        contracts: str = ""
    ) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) for page generation"""

        rag_section = ""
        if rag_context:
            rag_section = (
                f"RETRIEVAL FINE-TUNING (Mandatory Architectural Lessons):\n"
                f"{rag_context}\n"
                f"\nCRITICAL: You must strictly adapt and follow the exact architectural patterns, state management, "
                f"and styling conventions shown in the lessons above for this specific page."
            )

        user = self.PAGE_TEMPLATE.format(
            page_name=page_name,
            route=route,
            title=title,
            description=description,
            components=", ".join(components) if components else "flexible",
            requires_auth=str(requires_auth).lower(),
            color_mode=design_tokens.get("color_mode", "dark"),
            primary_color=design_tokens.get("primary_color", "#6366f1"),
            style=design_tokens.get("style", "glassmorphism"),
            font=design_tokens.get("font", "Inter"),
            rag_context=rag_section,
            contracts=contracts
        )
        return self.PAGE_SYSTEM, user

    def build_component_prompt(
        self,
        component_name: str,
        purpose: str,
        props_description: str,
        design_tokens: Dict[str, Any],
        rag_context: str = ""
    ) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) for component generation"""

        rag_section = ""
        if rag_context:
            rag_section = (
                f"RETRIEVAL FINE-TUNING (Mandatory Architectural Lessons):\n"
                f"{rag_context}\n"
                f"\nCRITICAL: You must strictly adapt and follow the exact architectural patterns, state management, "
                f"and styling conventions shown in the lessons above for this specific component."
            )

        user = self.COMPONENT_TEMPLATE.format(
            component_name=component_name,
            purpose=purpose,
            props_description=props_description,
            color_mode=design_tokens.get("color_mode", "dark"),
            primary_color=design_tokens.get("primary_color", "#6366f1"),
            style=design_tokens.get("style", "glassmorphism"),
            rag_context=rag_section,
        )
        return self.COMPONENT_SYSTEM, user

    def build_schema_prompt(
        self,
        project_name: str,
        project_type: str,
        features: List[str],
        pages: List[str]
    ) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt) for backend schema generation"""
        user = self.SCHEMA_TEMPLATE.format(
            project_name=project_name,
            project_type=project_type,
            features=", ".join(features) if features else "standard features",
            pages=", ".join(pages) if pages else "standard pages",
        )
        return self.SCHEMA_SYSTEM, user

    def build_repair_prompt(
        self,
        file_path: str,
        code: str,
        bugs: List[Any],
        max_code_chars: int = 12000
    ) -> tuple[str, str]:
        """
        Returns (system_prompt, user_prompt) for repair.
        Truncates code if needed to fit context window.
        """
        bug_list = "\n".join([
            f"- Line {getattr(b, 'line_number', '?')}: [{getattr(b, 'bug_type', b)}] "
            f"{getattr(b, 'description', str(b))}"
            for b in bugs
        ])

        # Truncate code if too long
        truncated = False
        if len(code) > max_code_chars:
            code = code[:max_code_chars]
            truncated = True
            logger.warning(
                f"Truncated {file_path} from {len(code)} to {max_code_chars} chars for repair"
            )

        user = self.REPAIR_TEMPLATE.format(
            file_path=file_path,
            bug_list=bug_list,
            code=code + ("\n... [TRUNCATED]" if truncated else ""),
        )
        return self.REPAIR_SYSTEM, user

    def inject_rag_context(self, raw_context: List[Dict]) -> str:
        """Format RAG retrieval results for prompt injection"""
        if not raw_context:
            return ""

        parts = []
        for i, item in enumerate(raw_context[:3], 1):  # Max 3 examples
            content = item.get("content", "") or item.get("document", "")
            meta = item.get("metadata", {})
            component_type = meta.get("component_type", "component")
            parts.append(f"Example {i} ({component_type}):\n```tsx\n{content[:800]}\n```")

        return "\n\n".join(parts)


# Singleton
_engine: Optional[PromptEngine] = None


def get_prompt_engine() -> PromptEngine:
    global _engine
    if _engine is None:
        _engine = PromptEngine()
    return _engine
