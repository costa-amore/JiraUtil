#!/usr/bin/env python3
"""
Generate PyInstaller spec file with version information.
"""

import json
from pathlib import Path


def generate_spec_file():
    """Generate JiraUtil.spec with current version information."""
    
    # Load version information
    version_file = Path("version.json")
    if not version_file.exists():
        print("Error: version.json not found. Run version_manager.py first.")
        return False
    
    with open(version_file, 'r') as f:
        version_data = json.load(f)
    
    version_string = f"{version_data['major']}.{version_data['minor']}.{version_data['build']}"
    description = version_data.get('description', 'JiraUtil - Jira Administration Tool')
    
    # Generate spec file content
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/JiraUtil.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('jira_config_example.env', '.'),
        ('README.md', '.'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'jira',
        'jira.exceptions',
        'jira.exceptions.JIRAError',
        'pandas',
        'dateutil',
        'dateutil.parser',
        'csv',
        'pathlib',
        'argparse',
        'os',
        're',
        'typing',
        'getpass',
        'jira_cleaner',
        'jira_field_extractor',
        'jira_dates_eu',
        'jira_testfixture',
        'jira_manager',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JiraUtil',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
)
'''
    
    # Write spec file
    with open('JiraUtil.spec', 'w') as f:
        f.write(spec_content)
    
    # Create version info file
    with open('version_info.txt', 'w') as f:
        f.write(f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=({version_data['major']},{version_data['minor']},{version_data['build']},0),
    prodvers=({version_data['major']},{version_data['minor']},{version_data['build']},0),
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
""")
    
    print(f"Generated JiraUtil.spec with version {version_string}")
    return True


if __name__ == "__main__":
    generate_spec_file()
