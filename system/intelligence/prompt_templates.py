"""
NOVARYX - Prompt Templates
Optimized LLM prompts for intent extraction.

Each template is crafted to produce valid, structured JSON.
Tested for consistent output across different LLM models.
"""


class PromptTemplates:
    """Collection of optimized prompt templates for the LLM"""
    
    INTENT_EXTRACTION = """You are NOVARYX, an expert AI application architect. Your job is to analyze a user's website/app request and produce a detailed, structured project specification.

USER REQUEST: "{prompt}"

Analyze the request deeply. Consider:
- What type of application is this?
- What features are explicitly or implicitly requested?
- Think as a Lead System Architect: What is the deep, hierarchical sitemap required for this specific domain? (Generate 5 to 20 pages depending on complexity, e.g., nested dashboards, settings, data views, etc.)
- What design style is described?
- What technical requirements are implied?

Return ONLY valid JSON. No explanations, no markdown, just the JSON object.

{{
  "project_name": "Extracted or generated project name (max 40 chars)",
  "project_description": "1-2 sentence summary of what this project is",
  "project_type": "saas_dashboard|landing_page|ecommerce|admin_panel|portfolio|blog|social_app|documentation|marketing_site",
  "project_type_confidence": 0.0-1.0,
  "complexity": "simple|medium|complex|enterprise",
  "target_audience": "Who is this for? (developers, businesses, consumers, etc.)",
  "industry": "technology|healthcare|finance|education|ecommerce|entertainment|other",
  
  "brand_name": "Brand or company name if mentioned",
  "tagline": "Tagline or slogan if mentioned",
  
  "design": {{
    "color_mode": "dark|light|auto",
    "primary_color_name": "purple|indigo|blue|teal|green|red|orange|pink|cyan|amber|slate",
    "accent_color_name": "cyan|amber|pink|teal|orange|purple|green|blue",
    "font_preference": "inter|poppins|roboto|mono|serif",
    "font_style": "modern|classic|playful|corporate|minimal",
    "glassmorphism": true|false,
    "three_d_enabled": true|false,
    "three_d_elements": ["list", "of", "3d", "elements", "if", "any"],
    "animation_level": "subtle|moderate|rich|none",
    "border_radius": "small|medium|large|none",
    "density": "compact|comfortable|spacious"
  }},
  
  "pages": [
    {{
      "name": "PageName",
      "route": "/page-route",
      "title": "Page Title",
      "description": "What this page shows",
      "components": ["component1", "component2"],
      "requires_auth": true|false,
      "is_landing": true|false
    }}
  ],
  
  "features": [
    {{
      "name": "Feature Name",
      "description": "What this feature does",
      "priority": "high|medium|low",
      "requires_auth": true|false,
      "requires_database": true|false,
      "requires_3d": true|false,
      "components_needed": ["component1"],
      "pages_affected": ["/route1"]
    }}
  ],
  
  "requires_authentication": true|false,
  "requires_database": true|false,
  "requires_payments": true|false,
  "requires_file_upload": true|false,
  "requires_real_time": true|false,
  "requires_search": true|false,
  "requires_email": true|false,
  "requires_ai_assistant": true|false,
  
  "sample_content": {{
    "hero_headline": "Suggested hero headline",
    "hero_subheadline": "Suggested subheadline",
    "cta_text": "Suggested CTA button text"
  }},
  
  "confidence_score": 0.0-1.0
}}

RULES:
1. Every field must be present. Use null for unknown values.
2. project_type MUST be one of the listed types.
3. Pages array must have at least 5-15 entries for complex applications (e.g. dashboards, ecommerce) representing a deep, domain-specific architecture (e.g., /dashboard/analytics, /settings/profile, /threat-map).
4. Features array can be empty [] if none specified.
5. For common apps, suggest appropriate pages and features.
6. Be specific and detailed. Better to over-specify than under-specify.
7. If the user mentions specific colors, fonts, or styles, capture them exactly.
"""

    INTENT_REFINEMENT = """You are refining a project specification. The user provided additional feedback.

ORIGINAL REQUEST: "{prompt}"

USER FEEDBACK: "{feedback}"

Update the project specification JSON to incorporate this feedback.
Return ONLY the updated JSON object with the same structure."""

    FEATURE_EXPANSION = """Given this feature: "{feature_name}"
And project context: "{project_context}"

List the specific UI components and technical requirements needed.
Return JSON:
{{
  "feature_name": "name",
  "components": ["list", "of", "needed", "components"],
  "technical_requirements": ["list", "of", "tech", "needs"],
  "estimated_pages": 3,
  "complexity": "simple|medium|complex"
}}"""

    PROJECT_NAME_GENERATOR = """Generate a creative, memorable project name for:
DESCRIPTION: "{prompt}"

Return JSON:
{{
  "suggestions": ["Name1", "Name2", "Name3"],
  "recommended": "Name1",
  "domain_hint": "name1.com"
}}"""

    COMPETITOR_ANALYSIS = """For a project described as: "{prompt}"
Suggest 3-5 similar existing products or websites for design reference.
Return JSON:
{{
  "similar_products": [
    {{"name": "ProductName", "url": "example.com", "why_similar": "reason"}}
  ]
}}"""