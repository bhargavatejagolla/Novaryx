"""
NOVARYX - Template Intelligence Engine
Advanced LLM + RAG system for semantic component selection.

Upgrades keyword matching to AI understanding:
  Prompt → LLM Semantic Analysis → RAG Retrieval → Confidence Scoring → Best Selection

Features:
  - Semantic intent extraction via LLM
  - RAG-based similar project retrieval
  - Confidence scoring for every selection
  - Fallback chain: LLM → RAG → Keywords → Defaults
  - Learning from generation history
  - Component relationship awareness
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from system.templates.dynamic.layouts.base_layout import BaseLayout, LayoutSlot, LayoutType
from system.templates.dynamic.layouts.layout_registry import LayoutRegistry
from system.templates.dynamic.components.component_registry import ComponentRegistry, ComponentMeta
from system.templates.dynamic.components.three_d.three_registry import ThreeRegistry, ThreeComponentMeta

logger = logging.getLogger("novaryx.intelligence")


@dataclass
class SelectionResult:
    """Result of intelligent component selection with confidence"""
    component_id: str
    component_name: str
    confidence: float  # 0.0 to 1.0
    source: str  # "llm", "rag", "keyword", "default"
    reasoning: str
    slot_name: str = ""


@dataclass
class IntentAnalysis:
    """LLM analysis of user intent"""
    project_type: str
    project_type_confidence: float
    features_requested: List[str]
    visual_style: Dict[str, Any]
    target_audience: str
    complexity_level: str  # simple, medium, complex
    similar_to: List[str]
    raw_analysis: str


class TemplateIntelligence:
    """
    Advanced AI-powered template and component selection.
    
    Uses:
      1. LLM for semantic intent understanding
      2. RAG (ChromaDB) for similar project retrieval
      3. Confidence scoring for every decision
      4. Component relationship graph for smart combinations
    """
    
    def __init__(self, use_llm: bool = True, use_rag: bool = True):
        self.use_llm = use_llm
        self.use_rag = use_rag
        self._inference = None
        self._rag_client = None
        self._retriever = None
        
        # Component relationship map (which components work well together)
        self.component_relationships = self._build_relationship_map()
        
        # Generation history for learning
        self.generation_history: List[Dict[str, Any]] = []
    
    def _get_inference(self):
        """Lazy load inference provider"""
        if self._inference is None:
            try:
                from system.inference.provider_factory import get_provider
                self._inference = get_provider()
            except Exception as e:
                logger.warning(f"Inference not available: {e}")
        return self._inference
    
    def _get_rag(self):
        """Lazy load RAG system"""
        if self._rag_client is None and self.use_rag:
            try:
                from system.rag_engine.chromadb_client import ChromaDBClient
                from system.rag_engine.retriever import TemplateRetriever
                self._rag_client = ChromaDBClient()
                self._retriever = TemplateRetriever(self._rag_client)
            except Exception as e:
                logger.warning(f"RAG not available: {e}")
        return self._retriever
    
    def _build_relationship_map(self) -> Dict[str, List[str]]:
        """Build map of which components work well together"""
        return {
            "sidebar": ["navbar", "breadcrumbs", "stats_card", "chart_widget", "data_table"],
            "navbar": ["sidebar", "hero", "footer", "theme_toggle"],
            "stats_card": ["chart_widget", "data_table", "activity_feed"],
            "chart_widget": ["stats_card", "data_table", "activity_feed"],
            "data_table": ["search_bar", "modal", "empty_state", "breadcrumbs"],
            "auth_form": ["modal", "toast_notification", "error_boundary"],
            "hero": ["navbar", "features_grid", "cta_section", "footer"],
            "features_grid": ["hero", "pricing_table", "testimonials"],
            "pricing_table": ["features_grid", "cta_section", "faq_section"],
            "globe": ["stats_card", "chart_widget", "particles"],
            "particles": ["hero", "globe", "card_3d"],
            "hero_scene": ["hero", "navbar", "scroll_reveal"],
        }
    
    # =====================================================================
    # MAIN INTELLIGENCE METHODS
    # =====================================================================
    
    def analyze_intent(self, prompt: str) -> IntentAnalysis:
        """
        Use LLM to semantically analyze user intent.
        
        Extracts:
        - What type of project
        - What features needed
        - Visual style preferences
        - Complexity level
        - Similar existing products
        """
        
        # Step 1: Try LLM analysis
        if self.use_llm:
            llm_analysis = self._llm_analyze(prompt)
            if llm_analysis:
                return llm_analysis
        
        # Step 2: Fallback to keyword analysis
        return self._keyword_analyze(prompt)
    
    def _llm_analyze(self, prompt: str) -> Optional[IntentAnalysis]:
        """Use LLM to analyze prompt intent"""
        provider = self._get_inference()
        if not provider:
            return None
        
        analysis_prompt = f"""Analyze this website/app request and extract structured information.

USER REQUEST: "{prompt}"

Return ONLY a JSON object with these fields:
{{
  "project_type": "saas_dashboard|landing_page|ecommerce|admin_panel|portfolio|blog|social_app",
  "project_type_confidence": 0.0-1.0,
  "features_requested": ["list", "of", "specific", "features"],
  "visual_style": {{
    "color_preference": "dark|light|colorful|minimal",
    "animation_level": "subtle|moderate|rich",
    "three_d_required": true|false,
    "glassmorphism": true|false,
    "font_style": "modern|classic|playful|corporate"
  }},
  "target_audience": "who is this for",
  "complexity_level": "simple|medium|complex",
  "similar_to": ["similar", "products", "or", "websites"]
}}

Rules:
- Be specific about features, don't use vague terms
- If unsure about a field, use your best guess
- project_type MUST be one of the listed types
- features_requested should list individual components/features needed
"""
        
        try:
            result = provider.generate(
                prompt=analysis_prompt,
                role="planning",
                temperature=0.1,
                max_tokens=500
            )
            
            if result.success and result.text:
                # Extract JSON from response
                text = result.text.strip()
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(text[json_start:json_end])
                    
                    return IntentAnalysis(
                        project_type=data.get("project_type", "saas_dashboard"),
                        project_type_confidence=data.get("project_type_confidence", 0.7),
                        features_requested=data.get("features_requested", []),
                        visual_style=data.get("visual_style", {}),
                        target_audience=data.get("target_audience", "general"),
                        complexity_level=data.get("complexity_level", "medium"),
                        similar_to=data.get("similar_to", []),
                        raw_analysis=text[:500]
                    )
        except Exception as e:
            logger.warning(f"LLM analysis failed: {e}")
        
        return None
    
    def _keyword_analyze(self, prompt: str) -> IntentAnalysis:
        """Fallback keyword-based intent analysis"""
        prompt_lower = prompt.lower()
        
        # Detect project type
        type_scores = {
            "saas_dashboard": sum(1 for kw in ["dashboard", "saas", "analytics", "admin", "metrics", "kpi"] if kw in prompt_lower),
            "landing_page": sum(1 for kw in ["landing", "hero", "pricing", "cta", "marketing", "waitlist"] if kw in prompt_lower),
            "ecommerce": sum(1 for kw in ["store", "shop", "product", "cart", "checkout", "buy"] if kw in prompt_lower),
            "admin_panel": sum(1 for kw in ["admin", "management", "crud", "users", "roles", "permissions"] if kw in prompt_lower),
            "portfolio": sum(1 for kw in ["portfolio", "showcase", "creative", "projects", "gallery", "work"] if kw in prompt_lower),
        }
        best_type = max(type_scores, key=type_scores.get)
        type_conf = min(type_scores[best_type] / 3.0, 1.0)
        
        # Detect features
        feature_keywords = {
            "authentication": ["login", "register", "auth", "sign in", "sign up", "password"],
            "dashboard": ["dashboard", "overview", "stats", "metrics", "kpi"],
            "analytics": ["analytics", "charts", "graphs", "reports", "insights"],
            "user_management": ["users", "user management", "team", "members"],
            "payments": ["payment", "billing", "stripe", "subscription", "pricing"],
            "notifications": ["notification", "alert", "notify", "inbox"],
            "search": ["search", "find", "filter", "lookup"],
            "3d_elements": ["3d", "three", "globe", "particle", "webgl"],
            "animations": ["animation", "motion", "smooth", "transition"],
            "dark_mode": ["dark mode", "dark theme", "night mode"],
            "messaging": ["chat", "message", "communication", "talk"],
            "file_upload": ["upload", "file", "image", "document", "attachment"],
            "ecommerce": ["cart", "product", "shop", "store", "checkout"],
            "social": ["social", "share", "comment", "like", "follow"],
            "kanban": ["kanban", "board", "drag", "drop", "task"],
        }
        
        features = []
        for feature, keywords in feature_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                features.append(feature)
        
        # Detect visual style
        visual_style = {
            "color_preference": "dark" if any(w in prompt_lower for w in ["dark", "night", "midnight"]) else "light" if any(w in prompt_lower for w in ["light", "white", "bright"]) else "colorful",
            "animation_level": "rich" if any(w in prompt_lower for w in ["animated", "motion", "smooth"]) else "moderate",
            "three_d_required": any(w in prompt_lower for w in ["3d", "three", "globe", "particle"]),
            "glassmorphism": any(w in prompt_lower for w in ["glass", "frosted", "translucent"]),
            "font_style": "modern"
        }
        
        return IntentAnalysis(
            project_type=best_type,
            project_type_confidence=type_conf,
            features_requested=features,
            visual_style=visual_style,
            target_audience="general",
            complexity_level="medium" if len(features) > 5 else "simple",
            similar_to=[],
            raw_analysis="Keyword-based analysis"
        )
    
    def retrieve_similar_projects(self, prompt: str, intent: IntentAnalysis) -> List[Dict[str, Any]]:
        """
        Use RAG to find similar past projects and their component selections.
        """
        retriever = self._get_rag()
        if not retriever:
            return []
        
        try:
            # Build search query from intent
            query = f"{intent.project_type} {' '.join(intent.features_requested)}"
            
            # Search templates
            templates = retriever.find_best_template(
                project_type=intent.project_type,
                requirements=intent.features_requested,
                top_k=3
            )
            
            # Search architecture patterns
            arch_results = retriever.find_architecture(
                project_description=query,
                scale=intent.complexity_level
            )
            
            similar = []
            for t in templates:
                if t.get("id") != "fallback":
                    similar.append({
                        "template_id": t.get("id", ""),
                        "name": t.get("metadata", {}).get("name", "Unknown"),
                        "similarity": 1.0 - t.get("distance", 1.0),
                        "type": "template"
                    })
            
            logger.info(f"RAG retrieved {len(similar)} similar projects")
            return similar
            
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            return []
    
    def select_components_intelligently(
        self,
        prompt: str,
        layout: BaseLayout,
        intent: IntentAnalysis = None
    ) -> Dict[str, List[SelectionResult]]:
        """
        Intelligently select components for each slot using LLM + RAG + Keywords.
        
        Returns: slot_name → list of SelectionResult with confidence scores
        """
        
        # Step 1: Analyze intent if not provided
        if intent is None:
            intent = self.analyze_intent(prompt)
        
        # Step 2: Retrieve similar projects
        similar_projects = self.retrieve_similar_projects(prompt, intent)
        
        # Step 3: Select components for each slot
        selections: Dict[str, List[SelectionResult]] = {}
        
        for slot in layout.get_all_slots():
            slot_selections = self._select_for_slot(
                slot=slot,
                prompt=prompt,
                intent=intent,
                similar_projects=similar_projects
            )
            selections[slot.name] = slot_selections
        
        return selections
    
    def _select_for_slot(
        self,
        slot: LayoutSlot,
        prompt: str,
        intent: IntentAnalysis,
        similar_projects: List[Dict[str, Any]]
    ) -> List[SelectionResult]:
        """
        Select the best components for a single slot.
        
        Uses multi-strategy approach:
        1. LLM recommendation (highest weight)
        2. RAG from similar projects
        3. Keyword matching
        4. Relationship-based suggestions
        5. Default fallback
        """
        
        candidates: List[Tuple[float, str, str, str]] = []  # (score, comp_id, source, reasoning)
        
        # Strategy 1: LLM-based selection
        if self.use_llm and intent.raw_analysis:
            llm_candidates = self._llm_select_for_slot(slot, prompt, intent)
            candidates.extend(llm_candidates)
        
        # Strategy 2: Keyword matching
        keyword_matches = ComponentRegistry.find_for_slot(
            slot_name=slot.name,
            slot_allowed_types=slot.allowed_component_types,
            prompt=prompt
        )
        
        for i, comp in enumerate(keyword_matches):
            score = 0.7 - (i * 0.1)  # Decreasing confidence for lower matches
            candidates.append((score, comp.component_id, "keyword", f"Keyword match: {comp.name}"))
        
        # Strategy 3: RAG-based from similar projects
        for project in similar_projects:
            project_type = project.get("template_id", "")
            rag_comps = self._get_components_from_template(project_type, slot)
            for comp_id in rag_comps:
                candidates.append((0.6, comp_id, "rag", f"Similar project used: {comp_id}"))
        
        # Strategy 4: Relationship-based (what works well with already selected)
        related = self._get_related_components(slot)
        for comp_id in related:
            candidates.append((0.5, comp_id, "relationship", f"Works well with other components"))
        
        # Deduplicate and sort by score
        seen = set()
        unique = []
        for score, comp_id, source, reasoning in sorted(candidates, key=lambda x: x[0], reverse=True):
            if comp_id not in seen:
                seen.add(comp_id)
                unique.append((score, comp_id, source, reasoning))
        
        # Build results
        results = []
        for score, comp_id, source, reasoning in unique[:slot.max_components]:
            comp = ComponentRegistry.get_component(comp_id)
            comp_name = comp.name if comp else comp_id
            
            results.append(SelectionResult(
                component_id=comp_id,
                component_name=comp_name,
                confidence=min(score, 1.0),
                source=source,
                reasoning=reasoning,
                slot_name=slot.name
            ))
        
        # Ensure required slots get at least a default
        if slot.required and not results and slot.default_component:
            results.append(SelectionResult(
                component_id=slot.default_component,
                component_name=slot.default_component,
                confidence=0.3,
                source="default",
                reasoning="Default fallback for required slot",
                slot_name=slot.name
            ))
        
        return results
    
    def _llm_select_for_slot(
        self,
        slot: LayoutSlot,
        prompt: str,
        intent: IntentAnalysis
    ) -> List[Tuple[float, str, str, str]]:
        """Use LLM to recommend components for a slot"""
        provider = self._get_inference()
        if not provider:
            return []
        
        allowed = ", ".join(slot.allowed_component_types)
        
        llm_prompt = f"""Select the best component for this slot in a {intent.project_type} project.

SLOT: {slot.name} - {slot.description}
ALLOWED TYPES: {allowed}
PROJECT REQUIREMENTS: {', '.join(intent.features_requested)}
COMPLEXITY: {intent.complexity_level}

Available components matching this slot:
{chr(10).join(f'- {c.name}: {c.description[:80]}' for c in ComponentRegistry.find_for_slot(slot.name, slot.allowed_component_types)[:5])}

Return JSON: {{"component_id": "string", "reasoning": "string"}}
Choose the SINGLE best component. Respond ONLY with JSON."""
        
        try:
            result = provider.generate(
                prompt=llm_prompt,
                role="planning",
                temperature=0.1,
                max_tokens=150
            )
            
            if result.success and result.text:
                text = result.text.strip()
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
                
                if json_start >= 0:
                    data = json.loads(text[json_start:json_end])
                    comp_id = data.get("component_id", "")
                    reasoning = data.get("reasoning", "LLM recommendation")
                    
                    if comp_id:
                        return [(0.85, comp_id, "llm", reasoning)]
        except Exception:
            pass
        
        return []
    
    def _get_components_from_template(self, template_id: str, slot: LayoutSlot) -> List[str]:
        """Get components that were used in a specific template for a slot"""
        # In production, this queries ChromaDB for past generation history
        # For now, use relationship map
        return self.component_relationships.get(slot.name, [])[:2]
    
    def _get_related_components(self, slot: LayoutSlot) -> List[str]:
        """Get components that work well with this slot type"""
        return self.component_relationships.get(slot.name, [])[:3]
    
    def record_generation(self, prompt: str, selections: Dict[str, List[SelectionResult]], success: bool):
        """Record a generation for future learning"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt[:500],
            "selections": {
                slot: [(s.component_id, s.confidence) for s in results]
                for slot, results in selections.items()
            },
            "success": success
        }
        self.generation_history.append(record)
        
        # Store in RAG for future retrieval
        retriever = self._get_rag()
        if retriever and self._rag_client:
            try:
                self._rag_client.add_generation_record(
                    generation_id=f"gen_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    prompt=prompt[:200],
                    result_summary=f"Selected {sum(len(v) for v in selections.values())} components",
                    success=success,
                    metadata={"selections": json.dumps({k: [s.component_id for s in v] for k, v in selections.items()})}
                )
            except Exception as e:
                logger.debug(f"Failed to record generation: {e}")
    
    def get_confidence_report(self, selections: Dict[str, List[SelectionResult]]) -> str:
        """Generate a confidence report for the selections"""
        lines = ["\nConfidence Report:", "-" * 40]
        
        total_conf = 0
        total_count = 0
        
        for slot_name, results in selections.items():
            for r in results:
                icon = "🟢" if r.confidence > 0.7 else "🟡" if r.confidence > 0.4 else "🔴"
                lines.append(f"  {icon} {slot_name}: {r.component_name} ({r.confidence:.0%}) [{r.source}]")
                total_conf += r.confidence
                total_count += 1
        
        avg = total_conf / max(total_count, 1)
        lines.append(f"\n  Average Confidence: {avg:.0%}")
        lines.append(f"  Source Mix: LLM + RAG + Keywords")
        lines.append("-" * 40)
        
        return "\n".join(lines)


# =====================================================================
# INTEGRATION WITH ASSEMBLY ENGINE
# =====================================================================

class IntelligentAssemblyEngine:
    """
    Upgraded assembly engine that uses TemplateIntelligence.
    Drop-in replacement for keyword-based assembly.
    """
    
    def __init__(self, use_llm: bool = True, use_rag: bool = True):
        self.intelligence = TemplateIntelligence(use_llm=use_llm, use_rag=use_rag)
    
    def assemble_with_intelligence(self, prompt: str, layout: BaseLayout) -> Dict[str, List[SelectionResult]]:
        """
        Full intelligent assembly pipeline.
        
        1. Analyze intent with LLM
        2. Retrieve similar projects with RAG
        3. Select components with confidence scoring
        4. Record for future learning
        """
        
        print("\n" + "=" * 60)
        print("🧠 INTELLIGENT ASSEMBLY")
        print("=" * 60)
        
        # Step 1: Analyze intent
        print("\n📊 Analyzing intent...")
        intent = self.intelligence.analyze_intent(prompt)
        print(f"   Type: {intent.project_type} ({intent.project_type_confidence:.0%})")
        print(f"   Features: {', '.join(intent.features_requested[:8])}")
        print(f"   Style: {intent.visual_style.get('color_preference', 'unknown')}")
        print(f"   Complexity: {intent.complexity_level}")
        
        # Step 2: Retrieve similar
        print("\n🔍 Retrieving similar projects...")
        similar = self.intelligence.retrieve_similar_projects(prompt, intent)
        print(f"   Found: {len(similar)} similar projects")
        
        # Step 3: Intelligent selection
        print("\n🧩 Selecting components...")
        selections = self.intelligence.select_components_intelligently(
            prompt=prompt,
            layout=layout,
            intent=intent
        )
        
        # Step 4: Display confidence
        report = self.intelligence.get_confidence_report(selections)
        print(report)
        
        # Step 5: Record for learning
        self.intelligence.record_generation(prompt, selections, True)
        
        return selections


# =====================================================================
# TEST
# =====================================================================

def test_template_intelligence():
    """Test the template intelligence system"""
    from system.templates.dynamic.layouts.layout_registry import get_layout_for_project
    
    print("\n" + "=" * 70)
    print("🧪 TEMPLATE INTELLIGENCE TEST")
    print("=" * 70)
    
    intelligence = TemplateIntelligence(use_llm=False, use_rag=True)
    
    test_prompts = [
        "Build a dark purple SaaS dashboard for tracking team productivity with analytics, user management, and real-time notifications",
        "Create a modern AI startup landing page with 3D animated hero, pricing table, and waitlist signup",
        "I need an admin panel to manage users, roles, and view system audit logs",
    ]
    
    for prompt in test_prompts:
        print(f"\n{'─' * 70}")
        print(f"📝 PROMPT: \"{prompt[:80]}...\"")
        
        # Analyze intent
        intent = intelligence.analyze_intent(prompt)
        print(f"\n   Intent Analysis:")
        print(f"   Type: {intent.project_type} (confidence: {intent.project_type_confidence:.0%})")
        print(f"   Features: {', '.join(intent.features_requested[:6])}")
        print(f"   Style: {json.dumps(intent.visual_style, indent=2) if isinstance(intent.visual_style, dict) else intent.visual_style}")
        print(f"   Complexity: {intent.complexity_level}")
        
        # Get layout
        layout = get_layout_for_project(intent.project_type)
        
        # Retrieve similar
        similar = intelligence.retrieve_similar_projects(prompt, intent)
        print(f"\n   Similar Projects: {len(similar)} found")
        for s in similar:
            print(f"      - {s.get('name', 'Unknown')} (match: {s.get('similarity', 0):.0%})")
        
        # Select components
        selections = intelligence.select_components_intelligently(prompt, layout, intent)
        report = intelligence.get_confidence_report(selections)
        print(report)
    
    print("\n" + "=" * 70)
    print("✅ Template Intelligence test complete")
    print("=" * 70)
    
    return intelligence


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_template_intelligence()