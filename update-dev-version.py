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
    version_file = Path("version.json")
    if not version_file.exists():
        print("Error: version.json not found. Run version_manager.py first.")
        return False
    
    with open(version_file, 'r') as f:
        version_data = json.load(f)
    
    version_string = f"{version_data['major']}.{version_data['minor']}.{version_data['build']}"
    
    # Read README.md
    readme_file = Path("README.md")
    if not readme_file.exists():
        print("Error: README.md not found.")
        return False
    
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update version in README
    # Look for existing version section and replace it, or add new one
    version_heading_pattern = r'## Version\n\nVersion: \d+\.\d+\.\d+'
    
    if re.search(version_heading_pattern, content):
        # Replace existing heading version
        new_content = re.sub(version_heading_pattern, f'## Version\n\nVersion: {version_string}', content)
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
