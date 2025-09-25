"""
CLI command scenarios for testing command-line interface functionality.

This module contains complete test scenarios that group CLI test data
with expected results for command parsing and execution.
"""

from .base_fixtures import create_temp_config_file, create_temp_env_file


def create_config_validation_scenarios():
    """Create scenarios for testing configuration validation."""
    return {
        'template_config': {
            'content': "# Jira Configuration\nJIRA_URL=https://yourcompany.atlassian.net\nJIRA_USERNAME=your.email@example.com\nJIRA_PASSWORD=your_api_token",
            'expected_has_template': True,
            'expected_message_contains': "template values"
        },
        'configured_config': {
            'content': "# Jira Configuration\nJIRA_URL=https://mycompany.atlassian.net\nJIRA_USERNAME=john.doe@mycompany.com\nJIRA_PASSWORD=abc123def456ghi789",
            'expected_has_template': False,
            'expected_message_contains': "appears to be configured"
        }
    }


def create_authentication_scenarios():
    """Create scenarios for testing authentication functionality."""
    return {
        'valid_credentials': {
            'url': 'https://test.atlassian.net',
            'username': 'test@example.com', 
            'password': 'test_token',
            'expected_url': 'https://test.atlassian.net',
            'expected_username': 'test@example.com',
            'expected_password': 'test_token'
        },
        'env_file_loading': {
            'url': 'https://test.atlassian.net',
            'username': 'test@example.com',
            'password': 'test_token',
            'expected_loads_without_error': True
        }
    }


def create_command_parsing_scenarios():
    """Create scenarios for testing command parsing."""
    return {
        'csv_export_commands': [
            {
                'args': ['csv-export', 'remove-newlines', 'input.csv'],
                'expected_command': 'csv-export',
                'expected_subcommand': 'remove-newlines',
                'expected_input': 'input.csv'
            },
            {
                'args': ['ce', 'rn', 'input.csv'],
                'expected_command': 'ce',
                'expected_subcommand': 'rn',
                'expected_input': 'input.csv'
            }
        ],
        'test_fixture_commands': [
            {
                'args': ['test-fixture', 'reset', 'custom-label'],
                'expected_command': 'test-fixture',
                'expected_subcommand': 'reset',
                'expected_label': 'custom-label'
            },
            {
                'args': ['tf', 'r'],
                'expected_command': 'tf',
                'expected_subcommand': 'r',
                'expected_label': 'rule-testing'
            }
        ],
        'utility_commands': [
            {
                'args': ['list'],
                'expected_command': 'list'
            },
            {
                'args': ['status'],
                'expected_command': 'status'
            }
        ]
    }


def create_display_scenarios():
    """Create scenarios for testing display functionality."""
    return {
        'list_command': {
            'expected_sections': [
                "CSV Export Commands:",
                "Test Fixture Commands:", 
                "Utility Commands:",
                "Short Aliases:"
            ],
            'expected_commands': [
                "csv-export remove-newlines",
                "test-fixture reset",
                "list",
                "status"
            ],
            'expected_aliases': [
                "ce rn",
                "tf r", 
                "ls",
                "st"
            ]
        },
        'status_command': {
            'expected_content': [
                "JiraUtil Status",
                "Status: Ready",
                "Configuration:",
                "Default test fixture label: rule-testing"
            ],
            'expected_version_pattern': r"Version: \d+\.\d+\.\d+"
        }
    }
