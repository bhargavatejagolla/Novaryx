"""
NOVARYX - Component Registry
Central registry of all available components with metadata for AI selection.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
# Add this import at the top of component_registry.py
from system.templates.dynamic.components.batch2_components import get_batch2_tsx_generators

@dataclass
class ComponentMeta:
    """Metadata for a component that the AI uses to decide what to use"""
    component_id: str
    name: str
    description: str
    component_type: str  # sidebar, card, chart, table, etc.
    allowed_layouts: List[str]  # Which layouts can use this
    allowed_slots: List[str]  # Which slot types this fits
    keywords: List[str]  # Prompt keywords that trigger this component
    required_deps: List[str] = field(default_factory=list)  # npm packages needed
    has_3d: bool = False
    has_animation: bool = True
    complexity: str = "medium"  # simple, medium, complex
    props_schema: Dict[str, Any] = field(default_factory=dict)
    
    def matches_prompt(self, prompt: str) -> bool:
        """Check if this component matches prompt keywords"""
        prompt_lower = prompt.lower()
        for keyword in self.keywords:
            if keyword.lower() in prompt_lower:
                return True
        return False
    
    def matches_slot(self, slot_name: str, slot_allowed_types: List[str]) -> bool:
        """Check if this component fits in a slot"""
        if slot_name in self.allowed_slots:
            return True
        if self.component_type in slot_allowed_types:
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.component_id,
            "name": self.name,
            "type": self.component_type,
            "allowed_layouts": self.allowed_layouts,
            "keywords": self.keywords,
            "has_3d": self.has_3d,
            "complexity": self.complexity
        }


class ComponentRegistry:
    """
    Registry of all components the AI can select from.
    
    The Assembly Engine queries this to:
    1. Find components matching prompt keywords
    2. Find components fitting specific slots
    3. Get component metadata for generation
    """
    
    COMPONENTS: Dict[str, ComponentMeta] = {
        # Navigation
        "sidebar": ComponentMeta(
            component_id="sidebar",
            name="Sidebar Navigation",
            description="Collapsible sidebar with icon navigation, sections, and user footer",
            component_type="sidebar",
            allowed_layouts=["dashboard", "admin"],
            allowed_slots=["sidebar"],
            keywords=["sidebar", "navigation", "menu", "side nav", "left panel"],
            complexity="medium"
        ),
        "navbar": ComponentMeta(
            component_id="navbar",
            name="Navigation Bar",
            description="Responsive top navbar with logo, links, search, and mobile hamburger menu",
            component_type="navbar",
            allowed_layouts=["landing", "ecommerce", "portfolio"],
            allowed_slots=["navbar", "header"],
            keywords=["navbar", "header", "top bar", "navigation bar", "menu bar"],
            complexity="medium"
        ),
        "breadcrumbs": ComponentMeta(
            component_id="breadcrumbs",
            name="Breadcrumbs",
            description="Auto-generated breadcrumb trail showing page hierarchy",
            component_type="breadcrumbs",
            allowed_layouts=["dashboard", "admin", "ecommerce"],
            allowed_slots=["header"],
            keywords=["breadcrumb", "breadcrumbs", "navigation path", "page trail"],
            complexity="simple"
        ),
        
        # Data Display
        "stats_card": ComponentMeta(
            component_id="stats_card",
            name="Statistics Card",
            description="KPI card showing metric value, label, trend indicator, and sparkline",
            component_type="stats_card",
            allowed_layouts=["dashboard", "admin"],
            allowed_slots=["stats"],
            keywords=["stats", "metrics", "kpi", "numbers", "analytics", "statistics", "overview"],
            complexity="simple"
        ),
        "chart_widget": ComponentMeta(
            component_id="chart_widget",
            name="Chart Widget",
            description="Interactive chart supporting line, bar, pie, and area types via Recharts",
            component_type="chart",
            allowed_layouts=["dashboard", "admin"],
            allowed_slots=["main", "stats", "content"],
            keywords=["chart", "graph", "plot", "visualization", "analytics", "revenue chart", "data viz"],
            required_deps=["recharts"],
            complexity="complex"
        ),
        "data_table": ComponentMeta(
            component_id="data_table",
            name="Data Table",
            description="Sortable, filterable, paginated data table with row selection and actions",
            component_type="data_table",
            allowed_layouts=["dashboard", "admin", "ecommerce"],
            allowed_slots=["main", "content", "products"],
            keywords=["table", "data table", "list", "records", "users table", "orders", "products table"],
            required_deps=["@tanstack/react-table"],
            complexity="complex"
        ),
        "activity_feed": ComponentMeta(
            component_id="activity_feed",
            name="Activity Feed",
            description="Timeline-style activity feed showing recent events with icons and timestamps",
            component_type="activity_feed",
            allowed_layouts=["dashboard", "admin"],
            allowed_slots=["panels", "main", "content"],
            keywords=["activity", "feed", "timeline", "recent", "log", "history", "events"],
            complexity="medium"
        ),
        
        # UI Controls
        "theme_toggle": ComponentMeta(
            component_id="theme_toggle",
            name="Theme Toggle",
            description="Dark/light mode toggle button with animated icon transition",
            component_type="theme_toggle",
            allowed_layouts=["dashboard", "landing", "admin", "portfolio", "ecommerce"],
            allowed_slots=["header", "navbar", "sidebar"],
            keywords=["theme", "dark mode", "light mode", "toggle theme", "switch theme"],
            complexity="simple"
        ),

        # Batch 2 Components
        "search_bar": ComponentMeta(
            component_id="search_bar",
            name="Search Bar",
            description="Animated search input with icon, clear button, keyboard shortcut, and suggestions dropdown",
            component_type="search_bar",
            allowed_layouts=["dashboard", "admin", "ecommerce", "landing"],
            allowed_slots=["header", "navbar"],
            keywords=["search", "find", "lookup", "search bar", "search input", "filter"],
            complexity="medium"
        ),
        "notification_bell": ComponentMeta(
            component_id="notification_bell",
            name="Notification Bell",
            description="Notification bell icon with unread badge and dropdown panel",
            component_type="notification_bell",
            allowed_layouts=["dashboard", "admin"],
            allowed_slots=["header"],
            keywords=["notification", "bell", "alert", "notify", "inbox"],
            complexity="medium"
        ),
        "modal": ComponentMeta(
            component_id="modal",
            name="Modal Dialog",
            description="Animated modal overlay with title, content, actions, and keyboard dismiss",
            component_type="modal",
            allowed_layouts=["dashboard", "admin", "landing", "ecommerce", "portfolio"],
            allowed_slots=["drawer", "main", "content"],
            keywords=["modal", "dialog", "popup", "overlay", "lightbox"],
            complexity="medium"
        ),
        "auth_form": ComponentMeta(
            component_id="auth_form",
            name="Authentication Form",
            description="Login/Register form with email, password, validation, social buttons, and loading state",
            component_type="auth_form",
            allowed_layouts=["dashboard", "landing", "ecommerce", "admin"],
            allowed_slots=["main", "content", "hero"],
            keywords=["login", "register", "sign up", "sign in", "auth", "authentication", "email password"],
            complexity="complex"
        ),
        "empty_state": ComponentMeta(
            component_id="empty_state",
            name="Empty State",
            description="Illustrated empty state with icon, title, description, and action button",
            component_type="empty_state",
            allowed_layouts=["dashboard", "admin", "ecommerce", "landing", "portfolio"],
            allowed_slots=["main", "content", "stats", "panels"],
            keywords=["empty", "no data", "nothing", "blank", "placeholder", "zero state"],
            complexity="simple"
        ),
        "error_boundary": ComponentMeta(
            component_id="error_boundary",
            name="Error Boundary",
            description="React error boundary with fallback UI, error details, and retry button",
            component_type="error_boundary",
            allowed_layouts=["dashboard", "admin", "ecommerce", "landing", "portfolio"],
            allowed_slots=["main", "content"],
            keywords=["error", "crash", "boundary", "fallback", "something went wrong"],
            complexity="simple"
        ),
        "skeleton_loader": ComponentMeta(
            component_id="skeleton_loader",
            name="Skeleton Loader",
            description="Configurable skeleton loading placeholder with pulse animation",
            component_type="skeleton_loader",
            allowed_layouts=["dashboard", "admin", "ecommerce", "landing", "portfolio"],
            allowed_slots=["main", "content", "stats", "panels"],
            keywords=["skeleton", "loading", "placeholder", "shimmer", "pulse loader"],
            complexity="simple"
        ),
        "toast_notification": ComponentMeta(
            component_id="toast_notification",
            name="Toast Notification",
            description="Slide-in toast notification with icon, message, action, and auto-dismiss",
            component_type="toast_notification",
            allowed_layouts=["dashboard", "admin", "ecommerce", "landing", "portfolio"],
            allowed_slots=["main", "content", "header"],
            keywords=["toast", "notification", "snackbar", "alert", "message", "popup message"],
            complexity="medium"
        ),
        "orbital_hero": ComponentMeta(
            component_id="orbital_hero",
            name="Orbital Hero",
            description="Massive hero section with glowing orbs, product console, and floating headers.",
            component_type="hero",
            allowed_layouts=["landing", "ai_startup"],
            allowed_slots=["hero", "main"],
            keywords=["hero", "ai startup hero", "landing hero", "orbital", "glow hero"],
            complexity="complex"
        ),
        "bento_grid": ComponentMeta(
            component_id="bento_grid",
            name="Feature Bento Grid",
            description="High-end bento box feature layout with glassmorphic cards and motion stagger.",
            component_type="feature_grid",
            allowed_layouts=["landing", "ai_startup"],
            allowed_slots=["features", "content", "main"],
            keywords=["bento", "grid", "features", "features grid", "bento box"],
            complexity="complex"
        ),
        "ai_console": ComponentMeta(
            component_id="ai_console",
            name="AI Console Demo",
            description="Interactive terminal or chat UI simulation representing the AI engine.",
            component_type="ai_console_demo",
            allowed_layouts=["landing", "ai_startup", "dashboard"],
            allowed_slots=["hero", "panels", "main"],
            keywords=["console", "ai demo", "terminal", "chatbot", "chat interface"],
            complexity="complex"
        ),
    }
    
    @classmethod
    def get_component(cls, component_id: str) -> Optional[ComponentMeta]:
        """Get component by ID"""
        return cls.COMPONENTS.get(component_id)
    
    @classmethod
    def find_by_keywords(cls, prompt: str, top_k: int = 5) -> List[ComponentMeta]:
        """Find components matching prompt keywords"""
        scored = []
        for comp in cls.COMPONENTS.values():
            score = 0
            for keyword in comp.keywords:
                if keyword.lower() in prompt.lower():
                    score += 1
            if score > 0:
                scored.append((score, comp))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [comp for _, comp in scored[:top_k]]
    
    @classmethod
    def find_for_slot(
        cls,
        slot_name: str,
        slot_allowed_types: List[str],
        prompt: str = ""
    ) -> List[ComponentMeta]:
        """Find components that fit in a specific slot, ranked by prompt match"""
        matching = []
        for comp in cls.COMPONENTS.values():
            if comp.matches_slot(slot_name, slot_allowed_types):
                score = 0
                if prompt:
                    for keyword in comp.keywords:
                        if keyword.lower() in prompt.lower():
                            score += 1
                matching.append((score, comp))
        
        matching.sort(key=lambda x: x[0], reverse=True)
        return [comp for _, comp in matching]
    
    @classmethod
    def find_by_type(cls, component_type: str) -> List[ComponentMeta]:
        """Find all components of a specific type"""
        return [c for c in cls.COMPONENTS.values() if c.component_type == component_type]
    
    @classmethod
    def get_component_tsx(cls, component_id: str) -> Optional[str]:
        """Get the TSX source code for a component"""
        component_generators = {
            "sidebar": _generate_sidebar_tsx,
            "navbar": _generate_navbar_tsx,
            "stats_card": _generate_stats_card_tsx,
            "chart_widget": _generate_chart_widget_tsx,
            "data_table": _generate_data_table_tsx,
            "activity_feed": _generate_activity_feed_tsx,
            "breadcrumbs": _generate_breadcrumbs_tsx,
            "theme_toggle": _generate_theme_toggle_tsx,
            "orbital_hero": _generate_orbital_hero_tsx,
            "bento_grid": _generate_bento_grid_features_tsx,
            "ai_console": _generate_ai_console_tsx,
        }
        
        generator = component_generators.get(component_id)
        if generator:
            return generator()
        return None
    
    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        """List all registered components"""
        return [comp.to_dict() for comp in cls.COMPONENTS.values()]
    
    @classmethod
    def display_registry(cls):
        """Display all registered components"""
        print("\n" + "=" * 60)
        print("COMPONENT REGISTRY")
        print("=" * 60)
        
        by_type: Dict[str, list] = {}
        for comp in cls.COMPONENTS.values():
            if comp.component_type not in by_type:
                by_type[comp.component_type] = []
            by_type[comp.component_type].append(comp)
        
        for ctype, comps in sorted(by_type.items()):
            print(f"\n  [{ctype.upper()}]")
            for comp in comps:
                deps = f" (deps: {', '.join(comp.required_deps)})" if comp.required_deps else ""
                print(f"    [COMP] {comp.name}")
                print(f"       Layouts: {', '.join(comp.allowed_layouts)}")
                print(f"       Keywords: {', '.join(comp.keywords[:4])}")
                print(f"       Complexity: {comp.complexity}{deps}")
        
        print(f"\n  Total: {len(cls.COMPONENTS)} components")
        print("=" * 60 + "\n")


# ---- Component TSX Generators (return complete component code) ----

def _generate_sidebar_tsx() -> str:
    return '''import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface SidebarItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href?: string;
  children?: SidebarItem[];
  badge?: string | number;
}

interface SidebarNavigationProps {
  items?: SidebarItem[];
  logo?: React.ReactNode;
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
  footer?: React.ReactNode;
  className?: string;
}

const defaultSidebarItems: SidebarItem[] = [
  { id: '1', label: 'Dashboard', href: '#', icon: <span className="w-4 h-4 rounded-full bg-current opacity-50 block"/> },
  { id: '2', label: 'Analytics', href: '#', icon: <span className="w-4 h-4 rounded-full bg-current opacity-50 block"/> },
];

export function SidebarNavigation({
  items = defaultSidebarItems,
  logo,
  collapsed: initialCollapsed = false,
  onCollapse,
  footer,
  className = "",
}: SidebarNavigationProps) {
  const [collapsed, setCollapsed] = useState(initialCollapsed);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [activeItem, setActiveItem] = useState<string>("");

  const toggleCollapse = () => {
    const newState = !collapsed;
    setCollapsed(newState);
    onCollapse?.(newState);
  };

  const toggleExpand = (id: string) => {
    const next = new Set(expandedItems);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpandedItems(next);
  };

  return (
    <motion.aside
      className={`flex flex-col h-full bg-[var(--surface-glass)] backdrop-blur-2xl border-r border-[var(--border)] shadow-xl relative z-40 ${className}`}
      animate={{ width: collapsed ? 80 : 280 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* Logo */}
      {logo && (
        <div className="flex items-center h-16 px-4 border-b border-[var(--border)]">
          {logo}
        </div>
      )}

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {items.map((item) => (
          <div key={item.id}>
            <button
              onClick={() => {
                setActiveItem(item.id);
                if (item.children) toggleExpand(item.id);
              }}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-[var(--radius-lg)] text-sm font-medium transition-all duration-300 relative overflow-hidden group ${
                activeItem === item.id
                  ? "text-white shadow-[var(--shadow-glow)]"
                  : "text-[var(--text-secondary)] hover:bg-[var(--surface-raised)] hover:text-[var(--text-primary)]"
              }`}
            >
              {activeItem === item.id && (
                <motion.div layoutId="sidebar-active" className="absolute inset-0 bg-gradient-premium rounded-[var(--radius-lg)] -z-10" />
              )}
              <span className="text-lg flex-shrink-0">{item.icon}</span>
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: "auto" }}
                    exit={{ opacity: 0, width: 0 }}
                    className="flex-1 text-left truncate"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
              {!collapsed && item.badge && (
                <span className="px-2 py-0.5 text-xs rounded-full bg-[var(--primary)] text-white">
                  {item.badge}
                </span>
              )}
              {!collapsed && item.children && (
                <span className="text-xs">
                  {expandedItems.has(item.id) ? "▾" : "▸"}
                </span>
              )}
            </button>

            {/* Children */}
            {item.children && expandedItems.has(item.id) && !collapsed && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="ml-8 mt-1 space-y-1"
              >
                {item.children.map((child) => (
                  <button
                    key={child.id}
                    onClick={() => setActiveItem(child.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                      activeItem === child.id
                        ? "text-[var(--primary)]"
                        : "text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
                    }`}
                  >
                    {child.label}
                  </button>
                ))}
              </motion.div>
            )}
          </div>
        ))}
      </nav>

      {/* Collapse Toggle */}
      <button
        onClick={toggleCollapse}
        className="mx-4 mb-2 p-2 rounded-lg hover:bg-[var(--surface-raised)] text-[var(--text-tertiary)] transition-colors"
      >
        {collapsed ? "→" : "←"}
      </button>

      {/* Footer */}
      {footer && (
        <div className="p-4 border-t border-[var(--border)]">
          {footer}
        </div>
      )}
    </motion.aside>
  );
}

// Icons (inline SVGs)
export const Icons = {
  Dashboard: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="7" height="7" rx="1" />
      <rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" />
      <rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  ),
  Analytics: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 3v18h18" />
      <path d="M7 16l4-8 4 4 4-6" />
    </svg>
  ),
  Users: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  ),
  Settings: () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  ),
};
'''

def _generate_navbar_tsx() -> str:
    return '''import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface NavLink {
  label: string;
  href: string;
  children?: NavLink[];
}

interface NavigationBarProps {
  logo?: React.ReactNode;
  links?: NavLink[];
  ctaText?: string;
  ctaHref?: string;
  transparent?: boolean;
  className?: string;
}

const defaultNavLinks: NavLink[] = [
  { label: 'Home', href: '#' },
  { label: 'Features', href: '#' },
  { label: 'Pricing', href: '#' }
];

export function NavigationBar({
  logo,
  links = defaultNavLinks,
  ctaText = "Get Started",
  ctaHref = "#",
  transparent = false,
  className = "",
}: NavigationBarProps) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const bgClass = transparent && !scrolled
    ? "bg-transparent"
    : "glass-panel shadow-lg";

  return (
    <div className="fixed top-0 left-0 right-0 z-50 flex justify-center pt-4 md:pt-6 pointer-events-none px-4">
      <motion.nav
        className={`pointer-events-auto rounded-full transition-colors duration-500 w-full max-w-7xl ${bgClass} ${className}`}
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center gap-2">
            {logo || <div className="w-8 h-8 rounded-full bg-gradient-premium animate-pulse-glow" />}
            <span className="text-xl font-bold tracking-tight text-gradient">{logo ? "" : "Project Name"}</span>
          </div>

          {/* Desktop Links */}
          <div className="hidden md:flex items-center gap-8">
            {links.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:-translate-y-0.5 transition-all duration-300"
              >
              {link.label}
            </a>
          ))}
        </div>

        {/* CTA Button */}
        <div className="hidden md:block">
          <motion.a
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            href={ctaHref}
            className="px-6 py-2.5 bg-gradient-premium rounded-full text-sm font-medium hover:shadow-[var(--shadow-glow)] transition-shadow inline-block text-white"
          >
            {ctaText}
          </motion.a>
        </div>

        {/* Mobile Toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden text-2xl text-[var(--text-primary)]"
        >
          {mobileOpen ? "✕" : "☰"}
        </button>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-[var(--surface)] border-t border-[var(--border)] rounded-b-3xl"
          >
            <div className="px-6 py-4 space-y-3">
              {links.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  className="block py-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                  onClick={() => setMobileOpen(false)}
                >
                  {link.label}
                </a>
              ))}
              <a
                href={ctaHref}
                className="block w-full text-center px-6 py-3 bg-gradient-premium rounded-full font-medium text-white"
                onClick={() => setMobileOpen(false)}
              >
                {ctaText}
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      </AnimatePresence>
      </motion.nav>
    </div>
  );
}
'''

def _generate_stats_card_tsx() -> str:
    return '''import React from "react";
import { motion } from "framer-motion";

interface StatisticsCardProps {
  title?: string;
  value?: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  variant?: "default" | "success" | "warning" | "error";
  loading?: boolean;
  className?: string;
}

export function StatisticsCard({
  title = "Metric Overview",
  value = "1,234",
  change = 12.5,
  changeLabel = "vs last month",
  icon,
  variant = "default",
  loading = false,
  className = "",
}: StatisticsCardProps) {
  const changeColor = !change
    ? "text-[var(--text-tertiary)]"
    : change > 0
    ? "text-[var(--success)]"
    : "text-[var(--error)]";

  const changeIcon = !change ? "" : change > 0 ? "↑" : "↓";

  if (loading) {
    return (
      <div className={`p-6 rounded-2xl glass-panel animate-pulse ${className}`}>
        <div className="h-4 w-20 bg-[var(--surface-raised)] rounded mb-3" />
        <div className="h-8 w-24 bg-[var(--surface-raised)] rounded mb-2" />
        <div className="h-3 w-16 bg-[var(--surface-raised)] rounded" />
      </div>
    );
  }

  return (
    <motion.div
      className={`group relative overflow-hidden p-6 rounded-2xl glass-panel border-glow transition-all duration-500 hover:shadow-[var(--shadow-lg)] ${className}`}
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <div className="absolute -right-8 -top-8 w-32 h-32 bg-[var(--primary)]/10 blur-[30px] rounded-full group-hover:bg-[var(--primary)]/20 transition-colors duration-700" />
      
      <div className="flex items-start justify-between mb-4 relative z-10">
        <span className="text-sm font-medium text-[var(--text-secondary)] tracking-wide">{title}</span>
        {icon && <div className="p-2.5 rounded-xl bg-[var(--surface-raised)] text-[var(--primary)] shadow-sm group-hover:shadow-[var(--shadow-glow)] transition-all duration-300 text-lg">{icon}</div>}
      </div>
      <div className="text-3xl font-bold text-shimmer mb-1 relative z-10">
        {value}
      </div>
      {change !== undefined && (
        <div className={`flex items-center gap-1 text-xs relative z-10 ${changeColor}`}>
          <span>{changeIcon}</span>
          <span>{Math.abs(change)}%</span>
          <span className="text-[var(--text-tertiary)]">{changeLabel}</span>
        </div>
      )}
    </motion.div>
  );
}
'''

def _generate_chart_widget_tsx() -> str:
    return '''import React from "react";
import { motion } from "framer-motion";

// Note: Requires recharts package
// import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface ChartWidgetProps {
  title?: string;
  type?: "line" | "bar" | "pie" | "area";
  data?: Record<string, any>[];
  dataKey?: string;
  xKey?: string;
  colors?: string[];
  height?: number;
  loading?: boolean;
  empty?: boolean;
  className?: string;
}

const defaultChartData = [
  { name: 'Jan', value: 400 },
  { name: 'Feb', value: 300 },
  { name: 'Mar', value: 550 },
  { name: 'Apr', value: 450 }
];

export function ChartWidget({
  title = "Overview Chart",
  type = "line",
  data = defaultChartData,
  dataKey = "value",
  xKey = "name",
  colors,
  height = 300,
  loading = false,
  empty = false,
  className = "",
}: ChartWidgetProps) {
  if (loading) {
    return (
      <div className={`p-6 rounded-xl bg-[var(--surface)] border border-[var(--border)] ${className}`}>
        <div className="h-5 w-32 bg-[var(--surface-raised)] rounded mb-4 animate-pulse" />
        <div className="h-[300px] bg-[var(--surface-raised)] rounded animate-pulse" />
      </div>
    );
  }

  if (empty || data.length === 0) {
    return (
      <div className={`p-6 rounded-xl bg-[var(--surface)] border border-[var(--border)] ${className}`}>
        <h3 className="text-sm font-medium text-[var(--text-secondary)] mb-4">{title}</h3>
        <div className="flex items-center justify-center h-[300px] text-[var(--text-tertiary)]">
          <div className="text-center">
            <div className="text-4xl mb-3">CHART</div>
            <p className="text-sm">No data available</p>
            <p className="text-xs mt-1">Data will appear here once available</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className={`p-6 rounded-[var(--radius-xl)] glass-card border border-[var(--border)] hover:border-[var(--border-focus)] transition-all duration-500 hover:shadow-[var(--shadow-lg)] relative overflow-hidden group ${className}`}
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {/* Decorative gradient flare */}
      <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-[var(--primary)]/5 blur-[50px] mix-blend-screen opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
      
      <h3 className="text-sm font-semibold tracking-wide text-[var(--text-secondary)] mb-6 relative z-10">{title}</h3>
      <div style={{ height }} className="relative z-10">
        {/* Chart implementation using Recharts would go here */}
        <div className="flex items-center justify-center h-full text-[var(--text-tertiary)] text-sm">
          [Chart: {type} visualization of {dataKey}]
          <br />
          <span className="text-xs">Install recharts for full chart rendering</span>
        </div>
      </div>
    </motion.div>
  );
}
'''

def _generate_data_table_tsx() -> str:
    return '''import React, { useState, useMemo } from "react";
import { motion } from "framer-motion";

interface Column {
  key: string;
  header: string;
  sortable?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
  width?: string;
}

interface DataTableProps {
  title?: string;
  columns?: Column[];
  data?: Record<string, any>[];
  loading?: boolean;
  empty?: boolean;
  emptyMessage?: string;
  pageSize?: number;
  searchable?: boolean;
  onRowClick?: (row: any) => void;
  className?: string;
}

const defaultColumns: Column[] = [
  { key: 'id', header: 'ID', sortable: true },
  { key: 'name', header: 'Name', sortable: true },
  { key: 'status', header: 'Status' }
];

const defaultData = [
  { id: '1', name: 'Alpha Project', status: 'Active' },
  { id: '2', name: 'Beta Module', status: 'Pending' },
  { id: '3', name: 'Gamma Protocol', status: 'Completed' }
];

export function DataTable({
  title = "Data Table",
  columns = defaultColumns,
  data = defaultData,
  loading = false,
  empty = false,
  emptyMessage = "No data found",
  pageSize = 10,
  searchable = false,
  onRowClick,
  className = "",
}: DataTableProps) {
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<string>("");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    if (!search) return data;
    return data.filter((row) =>
      Object.values(row).some((val) =>
        String(val).toLowerCase().includes(search.toLowerCase())
      )
    );
  }, [data, search]);

  const sorted = useMemo(() => {
    if (!sortKey) return filtered;
    return [...filtered].sort((a, b) => {
      const aVal = a[sortKey] ?? "";
      const bVal = b[sortKey] ?? "";
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [filtered, sortKey, sortDir]);

  const paginated = sorted.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(sorted.length / pageSize);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  if (loading) {
    return (
      <div className={`rounded-xl bg-[var(--surface)] border border-[var(--border)] ${className}`}>
        {title && <div className="px-6 py-4 border-b border-[var(--border)]"><div className="h-5 w-32 bg-[var(--surface-raised)] rounded animate-pulse" /></div>}
        <div className="p-6 space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-4 bg-[var(--surface-raised)] rounded animate-pulse" style={{ width: `${60 + Math.random() * 30}%` }} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className={`rounded-[var(--radius-xl)] glass-card border flex flex-col border-[var(--border)] hover:border-white/10 transition-all duration-300 hover:shadow-[var(--shadow-lg)] overflow-hidden ${className}`}
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, staggerChildren: 0.05 }}
    >
      {/* Header */}
      {(title || searchable) && (
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
          {title && <h3 className="text-sm font-medium text-[var(--text-secondary)]">{title}</h3>}
          {searchable && (
            <input
              type="text"
              placeholder="Search..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0); }}
              className="px-3 py-1.5 text-sm rounded-lg bg-[var(--background)] border border-[var(--border)] text-[var(--text-primary)] placeholder-[var(--text-tertiary)] focus:outline-none focus:border-[var(--border-focus)]"
            />
          )}
        </div>
      )}

      {/* Table */}
      {empty || data.length === 0 ? (
        <div className="flex items-center justify-center h-48 text-[var(--text-tertiary)]">
          <div className="text-center">
            <div className="text-3xl mb-2">EMPTY</div>
            <p className="text-sm">{emptyMessage}</p>
          </div>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  {columns.map((col) => (
                    <th
                      key={col.key}
                      onClick={() => col.sortable && handleSort(col.key)}
                      className={`px-6 py-3 text-left text-xs font-medium text-[var(--text-tertiary)] uppercase tracking-wider ${
                        col.sortable ? "cursor-pointer hover:text-[var(--text-primary)] select-none" : ""
                      }`}
                      style={{ width: col.width }}
                    >
                      {col.header}
                      {sortKey === col.key && (
                        <span className="ml-1">{sortDir === "asc" ? "↑" : "↓"}</span>
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {paginated.map((row, i) => (
                  <motion.tr
                    key={row.id || i}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ delay: i * 0.04 }}
                    onClick={() => onRowClick?.(row)}
                    className={`border-b border-[var(--divider)] group transition-all duration-200 ${
                      onRowClick ? "cursor-pointer hover:bg-[var(--surface-raised)]" : "hover:bg-[var(--surface-raised)]/50"
                    }`}
                  >
                    {columns.map((col) => (
                      <td key={col.key} className="px-6 py-4 text-sm text-[var(--text-primary)] whitespace-nowrap">
                        {col.render ? col.render(row[col.key], row) : row[col.key]}
                      </td>
                    ))}
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-6 py-3 border-t border-[var(--border)]">
              <span className="text-xs text-[var(--text-tertiary)]">
                Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, sorted.length)} of {sorted.length}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="px-3 py-1 text-xs rounded-lg border border-[var(--border)] disabled:opacity-30 hover:bg-[var(--surface-raised)] transition-colors"
                >
                  Prev
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page >= totalPages - 1}
                  className="px-3 py-1 text-xs rounded-lg border border-[var(--border)] disabled:opacity-30 hover:bg-[var(--surface-raised)] transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </motion.div>
  );
}
'''

def _generate_activity_feed_tsx() -> str:
    return '''import React from "react";
import { motion } from "framer-motion";

interface Activity {
  id: string;
  user: string;
  action: string;
  target?: string;
  timestamp: string;
  icon?: React.ReactNode;
}

interface ActivityFeedProps {
  title?: string;
  activities?: Activity[];
  loading?: boolean;
  empty?: boolean;
  maxItems?: number;
  className?: string;
}

const defaultActivities: Activity[] = [
  { id: '1', user: 'System', action: 'initialized workspace', timestamp: 'Just now' },
  { id: '2', user: 'Admin', action: 'updated settings', timestamp: '2 hours ago' }
];

export function ActivityFeed({
  title = "Recent Activity",
  activities = defaultActivities,
  loading = false,
  empty = false,
  maxItems = 10,
  className = "",
}: ActivityFeedProps) {
  if (loading) {
    return (
      <div className={`p-6 rounded-xl bg-[var(--surface)] border border-[var(--border)] ${className}`}>
        <div className="h-5 w-28 bg-[var(--surface-raised)] rounded mb-4 animate-pulse" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-[var(--surface-raised)] animate-pulse" />
            <div className="flex-1 space-y-1">
              <div className="h-3 w-3/4 bg-[var(--surface-raised)] rounded animate-pulse" />
              <div className="h-2 w-1/4 bg-[var(--surface-raised)] rounded animate-pulse" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <motion.div
      className={`p-6 rounded-xl bg-[var(--surface)] border border-[var(--border)] ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <h3 className="text-sm font-medium text-[var(--text-secondary)] mb-4">{title}</h3>
      
      {empty || activities.length === 0 ? (
        <div className="text-center py-8 text-[var(--text-tertiary)] text-sm">
          No recent activity
        </div>
      ) : (
        <div className="space-y-4">
          {activities.slice(0, maxItems).map((activity, i) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex gap-3"
            >
              <div className="w-8 h-8 rounded-full bg-[var(--primary)]/10 flex items-center justify-center text-xs text-[var(--primary)] flex-shrink-0">
                {activity.icon || activity.user[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-[var(--text-primary)] truncate">
                  <span className="font-medium">{activity.user}</span>{" "}
                  {activity.action}{" "}
                  {activity.target && (
                    <span className="font-medium">{activity.target}</span>
                  )}
                </p>
                <p className="text-xs text-[var(--text-tertiary)] mt-0.5">
                  {activity.timestamp}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
'''

def _generate_breadcrumbs_tsx() -> str:
    return '''import React from "react";

interface Breadcrumb {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items?: Breadcrumb[];
  separator?: string;
  className?: string;
}

const defaultBreadcrumbs: Breadcrumb[] = [
  { label: 'Home', href: '/' },
  { label: 'Dashboard' }
];

export function Breadcrumbs({
  items = defaultBreadcrumbs,
  separator = "/",
  className = "",
}: BreadcrumbsProps) {
  return (
    <nav className={`flex items-center gap-2 text-sm ${className}`}>
      {items.map((item, i) => (
        <React.Fragment key={i}>
          {i > 0 && (
            <span className="text-[var(--text-tertiary)] select-none">{separator}</span>
          )}
          {item.href ? (
            <a
              href={item.href}
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
            >
              {item.label}
            </a>
          ) : (
            <span className="text-[var(--text-primary)] font-medium">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
}
'''

def _generate_theme_toggle_tsx() -> str:
    return '''import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

interface ThemeToggleProps {
  className?: string;
  onThemeChange?: (theme: "dark" | "light") => void;
}

export function ThemeToggle({ className = "", onThemeChange }: ThemeToggleProps) {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const saved = localStorage.getItem("novaryx-theme") as "dark" | "light" | null;
    if (saved) setTheme(saved);
  }, []);

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem("novaryx-theme", next);
    document.documentElement.setAttribute("data-theme", next);
    onThemeChange?.(next);
  };

  return (
    <button
      onClick={toggle}
      className={`relative w-12 h-6 rounded-full transition-colors duration-300 ${
        theme === "dark" ? "bg-[var(--primary)]" : "bg-[var(--surface-raised)]"
      } ${className}`}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
    >
      <motion.div
        className="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-md flex items-center justify-center text-xs"
        animate={{ left: theme === "dark" ? "26px" : "2px" }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      >
        {theme === "dark" ? "D" : "L"}
      </motion.div>
    </button>
  );
}
'''


def _generate_orbital_hero_tsx() -> str:
    return '''import React from 'react';
import { motion } from 'framer-motion';

export interface OrbitalHeroProps {
  headline?: string;
  subheadline?: string;
  ctaText?: string;
  [key: string]: any;
}

export function OrbitalHero({
  headline = "The Future of Artificial Intelligence",
  subheadline = "Accelerate your workflows by embedding our cutting-edge neural models directly into your pipeline.",
  ctaText = "Start Building Free"
}: OrbitalHeroProps) {
  return (
    <div className="relative w-full h-[80vh] min-h-[600px] flex items-center justify-center overflow-hidden">
      {/* Animated Glowing Orbs */}
      <motion.div 
        animate={{ scale: [1, 1.2, 1], rotate: [0, 90, 0] }} 
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="absolute top-10 left-1/4 w-96 h-96 bg-[var(--primary)] rounded-full mix-blend-screen mix-blend-lighten filter blur-[100px] opacity-40 z-0" 
      />
      <motion.div 
        animate={{ scale: [1, 1.3, 1], rotate: [0, -90, 0] }} 
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        className="absolute bottom-10 right-1/4 w-80 h-80 bg-[var(--accent)] rounded-full mix-blend-screen filter blur-[100px] opacity-30 z-0" 
      />
      
      {/* Foreground Content */}
      <div className="z-10 text-center max-w-4xl px-6 flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="inline-flex items-center px-4 py-2 border border-[var(--primary)] bg-[var(--primary)]/10 rounded-full mb-8"
        >
          <span className="text-[var(--primary)] text-sm font-semibold tracking-wide uppercase">Introducing NOVARYX V2</span>
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
          className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-white to-[var(--text-secondary)]"
        >
          {headline}
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="text-xl md:text-2xl text-[var(--text-secondary)] mb-10 max-w-2xl font-light"
        >
          {subheadline}
        </motion.p>
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.3, ease: "backOut" }}
          className="flex space-x-4"
        >
          <button className="px-8 py-4 bg-gradient-premium rounded-xl font-bold text-white shadow-lg hover:shadow-[var(--primary)]/50 transition-all duration-300 transform hover:-translate-y-1">
            {ctaText}
          </button>
          <button className="px-8 py-4 bg-[var(--surface-raised)] border border-[var(--border)] rounded-xl font-bold text-[var(--text-primary)] hover:bg-[var(--surface-hover)] transition-all duration-300">
            View Documentation
          </button>
        </motion.div>
      </div>
    </div>
  );
}
'''


def _generate_bento_grid_features_tsx() -> str:
    return '''import React from 'react';
import { motion } from 'framer-motion';

export interface BentoGridFeaturesProps {
  features?: Array<{ title: string; description: string; colSpan?: string; rowSpan?: string }>;
  [key: string]: any;
}

export function FeatureBentoGrid({
  features = [
    { title: "Real-time Inference", description: "Edge-deployed models with zero latency capability.", colSpan: "md:col-span-2", rowSpan: "md:row-span-2" },
    { title: "Quantum Security", description: "End-to-end encrypted model payloads.", colSpan: "md:col-span-1", rowSpan: "md:row-span-1" },
    { title: "Global CDN", description: "Deploy endpoints to 45 regions instantly.", colSpan: "md:col-span-1", rowSpan: "md:row-span-1" },
    { title: "Advanced Analytics", description: "Deep token tracking and cost predictions.", colSpan: "md:col-span-2", rowSpan: "md:row-span-1" }
  ]
}: BentoGridFeaturesProps) {
  return (
    <div className="w-full max-w-6xl mx-auto py-20 px-6">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-5xl font-bold mb-4">Enterprise Grade Architecture</h2>
        <p className="text-[var(--text-secondary)]">Everything you need to scale your LLM startup instantly.</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 auto-rows-[250px] gap-6">
        {features.map((feature, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            className={`glass-card p-8 flex flex-col justify-end group hover:border-[var(--primary)] transition-colors duration-500 ${feature.colSpan || ""} ${feature.rowSpan || ""}`}
          >
            <div className="w-12 h-12 rounded-full mb-auto bg-gradient-to-br from-[var(--primary)] to-[var(--accent)] opacity-20 group-hover:opacity-100 transition-opacity duration-500" />
            <h3 className="text-2xl font-semibold mb-2">{feature.title}</h3>
            <p className="text-[var(--text-secondary)]">{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
'''


def _generate_ai_console_tsx() -> str:
    return '''import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface AiConsoleDemoProps {
  [key: string]: any;
}

export function AiConsoleDemo(props: AiConsoleDemoProps) {
  const [messages, setMessages] = useState<{role: string, text: string}[]>([
    { role: "system", text: "NOVARYX AI Engine initialized..." }
  ]);
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: "user", text: input }]);
    setInput("");
    
    // Fake typing response
    setTimeout(() => {
      setMessages(prev => [...prev, { role: "system", text: `Analyzing objective: "${input}". Synthesizing deployment vector.` }]);
    }, 1000);
  };

  return (
    <div className="w-full max-w-4xl mx-auto rounded-2xl overflow-hidden glass-card border border-[var(--border)] shadow-2xl relative">
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[var(--primary)] to-[var(--accent)]" />
      
      {/* Console Header */}
      <div className="bg-[#111] px-4 py-3 flex items-center border-b border-[#333]">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
        </div>
        <div className="mx-auto text-xs text-gray-500 font-mono tracking-wider">NOVARYX CLI v2.4.1</div>
      </div>
      
      {/* Console Body */}
      <div className="bg-[#0a0a0a] font-mono text-sm h-96 p-6 overflow-y-auto flex flex-col">
        <AnimatePresence>
          {messages.map((m, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, x: -10 }} 
              animate={{ opacity: 1, x: 0 }} 
              className={`mb-4 flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`px-4 py-2 rounded-lg ${m.role === 'user' ? 'bg-[#222] text-white' : 'text-[var(--primary)]'}`}>
                {m.role === 'system' && <span className="mr-2 opacity-50">></span>}
                {m.text}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
      
      {/* Console Input */}
      <form onSubmit={handleSubmit} className="border-t border-[#333] bg-[#0f0f0f] p-4 flex">
        <span className="text-[var(--primary)] mr-3 font-mono mt-1">></span>
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Deploy a full-stack SaaS..." 
          className="bg-transparent border-none outline-none w-full text-white font-mono placeholder-[#444]"
        />
        <button type="submit" className="text-xs bg-[var(--primary)]/20 text-[var(--primary)] px-3 py-1 rounded hover:bg-[var(--primary)]/40 hover:text-white transition-colors">
          EXECUTE
        </button>
      </form>
    </div>
  );
}
'''


# ---- Test ----

def test_component_registry():
    """Test the component registry"""
    
    print("\n" + "=" * 60)
    print("COMPONENT REGISTRY TEST")
    print("=" * 60)
    
    # Display all components
    ComponentRegistry.display_registry()
    
    # Test keyword matching
    test_prompts = [
        "Build a dashboard with stats cards and charts for analytics",
        "I need a sidebar navigation with settings",
        "Create a landing page with a navbar",
        "Add a data table for user management",
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: '{prompt[:60]}...'")
        matches = ComponentRegistry.find_by_keywords(prompt, top_k=3)
        print(f"   Matches: {[c.name for c in matches]}")
    
    # Test slot matching
    print(f"\nComponents for 'sidebar' slot in dashboard:")
    matches = ComponentRegistry.find_for_slot("sidebar", ["sidebar", "navigation", "logo"])
    print(f"   {[c.name for c in matches]}")
    
    print(f"\nComponents for 'stats' slot in dashboard:")
    matches = ComponentRegistry.find_for_slot("stats", ["stats_card", "kpi_card"])
    print(f"   {[c.name for c in matches]}")
    
    # Test TSX generation
    print(f"\nSample TSX (first 200 chars of Sidebar):")
    tsx = ComponentRegistry.get_component_tsx("sidebar")
    if tsx:
        print(f"   {tsx[:200]}...")
    
    print(f"\nComponent Registry test complete")
    
    return ComponentRegistry


if __name__ == "__main__":
    test_component_registry()