"""
Base test class for JiraUtils command testing.
"""

import sys
from pathlib import Path
from unittest.mock import patch, Mock


class TestJiraUtilsCommand:
    """Base class for testing JiraUtils CLI commands."""

    def _setup_mock_credentials(self, mock_get_credentials):
        """Setup mock credentials for testing."""
        mock_get_credentials.return_value = ('http://test.com', 'user', 'pass')

    def _execute_JiraUtil_with_args(self, mock_get_credentials, mock_jira_class, *args):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        from JiraUtil import run_cli
        
        with patch('sys.argv', ['JiraUtil.py'] + list(args)):
            with patch('builtins.print') as mock_print:
                with patch('testfixture_cli.handlers.get_jira_credentials', mock_get_credentials):
                    with patch('testfixture_cli.handlers.JiraInstanceManager', mock_jira_class):
                        run_cli()
                        return mock_print
