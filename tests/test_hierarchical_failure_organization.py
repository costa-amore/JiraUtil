"""
Test hierarchical failure organization for assert operations.

This module tests the organization of assert failures in a hierarchical way:
- Epics that failed or have failed child stories
- Children indented under parent epics
- Orphaned items (not epics or epic children) at same level as epics
- Ordering by rank (ascending)
"""

import unittest
from unittest.mock import Mock
from io import StringIO
import sys
import os

# Setup paths and imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from testfixture.workflow import run_assert_expectations
from tests.fixtures import create_assert_scenario, create_mock_manager


class TestHierarchicalFailureOrganization(unittest.TestCase):
    """Test hierarchical organization of assert failures."""

    # Test constants
    HIGHER_RANK = 10
    LOWER_RANK = 5
    MID_RANK = 7

    def test_assert_failures_are_listed_according_to_rank(self):
        """Test that assert operation displays three epics without children."""
        # Given: Three epics that failed, no child stories
        mock_jira_manager = self._create_three_failing_epics_scenario(self.HIGHER_RANK, self.LOWER_RANK, self.MID_RANK)
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify all epics are displayed in rank order (PROJ-2, PROJ-3, PROJ-1)
        self._verify_epics_displayed_in_rank_order(output, 'PROJ-2', 'PROJ-3', 'PROJ-1')

    # Private helper methods (sorted alphabetically)
    def _create_three_failing_epics_scenario(self, first_epic_rank, second_epic_rank, third_epic_rank):
        epic1 = self._create_epic_failing_assertion("PROJ-1", first_epic_rank)
        epic2 = self._create_epic_failing_assertion("PROJ-2", second_epic_rank)
        epic3 = self._create_epic_failing_assertion("PROJ-3", third_epic_rank)
        
        return create_mock_manager([epic1, epic2, epic3])

    def _create_epic_failing_assertion(self, key, rank):
        status = 'To Do'
        summary = f"Some epic context - starting in {status} - expected to be in Done"
        scenario = create_assert_scenario(issue_type="Epic", issue_key=key, summary=summary, rank=rank)
        epic = scenario.get_issues_by_label.return_value[0]
        epic['status'] = status
        return epic

    def _execute_assert_operation_with_print_capture(self, mock_jira_manager):
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output
        
        try:
            run_assert_expectations(mock_jira_manager, 'rule-testing')
        finally:
            sys.stdout = original_stdout
        
        return captured_output.getvalue()

    def _verify_epics_displayed_in_rank_order(self, output, first_epic, second_epic, third_epic):
        # Verify all epics are displayed
        self.assertIn(f'[Epic] {first_epic}:', output)
        self.assertIn(f'[Epic] {second_epic}:', output)
        self.assertIn(f'[Epic] {third_epic}:', output)
        
        # Verify epics appear in rank order
        first_pos = output.find(f'[Epic] {first_epic}:')
        second_pos = output.find(f'[Epic] {second_epic}:')
        third_pos = output.find(f'[Epic] {third_epic}:')
        
        self.assertLess(first_pos, second_pos, f"{first_epic} should appear before {second_epic} due to lower rank")
        self.assertLess(second_pos, third_pos, f"{second_epic} should appear before {third_epic} due to lower rank")


if __name__ == '__main__':
    unittest.main()
