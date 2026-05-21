"""
NOVARYX - Intent Parser
THE intelligence layer. Uses LLM to extract structured project specs from prompts.

Flow:
  Natural Language Prompt → LLM Analysis → JSON Spec → Validation → ProjectSpec
"""

import sys
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from system.intelligence.intent_schema import ProjectSpec
from system.intelligence.intent_validator import IntentValidator
from system.intelligence.prompt_templates import PromptTemplates

logger = logging.getLogger("novaryx.intent_parser")


class IntentParser:
    """
    LLM-powered intent parser.
    
    Takes natural language → produces structured ProjectSpec.
    Falls back to keyword analysis if LLM unavailable.
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self._inference = None
        self.validator = IntentValidator()
        
        # Track parsing stats
        self.stats = {
            "total_parsed": 0,
            "llm_parsed": 0,
            "fallback_parsed": 0,
            "validation_fixes": 0,
        }
    
    def _get_inference(self):
        """Lazy load inference provider"""
        if self._inference is None:
            try:
                from system.inference.provider_factory import get_provider
                self._inference = get_provider()
            except Exception as e:
                logger.warning(f"Inference unavailable: {e}")
        return self._inference
    
    def parse(self, prompt: str) -> ProjectSpec:
        """
        Parse a natural language prompt into a structured ProjectSpec.
        
        Args:
            prompt: User's project description
        
        Returns:
            Complete ProjectSpec ready for the generation pipeline
        """
        self.stats["total_parsed"] += 1
        
        print("\n" + "=" * 70)
        print("🧠 INTENT PARSER")
        print("=" * 70)
        print(f"   Prompt: {prompt[:100]}...")
        
        # Step 1: Try LLM parsing
        if self.use_llm:
            spec = self._llm_parse(prompt)
            if spec and spec.confidence_score > 0.4:
                self.stats["llm_parsed"] += 1
                print(f"   Method: LLM (confidence: {spec.confidence_score:.0%})")
                spec.raw_prompt = prompt
                spec.parsed_at = datetime.now().isoformat()
                spec.display()
                return spec
        
        # Step 2: Fallback to keyword parsing
        self.stats["fallback_parsed"] += 1
        print(f"   Method: Keyword Analysis (LLM unavailable or low confidence)")
        spec = self._keyword_parse(prompt)
        spec.raw_prompt = prompt
        spec.parsed_at = datetime.now().isoformat()
        spec.display()
        return spec
    
    def _llm_parse(self, prompt: str) -> Optional[ProjectSpec]:
        """Use LLM to parse the prompt"""
        provider = self._get_inference()
        if not provider:
            return None
        
        try:
            # Build the extraction prompt
            extraction_prompt = PromptTemplates.INTENT_EXTRACTION.format(
                prompt=prompt
            )
            
            # Call LLM
            result = provider.generate(
                prompt=extraction_prompt,
                role="planning",
                temperature=0.1,
                max_tokens=2000
            )
            
            # Smart Fallback to local Ollama if Groq fails
            if (not result.success or not result.text) and provider.name == "groq":
                logger.warning("Primary Groq provider failed or rate-limited. Trying local Ollama fallback...")
                try:
                    from system.inference.provider_factory import _ollama_instance, _init_providers
                    _init_providers()
                    if _ollama_instance and _ollama_instance._available:
                        logger.info("Ollama is available, routing planning role to local Ollama fallback...")
                        result = _ollama_instance.generate(
                            prompt=extraction_prompt,
                            role="planning",
                            temperature=0.1,
                            max_tokens=2000
                        )
                except Exception as fallback_err:
                    logger.error(f"Fallback to Ollama failed: {fallback_err}")

            if not result.success or not result.text:
                logger.warning("LLM returned empty response or both providers failed")
                return None
            
            # Extract JSON from response
            data = self._extract_json(result.text)
            
            if not data:
                logger.warning("Failed to extract JSON from LLM response")
                return None
            
            # Validate and repair
            is_valid, warnings, data = self.validator.validate(data)
            
            if warnings:
                self.stats["validation_fixes"] += len(warnings)
                for w in warnings:
                    logger.info(f"Validation: {w}")
            
            # Convert to ProjectSpec
            spec = self.validator.to_project_spec(data)
            
            return spec
            
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return None
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from LLM response text"""
        
        # Try direct parse first
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON between braces
        text = text.strip()
        
        # Find first { and last }
        start = text.find('{')
        end = text.rfind('}')
        
        if start >= 0 and end > start:
            json_str = text[start:end + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Try removing markdown code blocks
        if '```json' in text:
            parts = text.split('```json')
            if len(parts) > 1:
                json_part = parts[1].split('```')[0]
                try:
                    return json.loads(json_part.strip())
                except json.JSONDecodeError:
                    pass
        
        if '```' in text:
            parts = text.split('```')
            for part in parts:
                if '{' in part and '}' in part:
                    try:
                        return json.loads(part.strip())
                    except json.JSONDecodeError:
                        continue
        
        logger.error(f"Could not extract JSON from: {text[:200]}...")
        return None
    
    def _keyword_parse(self, prompt: str) -> ProjectSpec:
        """Fallback keyword-based parsing"""
        from system.templates.dynamic.template_intelligence import TemplateIntelligence
        
        intelligence = TemplateIntelligence(use_llm=False, use_rag=False)
        intent = intelligence.analyze_intent(prompt)
        
        # Build pages from features
        pages = []
        if intent.features_requested:
            pages.append({
                "name": "Dashboard" if "dashboard" in intent.features_requested else "Home",
                "route": "/",
                "title": "Home",
                "description": "Main page",
                "components": [],
                "requires_auth": False,
                "is_landing": True
            })
        
        # Build features
        features = [
            {"name": f, "description": f"Requested feature: {f}", "priority": "medium"}
            for f in intent.features_requested[:10]
        ]
        
        data = {
            "project_name": "",
            "project_type": intent.project_type,
            "project_type_confidence": intent.project_type_confidence,
            "complexity": intent.complexity_level,
            "design": {
                "color_mode": intent.visual_style.get("color_preference", "dark"),
                "three_d_enabled": intent.visual_style.get("three_d_required", False),
                "glassmorphism": intent.visual_style.get("glassmorphism", False),
                "animation_level": intent.visual_style.get("animation_level", "moderate"),
            },
            "pages": pages,
            "features": features,
            "confidence_score": 0.3
        }
        
        _, _, data = self.validator.validate(data)
        return self.validator.to_project_spec(data)
    
    def refine(self, prompt: str, feedback: str) -> ProjectSpec:
        """Refine a spec based on user feedback"""
        provider = self._get_inference()
        if not provider:
            return self.parse(f"{prompt}. {feedback}")
        
        try:
            refinement_prompt = PromptTemplates.INTENT_REFINEMENT.format(
                prompt=prompt,
                feedback=feedback
            )
            
            result = provider.generate(
                prompt=refinement_prompt,
                role="planning",
                temperature=0.1,
                max_tokens=1500
            )
            
            if result.success:
                data = self._extract_json(result.text)
                if data:
                    _, _, data = self.validator.validate(data)
                    spec = self.validator.to_project_spec(data)
                    spec.raw_prompt = f"{prompt} | Feedback: {feedback}"
                    return spec
        except Exception:
            pass
        
        return self.parse(f"{prompt}. {feedback}")
    
    def display_stats(self):
        """Display parsing statistics"""
        print("\n" + "=" * 50)
        print("📊 INTENT PARSER STATS")
        print("=" * 50)
        print(f"   Total Parsed: {self.stats['total_parsed']}")
        print(f"   LLM Parsed: {self.stats['llm_parsed']}")
        print(f"   Fallback: {self.stats['fallback_parsed']}")
        print(f"   Validation Fixes: {self.stats['validation_fixes']}")
        print("=" * 50)


# ---- Test ----

def test_intent_parser():
    """Test the intent parser"""
    
    print("\n" + "=" * 70)
    print("🧪 INTENT PARSER TEST")
    print("=" * 70)
    
    parser = IntentParser(use_llm=False)
    
    test_prompts = [
        "Build a dark purple SaaS dashboard for tracking team productivity with real-time analytics, user management, kanban board, and a 3D globe showing active users worldwide. Include dark mode and glassmorphism effects.",
        "Create a modern AI startup landing page called 'NeuralFlow' with a 3D animated hero section, pricing table with 3 tiers, customer testimonials carousel, waitlist signup form, and smooth scroll animations.",
        "I need an admin panel to manage users with roles and permissions, view system audit logs, CRUD operations for content, and a rich analytics dashboard with export capabilities.",
    ]
    
    for prompt in test_prompts:
        spec = parser.parse(prompt)
        print(f"\n   Pages: {[p.route for p in spec.pages]}")
        print(f"   Features: {[f.name for f in spec.features]}")
        print(f"   Components needed: {spec.get_component_list()}")
    
    parser.display_stats()
    
    print("\n✅ Intent Parser test complete")
    return parser


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_intent_parser()