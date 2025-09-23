#!/usr/bin/env python3
"""
Create version_info.txt for PyInstaller with current version information.
"""

import json
import os
import sys
from pathlib import Path


def create_version_info(version_file_path=None, output_file_path=None):
    """
    Create version_info.txt file for PyInstaller.
    
    Args:
        version_file_path: Path to version.json file (default: scripts/version.json)
        output_file_path: Path for output file (default: version_info.txt)
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Use provided path or environment variable or default
    if version_file_path is None:
        version_file_path = os.environ.get("VERSION_FILE", "scripts/version.json")
    
    version_file = Path(version_file_path)
    if not version_file.exists():
        print(f"Error: {version_file} not found. Run version_manager.py first.")
        return False
    
    if output_file_path is None:
        output_file_path = "version_info.txt"
    
    with open(version_file, 'r') as f:
        version_data = json.load(f)
    
    # Use 4-component version for display but 3-component for Windows file version
    version_string = f"{version_data['major']}.{version_data['minor']}.{version_data['build']}"
    local_build = version_data.get('local', 0)
    description = version_data.get('description', 'JiraUtil - Jira Administration Tool')
    
    # Create version info content
    version_info_content = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=({version_data['major']},{version_data['minor']},{version_data['build']},{local_build}),
    prodvers=({version_data['major']},{version_data['minor']},{version_data['build']},{local_build}),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'JiraUtil'),
        StringStruct(u'FileDescription', u'{description}'),
        StringStruct(u'FileVersion', u'{version_string}'),
        StringStruct(u'InternalName', u'JiraUtil'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2025 JiraUtil'),
        StringStruct(u'OriginalFilename', u'JiraUtil.exe'),
        StringStruct(u'ProductName', u'JiraUtil'),
        StringStruct(u'ProductVersion', u'{version_string}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    # Write version info file
    with open(output_file_path, 'w') as f:
        f.write(version_info_content)
    
    print(f"Created {output_file_path} with version {version_string}")
    return True


if __name__ == "__main__":
    # Support command line arguments for testing
    version_file = None
    output_file = None
    
    if len(sys.argv) > 1:
        version_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    success = create_version_info(version_file, output_file)
    sys.exit(0 if success else 1)
