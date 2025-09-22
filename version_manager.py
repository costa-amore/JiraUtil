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
    def __init__(self, version_file: str = "version.json"):
        self.version_file = Path(version_file)
        self.version_data = self._load_version()
        self.change_detector = CodeChangeDetector()
    
    def _load_version(self) -> dict:
        """Load version data from JSON file."""
        if not self.version_file.exists():
            # Create default version file
            default_version = {
                "major": 1,
                "minor": 0,
                "build": 0,
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
        """Get version string in M.m.bld format."""
        return f"{self.version_data['major']}.{self.version_data['minor']}.{self.version_data['build']}"
    
    def get_version_info(self) -> Tuple[int, int, int]:
        """Get version components as tuple (major, minor, build)."""
        return (self.version_data['major'], self.version_data['minor'], self.version_data['build'])
    
    def increment_build(self) -> str:
        """Increment build number and return new version string."""
        self.version_data['build'] += 1
        self._save_version(self.version_data)
        return self.get_version_string()
    
    def increment_build_if_changed(self) -> Tuple[str, bool]:
        """
        Increment build number only if code has changed.
        
        Returns:
            Tuple of (version_string, was_incremented)
        """
        if self.change_detector.has_code_changed():
            self.version_data['build'] += 1
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
    
    def get_file_version_info(self) -> dict:
        """Get version info formatted for Windows executable attributes."""
        major, minor, build = self.get_version_info()
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
        print("  python version_manager.py increment              # Increment build number")
        print("  python version_manager.py increment-if-changed   # Increment only if code changed")
        print("  python version_manager.py set <major> <minor>    # Set major.minor version")
        print("  python version_manager.py set <major> <minor> <build>  # Set full version")
        sys.exit(1)
    
    manager = VersionManager()
    command = sys.argv[1].lower()
    
    if command == "get":
        print(manager.get_version_string())
    elif command == "increment":
        new_version = manager.increment_build()
        print(f"Version incremented to: {new_version}")
    elif command == "increment-if-changed":
        version, was_incremented = manager.increment_build_if_changed()
        if was_incremented:
            print(f"Version incremented to: {version}")
        else:
            print(f"Version unchanged: {version} (no code changes)")
    elif command == "set":
        if len(sys.argv) < 4:
            print("Error: set command requires major and minor version")
            sys.exit(1)
        
        try:
            major = int(sys.argv[2])
            minor = int(sys.argv[3])
            build = int(sys.argv[4]) if len(sys.argv) > 4 else None
            new_version = manager.set_version(major, minor, build)
            print(f"Version set to: {new_version}")
        except ValueError:
            print("Error: Version numbers must be integers")
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
