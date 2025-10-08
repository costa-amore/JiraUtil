"""
Tests for chained test fixture commands functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from cli.parser import build_parser
from testfixture_cli.handlers import handle_test_fixture_commands


class TestTFChainedCommands(unittest.TestCase):
    """Test chained test fixture commands functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = build_parser()

    def test_parse_chained_commands_reset_trigger(self):
        """Test parsing chained commands: reset then trigger."""
        args = self.parser.parse_args(['tf', 'r', 't', '--tsl', 'test-label', '--tl', 'trigger-label'])
        
        self.assertEqual(args.command, 'tf')  # alias is preserved
        self.assertEqual(args.commands, ['r', 't'])
        self.assertEqual(args.tsl, 'test-label')
        self.assertEqual(args.tl, 'trigger-label')
        self.assertEqual(args.key, 'TAPS-212')  # default

    def test_parse_chained_commands_reset_assert_trigger(self):
        """Test parsing chained commands: reset, assert, then trigger."""
        args = self.parser.parse_args(['tf', 'r', 'a', 't', '--tsl', 'test-label', '--tl', 'trigger-label', '-k', 'TEST-123'])
        
        self.assertEqual(args.command, 'tf')  # alias is preserved
        self.assertEqual(args.commands, ['r', 'a', 't'])
        self.assertEqual(args.tsl, 'test-label')
        self.assertEqual(args.tl, 'trigger-label')
        self.assertEqual(args.key, 'TEST-123')

    def test_parse_chained_commands_with_multiple_labels(self):
        """Test parsing chained commands with multiple labels."""
        args = self.parser.parse_args(['tf', 'r', 'a', 't', '--tsl', 'label1,label2', '--tl', 'trigger1,trigger2'])
        
        self.assertEqual(args.command, 'tf')  # alias is preserved
        self.assertEqual(args.commands, ['r', 'a', 't'])
        self.assertEqual(args.tsl, 'label1,label2')
        self.assertEqual(args.tl, 'trigger1,trigger2')

    def test_parse_chained_commands_without_label_fails(self):
        """Test that chained commands without label fail for trigger."""
        # This should parse successfully, but fail at runtime
        args = self.parser.parse_args(['tf', 'r', 't'])  # Missing --tl for trigger
        self.assertEqual(args.command, 'tf')
        self.assertEqual(args.commands, ['r', 't'])
        self.assertIsNone(args.tsl)
        self.assertIsNone(args.tl)

    def test_parse_chained_commands_reset_assert_only(self):
        """Test parsing chained commands without trigger (no label required)."""
        args = self.parser.parse_args(['tf', 'r', 'a'])
        
        self.assertEqual(args.command, 'tf')  # alias is preserved
        self.assertEqual(args.commands, ['r', 'a'])
        self.assertIsNone(args.tsl)
        self.assertIsNone(args.tl)

    @patch('testfixture_cli.handlers.execute_with_jira_manager')
    @patch('testfixture_cli.handlers.get_jira_credentials')
    def test_handle_chained_commands_reset_trigger(self, mock_get_creds, mock_execute):
        """Test handling chained commands: reset then trigger."""
        # Setup mocks
        mock_get_creds.return_value = ('http://test.com', 'user', 'pass')
        mock_execute.return_value = None
        
        # Create mock args
        args = MagicMock()
        args.commands = ['r', 't']
        args.tsl = 'test-label'
        args.tl = 'trigger-label'
        args.key = 'TEST-123'
        args.jira_url = None
        args.username = None
        args.password = None
        
        # Execute
        result = handle_test_fixture_commands(args, {})
        
        # Verify
        self.assertEqual(mock_execute.call_count, 2)
        
        # Check first call (reset)
        first_call = mock_execute.call_args_list[0]
        self.assertEqual(first_call[0][4], 'test-label')  # label argument (args[4])
        
        # Check second call (trigger)
        second_call = mock_execute.call_args_list[1]
        self.assertEqual(second_call[0][4], 'TEST-123')    # key argument (args[4])
        self.assertEqual(second_call[0][5], 'trigger-label')  # trigger-label argument (args[5])

    @patch('testfixture_cli.handlers.execute_with_jira_manager')
    @patch('testfixture_cli.handlers.get_jira_credentials')
    def test_handle_chained_commands_reset_assert_trigger(self, mock_get_creds, mock_execute):
        """Test handling chained commands: reset, assert, then trigger."""
        # Setup mocks
        mock_get_creds.return_value = ('http://test.com', 'user', 'pass')
        mock_execute.return_value = None
        
        # Create mock args
        args = MagicMock()
        args.commands = ['r', 'a', 't']
        args.tsl = 'test-label'
        args.tl = 'trigger-label'
        args.key = 'TEST-123'
        args.jira_url = None
        args.username = None
        args.password = None
        
        # Execute
        result = handle_test_fixture_commands(args, {})
        
        # Verify
        self.assertEqual(mock_execute.call_count, 3)
        
        # Check calls in order
        calls = mock_execute.call_args_list
        self.assertEqual(calls[0][0][4], 'test-label')  # reset (args[4])
        self.assertEqual(calls[1][0][4], 'test-label')  # assert (args[4])
        self.assertEqual(calls[2][0][4], 'TEST-123')    # trigger key (args[4])
        self.assertEqual(calls[2][0][5], 'trigger-label')  # trigger label (args[5])

    @patch('testfixture_cli.handlers.execute_with_jira_manager')
    @patch('testfixture_cli.handlers.get_jira_credentials')
    def test_handle_chained_commands_with_default_label(self, mock_get_creds, mock_execute):
        """Test handling chained commands with default label for reset/assert."""
        # Setup mocks
        mock_get_creds.return_value = ('http://test.com', 'user', 'pass')
        mock_execute.return_value = None
        
        # Create mock args (no label provided)
        args = MagicMock()
        args.commands = ['r', 'a']
        args.tsl = None
        args.tl = None
        args.key = 'TEST-123'
        args.jira_url = None
        args.username = None
        args.password = None
        
        # Execute
        result = handle_test_fixture_commands(args, {})
        
        # Verify
        self.assertEqual(mock_execute.call_count, 2)
        
        # Check that default label is used
        calls = mock_execute.call_args_list
        # The default label should be used (this will be tested when we implement the handler)

    @patch('testfixture_cli.handlers.execute_with_jira_manager')
    @patch('testfixture_cli.handlers.get_jira_credentials')
    def test_handle_chained_commands_unknown_command_fails(self, mock_get_creds, mock_execute):
        """Test that unknown commands in chain fail."""
        mock_get_creds.return_value = ('http://test.com', 'user', 'pass')
        mock_execute.return_value = None
        
        args = MagicMock()
        args.commands = ['r', 'unknown', 't']
        args.tsl = 'test-label'
        args.tl = 'trigger-label'
        args.key = 'TEST-123'
        args.jira_url = None
        args.username = None
        args.password = None
        
        with self.assertRaises(SystemExit):
            handle_test_fixture_commands(args, {})

    @patch('testfixture_cli.handlers.execute_with_jira_manager')
    @patch('testfixture_cli.handlers.get_jira_credentials')
    def test_handle_chained_commands_trigger_without_label_fails(self, mock_get_creds, mock_execute):
        mock_get_creds.return_value = ('http://test.com', 'user', 'pass')
        mock_execute.return_value = None
        
        args = MagicMock()
        args.commands = ['r', 't']
        args.tsl = None
        args.tl = None
        args.key = 'TEST-123'
        args.jira_url = None
        args.username = None
        args.password = None
        
        with patch('builtins.print') as mock_print:
            handle_test_fixture_commands(args, {})
            mock_print.assert_called_with("[FATAL] ERROR: Trigger command requires --tl/--trigger-label argument")

    def test_parse_chained_commands_same_command_multiple_times(self):
        """Test parsing chained commands with same command repeated multiple times."""
        args = self.parser.parse_args(['tf', 'r', 'r', 'r', 't', '--tsl', 'test-label', '--tl', 'trigger-label'])
        
        self.assertEqual(args.command, 'tf')
        self.assertEqual(args.commands, ['r', 'r', 'r', 't'])
        self.assertEqual(args.tsl, 'test-label')
        self.assertEqual(args.tl, 'trigger-label')
        self.assertEqual(args.key, 'TAPS-212')  # default

    def test_parse_chained_commands_complex_mixed_commands(self):
        """Test parsing complex chained commands with mixed repeated commands."""
        args = self.parser.parse_args(['tf', 'a', 'r', 'a', 't', 'a', 'a', 'a', 'a', '--tsl', 'test-label', '--tl', 'trigger-label', '-k', 'TEST-456'])
        
        self.assertEqual(args.command, 'tf')
        self.assertEqual(args.commands, ['a', 'r', 'a', 't', 'a', 'a', 'a', 'a'])
        self.assertEqual(args.tsl, 'test-label')
        self.assertEqual(args.tl, 'trigger-label')
        self.assertEqual(args.key, 'TEST-456')

    @patch('testfixture_cli.handlers.execute_with_jira_manager')
    @patch('testfixture_cli.handlers.get_jira_credentials')
    def test_handle_chained_commands_same_command_multiple_times(self, mock_get_creds, mock_execute):
        """Test handling chained commands with same command repeated multiple times."""
        # Setup mocks
        mock_get_creds.return_value = ('http://test.com', 'user', 'pass')
        mock_execute.return_value = None
        
        # Create mock args - reset 3 times then trigger
        args = MagicMock()
        args.commands = ['r', 'r', 'r', 't']
        args.tsl = 'test-label'
        args.tl = 'trigger-label'
        args.key = 'TEST-123'
        args.jira_url = None
        args.username = None
        args.password = None
        
        # Execute
        result = handle_test_fixture_commands(args, {})
        
        # Verify
        self.assertEqual(mock_execute.call_count, 4)
        
        # Check that all calls use the same parameters
        calls = mock_execute.call_args_list
        for i in range(3):  # First 3 calls should be reset
            self.assertEqual(calls[i][0][4], 'test-label')  # label argument
        
        # Last call should be trigger
        self.assertEqual(calls[3][0][4], 'TEST-123')    # key argument
        self.assertEqual(calls[3][0][5], 'trigger-label')  # trigger-label argument

    @patch('testfixture_cli.handlers.execute_with_jira_manager')
    @patch('testfixture_cli.handlers.get_jira_credentials')
    def test_handle_chained_commands_complex_mixed_commands(self, mock_get_creds, mock_execute):
        """Test handling complex chained commands with mixed repeated commands."""
        # Setup mocks
        mock_get_creds.return_value = ('http://test.com', 'user', 'pass')
        mock_execute.return_value = None
        
        # Create mock args - a, r, a, t, a, a, a, a
        args = MagicMock()
        args.commands = ['a', 'r', 'a', 't', 'a', 'a', 'a', 'a']
        args.tsl = 'test-label'
        args.tl = 'trigger-label'
        args.key = 'TEST-456'
        args.jira_url = None
        args.username = None
        args.password = None
        
        # Execute
        result = handle_test_fixture_commands(args, {})
        
        # Verify
        self.assertEqual(mock_execute.call_count, 8)
        
        # Check that all calls use the same parameters
        calls = mock_execute.call_args_list
        for i in range(8):
            if i == 3:  # Trigger command (4th call, index 3)
                self.assertEqual(calls[i][0][4], 'TEST-456')    # key argument
                self.assertEqual(calls[i][0][5], 'trigger-label')  # trigger-label argument
            else:  # All other commands (assert or reset)
                self.assertEqual(calls[i][0][4], 'test-label')  # label argument


if __name__ == '__main__':
    unittest.main()
