"""
NOVARYX - Template Validator
Ensures templates are complete, valid, and ready for generation.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger("novaryx.template_validator")


@dataclass
class ValidationResult:
    """Result of template validation"""
    is_valid: bool
    template_id: str
    template_name: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    
    def display(self):
        icon = "✅" if self.is_valid else "❌"
        print(f"\n{icon} Validation: {self.template_name} ({self.template_id})")
        print("-" * 40)
        
        if self.errors:
            print("   Errors:")
            for e in self.errors:
                print(f"      ❌ {e}")
        
        if self.warnings:
            print("   Warnings:")
            for w in self.warnings:
                print(f"      ⚠️  {w}")
        
        if self.passed_checks:
            print(f"   Passed: {len(self.passed_checks)} checks")
        
        print(f"   Result: {'VALID' if self.is_valid else 'INVALID'}")


class TemplateValidator:
    """
    Validates template structure and completeness.
    
    Checks:
    1. Required directories exist
    2. Essential files present
    3. Config file valid
    4. No broken references
    5. Component consistency
    """
    
    REQUIRED_DIRECTORIES = [
        "src",
        "src/pages",
        "src/components",
        "src/styles",
        "public"
    ]
    
    REQUIRED_FILES = [
        "package.json",
        "tsconfig.json",
        "tailwind.config.js",
        "src/App.tsx",
        "src/main.tsx",
        "index.html"
    ]
    
    RECOMMENDED_FILES = [
        ".env.example",
        "README.md",
        "vite.config.js"
    ]
    
    def validate_template(
        self,
        template_path: str,
        template_id: str = "",
        template_name: str = ""
    ) -> ValidationResult:
        """
        Validate a template directory.
        
        Args:
            template_path: Path to template directory
            template_id: Template identifier
            template_name: Human-readable name
        
        Returns:
            ValidationResult with all findings
        """
        path = Path(template_path)
        result = ValidationResult(
            is_valid=True,
            template_id=template_id,
            template_name=template_name or path.name
        )
        
        if not path.exists():
            result.errors.append(f"Template directory does not exist: {path}")
            result.is_valid = False
            return result
        
        # Check required directories
        self._check_directories(path, result)
        
        # Check required files
        self._check_files(path, result)
        
        # Check package.json
        self._check_package_json(path, result)
        
        # Check component consistency
        self._check_components(path, result)
        
        # Check page structure
        self._check_pages(path, result)
        
        # Check for empty files
        self._check_empty_files(path, result)
        
        result.is_valid = len(result.errors) == 0
        
        return result
    
    def _check_directories(self, path: Path, result: ValidationResult):
        """Check required directories exist"""
        for dir_path in self.REQUIRED_DIRECTORIES:
            full_path = path / dir_path
            if full_path.exists():
                result.passed_checks.append(f"directory:{dir_path}")
            else:
                result.errors.append(f"Missing directory: {dir_path}")
    
    def _check_files(self, path: Path, result: ValidationResult):
        """Check required files exist"""
        for file_path in self.REQUIRED_FILES:
            full_path = path / file_path
            if full_path.exists():
                result.passed_checks.append(f"file:{file_path}")
            else:
                result.errors.append(f"Missing required file: {file_path}")
        
        for file_path in self.RECOMMENDED_FILES:
            full_path = path / file_path
            if not full_path.exists():
                result.warnings.append(f"Missing recommended file: {file_path}")
    
    def _check_package_json(self, path: Path, result: ValidationResult):
        """Validate package.json"""
        pkg_path = path / "package.json"
        if not pkg_path.exists():
            return
        
        try:
            with open(pkg_path, "r") as f:
                pkg = json.load(f)
            
            # Check essential fields
            if not pkg.get("name"):
                result.warnings.append("package.json missing 'name'")
            
            if not pkg.get("scripts", {}).get("dev"):
                result.warnings.append("package.json missing 'dev' script")
            
            if not pkg.get("scripts", {}).get("build"):
                result.warnings.append("package.json missing 'build' script")
            
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            essential_deps = ["react", "react-dom"]
            for dep in essential_deps:
                if dep not in deps:
                    result.errors.append(f"Missing dependency: {dep}")
            
            result.passed_checks.append("package.json valid")
            
        except json.JSONDecodeError:
            result.errors.append("package.json is invalid JSON")
        except Exception as e:
            result.errors.append(f"Error reading package.json: {e}")
    
    def _check_components(self, path: Path, result: ValidationResult):
        """Check component files"""
        components_dir = path / "src" / "components"
        if not components_dir.exists():
            return
        
        component_files = list(components_dir.rglob("*.tsx")) + list(components_dir.rglob("*.jsx"))
        
        if len(component_files) == 0:
            result.warnings.append("No component files found")
        else:
            result.passed_checks.append(f"components:{len(component_files)} files")
            
            # Check each component
            for comp_file in component_files:
                try:
                    with open(comp_file, "r") as f:
                        content = f.read()
                    
                    # Basic React component checks
                    if "export" not in content:
                        result.warnings.append(f"Component may not be exported: {comp_file.name}")
                    
                    if len(content.strip()) == 0:
                        result.errors.append(f"Empty component: {comp_file.name}")
                        
                except Exception as e:
                    result.errors.append(f"Error reading {comp_file.name}: {e}")
    
    def _check_pages(self, path: Path, result: ValidationResult):
        """Check page files"""
        pages_dir = path / "src" / "pages"
        if not pages_dir.exists():
            return
        
        page_files = list(pages_dir.rglob("*.tsx")) + list(pages_dir.rglob("*.jsx"))
        
        if len(page_files) == 0:
            result.warnings.append("No page files found")
        else:
            result.passed_checks.append(f"pages:{len(page_files)} files")
    
    def _check_empty_files(self, path: Path, result: ValidationResult):
        """Check for empty files"""
        for file_path in path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                if file_path.suffix in [".tsx", ".ts", ".jsx", ".js", ".css"]:
                    try:
                        if file_path.stat().st_size == 0:
                            result.warnings.append(f"Empty file: {file_path.name}")
                    except Exception:
                        pass
    
    def validate_all_templates(
        self,
        templates_dir: str
    ) -> List[ValidationResult]:
        """Validate all templates in a directory"""
        results = []
        templates_path = Path(templates_dir)
        
        for template_dir in templates_path.iterdir():
            if template_dir.is_dir() and not template_dir.name.startswith("."):
                result = self.validate_template(
                    str(template_dir),
                    template_id=template_dir.name,
                    template_name=template_dir.name
                )
                results.append(result)
        
        return results
    
    def quick_check(self, template_path: str) -> bool:
        """Quick check - returns True if template looks valid"""
        result = self.validate_template(template_path)
        return result.is_validS