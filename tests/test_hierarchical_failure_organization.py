import unittest
from unittest.mock import Mock
from io import StringIO
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from testfixture.workflow import run_assert_expectations
from tests.fixtures import create_assert_scenario, create_mock_manager


class TestHierarchicalFailureOrganization:
    HIGHER_RANK = 10
    LOWER_RANK = 5
    MID_RANK = 7
    NO_RANK = 0

    @pytest.mark.parametrize("first_rank,second_rank,third_rank,expected_order", [
        (HIGHER_RANK, LOWER_RANK, MID_RANK, ['PROJ-2', 'PROJ-3', 'PROJ-1']),
        (HIGHER_RANK, LOWER_RANK, NO_RANK, ['PROJ-3', 'PROJ-2', 'PROJ-1'])
    ])
    def test_assert_failures_are_listed_according_to_rank(self, first_rank, second_rank, third_rank, expected_order):
        # Given: Three epics that failed with specified ranks
        mock_jira_manager = self._create_three_failing_epics_scenario(first_rank, second_rank, third_rank)
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epics are displayed in rank order
        self._verify_epics_displayed_in_rank_order(output, *expected_order)

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
        assert f'[Epic] {first_epic}:' in output
        assert f'[Epic] {second_epic}:' in output
        assert f'[Epic] {third_epic}:' in output
        
        first_pos = output.find(f'[Epic] {first_epic}:')
        second_pos = output.find(f'[Epic] {second_epic}:')
        third_pos = output.find(f'[Epic] {third_epic}:')
        
        assert first_pos < second_pos, f"{first_epic} should appear before {second_epic} due to lower rank"
        assert second_pos < third_pos, f"{second_epic} should appear before {third_epic} due to lower rank"


if __name__ == '__main__':
    pytest.main([__file__])
