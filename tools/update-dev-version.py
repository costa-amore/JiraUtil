#!/usr/bin/env python3
"""
Update development README.md with current version.
"""

import json
import re
from pathlib import Path


def update_dev_readme():
    """Update README.md with current version from version.json."""
    
    # Load version information
    version_file = Path("scripts/version.json")
    if not version_file.exists():
        print("Error: scripts/version.json not found. Run version_manager.py first.")
        return False
    
    with open(version_file, 'r') as f:
        version_data = json.load(f)
    
    # Use full 4-component version
    version_string = f"{version_data['major']}.{version_data['minor']}.{version_data['build']}.{version_data.get('local', 0)}"
    
    # Read README.md
    readme_file = Path("README.md")
    if not readme_file.exists():
        print("Error: README.md not found.")
        return False
    
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update version in README
    # Look for existing version line and replace it
    version_pattern = r'Version: \d+\.\d+\.\d+(?:\.\d+)?'
    
    if re.search(version_pattern, content):
        # Replace existing version
        new_content = re.sub(version_pattern, f'Version: {version_string}', content)
    else:
        # Add version after title as proper heading
        new_content = re.sub(
            r'(# JIRA utility\n\nA Python utility for supporting Jira admins\.)',
            f'\\1\n\n## Version\n\nVersion: {version_string}',
            content
        )
    
    # Write updated README
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated README.md with version {version_string}")
    return True


if __name__ == "__main__":
    update_dev_readme()
