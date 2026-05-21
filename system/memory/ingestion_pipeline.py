"""
NOVARYX - Ingestion Pipeline
Analyzes raw components, documents them using an LLM, and indexes them into ChromaDB for continuous learning.
"""

import os
import glob
import logging
from typing import List, Dict, Any
import json
import requests
import chromadb
from groq import Groq

logger = logging.getLogger("novaryx.ingestion")

class IngestionPipeline:
    """Handles parsing, analyzing, and indexing new components into NOVARYX memory."""

    def __init__(self, chroma_path: str = None):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model_name = "llama-3.3-70b-versatile"
        
        db_path = chroma_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "rag_engine", "chromadb")
        self.chroma = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma.get_or_create_collection(
            name="novaryx_components",
            metadata={"hnsw:space": "cosine"}
        )

    def ingest_directory(self, dir_path: str) -> List[Dict[str, Any]]:
        """Scans a directory for TSX/CSS files and ingests them."""
        results = []
        search_pattern = os.path.join(dir_path, "**", "*.[t|j]sx")
        files = glob.glob(search_pattern, recursive=True)
        
        logger.info(f"Found {len(files)} components to ingest from {dir_path}")
        
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_name = os.path.basename(file_path)
            comp_name = os.path.splitext(file_name)[0]
            
            result = self.ingest_component(comp_name, content, source_path=file_path)
            if result:
                results.append(result)
                
        return results

    def ingest_component(self, name: str, code: str, css: str = "", source_path: str = "") -> Dict[str, Any]:
        """Analyzes and indexes a single component."""
        logger.info(f"Ingesting component: {name}")
        
        # 1. Analyze with LLM
        analysis = self._analyze_component(name, code, css)
        if not analysis:
            logger.error(f"Failed to analyze component {name}")
            return None

        # 2. Combine into a comprehensive document
        document = f"COMPONENT: {name}\n\nDESCRIPTION:\n{analysis['description']}\n\nPROPS:\n{analysis['props']}\n\nTAGS: {', '.join(analysis['tags'])}\n\nCODE:\n```tsx\n{code}\n```"
        if css:
            document += f"\n\nCSS:\n```css\n{css}\n```"

        # 3. Store in ChromaDB
        metadata = {
            "type": "component",
            "name": name,
            "description": analysis["description"],
            "source": source_path or "manual_ingestion",
            "tags": ",".join(analysis["tags"])
        }
        
        # Generate an ID
        doc_id = f"comp_{name.lower().replace(' ', '_')}_{hash(code) % 10000}"
        
        try:
            self.collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.info(f"Successfully indexed component {name} into ChromaDB.")
            
            return {
                "id": doc_id,
                "name": name,
                "metadata": metadata,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Failed to index {name} into ChromaDB: {e}")
            return None

    def _analyze_component(self, name: str, code: str, css: str) -> Dict[str, Any]:
        """Uses Groq to analyze the component and extract metadata."""
        if not os.environ.get("GROQ_API_KEY"):
            logger.warning("No GROQ_API_KEY found, returning basic metadata.")
            return {
                "description": f"Custom component {name}",
                "props": "Unknown",
                "tags": [name.lower()]
            }

        prompt = f"""Analyze this React component and provide a JSON response.
Component Name: {name}

CODE:
```tsx
{code}
```

Return ONLY a raw JSON object with the following schema:
{{
    "description": "A 2-3 sentence description of what this component does and how it looks.",
    "props": "A brief explanation of the props it accepts.",
    "tags": ["tag1", "tag2", "tag3", "ui", "react"] // 5-8 relevant searchable tags
}}"""

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert React architect analyzing code."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "description": f"Component {name}",
                "props": "Unknown",
                "tags": [name.lower()]
            }

# --- Quick Test ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = IngestionPipeline()
    # pipeline.ingest_directory("./my_components")
