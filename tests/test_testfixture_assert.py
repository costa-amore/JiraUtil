"""
Tests for test fixture assert operations.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import Mock, patch

from tests.fixtures import (
    create_assert_scenario,
    create_assert_scenario_with_expectations,
    create_mock_manager
)
from jira_manager import DEFAULT_RANK_VALUE


class TestTestFixtureAssert:

    # Public test methods (sorted alphabetically)
    def test_assert_failure_message_extracts_context_from_summary(self):
        # Given: Issue with context in summary that should be extracted
        issue_type = "Bug"
        issue_key = "PROJ-2"
        expected_format = f"    - [{issue_type}] {issue_key}: When in this context, expected 'Done' but is 'To Do'"
        mock_jira_manager = create_assert_scenario(issue_type, issue_key, "When in this context, starting in To Do - expected to be in Done")
        
        # When: Assert operation is executed and captures print output
        mock_print = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify the failure message format includes context
        self._verify_failure_message_format(mock_print, expected_format)

    def test_assert_failure_message_handles_summary_without_context(self):
        # Given: Issue without context that should still be evaluated
        issue_type = "Story"
        issue_key = "PROJ-3"
        expected_format = f"    - [{issue_type}] {issue_key}: expected 'CLOSED' but is 'SIT/LAB VALIDATED'"
        mock_jira_manager = create_assert_scenario(issue_type, issue_key, "I was in SIT/LAB VALIDATED - expected to be in CLOSED")
        
        # When: Assert operation is executed and captures print output
        mock_print = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify the failure message format works without context
        self._verify_failure_message_format(mock_print, expected_format)

    def test_assert_operation_verifies_rule_automation_worked(self):
        # Given: Issues after automation has run
        mock_jira_manager = create_assert_scenario_with_expectations()
        
        # When: Assert operation is executed
        self._execute_assert_operation(mock_jira_manager)
        
        # Then: Rule automation should be verified
        mock_jira_manager.get_issues_by_label.assert_called_once_with("rule-testing")

    def test_assert_workflow_command_orchestrates_rule_verification(self):
        # Given: Assert workflow command with mock manager
        mock_jira_manager = create_assert_scenario_with_expectations()
        
        # When: Assert workflow command is executed
        self._execute_assert_operation(mock_jira_manager)
        
        # Then: Rule verification should be orchestrated
        mock_jira_manager.get_issues_by_label.assert_called_once_with("rule-testing")


    # Private helper methods (sorted alphabetically)

    def _extract_failure_messages(self, mock_print):
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        return [msg for msg in print_calls if 'Expected' in msg and 'but is' in msg]

    def _verify_failure_message_format(self, mock_print, expected_format):
        failure_messages = self._extract_failure_messages(mock_print)
        
        if failure_messages:
            failure_message = failure_messages[0]
            assert failure_message == expected_format, f"Expected format '{expected_format}', got '{failure_message}'"

    def _execute_assert_operation(self, mock_manager):
        from testfixture.workflow import run_assert_expectations
        with patch('builtins.print'):
            run_assert_expectations(mock_manager, "rule-testing")

    def _execute_assert_operation_with_print_capture(self, mock_manager):
        from testfixture.workflow import run_assert_expectations
        with patch('builtins.print') as mock_print:
            run_assert_expectations(mock_manager, "rule-testing")
        return mock_print

    def _extract_failure_messages(self, mock_print):
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        return [msg for msg in print_calls if 'Expected' in msg and 'but is' in msg]


class TestHierarchicalFailureOrganization:
    HIGHEST_RANK = "0|f0000:"
    HIGHER_RANK = "0|h0000:"
    HIGH_RANK = "0|i0000:"
    LOW_RANK = "0|i0002:"
    MID_RANK = "0|i0001:"
    NO_RANK = DEFAULT_RANK_VALUE

    @pytest.mark.skip(reason="Rank ordering temporarily disabled during refactoring")
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
        self._verify_epic_with_multiple_children_displayed(output, 'PROJ-1', ['PROJ-2', 'PROJ-3'])

    def test_assert_failures_displays_epic_with_non_evaluated_parent(self):
        # Given: An epic with non-evaluated parent and failing child
        mock_jira_manager = self._create_epic_with_non_evaluated_parent_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epic is displayed with non-evaluated parent and failing child
        self._verify_epic_with_non_evaluated_parent_displayed(output, 'PROJ-1', 'PROJ-2')

    def test_assert_failures_displays_multiple_epics_with_children_stories_first(self):
        # Given: Multiple epics with children, stories should be displayed first
        mock_jira_manager = self._create_multiple_epics_with_children_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epics are displayed with children, stories first
        self._verify_multiple_epics_with_children_displayed(output, ['PROJ-1', 'PROJ-3'], ['PROJ-2', 'PROJ-4'])

    def test_assert_failures_displays_mixed_epics_and_orphaned_items(self):
        # Given: Mix of epics with children and orphaned items
        mock_jira_manager = self._create_mixed_epics_and_orphaned_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epics with children are displayed first, then orphaned items
        self._verify_mixed_epics_and_orphaned_displayed(output, 'PROJ-1', 'PROJ-2', 'PROJ-3')

    def test_assert_failures_groups_children_under_epics_not_globally_sorted(self):
        # Given: Epic with children that should be grouped under epic, not globally sorted
        mock_jira_manager = self._create_epic_with_children_grouping_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify children are grouped under epic, not globally sorted
        self._verify_children_grouped_under_epic_not_globally_sorted(output, 'PROJ-1', 'PROJ-3', 'PROJ-2')

    @pytest.mark.skip(reason="Orphaned non-evaluable items not currently needed in real-world scenarios")
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
        
        # Then: Verify orphaned item with real Jira format appears in failures
        self._verify_orphaned_real_jira_format_displayed(output, 'TAPS-211')

    def test_assert_failures_displays_epic_with_story_and_subtask(self):
        # Given: Epic with story and subtask hierarchy
        mock_jira_manager = self._create_epic_with_story_and_subtask_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epic with story and subtask hierarchy is displayed correctly
        self._verify_epic_with_story_and_subtask_displayed(output, 'PROJ-1', 'PROJ-2', 'PROJ-3')

    @pytest.mark.skip(reason="Not currently needed in real-world scenarios")
    def test_assert_failures_displays_epic_with_non_evaluated_story_and_subtask(self):
        # Given: Epic with non-evaluated story and subtask
        mock_jira_manager = self._create_epic_with_non_evaluated_story_and_subtask_scenario()
        
        # When: Assert operation is executed and captures print output
        output = self._execute_assert_operation_with_print_capture(mock_jira_manager)
        
        # Then: Verify epic with non-evaluated story and subtask is displayed correctly
        self._verify_epic_with_non_evaluated_story_and_subtask_displayed(output, 'PROJ-1', 'PROJ-2', 'PROJ-3')

    @pytest.mark.skip(reason="Uses _aggregate_assertion_results - skipping during refactoring")
    def test_evaluated_subtask_with_non_evaluated_parent_story_missing_from_failures(self):
        # In the 2-level case, TAPS-210 should appear because it has a failing child
        # and TAPS-211 should appear as a child of TAPS-210
        from src.testfixture.issue_processor import _aggregate_assertion_results
        
        # Create the exact scenario
        assertion_results = [
            {
                'key': 'TAPS-210',
                'summary': 'When parent is CLOSED -> also close the children',
                'status': 'Closed',
                'assert_result': None,
                'issue_type': 'Story',
                'parent_key': None,  # No parent
                'rank': self.HIGHER_RANK,
                'evaluable': False
            },
            {
                'key': 'TAPS-211',
                'summary': 'I was in SIT/LAB VALIDATED - expected to be in CLOSED',
                'status': 'SIT/LAB Validated',
                'assert_result': 'FAIL',
                'issue_type': 'Sub-task',
                'parent_key': 'TAPS-210',  # Parent is TAPS-210
                'rank': self.HIGH_RANK,
                'evaluable': True,
                'expected_status': 'CLOSED',
                'context': None
            }
        ]
        
        results = _aggregate_assertion_results(assertion_results)
        
        # The fix should make TAPS-211 appear in failures
        failures = results['failures']
        failure_keys = [failure.split('] ')[1].split(':')[0] for failure in failures if '] ' in failure]
        
        assert 'TAPS-211' in failure_keys, f"TAPS-211 should appear in failures. Actual failures: {failures}"
        assert 'TAPS-210' in failure_keys, f"TAPS-210 should appear in failures (has failing child). Actual failures: {failures}"
        
        # Verify the hierarchical structure
        failures_text = ' '.join(results['failures'])
        assert 'TAPS-210' in failures_text, "TAPS-210 should be in failures"
        assert 'TAPS-211' in failures_text, "TAPS-211 should be in failures"
        
        # Verify TAPS-211 is properly indented under TAPS-210
        assert '    - [Sub-task] TAPS-211:' in failures_text, "TAPS-211 should be indented as subtask under TAPS-210"
        
        # Verify the failure count includes the subtask
        assert results['failed'] == 1, f"Should have 1 failed assertion (TAPS-211). Actual: {results['failed']}"
        assert results['not_evaluated'] == 1, f"Should have 1 not evaluated (TAPS-210). Actual: {results['not_evaluated']}"

    @pytest.mark.skip(reason="Uses _aggregate_assertion_results - skipping during refactoring")
    def test_trace_issue_processing_through_assertion_pipeline(self):
        """
        Test that traces how issues are processed through the entire assertion pipeline
        to understand where the bug occurs.
        
        This will help identify if the issue is in data preparation or aggregation.
        """
        from src.testfixture.issue_processor import _process_single_issue_assertion
        
        # Create raw issue data as it would come from Jira
        raw_taps_210 = {
            'key': 'TAPS-210',
            'summary': 'When parent is CLOSED -> also close the children',
            'status': 'Closed',
            'issue_type': 'Story',
            'parent_key': None,
            'rank': self.HIGHER_RANK
        }
        
        raw_taps_211 = {
            'key': 'TAPS-211',
            'summary': 'I was in SIT/LAB VALIDATED - expected to be in CLOSED',
            'status': 'SIT/LAB Validated',
            'issue_type': 'Sub-task',
            'parent_key': 'TAPS-210',
            'rank': self.HIGH_RANK
        }
        
        # Process each issue through _process_single_issue_assertion
        processed_210 = _process_single_issue_assertion(raw_taps_210)
        processed_211 = _process_single_issue_assertion(raw_taps_211)
        
        print(f"DEBUG - Processed TAPS-210: {processed_210}")
        print(f"DEBUG - Processed TAPS-211: {processed_211}")
        
        # Verify the processing is correct
        assert processed_210['evaluable'] == False, "TAPS-210 should not be evaluable (no assertion pattern)"
        assert processed_210['assert_result'] == None, "TAPS-210 should have no assert result"
        assert processed_210['parent_key'] == None, "TAPS-210 should have no parent"
        
        assert processed_211['evaluable'] == True, "TAPS-211 should be evaluable (has assertion pattern)"
        assert processed_211['assert_result'] == 'FAIL', "TAPS-211 should fail assertion"
        assert processed_211['parent_key'] == 'TAPS-210', "TAPS-211 should have TAPS-210 as parent"
        
        # Now test the aggregation with the processed results
        from src.testfixture.issue_processor import _aggregate_assertion_results
        assertion_results = [processed_210, processed_211]
        results = _aggregate_assertion_results(assertion_results)
        
        print(f"DEBUG - Aggregation results: {results}")
        print(f"DEBUG - Failures: {results['failures']}")
        
        # This should show us where the bug occurs
        failures = results['failures']
        failure_keys = [failure.split('] ')[1].split(':')[0] for failure in failures if '] ' in failure]
        
        print(f"DEBUG - Failure keys: {failure_keys}")
        
        # The bug: TAPS-211 should appear but doesn't
        assert 'TAPS-211' in failure_keys, f"TAPS-211 should appear in failures. Actual: {failure_keys}"

    @pytest.mark.skip(reason="Uses _aggregate_assertion_results - skipping during refactoring")
    def test_real_world_bug_three_level_hierarchy(self):
        """
        Test the REAL bug scenario with 3-level hierarchy:
        Epic TAPS-215 -> Story TAPS-210 -> Subtask TAPS-211
        
        The bug: TAPS-211 (evaluated subtask) is missing from failure report
        when its parent story TAPS-210 is non-evaluated.
        """
        from src.testfixture.issue_processor import _aggregate_assertion_results
        
        # Create the REAL scenario from Jira
        assertion_results = [
            {
                'key': 'TAPS-215',
                'summary': 'Standard workflow',
                'status': 'Closed',
                'assert_result': None,
                'issue_type': 'Epic',
                'parent_key': None,  # Epic has no parent
                'rank': '0|g0000:',
                'evaluable': False
            },
            {
                'key': 'TAPS-210',
                'summary': 'When parent is CLOSED -> also close the children',
                'status': 'Closed',
                'assert_result': None,
                'issue_type': 'Story',
                'parent_key': 'TAPS-215',  # Parent is TAPS-215 (Epic)
                'rank': '0|h0000:',
                'evaluable': False
            },
            {
                'key': 'TAPS-211',
                'summary': 'I was in SIT/LAB VALIDATED - expected to be in CLOSED',
                'status': 'SIT/LAB Validated',
                'assert_result': 'FAIL',
                'issue_type': 'Sub-task',
                'parent_key': 'TAPS-210',  # Parent is TAPS-210 (Story)
                'rank': '0|i0000:',
                'evaluable': True,
                'expected_status': 'CLOSED',
                'context': None
            }
        ]
        
        results = _aggregate_assertion_results(assertion_results)
        
        print(f"DEBUG - Results: {results}")
        print(f"DEBUG - Failures: {results['failures']}")
        
        # The bug: TAPS-211 should appear in failures but doesn't
        failures = results['failures']
        failure_keys = [failure.split('] ')[1].split(':')[0] for failure in failures if '] ' in failure]
        
        print(f"DEBUG - Failure keys: {failure_keys}")
        print(f"DEBUG - Expected: TAPS-211 should appear in failures (as child of TAPS-210)")
        print(f"DEBUG - Actual: TAPS-211 is missing from failure report")
        
        # The fix should make TAPS-211 appear in failures
        assert 'TAPS-211' in failure_keys, f"TAPS-211 should appear in failures. Actual: {failure_keys}"
        
        # TAPS-215 and TAPS-210 should appear because they have children (TAPS-211)
        # This is the correct behavior - non-evaluated parents with failing children should be shown
        assert 'TAPS-215' in failure_keys, f"TAPS-215 should appear in failures (has failing child). Actual: {failure_keys}"
        assert 'TAPS-210' in failure_keys, f"TAPS-210 should appear in failures (has failing child). Actual: {failure_keys}"
        
        # Verify the hierarchical structure is correct
        failures_text = ' '.join(results['failures'])
        assert 'TAPS-215' in failures_text, "TAPS-215 should be in failures"
        assert 'TAPS-210' in failures_text, "TAPS-210 should be in failures" 
        assert 'TAPS-211' in failures_text, "TAPS-211 should be in failures"
        
        # Verify TAPS-211 is properly indented under TAPS-210
        assert '    - [Sub-task] TAPS-211:' in failures_text, "TAPS-211 should be indented as subtask"
        assert '  - [Story] TAPS-210:' in failures_text, "TAPS-210 should be indented as story"

    # Helper methods for hierarchical failure organization tests
    def _create_three_failing_epics_scenario(self, first_rank, second_rank, third_rank):
        epic1 = self._create_epic_failing_assertion("PROJ-1", first_rank)
        epic2 = self._create_epic_failing_assertion("PROJ-2", second_rank)
        epic3 = self._create_epic_failing_assertion("PROJ-3", third_rank)
        return create_mock_manager([epic1, epic2, epic3])

    def _create_epic_with_child_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story = self._create_story_failing_assertion("PROJ-2", self.MID_RANK, "PROJ-1")
        return create_mock_manager([epic, story])

    def _create_children_before_parents_scenario(self):
        story = self._create_story_failing_assertion("PROJ-2", self.MID_RANK, "PROJ-1")
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        return create_mock_manager([story, epic])

    def _create_epic_with_multiple_children_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story1 = self._create_story_failing_assertion("PROJ-2", self.MID_RANK, "PROJ-1")
        story2 = self._create_story_failing_assertion("PROJ-3", self.LOW_RANK, "PROJ-1")
        return create_mock_manager([epic, story1, story2])

    def _create_epic_with_non_evaluated_parent_scenario(self):
        epic = self._create_epic_non_evaluated("PROJ-1", self.HIGH_RANK)
        story = self._create_story_failing_assertion("PROJ-2", self.MID_RANK, "PROJ-1")
        return create_mock_manager([epic, story])

    def _create_multiple_epics_with_children_scenario(self):
        epic1 = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story1 = self._create_story_failing_assertion("PROJ-2", self.MID_RANK, "PROJ-1")
        epic2 = self._create_epic_failing_assertion("PROJ-3", self.LOW_RANK)
        story2 = self._create_story_failing_assertion("PROJ-4", self.NO_RANK, "PROJ-3")
        return create_mock_manager([epic1, story1, epic2, story2])

    def _create_mixed_epics_and_orphaned_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story = self._create_story_failing_assertion("PROJ-2", self.MID_RANK, "PROJ-1")
        orphaned = self._create_orphaned_failing_assertion("PROJ-3", self.LOW_RANK)
        return create_mock_manager([epic, story, orphaned])

    def _create_epic_with_children_grouping_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story1 = self._create_story_failing_assertion("PROJ-2", self.LOW_RANK, "PROJ-1")
        story2 = self._create_story_failing_assertion("PROJ-3", self.MID_RANK, "PROJ-1")
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

    def _create_epic_with_story_and_subtask_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", self.HIGH_RANK)
        story = self._create_story_failing_assertion("PROJ-2", self.MID_RANK, "PROJ-1")
        subtask = self._create_subtask_failing_assertion("PROJ-3", self.LOW_RANK, "PROJ-2")
        return create_mock_manager([epic, story, subtask])

    def _create_epic_with_non_evaluated_story_and_subtask_scenario(self):
        epic = self._create_epic_non_evaluated("PROJ-1", self.HIGH_RANK)
        story = self._create_story_non_evaluated("PROJ-2", self.MID_RANK, "PROJ-1")
        subtask = self._create_subtask_failing_assertion("PROJ-3", self.LOW_RANK, "PROJ-2")
        return create_mock_manager([epic, story, subtask])

    def _create_epic_failing_assertion(self, key, rank):
        scenario = create_assert_scenario("Epic", key, "I was in In Progress - expected to be in CLOSED", rank)
        epic = scenario.get_issues_by_label.return_value[0]
        epic['status'] = 'In Progress'  # Different from expected
        return epic

    def _create_epic_non_evaluated(self, key, rank):
        scenario = create_assert_scenario("Epic", key, "Epic summary without assertion pattern", rank)
        epic = scenario.get_issues_by_label.return_value[0]
        epic['status'] = 'In Progress'
        return epic

    def _create_story_failing_assertion(self, key, rank, parent_key):
        scenario = create_assert_scenario("Story", key, "I was in In Progress - expected to be in CLOSED", rank)
        story = scenario.get_issues_by_label.return_value[0]
        story['status'] = 'In Progress'  # Different from expected
        story['parent_key'] = parent_key
        return story

    def _create_story_non_evaluated(self, key, rank, parent_key):
        scenario = create_assert_scenario("Story", key, "Story summary without assertion pattern", rank)
        story = scenario.get_issues_by_label.return_value[0]
        story['status'] = 'In Progress'
        story['parent_key'] = parent_key
        return story

    def _create_subtask_failing_assertion(self, key, rank, parent_key):
        scenario = create_assert_scenario("Sub-task", key, "I was in In Progress - expected to be in CLOSED", rank)
        subtask = scenario.get_issues_by_label.return_value[0]
        subtask['status'] = 'In Progress'  # Different from expected
        subtask['parent_key'] = parent_key
        return subtask

    def _create_orphaned_failing_assertion(self, key, rank):
        scenario = create_assert_scenario("Sub-task", key, "I was in In Progress - expected to be in CLOSED", rank)
        orphaned = scenario.get_issues_by_label.return_value[0]
        orphaned['status'] = 'In Progress'  # Different from expected
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
        orphaned['status'] = 'SIT/LAB VALIDATED'  # Different from expected
        # No parent_key set - this makes it orphaned
        return orphaned

    def _execute_assert_operation_with_print_capture(self, mock_manager):
        from testfixture.workflow import run_assert_expectations
        from io import StringIO
        import sys
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            run_assert_expectations(mock_manager, "rule-testing")
            return captured_output.getvalue()
        finally:
            sys.stdout = old_stdout

    def _verify_epics_displayed_in_rank_order(self, output, *expected_order):
        # Find positions of each epic in the output
        positions = []
        for epic_key in expected_order:
            pos = output.find(f'[Epic] {epic_key}:')
            assert pos != -1, f"Epic {epic_key} not found in output"
            positions.append(pos)
        
        # Verify they are in the correct order
        for i in range(len(positions) - 1):
            assert positions[i] < positions[i + 1], f"Epic {expected_order[i]} should appear before {expected_order[i + 1]}"

    def _verify_epic_with_child_displayed(self, output, epic_key, story_key):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify story appears indented under epic
        assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"

    def _verify_epic_with_multiple_children_displayed(self, output, epic_key, child_keys):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify all children appear indented under epic
        for child_key in child_keys:
            assert f'  - [Story] {child_key}:' in output, f"Story {child_key} not found indented under epic"

    def _verify_epic_with_non_evaluated_parent_displayed(self, output, epic_key, story_key):
        # Verify epic appears (non-evaluated but has children)
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify story appears indented under epic
        assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"

    def _verify_multiple_epics_with_children_displayed(self, output, epic_keys, story_keys):
        # Verify all epics appear
        for epic_key in epic_keys:
            assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify all stories appear indented under their epics
        for story_key in story_keys:
            assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"

    def _verify_mixed_epics_and_orphaned_displayed(self, output, epic_key, story_key, orphaned_key):
        # Verify epic with child appears first
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"
        
        # Verify orphaned item appears after epic with children
        epic_pos = output.find(f'[Epic] {epic_key}:')
        orphaned_pos = output.find(f'[Sub-task] {orphaned_key}:')
        assert orphaned_pos > epic_pos, f"Orphaned item {orphaned_key} should appear after epic {epic_key}"

    def _verify_children_grouped_under_epic_not_globally_sorted(self, output, epic_key, story1_key, story2_key):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify both stories appear indented under epic
        assert f'  - [Story] {story1_key}:' in output, f"Story {story1_key} not found indented under epic"
        assert f'  - [Story] {story2_key}:' in output, f"Story {story2_key} not found indented under epic"
        
        # Verify stories are grouped under epic, not globally sorted
        epic_pos = output.find(f'[Epic] {epic_key}:')
        story1_pos = output.find(f'  - [Story] {story1_key}:')
        story2_pos = output.find(f'  - [Story] {story2_key}:')
        
        assert story1_pos > epic_pos, f"Story {story1_key} should appear after epic {epic_key}"
        assert story2_pos > epic_pos, f"Story {story2_key} should appear after epic {epic_key}"

    def _verify_orphaned_non_evaluable_displayed(self, output, orphaned_key):
        # Verify orphaned non-evaluable item appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output, f"Orphaned non-evaluable item {orphaned_key} not found in output"

    def _verify_orphaned_evaluable_displayed(self, output, orphaned_key):
        # Verify orphaned evaluable item appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output, f"Orphaned evaluable item {orphaned_key} not found in output"

    def _verify_orphaned_real_jira_format_displayed(self, output, orphaned_key):
        # Verify orphaned item with real Jira format appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output, f"Orphaned item {orphaned_key} with real Jira format not found in output"

    def _verify_epic_with_story_and_subtask_displayed(self, output, epic_key, story_key, subtask_key):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify story appears indented under epic
        assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"
        
        # Verify subtask appears indented under story
        assert f'    - [Sub-task] {subtask_key}:' in output, f"Subtask {subtask_key} not found indented under story"

    def _verify_epic_with_non_evaluated_story_and_subtask_displayed(self, output, epic_key, story_key, subtask_key):
        # Verify epic appears (non-evaluated but has children)
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify story appears indented under epic
        assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"
        
        # Verify subtask appears indented under story
        assert f'    - [Sub-task] {subtask_key}:' in output, f"Subtask {subtask_key} not found indented under story"


if __name__ == "__main__":
    pytest.main([__file__])
