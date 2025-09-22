#!/usr/bin/env python3
"""
Dev-friendly command to manually set version numbers.
This script provides a simple interface for developers to set version numbers
and automatically handles the version update completion.
"""

import sys
import argparse
from pathlib import Path
from version_manager import VersionManager


def main():
    """Command line interface for setting version numbers."""
    parser = argparse.ArgumentParser(
        description="Set JiraUtil version number",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python set-version.py 1.0.0          # Set to version 1.0.0
  python set-version.py 2.1.0          # Set to version 2.1.0
  python set-version.py 1.5.10         # Set to version 1.5.10
  python set-version.py --current      # Show current version
  python set-version.py --help         # Show this help

Note: After setting a version, the system will automatically mark the change
as complete, so subsequent builds will use the exact version you set.
        """
    )
    
    parser.add_argument(
        'version',
        nargs='?',
        help='Version to set in format M.m.b (e.g., 1.0.0)'
    )
    parser.add_argument(
        '--current',
        action='store_true',
        help='Show current version'
    )
    
    args = parser.parse_args()
    
    manager = VersionManager()
    
    if args.current:
        current_version = manager.get_version_string()
        print(f"Current version: {current_version}")
        return
    
    if not args.version:
        parser.print_help()
        return
    
    # Parse version string
    try:
        version_parts = args.version.split('.')
        if len(version_parts) != 3:
            raise ValueError("Version must be in format M.m.b (e.g., 1.0.0)")
        
        major = int(version_parts[0])
        minor = int(version_parts[1])
        build = int(version_parts[2])
        
        if major < 0 or minor < 0 or build < 0:
            raise ValueError("Version numbers must be non-negative")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Version must be in format M.m.b (e.g., 1.0.0)")
        sys.exit(1)
    
    # Get current version for comparison
    old_version = manager.get_version_string()
    
    # Set the new version
    new_version = manager.set_version(major, minor, build)
    
    print(f"Version changed: {old_version} → {new_version}")
    
    # Mark version update as complete to update file hashes
    manager.mark_version_update_complete()
    print("✅ Version update marked as complete")
    print()
    print("Next steps:")
    print("1. Run a build to create executables with the new version")
    print("2. The version will remain stable until you make code changes")
    print("3. Use 'python set-version.py --current' to check the current version")


if __name__ == "__main__":
    main()
