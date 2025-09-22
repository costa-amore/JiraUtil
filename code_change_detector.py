#!/usr/bin/env python3
"""
Code change detection system for smart versioning.
Calculates and stores file hashes to detect actual code changes.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Set, List


class CodeChangeDetector:
    def __init__(self, hash_file: str = ".code_hash"):
        self.hash_file = Path(hash_file)
        self.stored_hashes = self._load_hashes()
        
        # Define which files and directories to track for code changes
        self.code_directories = ['src/', 'docs/', '.']
        self.code_extensions = {'.py', '.md', '.ps1', '.sh', '.spec', '.json'}
        self.ignore_patterns = {
            'version.json',      # Don't track version file itself
            '.code_hash',        # Don't track hash file itself
            'version_info.txt',  # Generated file
            '__pycache__',       # Python cache
            '.git',              # Git directory
            '.venv',             # Virtual environment
            'build',             # Build output
            'build-executables', # Build output
            'dist',              # Dist output
        }
        
        # Files that are generated during build and should be ignored
        self.build_generated_files = {
            'version_info.txt',  # Generated during build
        }
    
    def _load_hashes(self) -> Dict[str, str]:
        """Load stored file hashes from .code_hash file."""
        if not self.hash_file.exists():
            return {}
        
        try:
            with open(self.hash_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_hashes(self, hashes: Dict[str, str]) -> None:
        """Save file hashes to .code_hash file."""
        with open(self.hash_file, 'w') as f:
            json.dump(hashes, f, indent=2)
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        # Check if any part of the path matches ignore patterns
        for part in file_path.parts:
            if part in self.ignore_patterns:
                return True
        
        # Check if file is generated during build process
        if file_path.name in self.build_generated_files:
            return True
        
        # Check if file extension is not in code extensions
        if file_path.suffix not in self.code_extensions:
            return True
        
        return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except (IOError, OSError):
            return ""
    
    def _get_tracked_files(self) -> List[Path]:
        """Get list of files that should be tracked for changes."""
        tracked_files = []
        
        for code_dir in self.code_directories:
            code_path = Path(code_dir)
            if code_path.exists():
                for file_path in code_path.rglob('*'):
                    if file_path.is_file() and not self._should_ignore_file(file_path):
                        tracked_files.append(file_path)
        
        return tracked_files
    
    def calculate_current_hashes(self) -> Dict[str, str]:
        """Calculate current hashes for all tracked files."""
        current_hashes = {}
        tracked_files = self._get_tracked_files()
        
        for file_path in tracked_files:
            relative_path = str(file_path)
            file_hash = self._calculate_file_hash(file_path)
            if file_hash:  # Only include files that could be read
                current_hashes[relative_path] = file_hash
        
        return current_hashes
    
    def has_code_changed(self) -> bool:
        """Check if any tracked code files have changed."""
        current_hashes = self.calculate_current_hashes()
        
        # If no stored hashes, consider it a change (first run)
        if not self.stored_hashes:
            return True
        
        # Check if any files have changed
        for file_path, current_hash in current_hashes.items():
            stored_hash = self.stored_hashes.get(file_path)
            if stored_hash != current_hash:
                return True
        
        # Check if any files were removed
        for file_path in self.stored_hashes:
            if file_path not in current_hashes:
                return True
        
        return False
    
    def get_changed_files(self) -> List[str]:
        """Get list of files that have changed."""
        current_hashes = self.calculate_current_hashes()
        changed_files = []
        
        # Check for changed or new files
        for file_path, current_hash in current_hashes.items():
            stored_hash = self.stored_hashes.get(file_path)
            if stored_hash != current_hash:
                changed_files.append(file_path)
        
        # Check for removed files
        for file_path in self.stored_hashes:
            if file_path not in current_hashes:
                changed_files.append(f"{file_path} (removed)")
        
        return changed_files
    
    def update_hashes(self) -> None:
        """Update stored hashes with current file hashes."""
        current_hashes = self.calculate_current_hashes()
        self._save_hashes(current_hashes)
        self.stored_hashes = current_hashes
    
    def mark_build_complete(self) -> None:
        """Mark build as complete by updating hashes (call before version increment)."""
        self.update_hashes()


def main():
    """Command line interface for code change detection."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python code-change-detector.py check     # Check if code has changed")
        print("  python code-change-detector.py changed   # List changed files")
        print("  python code-change-detector.py update    # Update stored hashes")
        print("  python code-change-detector.py reset     # Reset stored hashes")
        sys.exit(1)
    
    detector = CodeChangeDetector()
    command = sys.argv[1].lower()
    
    if command == "check":
        if detector.has_code_changed():
            print("Code has changed")
            sys.exit(0)
        else:
            print("No code changes detected")
            sys.exit(1)
    elif command == "changed":
        changed_files = detector.get_changed_files()
        if changed_files:
            print("Changed files:")
            for file_path in changed_files:
                print(f"  - {file_path}")
        else:
            print("No changed files")
    elif command == "update":
        detector.update_hashes()
        print("Hashes updated")
    elif command == "reset":
        detector.update_hashes()
        print("Hashes reset")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
