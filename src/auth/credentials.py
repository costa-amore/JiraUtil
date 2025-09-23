"""
Jira credential management functionality.

This module handles loading Jira credentials from various sources including
environment files, environment variables, and user prompts.
"""

import os
import getpass
from pathlib import Path
from typing import Tuple


def load_env_file(env_file_path: str) -> None:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file_path: Path to the .env file
    """
    env_path = Path(env_file_path)
    if not env_path.exists():
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value


def get_jira_credentials() -> Tuple[str, str, str]:
    """
    Get Jira credentials from .env file, environment variables, or prompt user.
    
    Returns:
        Tuple of (jira_url, username, password)
    """
    # Try to load from .venv/jira_config.env first
    venv_config = Path('.venv') / 'jira_config.env'
    if venv_config.exists():
        load_env_file(str(venv_config))
    
    # Try to load from jira_config.env in current directory
    local_config = Path('jira_config.env')
    if local_config.exists():
        load_env_file(str(local_config))
    
    # Try to get from environment variables
    jira_url = os.getenv('JIRA_URL')
    username = os.getenv('JIRA_USERNAME')
    password = os.getenv('JIRA_PASSWORD')
    
    # Check if values are template/placeholder values
    def is_template_value(value, field_type):
        if not value or value.strip() == '':
            return True
        
        template_patterns = {
            'url': ['yourcompany', 'example', 'placeholder'],
            'username': ['your.email', 'example', 'placeholder', 'user@'],
            'password': ['your_api', 'example', 'placeholder', 'token_here']
        }
        
        value_lower = value.lower()
        for pattern in template_patterns.get(field_type, []):
            if pattern in value_lower:
                return True
        return False
    
    if is_template_value(jira_url, 'url'):
        jira_url = input("Enter Jira URL: ").strip()
    
    if is_template_value(username, 'username'):
        username = input("Enter Jira username: ").strip()
    
    if is_template_value(password, 'password'):
        password = getpass.getpass("Enter Jira password/API token: ")
    
    return jira_url, username, password
