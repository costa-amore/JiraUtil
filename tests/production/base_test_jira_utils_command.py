"""
Base test class for JiraUtils command testing.
"""

import sys
from pathlib import Path
from unittest.mock import patch


class TestJiraUtilsCommand:
    """Base class for testing JiraUtils CLI commands."""

    def _execute_JiraUtil_with_args(self, *args):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        from JiraUtil import run_cli
        with patch('sys.argv', ['JiraUtil.py'] + list(args)):
            with patch('builtins.print') as mock_print:
                run_cli()
                return mock_print
