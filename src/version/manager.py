"""
Version detection and management functionality.

This module handles version detection from both executable file properties
and version.json files for development contexts.
"""

import json
import sys
from pathlib import Path


def is_frozen() -> bool:
    """Check if running as a frozen executable."""
    return getattr(sys, 'frozen', False)


def get_version() -> str:
    """Get the current version from executable file properties or version.json."""
    
    # If running as executable, try to get version from file properties
    if is_frozen():
        try:
            import win32api
            import win32file
            
            # Get the executable path
            exe_path = sys.executable
            
            # Get file version info
            version_info = win32api.GetFileVersionInfo(exe_path, "\\")
            # Parse version correctly: MS contains major.minor, LS contains build.revision
            major = version_info['FileVersionMS'] >> 16
            minor = version_info['FileVersionMS'] & 0xFFFF
            build = version_info['FileVersionLS'] >> 16
            revision = version_info['FileVersionLS'] & 0xFFFF
            
            # Format as M.m.bld (ignore revision)
            return f"{major}.{minor}.{build}"
        except ImportError:
            # pywin32 not available, fall back to version.json
            pass
        except Exception:
            # Error reading file properties, fall back to version.json
            pass
    
    # Fallback to version.json (for development or if file properties fail)
    try:
        version_file = Path("scripts/version.json")
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
                return f"{version_data['major']}.{version_data['minor']}.{version_data['build']}"
        else:
            return "unknown"
    except (json.JSONDecodeError, KeyError, IOError):
        return "unknown"
