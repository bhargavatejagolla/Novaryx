"""
NOVARYX - Project Exporter
Complete export orchestrator. Produces everything needed to ship.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .zip_packager import ZipPackager
from .docker_packager import DockerPackager
from .deploy_configs import DeployConfigGenerator
from .run_scripts import RunScriptGenerator
from system.intelligence.dependency_governor import DependencyGovernor

logger = logging.getLogger("novaryx.exporter")


@dataclass
class ExportResult:
    """Complete export result"""
    project_name: str
    export_dir: str
    files_written: int
    zip_path: Optional[str] = None
    docker_ready: bool = False
    deploy_configs: list = field(default_factory=list)
    exported_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ProjectExporter:
    """
    Complete project export pipeline.
    
    Produces:
      - Full project directory
      - ZIP archive
      - Docker files
      - Deployment configs
      - Run scripts
      - Setup guide
    """
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = str(Path.home() / "novaryx" / "exports")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.zip_packager = ZipPackager(str(self.output_dir / "archives"))
        self.docker_packager = DockerPackager()
        self.deploy_gen = DeployConfigGenerator()
        self.script_gen = RunScriptGenerator()
        self.dependency_governor = DependencyGovernor()
    
    def export(
        self,
        files: Dict[str, str],
        project_name: str,
        has_backend: bool = False,
        create_zip: bool = True
    ) -> ExportResult:
        """
        Complete export of a generated project.
        
        Args:
            files: All project files
            project_name: Project name
            has_backend: Whether backend is included
            create_zip: Whether to create ZIP archive
        
        Returns:
            ExportResult with all output paths
        """
        
        print("\n" + "=" * 60)
        print("📦 PROJECT EXPORTER")
        print("=" * 60)
        print(f"   Project: {project_name}")
        print(f"   Files: {len(files)}")
        print(f"   Backend: {'Yes' if has_backend else 'No'}")
        print(f"   ZIP: {'Yes' if create_zip else 'No'}")
        
        # Step 0: Autonomous Dependency Governance (Ecosystem Repair)
        print(f"\n   Running Dependency Governance Pass...")
        # Determine stack based on files (heuristic)
        project_type = "nextjs" if "next.config.js" in files else "vite_react"
        files = self.dependency_governor.govern_project(files, project_type)
        print(f"   ✅ Integrity check complete")
        
        slug = project_name.lower().replace(" ", "-")
        project_dir = self.output_dir / slug
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Write all files to project directory
        print(f"\n   Writing project files...")
        written = 0
        for filepath, content in files.items():
            full_path = project_dir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            written += 1
        print(f"   ✅ {written} files written")
        
        # Step 2: Generate Docker files
        print(f"\n   Generating Docker config...")
        docker_files = {
            "Dockerfile": self.docker_packager.generate_dockerfile(project_name, has_backend),
            ".dockerignore": self.docker_packager.generate_dockerignore(),
            "docker-compose.yml": self.docker_packager.generate_docker_compose(project_name, has_backend),
            "deploy.sh": self.docker_packager.generate_deploy_script(project_name),
        }
        
        for fname, content in docker_files.items():
            fpath = project_dir / fname
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
        
        if has_backend:
            deploy_sh = project_dir / "deploy.sh"
            if deploy_sh.exists():
                deploy_sh.chmod(0o755)
        
        print(f"   ✅ Docker config generated")
        
        # Step 3: Generate deployment configs
        print(f"\n   Generating deployment configs...")
        deploy_configs = self.deploy_gen.generate_all_configs(project_name, has_backend)
        
        for fname, content in deploy_configs.items():
            fpath = project_dir / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
        
        deploy_names = list(deploy_configs.keys())
        print(f"   ✅ {len(deploy_names)} configs: {', '.join(deploy_names)}")
        
        # Step 4: Generate run scripts
        print(f"\n   Generating run scripts...")
        scripts = self.script_gen.generate_all_scripts(project_name, has_backend)
        
        for fname, content in scripts.items():
            fpath = project_dir / fname
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
        
        # Make .sh executable
        run_sh = project_dir / "run.sh"
        if run_sh.exists():
            run_sh.chmod(0o755)
        
        print(f"   ✅ Scripts: {', '.join(scripts.keys())}")
        
        # Step 5: Create ZIP archive
        zip_path = None
        if create_zip:
            print(f"\n   Creating ZIP archive...")
            zip_path = self.zip_packager.create_zip_from_dir(str(project_dir))
        
        # Step 6: Generate .gitignore if not present
        gitignore_path = project_dir / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w") as f:
                f.write("""node_modules/
dist/
.env
.env.local
*.log
.DS_Store
""")
        
        # Summary
        total_files = written + len(docker_files) + len(deploy_configs) + len(scripts)
        
        print(f"\n" + "=" * 60)
        print(f"✅ EXPORT COMPLETE")
        print(f"=" * 60)
        print(f"   Project: {project_dir}")
        print(f"   Files: {total_files}")
        print(f"   ZIP: {zip_path or 'Skipped'}")
        print(f"   Docker: Ready")
        print(f"   Deploy: {', '.join(deploy_names)}")
        print(f"")
        print(f"   Quick start:")
        print(f"   cd {project_dir}")
        print(f"   run.bat    (Windows)")
        print(f"   ./run.sh   (Mac/Linux)")
        print(f"   docker-compose up -d")
        print("=" * 60 + "\n")
        
        return ExportResult(
            project_name=project_name,
            export_dir=str(project_dir),
            files_written=total_files,
            zip_path=zip_path,
            docker_ready=True,
            deploy_configs=deploy_names,
        )


# ---- Quick export ----

def export_project(files: Dict[str, str], project_name: str, has_backend: bool = False) -> ExportResult:
    """Quick project export"""
    exporter = ProjectExporter()
    return exporter.export(files, project_name, has_backend)


# ---- Test ----

def test_exporter():
    """Test the project exporter"""
    
    print("\n" + "=" * 60)
    print("🧪 PROJECT EXPORTER TEST")
    print("=" * 60)
    
    # Create test files
    test_files = {
        "src/App.tsx": "export default function App() { return <div>Hello</div>; }",
        "src/main.tsx": "import App from './App';",
        "index.html": "<!DOCTYPE html><html><body><div id='root'></div></body></html>",
        "package.json": '{"name":"test","scripts":{"dev":"vite","build":"vite build"}}',
        "tsconfig.json": '{"compilerOptions":{"jsx":"react-jsx"}}',
        "vite.config.js": "export default { plugins: [] }",
        "src/styles/tokens.css": ":root { --primary: #7c3aed; --background: #0f0f1a; }",
    }
    
    exporter = ProjectExporter()
    result = exporter.export(
        files=test_files,
        project_name="TestExportApp",
        has_backend=False,
        create_zip=True
    )
    
    print(f"\n   Export dir: {result.export_dir}")
    print(f"   Files: {result.files_written}")
    print(f"   ZIP: {result.zip_path}")
    print(f"   Docker: {result.docker_ready}")
    print(f"   Configs: {result.deploy_configs}")
    
    print("\n✅ Project Exporter test complete")
    
    return result


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    test_exporter()