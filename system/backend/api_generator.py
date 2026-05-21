"""
NOVARYX - API Generator
Generates API documentation and endpoint metadata.
"""

class APIGenerator:
    """Generates API documentation from collections"""
    
    @staticmethod
    def generate_api_docs(collections: list, app_name: str) -> str:
        """Generate markdown documentation for the API"""
        lines = [f"# {app_name} API Documentation\n", "## Collections\n"]
        for c in collections:
            lines.append(f"\n### {c['name']}")
            lines.append(f"- Type: {c.get('type', 'base')}")
            lines.append(f"- Fields: {len(c.get('schema', []))}")
            for f in c.get('schema', []):
                lines.append(f"  - `{f['name']}` ({f['type']})")
            lines.append(f"\n**Endpoints:**")
            lines.append(f"- `GET /api/collections/{c['name']}/records`")
            lines.append(f"- `GET /api/collections/{c['name']}/records/:id`")
            if c.get('createRule'): lines.append(f"- `POST /api/collections/{c['name']}/records`")
            if c.get('updateRule'): lines.append(f"- `PATCH /api/collections/{c['name']}/records/:id`")
            if c.get('deleteRule'): lines.append(f"- `DELETE /api/collections/{c['name']}/records/:id`")
        return "\n".join(lines)
    
    @staticmethod
    def extract_endpoints(collections: list) -> list:
        """Extract endpoint metadata for consumption elsewhere"""
        endpoints = []
        for c in collections:
            base = f"/api/collections/{c['name']}/records"
            endpoints.append({"method": "GET", "path": base})
            endpoints.append({"method": "GET", "path": f"{base}/:id"})
            if c.get('createRule'): endpoints.append({"method": "POST", "path": base})
            if c.get('updateRule'): endpoints.append({"method": "PATCH", "path": f"{base}/:id"})
            if c.get('deleteRule'): endpoints.append({"method": "DELETE", "path": f"{base}/:id"})
        return endpoints
