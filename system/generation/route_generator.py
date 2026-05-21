"""
NOVARYX - Route Generator
Generates React Router configuration from page specs.

Hardened v2:
- Strict PascalCase sanitization on all names
- Default imports (no named import syntax issues)
- Auth/public route separation
- Proper Outlet-based layout pattern
"""

import json
import re
from typing import List, Dict


def _pascal(raw: str) -> str:
    """Convert any string to strict PascalCase — no spaces, no specials."""
    # Strip non-alphanumeric except spaces/hyphens/underscores
    cleaned = re.sub(r"[^a-zA-Z0-9\s\-_]", "", str(raw))
    return "".join(w.capitalize() for w in cleaned.replace("-", " ").replace("_", " ").split()) or "Page"


class RouteGenerator:
    """Generates React Router setup — hardened against LLM naming artifacts."""

    @staticmethod
    def generate_routes_config(pages: List[Dict]) -> str:
        """Generate route configuration array"""
        routes = []
        for page in pages:
            safe_name = _pascal(page.get("name", "Page"))
            route = {
                "path": page.get("route", "/"),
                "component": safe_name,
                "protected": bool(page.get("requires_auth", False)),
                "is_landing": bool(page.get("is_landing", False)),
            }
            routes.append(route)
        return json.dumps(routes, indent=2)

    @staticmethod
    def generate_app_tsx(
        pages: List[Dict],
        has_auth: bool = False,
        layout_component: str = "DashboardLayout"
    ) -> str:
        """Generate complete App.tsx with routing.

        Uses default imports and Outlet-based layout to match
        what the page generator produces. Auth pages are always
        separated from protected routes.
        """

        # Separate auth pages (login/register) from app pages
        auth_names = {"login", "register", "signup", "signin", "forgot", "reset"}
        public_pages = []
        protected_pages = []
        landing_pages = []

        for page in pages:
            safe_name = _pascal(page.get("name", "Page"))
            route = page.get("route", "/")
            requires_auth = page.get("requires_auth", False)
            is_landing = page.get("is_landing", False)

            entry = {"name": safe_name, "route": route}

            if safe_name.lower() in auth_names:
                public_pages.append(entry)
            elif is_landing:
                landing_pages.append(entry)
            elif requires_auth:
                protected_pages.append(entry)
            else:
                protected_pages.append(entry)  # Default inside layout

        # All pages for import generation (dedup by name)
        seen = set()
        all_pages = public_pages + landing_pages + protected_pages
        unique_pages = []
        for p in all_pages:
            if p["name"] not in seen:
                seen.add(p["name"])
                unique_pages.append(p)

        # Build import lines — use DEFAULT imports to match page exports
        import_lines = "\n".join(
            f"import {p['name']} from './pages/{p['name']}'"
            for p in unique_pages
        )

        # Auth imports
        protected_route_import = ""
        auth_provider_import = ""
        if has_auth:
            protected_route_import = "import { ProtectedRoute } from './components/ProtectedRoute'"
            auth_provider_import = "import { AuthProvider } from './hooks/useAuth'"

        # Build public routes (login/register etc.)
        public_route_lines = []
        for p in public_pages:
            public_route_lines.append(
                f'            <Route path="{p["route"]}" element={{<{p["name"]} />}} />'
            )

        # Build protected / layout routes
        inner_route_lines = []
        for p in landing_pages:
            inner_route_lines.append(
                f'              <Route index element={{<{p["name"]} />}} />'
            )
        for p in protected_pages:
            inner_route_lines.append(
                f'              <Route path="{p["route"]}" element={{<{p["name"]} />}} />'
            )

        public_block = "\n".join(public_route_lines)
        inner_block = "\n".join(inner_route_lines)

        # Layout wrapper with optional ProtectedRoute
        if has_auth:
            layout_open = f'          <Route element={{<ProtectedRoute><{layout_component} /></ProtectedRoute>}}>'
        else:
            layout_open = f'          <Route element={{<{layout_component} />}}>'
        layout_close = "          </Route>"

        # Render conditional wrappers
        if has_auth:
            app_wrapper_start = "<AuthProvider>\n        <BrowserRouter>"
            app_wrapper_end = "</BrowserRouter>\n      </AuthProvider>"
        else:
            app_wrapper_start = "<BrowserRouter>"
            app_wrapper_end = "</BrowserRouter>"

        return f"""import React from 'react'
import {{ BrowserRouter, Routes, Route, Navigate }} from 'react-router-dom'
import {{ ThemeProvider }} from './components/ThemeProvider'
{auth_provider_import}
import {layout_component} from './layouts/{layout_component}'
{protected_route_import}
{import_lines}

export default function App() {{
  return (
    <ThemeProvider>
      {app_wrapper_start}
          <Routes>
{public_block}
{layout_open}
{inner_block}
{layout_close}
            <Route path="*" element={{<Navigate to="/" replace />}} />
          </Routes>
      {app_wrapper_end}
    </ThemeProvider>
  )
}}
"""

    @staticmethod
    def generate_route_types(pages: List[Dict]) -> str:
        """Generate TypeScript types for routes"""
        routes_type = [f"  | '{page.get('route', '/')}'" for page in pages]
        return f"""// Auto-generated route types
export type AppRoute =
{chr(10).join(routes_type)};

export interface RouteConfig {{
  path: AppRoute;
  title: string;
  requiresAuth: boolean;
  component: React.ComponentType;
}}
"""