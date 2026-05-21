#!/usr/bin/env python3
"""
NOVARYX - Version Manager
Manages version tracking, changelog generation, and release tagging.

Usage:
  python scripts/version.py              # Show current version
  python scripts/version.py bump patch   # Bump patch (0.8.0 -> 0.8.1)
  python scripts/version.py bump minor   # Bump minor (0.8.0 -> 0.9.0)
  python scripts/version.py bump major   # Bump major (0.8.0 -> 1.0.0)
  python scripts/version.py log          # Show changelog
  python scripts/version.py check        # Verify all versions match
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional


class VersionManager:
    """Manages NOVARYX version information"""
    
    def __init__(self):
        self.root = self._find_root()
        self.version_file = self.root / "config" / "version.json"
        self.version_data = self._load_version()
    
    def _find_root(self) -> Path:
        """Find project root directory"""
        # Start from script location
        current = Path(__file__).resolve().parent.parent
        
        # Verify by checking for config/version.json
        if (current / "config" / "version.json").exists():
            return current
        
        # Try current working directory
        cwd = Path.cwd()
        if (cwd / "config" / "version.json").exists():
            return cwd
        
        raise FileNotFoundError("Cannot find NOVARYX root directory")
    
    def _load_version(self) -> dict:
        """Load version data from file"""
        if self.version_file.exists():
            with open(self.version_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_version(self):
        """Save version data to file"""
        with open(self.version_file, "w") as f:
            json.dump(self.version_data, f, indent=2)
        print(f"✅ Version saved: {self.get_version_string()}")
    
    def get_version_string(self) -> str:
        """Get current version as string"""
        return self.version_data.get("version", "0.0.0")
    
    def get_version_tuple(self) -> Tuple[int, int, int]:
        """Get version as (major, minor, patch) tuple"""
        version = self.get_version_string()
        parts = version.split(".")
        return (
            int(parts[0]) if len(parts) > 0 else 0,
            int(parts[1]) if len(parts) > 1 else 0,
            int(parts[2]) if len(parts) > 2 else 0
        )
    
    def bump_version(self, bump_type: str, message: str = "") -> str:
        """
        Bump version number.
        
        Args:
            bump_type: 'major', 'minor', or 'patch'
            message: Optional changelog message
        
        Returns:
            New version string
        """
        major, minor, patch = self.get_version_tuple()
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            print(f"❌ Invalid bump type: {bump_type}")
            print("   Use: major, minor, or patch")
            return self.get_version_string()
        
        new_version = f"{major}.{minor}.{patch}"
        old_version = self.get_version_string()
        
        print(f"📦 Version bump: {old_version} → {new_version} ({bump_type})")
        
        # Update version data
        self.version_data["version"] = new_version
        
        # Add changelog entry
        if message:
            self.version_data["changelog"].append({
                "version": new_version,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "changes": [message]
            })
        
        self._save_version()
        
        # Update version in __init__ files if needed
        self._sync_version_to_files(new_version)
        
        return new_version
    
    def _sync_version_to_files(self, version: str):
        """Sync version to other files that might reference it"""
        # Update system_config.json if it exists
        config_file = self.root / "config" / "system_config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                config["version"] = version
                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)
                print(f"   Updated: config/system_config.json")
            except Exception as e:
                print(f"   ⚠️  Could not update system_config.json: {e}")
    
    def add_changelog_entry(self, message: str):
        """Add a changelog entry for current version"""
        version = self.get_version_string()
        
        # Find existing entry or create new one
        for entry in self.version_data["changelog"]:
            if entry["version"] == version:
                entry["changes"].append(message)
                entry["date"] = datetime.now().strftime("%Y-%m-%d")
                break
        else:
            self.version_data["changelog"].append({
                "version": version,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "changes": [message]
            })
        
        self._save_version()
        print(f"✅ Added changelog entry for v{version}")
    
    def show_changelog(self, count: int = 0):
        """Display changelog"""
        changelog = self.version_data.get("changelog", [])
        
        print("\n" + "=" * 60)
        print(f"📋 NOVARYX CHANGELOG")
        print("=" * 60)
        
        entries = changelog[-count:] if count > 0 else changelog
        
        for entry in reversed(entries):
            print(f"\n  v{entry['version']} ({entry['date']})")
            for change in entry.get("changes", []):
                print(f"    • {change}")
        
        print("\n" + "=" * 60 + "\n")
    
    def show_status(self):
        """Show current version status"""
        print("\n" + "=" * 60)
        print("📦 NOVARYX VERSION STATUS")
        print("=" * 60)
        
        print(f"   Project: {self.version_data.get('project', 'Unknown')}")
        print(f"   Version: {self.get_version_string()}")
        print(f"   Codename: {self.version_data.get('codename', 'Unknown')}")
        print(f"   Phase: {self.version_data.get('phase', '?')}")
        print(f"   Step: {self.version_data.get('step', '?')}")
        print(f"   Status: {self.version_data.get('status', 'unknown')}")
        
        components = self.version_data.get("components", {})
        if components:
            print(f"\n   Component Versions:")
            for comp, ver in components.items():
                print(f"      {comp}: v{ver}")
        
        print(f"\n   Next Milestone: {self.version_data.get('next_milestone', 'Unknown')}")
        
        print("=" * 60 + "\n")
    
    def check_consistency(self) -> bool:
        """Check version consistency across files"""
        print("\n🔍 Checking version consistency...")
        
        all_ok = True
        current = self.get_version_string()
        
        # Check system_config.json
        config_file = self.root / "config" / "system_config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
            config_version = config.get("system", {}).get("version", "")
            if config_version != current:
                print(f"   ⚠️  system_config.json: {config_version} (expected {current})")
                all_ok = False
        
        # Check component versions
        components = self.version_data.get("components", {})
        expected_phase = self.version_data.get("phase", 0)
        
        if components:
            for comp, ver in components.items():
                try:
                    comp_phase = int(ver.split(".")[1]) if "." in ver else 0
                except:
                    comp_phase = 0
        
        if all_ok:
            print(f"   ✅ All versions consistent (v{current})")
        else:
            print(f"   ❌ Version inconsistencies found")
        
        return all_ok
    
    def init_git(self):
        """Initialize git repository if not already done"""
        git_dir = self.root / ".git"
        
        if git_dir.exists():
            print("📦 Git already initialized")
        else:
            try:
                subprocess.run(
                    ["git", "init"],
                    cwd=str(self.root),
                    check=True,
                    capture_output=True
                )
                print("✅ Git repository initialized")
            except subprocess.CalledProcessError as e:
                print(f"❌ Git init failed: {e}")
                return
            except FileNotFoundError:
                print("❌ Git not found. Install Git: https://git-scm.com")
                return
        
        # Check gitignore
        gitignore = self.root / ".gitignore"
        if gitignore.exists():
            print("✅ .gitignore found")
        else:
            print("⚠️  .gitignore not found")
        
        # Check gitattributes
        gitattributes = self.root / ".gitattributes"
        if gitattributes.exists():
            print("✅ .gitattributes found")
        else:
            print("⚠️  .gitattributes not found")
    
    def get_git_status(self) -> dict:
        """Get git repository status"""
        status = {
            "initialized": False,
            "branch": "",
            "commits": 0,
            "modified_files": 0,
            "untracked_files": 0
        }
        
        git_dir = self.root / ".git"
        if not git_dir.exists():
            return status
        
        status["initialized"] = True
        
        try:
            # Get branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            status["branch"] = result.stdout.strip()
            
            # Get commit count
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            status["commits"] = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
            
            # Get modified files
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            status["modified_files"] = len([l for l in lines if l and not l.startswith("??")])
            status["untracked_files"] = len([l for l in lines if l and l.startswith("??")])
            
        except Exception as e:
            print(f"⚠️  Error getting git status: {e}")
        
        return status
    
    def display_git_status(self):
        """Display git repository status"""
        status = self.get_git_status()
        
        print("\n" + "=" * 50)
        print("📦 GIT REPOSITORY STATUS")
        print("=" * 50)
        
        if status["initialized"]:
            print(f"   Branch: {status['branch'] or 'N/A'}")
            print(f"   Commits: {status['commits']}")
            print(f"   Modified: {status['modified_files']} files")
            print(f"   Untracked: {status['untracked_files']} files")
        else:
            print("   ❌ Not a git repository")
            print("   Run: git init")
        
        print("=" * 50 + "\n")


def main():
    """Main CLI for version management"""
    
    if len(sys.argv) < 2:
        # Default: show status
        vm = VersionManager()
        vm.show_status()
        vm.display_git_status()
        return
    
    command = sys.argv[1]
    vm = VersionManager()
    
    if command == "bump" and len(sys.argv) >= 3:
        bump_type = sys.argv[2]
        message = sys.argv[3] if len(sys.argv) > 3 else ""
        vm.bump_version(bump_type, message)
    
    elif command == "log":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        vm.show_changelog(count)
    
    elif command == "check":
        vm.check_consistency()
    
    elif command == "init":
        vm.init_git()
        vm.display_git_status()
    
    elif command == "add":
        message = sys.argv[2] if len(sys.argv) > 2 else ""
        if message:
            vm.add_changelog_entry(message)
        else:
            print("❌ Please provide a changelog message")
    
    elif command == "status":
        vm.show_status()
        vm.display_git_status()
    
    elif command == "git":
        vm.display_git_status()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("\nUsage:")
        print("  python scripts/version.py              Show status")
        print("  python scripts/version.py bump patch   Bump patch version")
        print("  python scripts/version.py bump minor   Bump minor version")
        print("  python scripts/version.py bump major   Bump major version")
        print("  python scripts/version.py log          Show changelog")
        print("  python scripts/version.py check        Check consistency")
        print("  python scripts/version.py init         Initialize git")
        print("  python scripts/version.py add 'msg'    Add changelog entry")


if __name__ == "__main__":
    main()
