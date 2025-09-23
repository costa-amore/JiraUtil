"""
Configuration management for Jira utilities.
"""

from .validator import check_config_file_for_template_values, get_config_file_status_message

__all__ = ['check_config_file_for_template_values', 'get_config_file_status_message']
