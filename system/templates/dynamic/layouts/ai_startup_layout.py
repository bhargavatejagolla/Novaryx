"""
NOVARYX - AI Startup Layout
Floating Headers, Hero with dynamic 3D elements, Bento Grids, and dark-mode elegance.

Grid Structure:
┌──────────────────────────────────────────┐
│              HEADER                      │
├──────────────────────────────────────────┤
│                                          │
│              HERO                        │
│                                          │
├──────────────────────────────────────────┤
│              FEATURES                    │
│          (Bento Grid)                    │
├──────────────────────────────────────────┤
│              PRICING                     │
├──────────────────────────────────────────┤
│              FOOTER                      │
└──────────────────────────────────────────┘
"""

from .base_layout import BaseLayout, LayoutSlot, LayoutConfig, LayoutType


class AiStartupLayout(BaseLayout):
    """Breathtaking layout for AI Startups"""
    
    @property
    def layout_type(self) -> LayoutType:
        return LayoutType.LANDING
    
    @property
    def layout_name(self) -> str:
        return "AI Startup Layout"
    
    @property
    def description(self) -> str:
        return "A state-of-the-art landing page optimized for AI SaaS startups. Features glowing orbital elements, floating headers, and comprehensive bento-box feature grids."
    
    def _define_slots(self):
        """Define all slots for AI Startup layout"""
        
        self.add_slot(LayoutSlot(
            name="header",
            description="Floating glassmorphic header",
            allowed_component_types=["header", "navigation"],
            required=True,
            max_components=1,
            grid_area="header"
        ))
        
        self.add_slot(LayoutSlot(
            name="hero",
            description="Massive hero section with glowing orbs and product console",
            allowed_component_types=["hero", "ai_console_demo"],
            required=True,
            max_components=2,
            grid_area="hero"
        ))
        
        self.add_slot(LayoutSlot(
            name="features",
            description="Bento box style grid for AI features",
            allowed_component_types=["bento_grid", "feature_grid"],
            required=True,
            max_components=1,
            grid_area="features"
        ))
        
        self.add_slot(LayoutSlot(
            name="pricing",
            description="Tiered pricing with glowing focus cards",
            allowed_component_types=["pricing_table", "pricing_cards"],
            required=False,
            max_components=1,
            grid_area="pricing"
        ))
        
        self.add_slot(LayoutSlot(
            name="footer",
            description="Dark minimal footer",
            allowed_component_types=["footer"],
            required=False,
            max_components=1,
            grid_area="footer"
        ))
    
    def generate_grid_css(self) -> str:
        """Generate CSS Layout variables"""
        return """
.ai-layout-container {
  min-height: 100vh;
  background-color: var(--background);
  color: var(--text-primary);
  overflow-x: hidden;
  position: relative;
}

/* Background gradient glows */
.ai-layout-container::before {
  content: '';
  position: absolute;
  top: -10vw;
  left: -10vw;
  width: 50vw;
  height: 50vw;
  background: radial-gradient(circle, var(--primary) 0%, transparent 70%);
  opacity: 0.15;
  filter: blur(100px);
  z-index: 0;
  pointer-events: none;
}

.ai-layout-container::after {
  content: '';
  position: absolute;
  top: 30vh;
  right: -10vw;
  width: 40vw;
  height: 40vw;
  background: radial-gradient(circle, var(--accent) 0%, transparent 60%);
  opacity: 0.1;
  filter: blur(80px);
  z-index: 0;
  pointer-events: none;
}

.ai-layout-content {
  position: relative;
  z-index: 10;
}

.slot-section {
  padding: 4rem 1.5rem;
  max-width: 80rem;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .slot-section {
    padding: 8rem 2rem;
  }
}
"""
    
    def generate_layout_tsx(self, design_system=None) -> str:
        """Generate complete React layout component"""
        
        ds_prefix = self.get_safe_project_name(design_system)
        
        return f'''import React from "react";
import {{ motion }} from "framer-motion";

interface {ds_prefix}AiStartupProps {{
  children?: React.ReactNode;
  headerContent?: React.ReactNode;
  heroContent?: React.ReactNode;
  featuresContent?: React.ReactNode;
  pricingContent?: React.ReactNode;
  footerContent?: React.ReactNode;
}}

export default function {ds_prefix}AiStartup({{
  headerContent,
  heroContent,
  featuresContent,
  pricingContent,
  footerContent,
}}: {ds_prefix}AiStartupProps) {{
  return (
    <div className="ai-layout-container text-[var(--text-primary)]">
      {{/* Header */}}
      {{headerContent && (
        <header className="fixed top-0 left-0 right-0 z-50">
          {{headerContent}}
        </header>
      )}}
      
      <main className="ai-layout-content">
        {{/* Hero */}}
        <section className="relative pt-32 pb-16 md:pt-48 md:pb-32 px-4 max-w-7xl mx-auto flex flex-col items-center justify-center text-center mt-20">
          {{heroContent}}
        </section>
        
        {{/* Features (Bento Grid) */}}
        {{featuresContent && (
          <section className="slot-section w-full">
            <motion.div
              initial={{{{ opacity: 0, y: 30 }}}}
              whileInView={{{{ opacity: 1, y: 0 }}}}
              viewport={{{{ once: true, margin: "-100px" }}}}
              transition={{{{ duration: 0.8, ease: "easeOut" }}}}
            >
              {{featuresContent}}
            </motion.div>
          </section>
        )}}
        
        {{/* Pricing */}}
        {{pricingContent && (
          <section className="slot-section w-full relative">
            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[var(--surface-raised)]/20 to-transparent pointer-events-none" />
            <motion.div
              className="relative z-10"
              initial={{{{ opacity: 0, scale: 0.95 }}}}
              whileInView={{{{ opacity: 1, scale: 1 }}}}
              viewport={{{{ once: true }}}}
              transition={{{{ duration: 0.6 }}}}
            >
              {{pricingContent}}
            </motion.div>
          </section>
        )}}
      </main>

      {{/* Footer */}}
      {{footerContent && (
        <footer className="w-full border-t border-[var(--border)] bg-[var(--surface)] text-sm">
          {{footerContent}}
        </footer>
      )}}
    </div>
  );
}}
'''
