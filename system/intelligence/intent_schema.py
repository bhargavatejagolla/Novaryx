"""
NOVARYX - Intent Schema
Structured output types that the LLM fills from natural language prompts.

Every field is validated. Every type is explicit.
This is the contract between the LLM and the generation pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class ProjectType(Enum):
    SAAS_DASHBOARD = "saas_dashboard"
    LANDING_PAGE = "landing_page"
    ECOMMERCE = "ecommerce"
    ADMIN_PANEL = "admin_panel"
    PORTFOLIO = "portfolio"
    BLOG = "blog"
    SOCIAL_APP = "social_app"
    DOCUMENTATION = "documentation"
    MARKETING_SITE = "marketing_site"


class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class ColorMode(Enum):
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


class AnimationLevel(Enum):
    SUBTLE = "subtle"
    MODERATE = "moderate"
    RICH = "rich"
    NONE = "none"


@dataclass
class DesignSpec:
    """Visual design preferences extracted from prompt"""
    color_mode: str = "dark"
    primary_color_name: str = "indigo"
    primary_color_hex: str = "#6366f1"
    accent_color_name: str = "cyan"
    accent_color_hex: str = "#06b6d4"
    font_preference: str = "inter"
    font_style: str = "modern"
    glassmorphism: bool = False
    three_d_enabled: bool = False
    three_d_elements: List[str] = field(default_factory=list)
    animation_level: str = "moderate"
    border_radius: str = "medium"
    density: str = "comfortable"
    custom_css_preferences: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "color_mode": self.color_mode,
            "primary_color": self.primary_color_name,
            "primary_hex": self.primary_color_hex,
            "accent_color": self.accent_color_name,
            "accent_hex": self.accent_color_hex,
            "font": self.font_preference,
            "font_style": self.font_style,
            "glassmorphism": self.glassmorphism,
            "3d_enabled": self.three_d_enabled,
            "3d_elements": self.three_d_elements,
            "animation_level": self.animation_level,
            "border_radius": self.border_radius,
            "density": self.density
        }


@dataclass
class FeatureSpec:
    """A specific feature requested by the user"""
    name: str
    description: str
    priority: str = "medium"  # high, medium, low
    requires_auth: bool = False
    requires_database: bool = False
    requires_3d: bool = False
    components_needed: List[str] = field(default_factory=list)
    pages_affected: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "requires_auth": self.requires_auth,
            "requires_database": self.requires_database,
            "requires_3d": self.requires_3d,
            "components_needed": self.components_needed,
            "pages_affected": self.pages_affected
        }


@dataclass
class PageSpec:
    """A page to be generated"""
    name: str
    route: str
    title: str
    description: str
    components: List[str] = field(default_factory=list)
    requires_auth: bool = False
    is_landing: bool = False
    seo_title: str = ""
    seo_description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "route": self.route,
            "title": self.title,
            "description": self.description,
            "components": self.components,
            "requires_auth": self.requires_auth,
            "is_landing": self.is_landing
        }


@dataclass
class DataModelSpec:
    """A database model to generate"""
    name: str
    fields: List[Dict[str, str]] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "fields": self.fields,
            "relationships": self.relationships
        }


@dataclass
class ProjectSpec:
    """Complete project specification extracted from prompt"""
    
    # Core
    project_name: str = ""
    project_description: str = ""
    project_type: str = "saas_dashboard"
    project_type_confidence: float = 0.0
    complexity: str = "medium"
    target_audience: str = "general"
    industry: str = "technology"
    
    # Design
    design: DesignSpec = field(default_factory=DesignSpec)
    
    # Structure
    pages: List[PageSpec] = field(default_factory=list)
    features: List[FeatureSpec] = field(default_factory=list)
    data_models: List[DataModelSpec] = field(default_factory=list)
    
    # Technical
    requires_authentication: bool = False
    requires_database: bool = False
    requires_payments: bool = False
    requires_file_upload: bool = False
    requires_real_time: bool = False
    requires_search: bool = False
    requires_email: bool = False
    requires_ai_assistant: bool = False
    
    # Content
    sample_content: Dict[str, Any] = field(default_factory=dict)
    brand_name: str = ""
    tagline: str = ""
    
    # Metadata
    raw_prompt: str = ""
    parsed_at: str = ""
    parser_version: str = "2.1.0"
    confidence_score: float = 0.0
    
    def get_component_list(self) -> List[str]:
        """Get flat list of all unique components needed"""
        components = set()
        for page in self.pages:
            for comp in page.components:
                components.add(comp)
        for feature in self.features:
            for comp in feature.components_needed:
                components.add(comp)
        return list(components)
    
    def get_all_routes(self) -> List[Dict[str, str]]:
        """Get all routes with metadata"""
        return [
            {
                "route": page.route,
                "name": page.name,
                "requires_auth": page.requires_auth,
                "is_landing": page.is_landing
            }
            for page in self.pages
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Full serialization"""
        return {
            "project_name": self.project_name,
            "project_description": self.project_description,
            "project_type": self.project_type,
            "project_type_confidence": self.project_type_confidence,
            "complexity": self.complexity,
            "target_audience": self.target_audience,
            "industry": self.industry,
            "design": self.design.to_dict(),
            "pages": [p.to_dict() for p in self.pages],
            "features": [f.to_dict() for f in self.features],
            "data_models": [d.to_dict() for d in self.data_models],
            "requires_authentication": self.requires_authentication,
            "requires_database": self.requires_database,
            "requires_payments": self.requires_payments,
            "requires_file_upload": self.requires_file_upload,
            "requires_real_time": self.requires_real_time,
            "requires_search": self.requires_search,
            "requires_email": self.requires_email,
            "requires_ai_assistant": self.requires_ai_assistant,
            "brand_name": self.brand_name,
            "tagline": self.tagline,
            "confidence_score": self.confidence_score,
            "total_pages": len(self.pages),
            "total_features": len(self.features),
            "total_components": len(self.get_component_list())
        }
    
    def display(self):
        """Display parsed project spec beautifully"""
        print("\n" + "=" * 70)
        print(f"🎯 PROJECT: {self.project_name or 'Unnamed'}")
        print("=" * 70)
        print(f"   Type: {self.project_type} ({self.project_type_confidence:.0%} confidence)")
        print(f"   Complexity: {self.complexity}")
        print(f"   Audience: {self.target_audience}")
        print(f"   Industry: {self.industry}")
        
        print(f"\n   🎨 Design:")
        print(f"      Mode: {self.design.color_mode}")
        print(f"      Primary: {self.design.primary_color_name}")
        print(f"      Accent: {self.design.accent_color_name}")
        print(f"      Font: {self.design.font_preference}")
        print(f"      Glassmorphism: {'Yes' if self.design.glassmorphism else 'No'}")
        print(f"      3D: {'Yes' if self.design.three_d_enabled else 'No'}")
        print(f"      Animation: {self.design.animation_level}")
        
        print(f"\n   📄 Pages ({len(self.pages)}):")
        for page in self.pages:
            auth_icon = "🔒" if page.requires_auth else "🌐"
            print(f"      {auth_icon} {page.route} → {page.title}")
            if page.components:
                print(f"         Components: {', '.join(page.components[:4])}")
        
        print(f"\n   ⚡ Features ({len(self.features)}):")
        for feature in self.features:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            print(f"      {priority_icon.get(feature.priority, '⚪')} {feature.name}")
        
        print(f"\n   🔧 Technical:")
        print(f"      Auth: {'Yes' if self.requires_authentication else 'No'}")
        print(f"      Database: {'Yes' if self.requires_database else 'No'}")
        print(f"      Payments: {'Yes' if self.requires_payments else 'No'}")
        print(f"      Real-time: {'Yes' if self.requires_real_time else 'No'}")
        
        print(f"\n   📊 Summary:")
        print(f"      Pages: {len(self.pages)}")
        print(f"      Features: {len(self.features)}")
        print(f"      Components: {len(self.get_component_list())}")
        print(f"      Confidence: {self.confidence_score:.0%}")
        print("=" * 70)