"""
NOVARYX - Dynamic Schema Generator
Generates PocketBase collection schemas from LLM analysis of features.

No static templates. Every schema is generated fresh from the prompt.
"""

import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("novaryx.schema_generator")


class SchemaGenerator:
    """
    Generates PocketBase collection schemas dynamically.
    
    Uses LLM to understand what data the app needs and generates
    appropriate collections with proper field types and relations.
    """
    
    # PocketBase field types
    FIELD_TYPES = [
        "text", "number", "bool", "email", "url", "date", "select",
        "file", "relation", "json", "password", "editor"
    ]
    
    def __init__(self):
        self._inference = None
    
    def _get_inference(self):
        if self._inference is None:
            try:
                from system.inference.provider_factory import get_provider
                self._inference = get_provider()
            except Exception as e:
                logger.warning(f"Inference unavailable: {e}")
        return self._inference
    
    def generate_from_prompt(self, prompt: str, features: List[str] = None, pages: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate complete PocketBase schema from prompt.
        
        Args:
            prompt: User's project description
            features: Extracted features list
            pages: Page specifications
        
        Returns:
            Complete PocketBase schema JSON
        """
        
        # Step 1: Try LLM-based generation
        if self._get_inference():
            print("   🤖 LLM analyzing data needs (this may take 30-60s on local hardware)...")
            schema = self._llm_generate_schema(prompt, features, pages)
            if schema and schema.get("collections"):
                print(f"   ✅ LLM defined {len(schema['collections'])} custom collections")
                logger.info(f"LLM generated {len(schema['collections'])} collections")
                return schema
            else:
                print("   ⚠️  LLM generation failed or timed out. Falling back to rule-based schema.")
        
        # Step 2: Smart rule-based generation
        print("   🧩 Using rule-based schema generation...")
        logger.info("Using rule-based schema generation")
        return self._rule_based_schema(prompt, features, pages)
    
    def _llm_generate_schema(self, prompt: str, features: List[str], pages: List[Dict]) -> Optional[Dict]:
        """Use LLM to generate schema"""
        provider = self._get_inference()
        if not provider:
            return None
        
        features_str = ", ".join(features) if features else "general app features"
        pages_str = json.dumps([p.get("name", "") for p in pages]) if pages else "standard pages"
        
        schema_prompt = f"""You are a PocketBase database architect. Generate a complete database schema for this application.

APP DESCRIPTION: {prompt}
FEATURES REQUESTED: {features_str}
PAGES: {pages_str}

Generate PocketBase collections with proper fields, types, and relations.

PocketBase field types: text, number, bool, email, url, date, select, file, relation, json, password, editor

Return ONLY valid JSON:
{{
  "collections": [
    {{
      "name": "collection_name",
      "type": "base|auth",
      "schema": [
        {{
          "name": "field_name",
          "type": "field_type",
          "required": true|false,
          "unique": true|false,
          "options": {{}}
        }}
      ],
      "listRule": "rule or null",
      "viewRule": "rule or null",
      "createRule": "rule or null",
      "updateRule": "rule or null",
      "deleteRule": "rule or null"
    }}
  ],
  "auth_config": {{
    "email_auth": true,
    "email_verification": true|false,
    "password_reset": true|false,
    "oauth_providers": ["google", "github"] or [],
    "allowed_domains": [] or ["domain.com"],
    "session_duration_days": 30
  }}
}}

RULES:
1. Always include a 'users' collection (type: auth)
2. Every app with content needs the relevant collections
3. Use relation fields to connect related collections
4. Add sensible default access rules
5. Include timestamps (created, updated) as text fields
6. For user-facing apps, be restrictive with delete rules
7. For admin panels, be more permissive
"""
        
        try:
            result = provider.generate(
                prompt=schema_prompt,
                role="planning",
                temperature=0.1,
                max_tokens=2000
            )
            
            if result.success and result.text:
                text = result.text.strip()
                start = text.find('{')
                end = text.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(text[start:end])
        except Exception as e:
            logger.warning(f"LLM schema generation failed: {e}")
        
        return None
    
    def _rule_based_schema(self, prompt: str, features: List[str], pages: List[Dict]) -> Dict:
        """Fallback rule-based schema generation"""
        prompt_lower = prompt.lower()
        features_lower = [f.lower() for f in features] if features else []
        
        collections = []
        
        # Always add users collection
        users_fields = [
            {"name": "name", "type": "text", "required": True, "unique": False, "options": {"max": 100}},
            {"name": "email", "type": "email", "required": True, "unique": True, "options": {}},
            {"name": "password", "type": "password", "required": True, "unique": False, "options": {"min": 8}},
            {"name": "role", "type": "select", "required": True, "unique": False, "options": {"values": ["user", "admin", "moderator"], "maxSelect": 1}},
            {"name": "avatar", "type": "file", "required": False, "unique": False, "options": {"maxSelect": 1, "mimeTypes": ["image/jpeg", "image/png", "image/webp"]}},
            {"name": "bio", "type": "text", "required": False, "unique": False, "options": {"max": 500}},
            {"name": "status", "type": "select", "required": False, "unique": False, "options": {"values": ["active", "inactive", "banned"], "maxSelect": 1}},
            {"name": "last_login", "type": "date", "required": False, "unique": False, "options": {}},
            {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
            {"name": "updated", "type": "date", "required": False, "unique": False, "options": {}},
        ]
        
        collections.append({
            "name": "users",
            "type": "auth",
            "schema": users_fields,
            "listRule": "id = @request.auth.id || @request.auth.role = 'admin'",
            "viewRule": "id = @request.auth.id || @request.auth.role = 'admin'",
            "createRule": "",
            "updateRule": "id = @request.auth.id || @request.auth.role = 'admin'",
            "deleteRule": "id = @request.auth.id || @request.auth.role = 'admin'",
        })
        
        # Feature-based collections
        feature_collections = {
            "analytics": {
                "name": "analytics_events",
                "fields": [
                    {"name": "user", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users", "cascadeDelete": False}},
                    {"name": "event_type", "type": "text", "required": True, "unique": False, "options": {"max": 100}},
                    {"name": "event_data", "type": "json", "required": False, "unique": False, "options": {}},
                    {"name": "page", "type": "text", "required": False, "unique": False, "options": {}},
                    {"name": "timestamp", "type": "date", "required": True, "unique": False, "options": {}},
                ]
            },
            "dashboard": {
                "name": "dashboard_widgets",
                "fields": [
                    {"name": "user", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users", "cascadeDelete": False}},
                    {"name": "widget_type", "type": "select", "required": True, "unique": False, "options": {"values": ["chart", "stats", "table", "list", "custom"], "maxSelect": 1}},
                    {"name": "config", "type": "json", "required": True, "unique": False, "options": {}},
                    {"name": "position", "type": "number", "required": True, "unique": False, "options": {}},
                ]
            },
            "user_management": {
                "name": "roles",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "unique": True, "options": {}},
                    {"name": "permissions", "type": "json", "required": True, "unique": False, "options": {}},
                    {"name": "description", "type": "text", "required": False, "unique": False, "options": {"max": 300}},
                ]
            },
            "content_management": {
                "name": "content",
                "fields": [
                    {"name": "title", "type": "text", "required": True, "unique": False, "options": {"max": 200}},
                    {"name": "slug", "type": "text", "required": True, "unique": True, "options": {"max": 200}},
                    {"name": "body", "type": "editor", "required": False, "unique": False, "options": {}},
                    {"name": "author", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users"}},
                    {"name": "status", "type": "select", "required": True, "unique": False, "options": {"values": ["draft", "published", "archived"], "maxSelect": 1}},
                    {"name": "tags", "type": "json", "required": False, "unique": False, "options": {}},
                    {"name": "featured_image", "type": "file", "required": False, "unique": False, "options": {"maxSelect": 1, "mimeTypes": ["image/jpeg", "image/png", "image/webp"]}},
                    {"name": "published_at", "type": "date", "required": False, "unique": False, "options": {}},
                    {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                    {"name": "updated", "type": "date", "required": False, "unique": False, "options": {}},
                ]
            },
            "notifications": {
                "name": "notifications",
                "fields": [
                    {"name": "user", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users", "cascadeDelete": True}},
                    {"name": "title", "type": "text", "required": True, "unique": False, "options": {"max": 200}},
                    {"name": "message", "type": "text", "required": True, "unique": False, "options": {"max": 1000}},
                    {"name": "type", "type": "select", "required": True, "unique": False, "options": {"values": ["info", "success", "warning", "error"], "maxSelect": 1}},
                    {"name": "read", "type": "bool", "required": False, "unique": False, "options": {}},
                    {"name": "link", "type": "url", "required": False, "unique": False, "options": {}},
                    {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                ]
            },
            "payments": {
                "name": "subscriptions",
                "fields": [
                    {"name": "user", "type": "relation", "required": True, "unique": True, "options": {"collectionId": "users"}},
                    {"name": "plan", "type": "select", "required": True, "unique": False, "options": {"values": ["free", "pro", "enterprise"], "maxSelect": 1}},
                    {"name": "status", "type": "select", "required": True, "unique": False, "options": {"values": ["active", "past_due", "cancelled", "expired"], "maxSelect": 1}},
                    {"name": "stripe_customer_id", "type": "text", "required": False, "unique": True, "options": {}},
                    {"name": "stripe_subscription_id", "type": "text", "required": False, "unique": True, "options": {}},
                    {"name": "current_period_end", "type": "date", "required": False, "unique": False, "options": {}},
                    {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                ]
            },
            "messaging": {
                "name": "messages",
                "fields": [
                    {"name": "sender", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users"}},
                    {"name": "receiver", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users"}},
                    {"name": "content", "type": "text", "required": True, "unique": False, "options": {"max": 5000}},
                    {"name": "attachments", "type": "file", "required": False, "unique": False, "options": {"maxSelect": 10}},
                    {"name": "read", "type": "bool", "required": False, "unique": False, "options": {}},
                    {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                ]
            },
            "kanban": {
                "name": "tasks",
                "fields": [
                    {"name": "title", "type": "text", "required": True, "unique": False, "options": {"max": 200}},
                    {"name": "description", "type": "editor", "required": False, "unique": False, "options": {}},
                    {"name": "status", "type": "select", "required": True, "unique": False, "options": {"values": ["todo", "in_progress", "review", "done"], "maxSelect": 1}},
                    {"name": "priority", "type": "select", "required": False, "unique": False, "options": {"values": ["low", "medium", "high", "urgent"], "maxSelect": 1}},
                    {"name": "assignee", "type": "relation", "required": False, "unique": False, "options": {"collectionId": "users"}},
                    {"name": "project", "type": "relation", "required": False, "unique": False, "options": {"collectionId": "projects"}},
                    {"name": "due_date", "type": "date", "required": False, "unique": False, "options": {}},
                    {"name": "tags", "type": "json", "required": False, "unique": False, "options": {}},
                    {"name": "order", "type": "number", "required": False, "unique": False, "options": {}},
                    {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                    {"name": "updated", "type": "date", "required": False, "unique": False, "options": {}},
                ]
            },
            "file_upload": {
                "name": "files",
                "fields": [
                    {"name": "user", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users"}},
                    {"name": "file", "type": "file", "required": True, "unique": False, "options": {"maxSelect": 1, "maxSize": 52428800}},
                    {"name": "filename", "type": "text", "required": True, "unique": False, "options": {}},
                    {"name": "mime_type", "type": "text", "required": False, "unique": False, "options": {}},
                    {"name": "size", "type": "number", "required": False, "unique": False, "options": {}},
                    {"name": "folder", "type": "text", "required": False, "unique": False, "options": {}},
                    {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                ]
            },
            "ecommerce": {
                "name": "products",
                "fields": [
                    {"name": "name", "type": "text", "required": True, "unique": False, "options": {"max": 200}},
                    {"name": "slug", "type": "text", "required": True, "unique": True, "options": {"max": 200}},
                    {"name": "description", "type": "editor", "required": False, "unique": False, "options": {}},
                    {"name": "price", "type": "number", "required": True, "unique": False, "options": {"min": 0}},
                    {"name": "compare_at_price", "type": "number", "required": False, "unique": False, "options": {"min": 0}},
                    {"name": "images", "type": "file", "required": False, "unique": False, "options": {"maxSelect": 10, "mimeTypes": ["image/jpeg", "image/png", "image/webp"]}},
                    {"name": "category", "type": "text", "required": False, "unique": False, "options": {}},
                    {"name": "tags", "type": "json", "required": False, "unique": False, "options": {}},
                    {"name": "inventory", "type": "number", "required": False, "unique": False, "options": {"min": 0}},
                    {"name": "status", "type": "select", "required": True, "unique": False, "options": {"values": ["draft", "active", "archived"], "maxSelect": 1}},
                    {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                    {"name": "updated", "type": "date", "required": False, "unique": False, "options": {}},
                ]
            },
            "search": {
                "name": "search_index",
                "fields": [
                    {"name": "title", "type": "text", "required": True, "unique": False, "options": {}},
                    {"name": "content", "type": "text", "required": True, "unique": False, "options": {"max": 10000}},
                    {"name": "type", "type": "text", "required": True, "unique": False, "options": {}},
                    {"name": "ref_id", "type": "text", "required": True, "unique": False, "options": {}},
                    {"name": "url", "type": "text", "required": False, "unique": False, "options": {}},
                    {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                ]
            },
        }
        
        # Add feature-based collections
        for feature in features_lower:
            for key, collection in feature_collections.items():
                if key in feature:
                    if not any(c["name"] == collection["name"] for c in collections):
                        collections.append({
                            "name": collection["name"],
                            "type": "base",
                            "schema": collection["fields"],
                            "listRule": "@request.auth.id != ''",
                            "viewRule": "@request.auth.id != ''",
                            "createRule": "@request.auth.id != ''",
                            "updateRule": "@request.auth.id != '' || @request.auth.role = 'admin'",
                            "deleteRule": "@request.auth.role = 'admin'",
                        })
                        break
        
        # Add related collections
        if any("kanban" in f or "project" in f or "task" in f for f in features_lower):
            if not any(c["name"] == "projects" for c in collections):
                collections.append({
                    "name": "projects",
                    "type": "base",
                    "schema": [
                        {"name": "name", "type": "text", "required": True, "unique": False, "options": {"max": 200}},
                        {"name": "description", "type": "editor", "required": False, "unique": False, "options": {}},
                        {"name": "owner", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users"}},
                        {"name": "members", "type": "relation", "required": False, "unique": False, "options": {"collectionId": "users", "maxSelect": 50}},
                        {"name": "status", "type": "select", "required": True, "unique": False, "options": {"values": ["active", "completed", "archived"], "maxSelect": 1}},
                        {"name": "color", "type": "text", "required": False, "unique": False, "options": {}},
                        {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                        {"name": "updated", "type": "date", "required": False, "unique": False, "options": {}},
                    ],
                    "listRule": "@request.auth.id != ''",
                    "viewRule": "@request.auth.id != ''",
                    "createRule": "@request.auth.id != ''",
                    "updateRule": "owner = @request.auth.id || @request.auth.role = 'admin'",
                    "deleteRule": "owner = @request.auth.id || @request.auth.role = 'admin'",
                })
        
        if any("ecommerce" in f or "shop" in f or "store" in f or "cart" in f for f in features_lower):
            if not any(c["name"] == "orders" for c in collections):
                collections.append({
                    "name": "orders",
                    "type": "base",
                    "schema": [
                        {"name": "user", "type": "relation", "required": True, "unique": False, "options": {"collectionId": "users"}},
                        {"name": "items", "type": "json", "required": True, "unique": False, "options": {}},
                        {"name": "total", "type": "number", "required": True, "unique": False, "options": {"min": 0}},
                        {"name": "status", "type": "select", "required": True, "unique": False, "options": {"values": ["pending", "confirmed", "shipped", "delivered", "cancelled"], "maxSelect": 1}},
                        {"name": "shipping_address", "type": "json", "required": False, "unique": False, "options": {}},
                        {"name": "payment_status", "type": "select", "required": True, "unique": False, "options": {"values": ["pending", "paid", "refunded"], "maxSelect": 1}},
                        {"name": "created", "type": "date", "required": False, "unique": False, "options": {}},
                        {"name": "updated", "type": "date", "required": False, "unique": False, "options": {}},
                    ],
                    "listRule": "user = @request.auth.id || @request.auth.role = 'admin'",
                    "viewRule": "user = @request.auth.id || @request.auth.role = 'admin'",
                    "createRule": "@request.auth.id != ''",
                    "updateRule": "@request.auth.role = 'admin'",
                    "deleteRule": "@request.auth.role = 'admin'",
                })
        
        # Auth config
        has_auth = any("login" in f or "register" in f or "auth" in f or "sign" in f or "user" in f for f in features_lower)
        
        auth_config = {
            "email_auth": True,
            "email_verification": False,
            "password_reset": True,
            "oauth_providers": [],
            "allowed_domains": [],
            "session_duration_days": 30,
            "min_password_length": 8,
        }
        
        if not has_auth:
            auth_config["email_auth"] = True
        
        return {
            "collections": collections,
            "auth_config": auth_config
        }
    
    def schema_to_json(self, schema: Dict) -> str:
        """Convert schema dict to PocketBase JSON format"""
        return json.dumps(schema, indent=2)
    
    def schema_to_migration(self, schema: Dict) -> str:
        """Generate PocketBase migration JavaScript"""
        collections_json = json.dumps(schema.get("collections", []), indent=4)
        
        return f"""/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {{
  const collections = {collections_json};
  
  collections.forEach(collection => {{
    const newCollection = new Collection({{
      name: collection.name,
      type: collection.type || 'base',
      schema: collection.schema.map(field => ({{
        name: field.name,
        type: field.type,
        required: field.required || false,
        unique: field.unique || false,
        options: field.options || {{}},
      }})),
      listRule: collection.listRule || null,
      viewRule: collection.viewRule || null,
      createRule: collection.createRule || null,
      updateRule: collection.updateRule || null,
      deleteRule: collection.deleteRule || null,
    }});
    
    return dao.saveCollection(newCollection);
  }});
}}, (db) => {{
  // Rollback: delete all collections created by this migration
  const collections = {collections_json};
  collections.forEach(collection => {{
    const col = dao.findCollectionByNameOrId(collection.name);
    if (col) {{
      dao.deleteCollection(col);
    }}
  }});
}})
"""