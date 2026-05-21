#!/usr/bin/env python3
"""
NOVARYX - Surgical Project Updater & Repair Loop
Directly updates an existing generated project based on user feedback or error logs.
"""

import sys
import time
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Force UTF-8 for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

sys.path.insert(0, str(Path(__file__).parent))

# Load .env variables
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)
except ImportError:
    _env_path = Path(__file__).parent / ".env"
    if _env_path.exists():
        import os
        for line in _env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() not in os.environ:
                    os.environ[k.strip()] = v.strip()

from system.inference.provider_factory import get_provider_for_role
from system.generation.llm_page_generator import LLMPageGenerator
from system.repair.surgical_repair import SurgicalRepairOrchestrator, RepairBudget

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("novaryx.update")

def _emit_stream(msg: str):
    print(f"STREAM_TOKEN: {msg}", flush=True)

def _emit_telemetry(module_id: str, status: str, trust: float = 1.0):
    payload = {
        "type": "telemetry",
        "module": module_id,
        "status": status,
        "trust": trust
    }
    print(f"STREAM_TOKEN: {json.dumps(payload)}", flush=True)

class ProjectUpdater:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir).resolve()
        if not self.project_dir.exists():
            raise FileNotFoundError(f"Project folder not found: {self.project_dir}")
        
        self.page_generator = LLMPageGenerator()
        self.surgical_repair = SurgicalRepairOrchestrator(
            budget=RepairBudget(
                max_files=10,
                max_llm_calls=0,
                max_time_sec=20.0,
                accept_threshold=0.90
            ),
            enable_llm=False
        )

    def scan_files(self) -> Dict[str, str]:
        """Read all relevant source files from the project."""
        files = {}
        exclude_dirs = {
            "node_modules", "dist", "build", ".next", ".git", "venv", ".idea", 
            "__pycache__", "archives", "public", ".github", "snapshots"
        }
        allowed_extensions = {".tsx", ".ts", ".css", ".js", ".jsx", ".html", ".json"}
        
        for path in self.project_dir.rglob("*"):
            if any(part in path.parts for part in exclude_dirs):
                continue
            if path.is_file() and path.suffix in allowed_extensions:
                # Get path relative to project root
                rel_path = path.relative_to(self.project_dir).as_posix()
                try:
                    content = path.read_text(encoding="utf-8")
                    files[rel_path] = content
                except Exception as e:
                    logger.debug(f"Skipping file {rel_path} due to read error: {e}")
        return files

    def run_update(self, prompt: str) -> bool:
        start_time = time.time()
        _emit_stream("Scanning existing project files...")
        
        project_files = self.scan_files()
        if not project_files:
            _emit_stream("❌ Error: No editable files found in project directory!")
            return False

        file_list_str = "\n".join([f"- {path}" for path in project_files.keys()])
        _emit_stream(f"Found {len(project_files)} editable files in project.")

        # ── Step 1: LLM Routing Pass ──
        # Ask LLM which files need to be modified or if new files need to be created
        _emit_stream("Phase 1: Routing update instructions to target modules...")
        try:
            planner = get_provider_for_role("planning")
        except Exception as e:
            _emit_stream("❌ Error: No cognitive provider available for planning.")
            return False

        system_prompt = """You are the Senior Technical Architect at NOVARYX.
Your task is to analyze the user's update request / error log, look at the list of files in the project, and decide:
1. Which existing files MUST be modified.
2. Which new files (if any) need to be created.

You MUST respond ONLY with a valid JSON object of this structure:
{
  "files_to_modify": ["relative/path/to/file1.tsx", ...],
  "files_to_create": [{"path": "relative/path/to/newfile.tsx", "description": "purpose/contents"}]
}

Ensure the paths are strictly from the project's file list or logical new directories (like src/components/NewCard.tsx). Do not guess file locations.
Do NOT output any markdown tags (like ```json), commentary, or reasoning. Output only the raw JSON string."""

        user_prompt = f"""Target Project Files:
{file_list_str}

User's Update Request / Error Log:
"{prompt}"

Analyze the request and output the JSON mapping."""

        _emit_stream("Analyzing request with Ollama/Groq...")
        result = planner.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            role="planning",
            temperature=0.1
        )

        plan_json = {}
        if result.success and result.text:
            text = result.text.strip()
            # Clean possible markdown block wrapping
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\n?", "", text)
                text = re.sub(r"\n?```$", "", text)
            text = text.strip()
            
            try:
                plan_json = json.loads(text)
            except Exception as e:
                logger.warning(f"Failed to parse LLM planning JSON: {e}. Output was: {text}")
                # Fallback heuristic: Try to match paths manually or default to all TSX pages
                plan_json = {
                    "files_to_modify": [f for f in project_files.keys() if "src/pages" in f or "src/components" in f],
                    "files_to_create": []
                }
        else:
            _emit_stream("⚠️ Planning fallback activated due to model empty response.")
            plan_json = {
                "files_to_modify": [f for f in project_files.keys() if "src/pages" in f or "src/components" in f],
                "files_to_create": []
            }

        modify_list = plan_json.get("files_to_modify", [])
        create_list = plan_json.get("files_to_create", [])

        # Filter modify_list to make sure they exist
        modify_list = [f for f in modify_list if f in project_files]

        if not modify_list and not create_list:
            _emit_stream("⚠️ No target files identified for update. Defaulting to main pages.")
            modify_list = [f for f in project_files.keys() if "App.tsx" in f or "src/pages/Home.tsx" in f]

        _emit_stream(f"Routing decisions:")
        for f in modify_list:
            _emit_stream(f"  👉 Modify: {f}")
        for f in create_list:
            _emit_stream(f"  🆕 Create: {f.get('path')}")

        # ── Step 2: Surgically modify files ──
        updated_files = dict(project_files)
        
        try:
            generator = get_provider_for_role("generation")
        except Exception as e:
            _emit_stream("❌ Error: No generator provider available.")
            return False

        # Phase 6: Page Generation / Modification
        _emit_stream("Phase 6: Surgically modifying existing files...")
        
        for file_path in modify_list:
            _emit_stream(f"Modifying {file_path}...")
            _emit_telemetry(file_path, "generating")
            
            original_code = project_files[file_path]
            
            # Context-budgeted surgical prompt
            mod_sys_prompt = """You are a Principal Frontend Developer at NOVARYX.
Your task is to modify the existing TSX or code file to implement the requested upgrades, layout enhancements, or error fixes.
STRICTLY follow these requirements:
1. Only modify the areas required to satisfy the user's prompt.
2. PRESERVE all existing imports, contexts, theme customizers, framer-motion animations, and layouts unless they are the direct target of the change.
3. Keep the file compiled and clean. No incomplete JSX, stray closing tags, or broken brackets.
4. Output the COMPLETE updated file. Do NOT use placeholders, '// rest of the code', or ellipsis.
5. Response MUST be only the raw code block without any prefix explanation or markdown code fences (no ```tsx).
6. Every list map item MUST have a unique 'key={item.id}' or similar. Use design-token variables (var(--primary)) for styling."""

            mod_user_prompt = f"""Existing File Content ({file_path}):
```tsx
{original_code}
```

User's Change/Fix Request:
"{prompt}"

Output the complete, updated file content below:"""

            result = generator.generate(
                prompt=mod_user_prompt,
                system_prompt=mod_sys_prompt,
                role="generation",
                temperature=0.3,
                max_tokens=4096
            )

            if result.success and result.text and len(result.text.strip()) > 100:
                cleaned_code = self.page_generator._clean_llm_output(result.text)
                updated_files[file_path] = cleaned_code
                _emit_telemetry(file_path, "validating")
                _emit_stream(f"✅ Modified {file_path}")
            else:
                _emit_stream(f"❌ Failed to modify {file_path}. Keeping original.")
                _emit_telemetry(file_path, "failed")

        # ── Step 3: Create new files ──
        if create_list:
            _emit_stream("Generating new components/modules...")
            for new_file in create_list:
                f_path = new_file.get("path")
                f_desc = new_file.get("description", "New component")
                if not f_path:
                    continue
                
                _emit_stream(f"Creating {f_path}...")
                _emit_telemetry(f_path, "generating")

                create_sys_prompt = """You are a Principal Frontend Developer at NOVARYX.
Generate a high-quality React TSX component or helper file based on the description.
Use modern aesthetics, Tailwind CSS, and Framer Motion. Close all tags.
Output ONLY the raw code, no fences, no commentary."""

                create_user_prompt = f"""Create file: {f_path}
Description: {f_desc}
Context/Prompt: "{prompt}"

Output the complete file content:"""

                result = generator.generate(
                    prompt=create_user_prompt,
                    system_prompt=create_sys_prompt,
                    role="generation",
                    temperature=0.4,
                    max_tokens=4096
                )

                if result.success and result.text:
                    cleaned_code = self.page_generator._clean_llm_output(result.text)
                    updated_files[f_path] = cleaned_code
                    _emit_telemetry(f_path, "validating")
                    _emit_stream(f"✅ Created {f_path}")
                else:
                    _emit_stream(f"❌ Failed to generate {f_path}")
                    _emit_telemetry(f_path, "failed")

        # ── Step 4: Run Surgical Repair and Validation ──
        _emit_stream("Phase 10: Running surgical repair and final validation...")
        
        # Get list of files that were actually modified or created
        changed_paths = set(modify_list) | {f.get("path") for f in create_list if f.get("path")}
        
        # We run the repair on all updated files
        repair_result = self.surgical_repair.repair(
            files=updated_files,
            frozen=set(project_files.keys()) - changed_paths, # Freeze unchanged files
            telemetry_callback=_emit_telemetry
        )

        final_files = repair_result.repaired_files
        _emit_stream("Phase 10: Surgical repair and validation complete.")

        # ── Step 5: Save files back to disk ──
        _emit_stream("Writing updated files to project folder...")
        written_count = 0
        for path_key, content in final_files.items():
            # Only write if file was changed
            if path_key in changed_paths or (path_key not in project_files) or (content != project_files.get(path_key)):
                full_path = self.project_dir / path_key
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
                written_count += 1
                logger.info(f"Updated file saved: {path_key}")

        total_time = time.time() - start_time
        _emit_stream(f"Project update complete! Modified {written_count} files in {total_time:.1f}s.")

        # ── Step 6: Output structured JSON result ──
        result_json = {
            "success": True,
            "project_name": self.project_dir.name,
            "files": list(final_files.keys()),
            "components": list(changed_paths),
            "componentCount": len(changed_paths),
            "pages": len([f for f in changed_paths if "src/pages" in f]),
            "bugs_fixed": repair_result.bugs_fixed,
            "export_path": str(self.project_dir),
            "errors": []
        }
        print("GENERATION_RESULT: " + json.dumps(result_json), flush=True)
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="NOVARYX - Project Updater")
    parser.add_argument("prompt", help="Feedback or error description")
    parser.add_argument("--project-dir", "-d", required=True, help="Absolute path to target project directory")
    
    args = parser.parse_args()
    
    try:
        updater = ProjectUpdater(args.project_dir)
        success = updater.run_update(args.prompt)
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Update failed: {e}", exc_info=True)
        print("GENERATION_RESULT: " + json.dumps({
            "success": False,
            "project_name": Path(args.project_dir).name,
            "files": [],
            "components": [],
            "errors": [str(e)]
        }), flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
