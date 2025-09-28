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

    def test_assert_failures_displays_epic_with_failing_child_story(self):
        # Given: An epic with one failing child story
        mock_jira_manager = self._create_epic_with_child_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epic is displayed with indented child story
        self._verify_epic_with_child_displayed(output, 'PROJ-1', 'PROJ-2')

    # TODO: Future test example - children found before parents
    # def test_assert_failures_handles_children_found_before_parents(self):
    #     # Given: Child story appears before parent epic in the issue list
    #     # This might break current code that assumes parents are found first
    #     # When: Assert operation is executed
    #     # Then: Should still display hierarchical structure correctly

    def _create_three_failing_epics_scenario(self, first_epic_rank, second_epic_rank, third_epic_rank):
        epic1 = self._create_epic_failing_assertion("PROJ-1", first_epic_rank)
        epic2 = self._create_epic_failing_assertion("PROJ-2", second_epic_rank)
        epic3 = self._create_epic_failing_assertion("PROJ-3", third_epic_rank)
        return create_mock_manager([epic1, epic2, epic3])

    def _create_epic_with_child_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGHER_RANK)
        story = self._create_story_failing_assertion("PROJ-2", self.LOWER_RANK, epic['key'])
        return create_mock_manager([epic, story])

    def _create_epic_failing_assertion(self, key, rank):
        status = 'To Do'
        summary = f"Some epic context - starting in {status} - expected to be in Done"
        scenario = create_assert_scenario(issue_type="Epic", issue_key=key, summary=summary, rank=rank)
        epic = scenario.get_issues_by_label.return_value[0]
        epic['status'] = status
        return epic

    def _create_story_failing_assertion(self, key, rank, parent_epic):
        status = 'To Do'
        summary = f"Some story context - starting in {status} - expected to be in Done"
        scenario = create_assert_scenario(issue_type="Story", issue_key=key, summary=summary, rank=rank)
        story = scenario.get_issues_by_label.return_value[0]
        story['status'] = status
        story['parent_epic'] = parent_epic
        return story

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

    def _verify_epic_with_child_displayed(self, output, epic_key, story_key):
        assert f'[Epic] {epic_key}:' in output
        assert f'  - [Story] {story_key}:' in output
        
        epic_pos = output.find(f'[Epic] {epic_key}:')
        story_pos = output.find(f'  - [Story] {story_key}:')
        
        assert epic_pos < story_pos, f"Epic {epic_key} should appear before child story {story_key}"
        assert story_pos - epic_pos > 0, f"Story {story_key} should be indented under epic {epic_key}"


if __name__ == '__main__':
    pytest.main([__file__])
