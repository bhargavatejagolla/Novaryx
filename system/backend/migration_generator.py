"""
NOVARYX - Migration Generator
Generates PocketBase initial migration scripts.
"""

import json


class MigrationGenerator:
    """Generates PocketBase migrations"""
    
    @staticmethod
    def generate_initial_migration(collections: list) -> str:
        """Generate the first schema migration script"""
        c_json = json.dumps(collections, indent=8)
        return f"""migrate((db) => {{
  const collections = {c_json};
  for (const c of collections) {{
    const col = new Collection({{ ...c }});
    dao.saveCollection(col);
  }}
}}, (db) => {{
  const collections = {c_json};
  for (const c of collections) {{
    const col = dao.findCollectionByNameOrId(c.name);
    if (col) dao.deleteCollection(col);
  }}
}})"""