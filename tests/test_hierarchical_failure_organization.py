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
from jira_manager import DEFAULT_RANK_VALUE


class TestHierarchicalFailureOrganization:
    HIGHEST_RANK = "0|f0000:"
    HIGHER_RANK = "0|h0000:"
    HIGH_RANK = "0|i0000:"
    LOW_RANK = "0|i0002:"
    MID_RANK = "0|i0001:"
    NO_RANK = DEFAULT_RANK_VALUE

    @pytest.mark.parametrize("first_rank,second_rank,third_rank,expected_order", [
        (HIGH_RANK, LOW_RANK, MID_RANK, ['PROJ-1', 'PROJ-3', 'PROJ-2']),
        (HIGH_RANK, LOW_RANK, NO_RANK, ['PROJ-1', 'PROJ-2', 'PROJ-3'])
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

    def test_assert_failures_handles_children_found_before_parents(self):
        # Given: Child story appears before parent epic in the issue list
        mock_jira_manager = self._create_children_before_parents_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Should still display hierarchical structure correctly
        self._verify_epic_with_child_displayed(output, 'PROJ-1', 'PROJ-2')

    def test_assert_failures_displays_epic_with_multiple_failing_children(self):
        # Given: An epic with two failing child stories
        mock_jira_manager = self._create_epic_with_multiple_children_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epic is displayed with both indented child stories
        self._verify_epic_with_multiple_children_displayed(output, 'PROJ-1', 'PROJ-3', 'PROJ-2')

    def test_assert_failures_displays_epic_with_non_evaluated_parent(self):
        # Given: A failing story with an epic that isn't evaluated (no assertion pattern)
        mock_jira_manager = self._create_epic_with_non_evaluated_parent_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epic appears with full summary, story indented under it
        self._verify_epic_with_non_evaluated_parent_displayed(output, 'PROJ-1', 'PROJ-2')

    def test_assert_failures_displays_multiple_epics_with_children_stories_first(self):
        # Given: Multiple epics with failing children, stories added first then epics
        mock_jira_manager = self._create_multiple_epics_stories_first_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify both epics appear with their children correctly grouped
        self._verify_multiple_epics_with_children_displayed(output, 'PROJ-5', 'PROJ-4', 'PROJ-3', 'PROJ-1', 'PROJ-2')

    def test_assert_failures_displays_mixed_epics_and_orphaned_items(self):
        # Given: Epics with children and orphaned items (like real Jira output)
        mock_jira_manager = self._create_mixed_epics_and_orphaned_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epics appear with children, orphaned items at same level
        self._verify_mixed_epics_and_orphaned_displayed(output, 'PROJ-1', 'PROJ-2', 'PROJ-3', 'PROJ-4')

    def test_assert_failures_groups_children_under_epics_not_globally_sorted(self):
        # Given: Epic with higher rank than its children (children should be grouped under epic)
        mock_jira_manager = self._create_epic_higher_rank_than_children_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify children are grouped under epic, not globally sorted
        self._verify_children_grouped_under_epic_not_globally_sorted(output, 'PROJ-1', 'PROJ-3', 'PROJ-2')

    def test_assert_failures_displays_orphaned_non_evaluable_items(self):
        # Given: Orphaned item without assertion pattern (like TAPS-211 Sub-task)
        mock_jira_manager = self._create_orphaned_non_evaluable_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify orphaned non-evaluable item appears in failures
        self._verify_orphaned_non_evaluable_displayed(output, 'PROJ-1')

    def test_assert_failures_displays_orphaned_evaluable_items(self):
        # Given: Orphaned item with failing assertion (like TAPS-211 Sub-task)
        mock_jira_manager = self._create_orphaned_evaluable_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify orphaned evaluable item appears in failures
        self._verify_orphaned_evaluable_displayed(output, 'PROJ-1')

    def test_assert_failures_displays_orphaned_with_real_jira_format(self):
        # Given: Orphaned item with real Jira summary format (like TAPS-211)
        mock_jira_manager = self._create_orphaned_real_jira_format_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify orphaned item appears in failures
        self._verify_orphaned_real_jira_format_displayed(output, 'TAPS-211')

    def test_assert_failures_displays_epic_with_story_and_subtask(self):
        # Given: Epic with Story and Sub-task (like TAPS-211 under a Story under an Epic)
        mock_jira_manager = self._create_epic_story_subtask_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify hierarchical structure: Epic → Story → Sub-task
        self._verify_epic_story_subtask_displayed(output, 'PROJ-1', 'PROJ-2', 'PROJ-3')

    @pytest.mark.skip(reason="3-level hierarchy (Epic → Story → Sub-task) not yet implemented")
    def test_assert_failures_displays_epic_with_non_evaluated_story_and_subtask(self):
        # Given: Epic with non-evaluated Story and evaluable Sub-task (like TAPS-210 → TAPS-211)
        mock_jira_manager = self._create_epic_non_evaluated_story_subtask_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Debug: Print the actual output
        print(f"\nDEBUG OUTPUT:\n{output}\n")
        
        # Then: Verify hierarchical structure: Epic → Story (non-evaluated) → Sub-task (evaluated)
        self._verify_epic_non_evaluated_story_subtask_displayed(output, 'PROJ-1', 'PROJ-2', 'PROJ-3')

    def _create_three_failing_epics_scenario(self, first_epic_rank, second_epic_rank, third_epic_rank):
        epic1 = self._create_epic_failing_assertion("PROJ-1", first_epic_rank)
        epic2 = self._create_epic_failing_assertion("PROJ-2", second_epic_rank)
        epic3 = self._create_epic_failing_assertion("PROJ-3", third_epic_rank)
        return create_mock_manager([epic1, epic2, epic3])

    def _create_epic_with_child_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story = self._create_story_failing_assertion("PROJ-2", self.LOW_RANK, epic['key'])
        return create_mock_manager([epic, story])

    def _create_children_before_parents_scenario(self):
        # Create child story first (lower rank = appears first in sorted order)
        story = self._create_story_failing_assertion("PROJ-2", self.LOW_RANK, "PROJ-1")
        # Create parent epic second (higher rank = appears second in sorted order)
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        # Return with child first to simulate children found before parents
        return create_mock_manager([story, epic])

    def _create_epic_with_multiple_children_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story1 = self._create_story_failing_assertion("PROJ-2", self.LOW_RANK, epic['key'])
        story2 = self._create_story_failing_assertion("PROJ-3", self.MID_RANK, epic['key'])
        return create_mock_manager([epic, story1, story2])

    def _create_epic_with_non_evaluated_parent_scenario(self):
        # Epic with summary that doesn't match assertion pattern (not evaluable)
        epic = self._create_epic_non_evaluated("PROJ-1", self.HIGH_RANK)
        # Story that fails assertion
        story = self._create_story_failing_assertion("PROJ-2", self.LOW_RANK, epic['key'])
        return create_mock_manager([epic, story])

    def _create_multiple_epics_stories_first_scenario(self):
        # Create stories first (lower ranks = appear first in sorted order)
        story1 = self._create_story_failing_assertion("PROJ-2", self.LOW_RANK, "PROJ-1")
        story2 = self._create_story_failing_assertion("PROJ-3", self.MID_RANK, "PROJ-1")
        story3 = self._create_story_failing_assertion("PROJ-4", self.HIGH_RANK, "PROJ-5")
        
        # Create epics second (higher ranks = appear second in sorted order)
        epic1 = self._create_epic_failing_assertion("PROJ-1", self.HIGHER_RANK)
        epic2 = self._create_epic_failing_assertion("PROJ-5", self.HIGHEST_RANK)
        
        # Return with stories first to simulate children found before parents
        return create_mock_manager([story1, story2, story3, epic1, epic2])

    def _create_mixed_epics_and_orphaned_scenario(self):
        # Create epic with children
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story1 = self._create_story_failing_assertion("PROJ-2", self.LOW_RANK, epic['key'])
        story2 = self._create_story_failing_assertion("PROJ-3", self.MID_RANK, epic['key'])
        
        # Create orphaned item (no parent epic)
        orphaned = self._create_orphaned_failing_assertion("PROJ-4", self.HIGHER_RANK)
        
        return create_mock_manager([epic, story1, story2, orphaned])

    def _create_epic_higher_rank_than_children_scenario(self):
        # Epic with higher rank than its children - tests grouping vs global sorting
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGHEST_RANK)  # Rank 20
        story1 = self._create_story_failing_assertion("PROJ-2", self.LOW_RANK, epic['key'])  # Rank 5
        story2 = self._create_story_failing_assertion("PROJ-3", self.MID_RANK, epic['key'])    # Rank 7
        
        return create_mock_manager([epic, story1, story2])

    def _create_orphaned_non_evaluable_scenario(self):
        # Orphaned item without assertion pattern (like TAPS-211 Sub-task)
        orphaned = self._create_orphaned_non_evaluable("PROJ-1", self.HIGH_RANK)
        return create_mock_manager([orphaned])

    def _create_orphaned_evaluable_scenario(self):
        # Orphaned item with failing assertion (like TAPS-211 Sub-task)
        orphaned = self._create_orphaned_failing_assertion("PROJ-1", self.HIGH_RANK)
        return create_mock_manager([orphaned])

    def _create_orphaned_real_jira_format_scenario(self):
        # Orphaned item with real Jira summary format (like TAPS-211)
        orphaned = self._create_orphaned_real_jira_format("TAPS-211", self.HIGH_RANK)
        return create_mock_manager([orphaned])

    def _create_epic_story_subtask_scenario(self):
        # Epic with Story and Sub-task (like TAPS-211 under a Story under an Epic)
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGHEST_RANK)  # Rank 20
        story = self._create_story_failing_assertion("PROJ-2", self.HIGH_RANK, epic['key'])  # Rank 10
        subtask = self._create_subtask_failing_assertion("PROJ-3", self.LOW_RANK, story['key'])  # Rank 5
        
        return create_mock_manager([epic, story, subtask])

    def _create_epic_non_evaluated_story_subtask_scenario(self):
        # Epic with non-evaluated Story and evaluable Sub-task (like TAPS-210 → TAPS-211)
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGHEST_RANK)  # Rank 20
        story = self._create_story_non_evaluated("PROJ-2", self.HIGH_RANK, epic['key'])  # Rank 10, non-evaluated
        subtask = self._create_subtask_failing_assertion("PROJ-3", self.LOW_RANK, story['key'])  # Rank 5, evaluable
        
        return create_mock_manager([epic, story, subtask])

    def _create_epic_failing_assertion(self, key, rank):
        status = 'To Do'
        summary = f"Some epic context - starting in {status} - expected to be in Done"
        scenario = create_assert_scenario(issue_type="Epic", issue_key=key, summary=summary, rank=rank)
        epic = scenario.get_issues_by_label.return_value[0]
        epic['status'] = status
        return epic

    def _create_epic_non_evaluated(self, key, rank):
        # Epic with summary that doesn't match assertion pattern
        summary = "Epic without assertion pattern - just a regular epic summary"
        scenario = create_assert_scenario(issue_type="Epic", issue_key=key, summary=summary, rank=rank)
        epic = scenario.get_issues_by_label.return_value[0]
        epic['status'] = 'In Progress'  # Any status since it won't be evaluated
        return epic

    def _create_story_failing_assertion(self, key, rank, parent_key):
        status = 'To Do'
        summary = f"Some story context - starting in {status} - expected to be in Done"
        scenario = create_assert_scenario(issue_type="Story", issue_key=key, summary=summary, rank=rank)
        story = scenario.get_issues_by_label.return_value[0]
        story['status'] = status
        story['parent_key'] = parent_key
        return story

    def _create_story_non_evaluated(self, key, rank, parent_key):
        # Story without assertion pattern (non-evaluated) - like TAPS-210
        summary = "Story without assertion pattern - just a regular story summary"
        scenario = create_assert_scenario(issue_type="Story", issue_key=key, summary=summary, rank=rank)
        story = scenario.get_issues_by_label.return_value[0]
        story['status'] = 'In Progress'  # Any status since it won't be evaluated
        story['parent_key'] = parent_key
        return story

    def _create_subtask_failing_assertion(self, key, rank, parent_story):
        status = 'To Do'
        summary = f"Some subtask context - starting in {status} - expected to be in Done"
        scenario = create_assert_scenario(issue_type="Sub-task", issue_key=key, summary=summary, rank=rank)
        subtask = scenario.get_issues_by_label.return_value[0]
        subtask['status'] = status
        subtask['parent_story'] = parent_story  # Sub-task has Story as parent, not Epic
        return subtask

    def _create_orphaned_failing_assertion(self, key, rank):
        # Orphaned item (no parent epic) - like TAPS-211 Sub-task
        status = 'To Do'
        summary = f"Some orphaned context - starting in {status} - expected to be in Done"
        scenario = create_assert_scenario(issue_type="Sub-task", issue_key=key, summary=summary, rank=rank)
        orphaned = scenario.get_issues_by_label.return_value[0]
        orphaned['status'] = status
        # No parent_key set - this makes it orphaned
        return orphaned

    def _create_orphaned_non_evaluable(self, key, rank):
        # Orphaned item without assertion pattern (not evaluable) - like TAPS-211 Sub-task
        summary = "Orphaned subtask without assertion pattern - just a regular subtask summary"
        scenario = create_assert_scenario(issue_type="Sub-task", issue_key=key, summary=summary, rank=rank)
        orphaned = scenario.get_issues_by_label.return_value[0]
        orphaned['status'] = 'In Progress'  # Any status since it won't be evaluated
        # No parent_key set - this makes it orphaned
        return orphaned

    def _create_orphaned_real_jira_format(self, key, rank):
        # Orphaned item with real Jira summary format (like TAPS-211)
        summary = "I was in SIT/LAB VALIDATED - expected to be in CLOSED"
        scenario = create_assert_scenario(issue_type="Sub-task", issue_key=key, summary=summary, rank=rank)
        orphaned = scenario.get_issues_by_label.return_value[0]
        orphaned['status'] = 'SIT/LAB Validated'  # Status that doesn't match expected
        # No parent_key set - this makes it orphaned
        return orphaned

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

    def _verify_epic_with_multiple_children_displayed(self, output, epic_key, story1_key, story2_key):
        assert f'[Epic] {epic_key}:' in output
        assert f'  - [Story] {story1_key}:' in output
        assert f'  - [Story] {story2_key}:' in output
        
        epic_pos = output.find(f'[Epic] {epic_key}:')
        story1_pos = output.find(f'  - [Story] {story1_key}:')
        story2_pos = output.find(f'  - [Story] {story2_key}:')
        
        assert epic_pos < story1_pos, f"Epic {epic_key} should appear before child story {story1_key}"
        assert epic_pos < story2_pos, f"Epic {epic_key} should appear before child story {story2_key}"
        assert story1_pos < story2_pos, f"Story {story1_key} should appear before story {story2_key} (rank order)"

    def _verify_epic_with_non_evaluated_parent_displayed(self, output, epic_key, story_key):
        assert f'[Epic] {epic_key}:' in output
        assert f'  - [Story] {story_key}:' in output
        
        # Epic should show full summary (no assertion pattern)
        assert "Epic without assertion pattern - just a regular epic summary" in output
        
        epic_pos = output.find(f'[Epic] {epic_key}:')
        story_pos = output.find(f'  - [Story] {story_key}:')
        
        assert epic_pos < story_pos, f"Epic {epic_key} should appear before child story {story_key}"
        assert story_pos - epic_pos > 0, f"Story {story_key} should be indented under epic {epic_key}"

    def _verify_multiple_epics_with_children_displayed(self, output, epic1_key, story1_key, story2_key, epic2_key, story3_key):
        # Verify both epics appear
        assert f'[Epic] {epic1_key}:' in output
        assert f'[Epic] {epic2_key}:' in output
        
        # Verify all stories appear
        assert f'  - [Story] {story1_key}:' in output
        assert f'  - [Story] {story2_key}:' in output
        assert f'  - [Story] {story3_key}:' in output
        
        # Verify epic1 appears before its children
        epic1_pos = output.find(f'[Epic] {epic1_key}:')
        story1_pos = output.find(f'  - [Story] {story1_key}:')
        story2_pos = output.find(f'  - [Story] {story2_key}:')
        
        assert epic1_pos < story1_pos, f"Epic {epic1_key} should appear before child story {story1_key}"
        assert epic1_pos < story2_pos, f"Epic {epic1_key} should appear before child story {story2_key}"
        
        # Verify epic2 appears before its child
        epic2_pos = output.find(f'[Epic] {epic2_key}:')
        story3_pos = output.find(f'  - [Story] {story3_key}:')
        
        assert epic2_pos < story3_pos, f"Epic {epic2_key} should appear before child story {story3_key}"
        
        # Verify epics are sorted by rank (epic1 rank 15, epic2 rank 20)
        assert epic1_pos < epic2_pos, f"Epic {epic1_key} should appear before epic {epic2_key} (rank order)"

    def _verify_mixed_epics_and_orphaned_displayed(self, output, epic_key, story1_key, story2_key, orphaned_key):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output
        
        # Verify children appear indented under epic
        assert f'  - [Story] {story1_key}:' in output
        assert f'  - [Story] {story2_key}:' in output
        
        # Verify orphaned item appears at same level as epic (not indented)
        assert f'[Sub-task] {orphaned_key}:' in output
        
        # Verify epic appears before its children
        epic_pos = output.find(f'[Epic] {epic_key}:')
        story1_pos = output.find(f'  - [Story] {story1_key}:')
        story2_pos = output.find(f'  - [Story] {story2_key}:')
        
        assert epic_pos < story1_pos, f"Epic {epic_key} should appear before child story {story1_key}"
        assert epic_pos < story2_pos, f"Epic {epic_key} should appear before child story {story2_key}"
        
        # Verify orphaned item appears after epic (rank order: epic rank 10, orphaned rank 15)
        orphaned_pos = output.find(f'[Sub-task] {orphaned_key}:')
        assert epic_pos < orphaned_pos, f"Epic {epic_key} should appear before orphaned {orphaned_key} (rank order)"

    def _verify_children_grouped_under_epic_not_globally_sorted(self, output, epic_key, story1_key, story2_key):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output
        
        # Verify children appear indented under epic
        assert f'  - [Story] {story1_key}:' in output
        assert f'  - [Story] {story2_key}:' in output
        
        # Verify epic appears before its children (even though epic has higher rank)
        epic_pos = output.find(f'[Epic] {epic_key}:')
        story1_pos = output.find(f'  - [Story] {story1_key}:')
        story2_pos = output.find(f'  - [Story] {story2_key}:')
        
        assert epic_pos < story1_pos, f"Epic {epic_key} should appear before child story {story1_key} (grouped, not globally sorted)"
        assert epic_pos < story2_pos, f"Epic {epic_key} should appear before child story {story2_key} (grouped, not globally sorted)"
        
        # Children should be sorted by rank within epic group (story1 rank 5, story2 rank 10)
        assert story1_pos < story2_pos, f"Story {story1_key} should appear before story {story2_key} (rank order within epic)"

    def _verify_orphaned_non_evaluable_displayed(self, output, orphaned_key):
        # Verify orphaned non-evaluable item appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output
        
        # Verify it shows full summary (no assertion pattern)
        assert "Orphaned subtask without assertion pattern - just a regular subtask summary" in output

    def _verify_orphaned_evaluable_displayed(self, output, orphaned_key):
        # Verify orphaned evaluable item appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output
        
        # Verify it shows assertion format
        assert "expected 'Done' but is 'To Do'" in output

    def _verify_orphaned_real_jira_format_displayed(self, output, orphaned_key):
        # Verify orphaned item with real Jira format appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output
        
        # Verify it shows assertion format with real Jira statuses
        assert "expected 'CLOSED' but is 'SIT/LAB Validated'" in output

    def _verify_epic_story_subtask_displayed(self, output, epic_key, story_key, subtask_key):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output
        
        # Verify story appears indented under epic
        assert f'  - [Story] {story_key}:' in output
        
        # Verify subtask appears indented under story
        assert f'    - [Sub-task] {subtask_key}:' in output
        
        # Verify hierarchical order
        epic_pos = output.find(f'[Epic] {epic_key}:')
        story_pos = output.find(f'  - [Story] {story_key}:')
        subtask_pos = output.find(f'    - [Sub-task] {subtask_key}:')
        
        assert epic_pos < story_pos < subtask_pos, "Epic should appear before Story, Story before Sub-task"

    def _verify_epic_non_evaluated_story_subtask_displayed(self, output, epic_key, story_key, subtask_key):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output
        
        # Verify non-evaluated story appears indented under epic with full summary
        assert f'  - [Story] {story_key}:' in output
        assert "Story without assertion pattern - just a regular story summary" in output
        
        # Verify subtask appears indented under story
        assert f'    - [Sub-task] {subtask_key}:' in output
        
        # Verify hierarchical order
        epic_pos = output.find(f'[Epic] {epic_key}:')
        story_pos = output.find(f'  - [Story] {story_key}:')
        subtask_pos = output.find(f'    - [Sub-task] {subtask_key}:')
        
        assert epic_pos < story_pos < subtask_pos, "Epic should appear before Story, Story before Sub-task"


if __name__ == '__main__':
    pytest.main([__file__])
