"""
Configuration file validation functionality.

This module handles validation of configuration files and provides
status messages for configuration state.
"""

from pathlib import Path
from typing import Tuple


def check_config_file_for_template_values(config_path: Path) -> Tuple[bool, str]:
    """
    Check if a config file contains template values.
    
    Returns:
        Tuple of (has_template_values, status_message)
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for template/placeholder values (ignore comments)
        lines = content.split('\n')
        non_comment_lines = [line for line in lines if not line.strip().startswith('#')]
        non_comment_content = '\n'.join(non_comment_lines)
        
        has_template_values = any(pattern in non_comment_content.lower() for pattern in [
            'yourcompany', 'your.email', 'your_api', 'token_here'
        ])
        
        if has_template_values:
            return True, f"⚠️  {config_path.name} contains template values - needs configuration"
        else:
            return False, f"✅ {config_path.name} appears to be configured"
    except Exception:
        return False, f"❌ Error reading {config_path.name}"


def get_config_file_status_message(config_path: Path, is_venv_config: bool = False) -> str:
    """
    Get the appropriate status message for a config file.
    
    Args:
        config_path: Path to the config file
        is_venv_config: Whether this is a .venv config file (for special messaging)
    """
    has_template_values, base_message = check_config_file_for_template_values(config_path)
    
    if has_template_values:
        return f"  Jira credentials: {base_message}"
    else:
        if is_venv_config and config_path.name == 'jira_config.env':
            return f"  Jira credentials: ✅ {config_path.name} appears to be correctly configured (in the .venv folder)"
        else:
            return f"  Jira credentials: {base_message}"
