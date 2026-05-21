"""
NOVARYX - Landing Page Layout
Full-page sections with hero, features, pricing, and CTA.

Structure (vertical scroll):
┌──────────────────────────────────┐
│           NAVBAR                 │
├──────────────────────────────────┤
│           HERO                   │
│         (with 3D canvas)         │
├──────────────────────────────────┤
│         FEATURES                 │
├──────────────────────────────────┤
│         PRICING                  │
├──────────────────────────────────┤
│       TESTIMONIALS               │
├──────────────────────────────────┤
│           CTA                    │
├──────────────────────────────────┤
│          FOOTER                  │
└──────────────────────────────────┘
"""

from .base_layout import BaseLayout, LayoutSlot, LayoutConfig, LayoutType


class LandingLayout(BaseLayout):
    """Landing page layout for SaaS/products"""
    
    @property
    def layout_type(self) -> LayoutType:
        return LayoutType.LANDING
    
    @property
    def layout_name(self) -> str:
        return "Landing Page Layout"
    
    @property
    def description(self) -> str:
        return "High-conversion landing page with hero section, features grid, pricing table, testimonials, and CTA. Supports 3D hero background."
    
    def _define_slots(self):
        
        self.add_slot(LayoutSlot(
            name="navbar",
            description="Top navigation bar with logo, links, and CTA button",
            allowed_component_types=["navbar", "navigation", "logo", "cta_button"],
            required=True,
            max_components=4,
            default_component="navbar"
        ))
        
        self.add_slot(LayoutSlot(
            name="hero",
            description="Hero section with headline, subheadline, CTA, and optional 3D background",
            allowed_component_types=["hero", "hero_3d", "hero_video", "hero_image", "cta_button"],
            required=True,
            max_components=3,
            default_component="hero"
        ))
        
        self.add_slot(LayoutSlot(
            name="features",
            description="Features grid showcasing product capabilities",
            allowed_component_types=["features_grid", "feature_card", "feature_list"],
            required=False,
            max_components=10,
            default_component="features_grid"
        ))
        
        self.add_slot(LayoutSlot(
            name="pricing",
            description="Pricing section with tier comparison",
            allowed_component_types=["pricing_table", "pricing_card", "pricing_comparison"],
            required=False,
            max_components=5,
            default_component="pricing_table"
        ))
        
        self.add_slot(LayoutSlot(
            name="testimonials",
            description="Customer testimonials and social proof",
            allowed_component_types=["testimonial_carousel", "testimonial_card", "testimonial_grid", "logo_cloud"],
            required=False,
            max_components=8
        ))
        
        self.add_slot(LayoutSlot(
            name="cta",
            description="Call-to-action section at bottom",
            allowed_component_types=["cta_section", "cta_button", "newsletter_form"],
            required=False,
            max_components=2,
            default_component="cta_section"
        ))
        
        self.add_slot(LayoutSlot(
            name="footer",
            description="Page footer with links, social, and copyright",
            allowed_component_types=["footer", "social_links", "newsletter_form"],
            required=True,
            max_components=4,
            default_component="footer"
        ))
    
    def generate_grid_css(self) -> str:
        return """
.landing-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--background);
  color: var(--text-primary);
}

.landing-layout .slot-navbar {
  position: sticky;
  top: 0;
  z-index: 100;
}

.landing-layout section {
  width: 100%;
}

.landing-layout .section-inner {
  max-width: var(--container-max-width, 1280px);
  margin: 0 auto;
  padding: var(--section-padding-y) var(--section-padding-x);
}

@media (max-width: 768px) {
  .landing-layout .section-inner {
    padding: 40px 20px;
  }
}
"""
    
    def generate_layout_tsx(self, design_system=None) -> str:
        ds_prefix = self.get_safe_project_name(design_system)
        
        return f'''import React from "react";
import {{ motion, useScroll, useSpring }} from "framer-motion";

interface {ds_prefix}LandingProps {{
  navbarContent?: React.ReactNode;
  heroContent?: React.ReactNode;
  featuresContent?: React.ReactNode;
  pricingContent?: React.ReactNode;
  testimonialsContent?: React.ReactNode;
  ctaContent?: React.ReactNode;
  footerContent?: React.ReactNode;
}}

export default function {ds_prefix}Landing({{
  navbarContent,
  heroContent,
  featuresContent,
  pricingContent,
  testimonialsContent,
  ctaContent,
  footerContent,
}}: {ds_prefix}LandingProps) {{
  const {{ scrollYProgress }} = useScroll();
  const scaleX = useSpring(scrollYProgress, {{
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  }});

  return (
    <div className="landing-layout">
      {{/* Scroll Progress Bar */}}
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-[var(--primary)] z-50 origin-left"
        style={{{{ scaleX }}}}
      />

      {{/* Navbar Slot */}}
      <nav className="slot-navbar">
        {{navbarContent || <DefaultNavbar />}}
      </nav>

      {{/* Hero Slot */}}
      <section id="hero" className="relative min-h-screen">
        {{heroContent || <DefaultHero />}}
      </section>

      {{/* Features Slot */}}
      {{featuresContent && (
        <section id="features">
          <div className="section-inner">
            <motion.div
              initial={{{{ opacity: 0, y: 40 }}}}
              whileInView={{{{ opacity: 1, y: 0 }}}}
              viewport={{{{ once: true, margin: "-100px" }}}}
              transition={{{{ duration: 0.6 }}}}
            >
              {{featuresContent}}
            </motion.div>
          </div>
        </section>
      )}}

      {{/* Pricing Slot */}}
      {{pricingContent && (
        <section id="pricing" className="bg-[var(--background-secondary)]">
          <div className="section-inner">
            <motion.div
              initial={{{{ opacity: 0, y: 40 }}}}
              whileInView={{{{ opacity: 1, y: 0 }}}}
              viewport={{{{ once: true }}}}
              transition={{{{ duration: 0.6 }}}}
            >
              {{pricingContent}}
            </motion.div>
          </div>
        </section>
      )}}

      {{/* Testimonials Slot */}}
      {{testimonialsContent && (
        <section id="testimonials">
          <div className="section-inner">
            {{testimonialsContent}}
          </div>
        </section>
      )}}

      {{/* CTA Slot */}}
      {{ctaContent && (
        <section id="cta" className="bg-[var(--primary)]">
          <div className="section-inner text-center">
            {{ctaContent}}
          </div>
        </section>
      )}}

      {{/* Footer Slot */}}
      <footer className="slot-footer mt-auto">
        {{footerContent || <DefaultFooter />}}
      </footer>
    </div>
  );
}}

function DefaultNavbar() {{
  return (
    <div className="bg-[var(--surface-glass)] backdrop-blur-xl border-b border-[var(--border)]">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <span className="text-xl font-bold">{{ "Project Name" }}</span>
        <div className="hidden md:flex items-center gap-8">
          {{["Features", "Pricing", "About"].map((item) => (
            <a key={{item}} href={{`#${{item.toLowerCase()}}` }} className="hover:text-[var(--primary)] transition-colors">
              {{item}}
            </a>
          ))}}
        </div>
        <button className="px-6 py-2 bg-[var(--primary)] text-white rounded-full hover:opacity-90 transition-opacity">
          Get Started
        </button>
      </div>
    </div>
  );
}}

function DefaultHero() {{
  return (
    <div className="flex items-center justify-center h-full text-center px-6">
      <div className="max-w-3xl">
        <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight text-gradient">
          {{ "Transform Your Workflow" }}
        </h1>
        <p className="text-xl text-[var(--text-secondary)] mb-8">
          {{ "The best SaaS tool ever created." }}
        </p>
        <div className="flex gap-4 justify-center">
          <button className="px-8 py-4 bg-gradient-premium rounded-full text-lg hover:shadow-[var(--shadow-glow)] animate-pulse-glow transition-all">
            Get Started Free
          </button>
          <button className="px-8 py-4 border border-[var(--border)] rounded-full text-lg hover:bg-[var(--surface-raised)] transition-colors">
            Learn More
          </button>
        </div>
      </div>
    </div>
  );
}}

function DefaultFooter() {{
  return (
    <div className="bg-[var(--surface)] border-t border-[var(--border)]">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {{["Product", "Company", "Resources", "Legal"].map((col) => (
            <div key={{col}}>
              <h4 className="font-semibold mb-4">{{col}}</h4>
              <div className="space-y-2 text-sm text-[var(--text-secondary)]">
                {{["Link 1", "Link 2", "Link 3"].map((link) => (
                  <a key={{link}} href="#" className="block hover:text-[var(--primary)] transition-colors">{{link}}</a>
                ))}}
              </div>
            </div>
          ))}}
        </div>
        <div className="mt-8 pt-8 border-t border-[var(--border)] text-center text-sm text-[var(--text-tertiary)]">
          © 2026 {{ "Project Name" }}. All rights reserved.
        </div>
      </div>
    </div>
  );
}}
'''