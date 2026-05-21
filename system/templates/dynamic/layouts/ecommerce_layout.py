"""
NOVARYX - E-Commerce Layout
Header + Product Grid + Cart Sidebar + Footer

Grid Structure:
┌──────────────────────────────────────────┐
│                HEADER                    │
├──────────────────────────────────────────┤
│  FILTERS  │     PRODUCT GRID      │ CART │
│  (left)   │                       │(right)│
├──────────────────────────────────────────┤
│                FOOTER                    │
└──────────────────────────────────────────┘
"""

from .base_layout import BaseLayout, LayoutSlot, LayoutConfig, LayoutType


class EcommerceLayout(BaseLayout):
    """E-Commerce store layout"""
    
    @property
    def layout_type(self) -> LayoutType:
        return LayoutType.ECOMMERCE
    
    @property
    def layout_name(self) -> str:
        return "E-Commerce Layout"
    
    @property
    def description(self) -> str:
        return "Online store with product grid, filters, shopping cart sidebar, and checkout flow."
    
    def _define_slots(self):
        
        self.add_slot(LayoutSlot(
            name="header",
            description="Store header with logo, search, cart icon, account",
            allowed_component_types=["header", "search_bar", "cart_icon", "user_menu", "logo"],
            required=True,
            max_components=5
        ))
        
        self.add_slot(LayoutSlot(
            name="filters",
            description="Product filters sidebar (categories, price, ratings)",
            allowed_component_types=["filter_panel", "category_list", "price_filter", "search_filters"],
            required=False,
            max_components=5
        ))
        
        self.add_slot(LayoutSlot(
            name="products",
            description="Product grid displaying items",
            allowed_component_types=["product_grid", "product_card", "product_list"],
            required=True,
            max_components=50,
            default_component="product_grid"
        ))
        
        self.add_slot(LayoutSlot(
            name="cart",
            description="Shopping cart sidebar",
            allowed_component_types=["cart_sidebar", "cart_drawer", "cart_summary"],
            required=False,
            max_components=3
        ))
        
        self.add_slot(LayoutSlot(
            name="footer",
            description="Store footer",
            allowed_component_types=["footer", "newsletter_form", "social_links"],
            required=True,
            max_components=4
        ))