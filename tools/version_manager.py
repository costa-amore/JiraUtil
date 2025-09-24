#!/usr/bin/env python3
"""
Version management script for JiraUtil.
Handles version incrementing and provides version information for builds.
"""

import json
import sys
from pathlib import Path
from typing import Tuple, Optional
try:
    from code_change_detector import CodeChangeDetector
except ImportError:
    # If running from a different directory, try to import from current directory
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from code_change_detector import CodeChangeDetector


class VersionManager:
    def __init__(self, version_file: str = "version.json", change_detector=None):
        self.version_file = Path(version_file)
        self.version_data = self._load_version()
        self.change_detector = change_detector or CodeChangeDetector()
    
    def _load_version(self) -> dict:
        """Load version data from JSON file."""
        if not self.version_file.exists():
            # Create default version file
            default_version = {
                "major": 1,
                "minor": 0,
                "build": 0,
                "local": 0,
                "description": "JiraUtil - Jira Administration Tool"
            }
            self._save_version(default_version)
            return default_version
        
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading version file: {e}")
            sys.exit(1)
    
    def _save_version(self, version_data: dict) -> None:
        """Save version data to JSON file."""
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2)
        except Exception as e:
            print(f"Error saving version file: {e}")
            sys.exit(1)
    
    def get_version_string(self) -> str:
        """Get version string in M.m.b.l format."""
        return f"{self.version_data['major']}.{self.version_data['minor']}.{self.version_data['build']}.{self.version_data.get('local', 0)}"
    
    def get_version_info(self) -> Tuple[int, int, int, int]:
        """Get version components as tuple (major, minor, build, local)."""
        return (self.version_data['major'], self.version_data['minor'], self.version_data['build'], self.version_data.get('local', 0))
    
    def increment_build(self) -> str:
        """Increment build number and reset local build to 0 (for releases)."""
        self.version_data['build'] += 1
        self.version_data['local'] = 0  # Reset local build for releases
        self._save_version(self.version_data)
        return self.get_version_string()
    
    def increment_build_if_changed(self) -> Tuple[str, bool]:
        """
        Increment build number only if code has changed.
        Resets local build to 0 for releases.
        
        Returns:
            Tuple of (version_string, was_incremented)
        """
        if self.change_detector.has_code_changed():
            self.version_data['build'] += 1
            self.version_data['local'] = 0  # Reset local build for releases
            self._save_version(self.version_data)
            return self.get_version_string(), True
        else:
            return self.get_version_string(), False
    
    def increment_local_build(self) -> str:
        """Increment local build number and return new version string."""
        self.version_data['local'] = self.version_data.get('local', 0) + 1
        self._save_version(self.version_data)
        return self.get_version_string()
    
    def increment_local_build_if_changed(self) -> Tuple[str, bool]:
        """
        Increment local build number only if code has changed.
        
        Returns:
            Tuple of (version_string, was_incremented)
        """
        if self.change_detector.has_code_changed():
            self.version_data['local'] = self.version_data.get('local', 0) + 1
            self._save_version(self.version_data)
            return self.get_version_string(), True
        else:
            return self.get_version_string(), False
    
    def mark_version_update_complete(self) -> None:
        """Mark version update as complete by updating hashes after version files are updated."""
        self.change_detector.mark_build_complete()
    
    def set_version(self, major: Optional[int] = None, minor: Optional[int] = None, build: Optional[int] = None) -> str:
        """Set specific version components."""
        if major is not None:
            self.version_data['major'] = major
        if minor is not None:
            self.version_data['minor'] = minor
        if build is not None:
            self.version_data['build'] = build
        
        self._save_version(self.version_data)
        return self.get_version_string()
    
    def set_manual_version(self, major: int, minor: int) -> str:
        """
        Set major.minor version manually (for developer use).
        Build and local numbers are always reset to 0 when manually setting version.
        """
        self.version_data['major'] = major
        self.version_data['minor'] = minor
        self.version_data['build'] = 0  # Always reset build to 0 for manual setting
        self.version_data['local'] = 0  # Always reset local to 0 for manual setting
        
        self._save_version(self.version_data)
        return self.get_version_string()
    
    def get_file_version_info(self) -> dict:
        """Get version info formatted for Windows executable attributes."""
        major, minor, build, local = self.get_version_info()
        return {
            "FileVersion": self.get_version_string(),
            "ProductVersion": self.get_version_string(),
            "FileDescription": self.version_data.get('description', 'JiraUtil'),
            "ProductName": "JiraUtil",
            "CompanyName": "JiraUtil",
            "LegalCopyright": f"Copyright (C) 2025 JiraUtil",
            "LegalTrademarks": "",
            "OriginalFilename": "JiraUtil.exe",
            "InternalName": "JiraUtil"
        }


def main():
    """Command line interface for version management."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python version_manager.py get                    # Get current version")
        print("  python version_manager.py build <context>        # Build with context (release, local, ci)")
        print("  python version_manager.py set <major> <minor>    # Set major.minor version (build and local will be 0)")
        print("")
        print("Build Contexts:")
        print("  release  - Create release (always increment build, reset local)")
        print("  local    - Local development (increment local if code changed)")
        print("  ci       - CI build (use existing version, no changes)")
        print("")
        print("Legacy commands (use 'build <context>' instead):")
        print("  python version_manager.py increment              # Increment build number")
        print("  python version_manager.py increment-if-changed   # Increment only if code changed")
        print("  python version_manager.py increment-local        # Increment local build number")
        print("  python version_manager.py increment-local-if-changed  # Increment local only if code changed")
        print("")
        print("Options:")
        print("  --version-file <path>                            # Specify version file path")
        print("")
        print("Examples:")
        print("  python version_manager.py get")
        print("  python version_manager.py build release")
        print("  python version_manager.py build local")
        print("  python version_manager.py build ci")
        print("  python version_manager.py set 2.0")
        print("  python version_manager.py build local --version-file custom/version.json")
        sys.exit(1)
    
    # Parse command line arguments
    version_file = "scripts/version.json"  # Default
    command_args = []
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--version-file" and i + 1 < len(sys.argv):
            version_file = sys.argv[i + 1]
            i += 2  # Skip both --version-file and its value
        else:
            command_args.append(sys.argv[i])
            i += 1
    
    if len(command_args) < 1:
        print("Error: Command required")
        sys.exit(1)
    
    manager = VersionManager(version_file)
    command = command_args[0].lower()
    
    if command == "get":
        print(manager.get_version_string())
    elif command == "build":
        if len(command_args) < 2:
            print("ERROR: build command requires a context")
            print("Usage: python version_manager.py build <context>")
            print("Contexts: release, local, ci")
            sys.exit(1)
        
        context = command_args[1].lower()
        
        if context == "release":
            new_version = manager.increment_build()
            print(f"Release created: {new_version}")
        elif context == "local":
            version, was_incremented = manager.increment_local_build_if_changed()
            if was_incremented:
                print(f"Local build incremented to: {version}")
            else:
                print(f"Version unchanged: {version} (no code changes)")
        elif context == "ci":
            version = manager.get_version_string()
            print(f"CI build using version: {version}")
        else:
            print(f"ERROR: Unknown build context '{context}'")
            print("Supported contexts: release, local, ci")
            sys.exit(1)
    elif command == "increment":
        new_version = manager.increment_build()
        print(f"Version incremented to: {new_version}")
    elif command == "increment-if-changed":
        version, was_incremented = manager.increment_build_if_changed()
        if was_incremented:
            print(f"Version incremented to: {version}")
        else:
            print(f"Version unchanged: {version} (no code changes)")
    elif command == "increment-local":
        new_version = manager.increment_local_build()
        print(f"Local build incremented to: {new_version}")
    elif command == "increment-local-if-changed":
        version, was_incremented = manager.increment_local_build_if_changed()
        if was_incremented:
            print(f"Local build incremented to: {version}")
        else:
            print(f"Version unchanged: {version} (no code changes)")
    elif command == "set":
        if len(command_args) < 3:
            print("Error: set command requires major and minor version")
            sys.exit(1)
        
        try:
            major = int(command_args[1])
            minor = int(command_args[2])
            new_version = manager.set_manual_version(major, minor)
            print(f"Version set to: {new_version} (build and local numbers reset to 0)")
        except ValueError:
            print("Error: Version numbers must be integers")
            sys.exit(1)
    else:
        print(f"ERROR: Unknown command '{command}'")
        print("")
        print("Supported commands:")
        print("  get, build <context>, set")
        print("  increment, increment-if-changed, increment-local, increment-local-if-changed (legacy)")
        print("")
        print("Run 'python version_manager.py' (without arguments) to see full usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
