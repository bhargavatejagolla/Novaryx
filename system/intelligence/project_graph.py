"""
NOVARYX - Project Graph Analyzer (Phase 1)
Builds an internal representation of the entire existing codebase.
Maps routing architecture, APIs, components, and dependencies.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Set

logger = logging.getLogger("novaryx.project_graph")


class ProjectGraphAnalyzer:
    """
    Analyzes an existing Next.js / React project.
    Builds a structured graph of:
    - Routes
    - APIs
    - Components
    - Dependencies
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.app_dir = self.src_dir / "app"
        self.components_dir = self.src_dir / "components"
        self.api_dir = self.app_dir / "api"
        
        self.graph = {
            "routes": [],
            "apis": [],
            "components": [],
            "package_dependencies": {}
        }

    def analyze(self) -> Dict[str, Any]:
        """Perform full analysis and return the graph."""
        logger.info(f"Starting Project Graph Analysis at {self.project_root}")
        
        if not self.project_root.exists():
            logger.warning("Project root does not exist.")
            return self.graph

        self._analyze_package_json()
        self._analyze_routes()
        self._analyze_apis()
        self._analyze_components()
        
        logger.info(f"Analysis complete. Found {len(self.graph['routes'])} routes, {len(self.graph['apis'])} APIs.")
        return self.graph
        
    def _analyze_package_json(self):
        """Parse package.json for dependencies."""
        pkg_path = self.project_root / "package.json"
        if pkg_path.exists():
            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    self.graph["package_dependencies"] = {**deps, **dev_deps}
            except Exception as e:
                logger.error(f"Error parsing package.json: {e}")

    def _analyze_routes(self):
        """Walk the app directory to find page.tsx files."""
        if not self.app_dir.exists():
            return
            
        for root, _, files in os.walk(self.app_dir):
            if "api" in root.split(os.sep):
                continue  # Skip API routes here
                
            for file in files:
                if file in ["page.tsx", "page.jsx"]:
                    rel_path = os.path.relpath(root, self.app_dir)
                    route = "/" if rel_path == "." else f"/{rel_path.replace(os.sep, '/')}"
                    self.graph["routes"].append({
                        "route": route,
                        "file_path": str(Path(root) / file),
                        "has_layout": (Path(root) / "layout.tsx").exists()
                    })

    def _analyze_apis(self):
        """Walk the app/api directory to find route.ts files."""
        if not self.api_dir.exists():
            return
            
        for root, _, files in os.walk(self.api_dir):
            for file in files:
                if file in ["route.ts", "route.js"]:
                    rel_path = os.path.relpath(root, self.app_dir)
                    route = f"/{rel_path.replace(os.sep, '/')}"
                    self.graph["apis"].append({
                        "route": route,
                        "file_path": str(Path(root) / file)
                    })

    def _analyze_components(self):
        """Walk the components directory to find reusable UI components."""
        if not self.components_dir.exists():
            return
            
        for root, _, files in os.walk(self.components_dir):
            for file in files:
                if file.endswith((".tsx", ".jsx")):
                    rel_path = os.path.relpath(Path(root) / file, self.components_dir)
                    self.graph["components"].append({
                        "name": Path(file).stem,
                        "path": str(rel_path)
                    })
                    
    def export_graph(self, output_path: str = None) -> str:
        """Export the graph as JSON string, optionally saving to a file."""
        out_json = json.dumps(self.graph, indent=2)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(out_json)
        return out_json


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = ProjectGraphAnalyzer("../../novaryx-web")
    graph = analyzer.analyze()
    print(json.dumps(graph, indent=2))
