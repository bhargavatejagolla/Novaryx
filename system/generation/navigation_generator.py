"""
NOVARYX - Navigation Generator
Auto-generates navigation components from route config.
"""

from typing import List, Dict


class NavigationGenerator:
    """Generates navigation from routes"""
    
    @staticmethod
    def generate_sidebar_navigation(pages: List[Dict]) -> str:
        """Generate sidebar nav items from pages"""
        
        nav_items = []
        for page in pages:
            if page.get("is_landing"):
                continue
            
            name = page.get("name", "Page")
            route = page.get("route", "/")
            requires_auth = page.get("requires_auth", False)
            
            icon_map = {
                "Dashboard": "LayoutDashboard",
                "Analytics": "BarChart3",
                "Users": "Users",
                "Settings": "Settings",
                "Profile": "User",
                "Billing": "CreditCard",
                "Projects": "FolderKanban",
                "Tasks": "CheckSquare",
                "Messages": "MessageSquare",
                "Notifications": "Bell",
                "Reports": "FileText",
                "Calendar": "Calendar",
            }
            
            icon = icon_map.get(name, "Circle")
            lock_icon = "Lock" if requires_auth else ""
            
            nav_items.append(f"""  {{
    id: "{name.lower()}",
    label: "{name}",
    href: "{route}",
    icon: <{icon} size={{20}} />,
  }}""")
        
        items_block = ",\n".join(nav_items)
        
        return items_block
    
    @staticmethod
    def generate_navbar_links(pages: List[Dict]) -> str:
        """Generate navbar link items"""
        
        links = []
        for page in pages:
            name = page.get("name", "Page")
            route = page.get("route", "/")
            
            if page.get("is_landing"):
                links.append(f'  {{ label: "{name}", href: "{route}" }}')
            else:
                links.append(f'  {{ label: "{name}", href: "{route}" }}')
        
        return ",\n".join(links) if links else "  { label: 'Home', href: '/' }"
    
    @staticmethod
    def generate_breadcrumb_config(pages: List[Dict]) -> str:
        """Generate breadcrumb configuration"""
        
        mappings = []
        for page in pages:
            route = page.get("route", "/")
            name = page.get("name", "Page")
            mappings.append(f"  '{route}': '{name}'")
        
        return ",\n".join(mappings)