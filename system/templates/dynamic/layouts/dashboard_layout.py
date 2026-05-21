"""
NOVARYX - Dashboard Layout
Sidebar + Header + Main content area with optional panels.

Grid Structure:
┌──────────┬──────────────────────────┐
│          │                          │
│  SIDEBAR │       HEADER             │
│          │                          │
│          ├──────────────────────────┤
│          │                          │
│          │       MAIN               │
│          │                          │
│          │                          │
│          ├──────────────────────────┤
│          │       PANELS (optional)  │
└──────────┴──────────────────────────┘
"""

from .base_layout import BaseLayout, LayoutSlot, LayoutConfig, LayoutType


class DashboardLayout(BaseLayout):
    """Dashboard application layout with sidebar navigation"""
    
    @property
    def layout_type(self) -> LayoutType:
        return LayoutType.DASHBOARD
    
    @property
    def layout_name(self) -> str:
        return "Dashboard Layout"
    
    @property
    def description(self) -> str:
        return "Full dashboard with collapsible sidebar, top header, main content area, and optional bottom panels. Ideal for SaaS apps, analytics, and management tools."
    
    def _define_slots(self):
        """Define all slots for dashboard layout"""
        
        self.add_slot(LayoutSlot(
            name="sidebar",
            description="Left sidebar navigation with logo, nav links, and user section",
            allowed_component_types=["sidebar", "navigation", "logo", "user_menu", "nav_links"],
            required=True,
            max_components=5,
            grid_area="sidebar"
        ))
        
        self.add_slot(LayoutSlot(
            name="header",
            description="Top header bar with search, notifications, breadcrumbs",
            allowed_component_types=["header", "search_bar", "breadcrumbs", "notifications", "theme_toggle"],
            required=True,
            max_components=5,
            grid_area="header"
        ))
        
        self.add_slot(LayoutSlot(
            name="stats",
            description="Stats cards row showing key metrics (KPIs)",
            allowed_component_types=["stats_card", "kpi_card", "metric_card", "chart"],
            required=False,
            max_components=6,
            grid_area="stats",
            default_component="stats_card"
        ))
        
        self.add_slot(LayoutSlot(
            name="main",
            description="Primary content area for charts, tables, dashboards",
            allowed_component_types=["chart", "data_table", "chart_grid", "activity_feed", "calendar", "map"],
            required=True,
            max_components=4,
            grid_area="main"
        ))
        
        self.add_slot(LayoutSlot(
            name="panels",
            description="Bottom row for additional panels and widgets",
            allowed_component_types=["activity_feed", "recent_activity", "quick_actions", "status_panel"],
            required=False,
            max_components=3,
            grid_area="panels"
        ))
    
    def generate_grid_css(self) -> str:
        """Generate CSS Grid template"""
        return """
.dashboard-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  grid-template-rows: 64px auto auto;
  grid-template-areas:
    "sidebar header"
    "sidebar stats"
    "sidebar main"
    "sidebar panels";
  min-height: 100vh;
  background: var(--background);
  color: var(--text-primary);
}

.dashboard-layout .slot-sidebar {
  grid-area: sidebar;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  background: var(--surface);
  border-right: 1px solid var(--border);
}

.dashboard-layout .slot-header {
  grid-area: header;
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--surface-glass);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.dashboard-layout .slot-stats {
  grid-area: stats;
}

.dashboard-layout .slot-main {
  grid-area: main;
}

.dashboard-layout .slot-panels {
  grid-area: panels;
}

/* Mobile: stack everything */
@media (max-width: 768px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
    grid-template-rows: 64px auto auto auto;
    grid-template-areas:
      "header"
      "stats"
      "main"
      "panels";
  }
  
  .dashboard-layout .slot-sidebar {
    position: fixed;
    left: -100%;
    transition: left 0.3s ease;
    z-index: 100;
  }
  
  .dashboard-layout .slot-sidebar.open {
    left: 0;
  }
}
"""
    
    def generate_layout_tsx(self, design_system=None) -> str:
        """Generate complete React layout component"""
        
        ds_prefix = self.get_safe_project_name(design_system)
        
        return f'''import React, {{ useState }} from "react";
import {{ motion, AnimatePresence }} from "framer-motion";

interface {ds_prefix}DashboardProps {{
  children?: React.ReactNode;
  sidebarContent?: React.ReactNode;
  headerContent?: React.ReactNode;
  statsContent?: React.ReactNode;
  mainContent?: React.ReactNode;
  panelsContent?: React.ReactNode;
}}

export default function {ds_prefix}Dashboard({{
  sidebarContent,
  headerContent,
  statsContent,
  mainContent,
  panelsContent,
}}: {ds_prefix}DashboardProps) {{
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[var(--background)]">
      {{/* Sidebar Slot */}}
      <aside
        className={{`z-40 h-full flex-shrink-0 transition-all duration-500 ease-in-out border-r border-[var(--border)] bg-[var(--surface-glass)] backdrop-blur-2xl ${{
          sidebarOpen ? "translate-x-0 absolute md:relative w-72" : "-translate-x-full absolute md:relative md:translate-x-0 w-20"
        }}`}}
      >
        {{sidebarContent || <DefaultSidebar />}}
      </aside>

      <AnimatePresence>
        {{sidebarOpen && (
          <motion.div
            initial={{{{ opacity: 0 }}}}
            animate={{{{ opacity: 1 }}}}
            exit={{{{ opacity: 0 }}}}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 md:hidden"
            onClick={{() => setSidebarOpen(false)}}
          />
        )}}
      </AnimatePresence>

      {{/* Main Container */}}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {{/* Header Slot */}}
        <header className="h-20 flex-shrink-0 px-6 flex items-center border-b border-[var(--border)] bg-[var(--surface-glass)] backdrop-blur-xl z-20">
          <button
            className="md:hidden mr-4 p-2 rounded-lg hover:bg-[var(--surface-raised)] text-[var(--text-secondary)] transition-colors"
            onClick={{() => setSidebarOpen(!sidebarOpen)}}
          >
            ☰
          </button>
          {{headerContent || <DefaultHeader />}}
        </header>

        {{/* Scrollable Content Area */}}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-[var(--background)] scroll-smooth relative">
          <div className="max-w-7xl mx-auto p-4 md:p-8 space-y-8">

            {{/* Stats Slot */}}
            {{statsContent && (
              <section className="slot-stats">
                <motion.div
                  className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
                  initial={{{{ opacity: 0, y: 20 }}}}
                  animate={{{{ opacity: 1, y: 0 }}}}
                  transition={{{{ duration: 0.5, staggerChildren: 0.1 }}}}
                >
                  {{statsContent}}
                </motion.div>
              </section>
            )}}

            {{/* Main Content Slot */}}
            <section className="slot-main">
              <AnimatePresence mode="wait">
                <motion.div
                  key="main-content"
                  initial={{{{ opacity: 0, y: 15 }}}}
                  animate={{{{ opacity: 1, y: 0 }}}}
                  exit={{{{ opacity: 0, y: -15 }}}}
                  transition={{{{ duration: 0.4 }}}}
                >
                  {{mainContent || <DefaultMain />}}
                </motion.div>
              </AnimatePresence>
            </section>
            {{panelsContent && (
              <section className="slot-panels">
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {{panelsContent}}
                </div>
              </section>
            )}}
          </div>
        </main>
      </div>
    </div>
  );
}}

/* Default placeholders */
function DefaultSidebar() {{
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-bold">{{ "Project Name" }}</h1>
      <nav className="space-y-1">
        {{["Dashboard", "Analytics", "Users", "Settings"].map((item) => (
          <a
            key={{item}}
            href="#"
            className="block px-4 py-2 rounded-lg hover:bg-[var(--surface-raised)] transition-colors"
          >
            {{item}}
          </a>
        ))}}
      </nav>
    </div>
  );
}}

function DefaultHeader() {{
  return (
    <div className="flex-1 flex items-center justify-between">
      <h2 className="text-lg font-semibold">Dashboard</h2>
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-[var(--primary)]" />
      </div>
    </div>
  );
}}

function DefaultMain() {{
  return (
    <div className="flex items-center justify-center h-64 text-[var(--text-secondary)]">
      <p>Select a component to display</p>
    </div>
  );
}}
'''