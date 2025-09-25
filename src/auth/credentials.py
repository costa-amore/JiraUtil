"""
Jira credential management functionality.

This module handles loading Jira credentials from various sources including
environment files, environment variables, and user prompts.
"""

import os
import getpass
from pathlib import Path
from typing import Tuple

# Environment variable names for Jira credentials
JIRA_ENV_VARS = {
    'url': 'JIRA_URL',
    'username': 'JIRA_USERNAME', 
    'password': 'JIRA_PASSWORD'
}

# Template patterns used for detecting placeholder values in credentials
CREDENTIAL_TEMPLATE_PATTERNS = {
    'url': ['yourcompany', 'example', 'placeholder'],
    'username': ['your.email', 'example', 'placeholder', 'user@'],
    'password': ['your_api', 'example', 'placeholder', 'token_here']
}

# Environment file structure and generation
def generate_env_file_content(url, username, password, comment_prefix="# Jira Configuration"):
    """
    Generate environment file content for given credentials.
    
    Args:
        url: Jira instance URL
        username: Jira username/email
        password: Jira password/API token
        comment_prefix: Comment line prefix
        
    Returns:
        String containing the environment file content
    """
    return f"""{comment_prefix}
{JIRA_ENV_VARS['url']}={url}
{JIRA_ENV_VARS['username']}={username}
{JIRA_ENV_VARS['password']}={password}
"""

def create_template_env_content():
    """Create template environment content using production constants."""
    # Use the actual template patterns from production code
    url_pattern = next((p for p in CREDENTIAL_TEMPLATE_PATTERNS['url'] if 'yourcompany' in p), 'yourcompany')
    username_pattern = next((p for p in CREDENTIAL_TEMPLATE_PATTERNS['username'] if 'your.email' in p), 'your.email')
    password_pattern = next((p for p in CREDENTIAL_TEMPLATE_PATTERNS['password'] if 'your_api' in p), 'your_api')
    
    return generate_env_file_content(
        url=f"https://{url_pattern}.atlassian.net",
        username=f"{username_pattern}@example.com", 
        password=f"{password_pattern}_token_here"
    )

def create_env_file(file_path: str, url: str, username: str, password: str, comment_prefix: str = "# Jira Configuration") -> None:
    """
    Create an environment file with the given credentials.
    
    Args:
        file_path: Path where to create the environment file
        url: Jira instance URL
        username: Jira username/email
        password: Jira password/API token
        comment_prefix: Comment line prefix
    """
    content = generate_env_file_content(url, username, password, comment_prefix)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


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
    jira_url = os.getenv(JIRA_ENV_VARS['url'])
    username = os.getenv(JIRA_ENV_VARS['username'])
    password = os.getenv(JIRA_ENV_VARS['password'])
    
    # Check if values are template/placeholder values
    def is_template_value(value, field_type):
        if not value or value.strip() == '':
            return True
        
        value_lower = value.lower()
        for pattern in CREDENTIAL_TEMPLATE_PATTERNS.get(field_type, []):
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
