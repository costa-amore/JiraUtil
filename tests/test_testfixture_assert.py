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
from enum import Enum


class RankValues(Enum):
    """Jira rank values used in test fixtures."""
    
    HIGHEST = "0|f0000:"
    HIGHER = "0|h0000:"
    HIGH = "0|i0000:"
    MID = "0|i0001:"
    LOW = "0|i0002:"
    LOWER = "0|i0003:"
    NO_RANK = "0|z0000:"  # Default rank value


# Convenience access to rank values
RANKS = RankValues

from tests.base_test_jira_utils_command import TestJiraUtilsCommand
from tests.fixtures import (
    create_assert_scenario,
    create_mock_manager
)
from tests.fixtures.base_fixtures import (
    create_mock_issue, execute_assert_testfixture_issues, 
    extract_issue_keys_from_report, verify_issue_in_report, 
    verify_issue_order, verify_context_extraction, DEFAULT_RANK_VALUE
)


class TestTestFixtureAssert(TestJiraUtilsCommand):

    # =============================================================================
    # PUBLIC TEST METHODS (sorted alphabetically)
    # =============================================================================

    @pytest.mark.parametrize("scenario,summary,current_state,expected_context,expected_start_state,expected_end_state", [
        ("extracts context from summary", "When in this context, starting in To Do - expected to be in Done", "In Progress", "When in this context,", "To Do", "Done"),
        ("handles summary without context", "I was in SIT/LAB VALIDATED - expected to be in CLOSED", "In Progress", None, "SIT/LAB VALIDATED", "CLOSED"),
        ("handles whitespace around states", "I was in    To Do    - expected to be in    CLOSED   ", "In Progress", None, "To Do", "CLOSED"),
    ])
    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_failure_message_extracts_context_and_states(self, mock_jira_class, scenario, summary, current_state, expected_context, expected_start_state, expected_end_state):
        # Given: Mock Jira manager with issue that has assertion failure (current != expected)
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, [
            {'key': 'PROJ-TEST', 'current': current_state, 'expected': expected_end_state, 'issue_type': 'Bug', 'context': expected_context, 'summary': summary}
        ])
        
        # When: Assert CLI command is executed with print capture
        mock_print = self._execute_JiraUtil_with_args('tf', 'a', '--tsl', 'rule-testing')
        
        # Then: Jira API should be called correctly
        mock_jira_instance.get_issues_by_label.assert_called_once_with("rule-testing")
        
        # And: The issue should appear in the output (since current != expected)
        printed_output = '\n'.join([call[0][0] for call in mock_print.call_args_list if call[0]])
        assert 'PROJ-TEST' in printed_output, f"Issue key should appear in output for scenario: {scenario}"
        
        # Verify context extraction from summary appears in output
        if expected_context:
            assert expected_context in printed_output, f"Context should appear in output for scenario: {scenario}"
        
        # Verify state information appears in output
        assert current_state in printed_output, f"Current state should appear in output for scenario: {scenario}"
        assert expected_end_state in printed_output, f"Expected state should appear in output for scenario: {scenario}"
        

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_cli_command_executes_successfully(self, mock_jira_class):
        # Given: Mock Jira manager with test issues for assertion testing
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, [
            {'key': 'PROJ-1', 'current': 'In Progress', 'expected': 'Done'},
            {'key': 'PROJ-2', 'current': 'Done',        'expected': 'Done'}
        ])
        
        # When: Assert CLI command is executed
        self._execute_JiraUtil_with_args('tf', 'a', '--tsl', 'rule-testing')
        
        # Then: Jira API should be called correctly
        mock_jira_instance.get_issues_by_label.assert_called_once_with("rule-testing")

    # =============================================================================
    # PRIVATE HELPER METHODS (sorted alphabetically)
    # =============================================================================



    def _execute_assert_operation_with_print_capture(self, mock_manager):
        from testfixture.workflow import run_assert_expectations
        with patch('builtins.print') as mock_print:
            run_assert_expectations(mock_manager, "rule-testing")
        return mock_print

    def _extract_failure_messages(self, mock_print):
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        return [msg for msg in print_calls if 'Expected' in msg and 'but is' in msg]

    def _verify_failure_message_format(self, mock_print, expected_format):
        failure_messages = self._extract_failure_messages(mock_print)
        
        if failure_messages:
            failure_message = failure_messages[0]
            assert failure_message == expected_format, f"Expected format '{expected_format}', got '{failure_message}'"

    def _extract_context_prefix_from_spec(self, spec):
        context = spec.get('context')
        if context is None and spec.get('issue_type') is not None:
            context = f"{spec.get('issue_type')}"
        return f"{context} - " if context else ""

    def _create_issue_data(self, spec, summary, current_state):
        return {
            'key': spec['key'],
            'summary': summary,
            'status': current_state,
            'issue_type': spec.get('issue_type', 'Story'),
            'parent_key': spec.get('parent_key'),
            'rank': spec.get('rank', '0|i0000:')
        }

    def _create_skipped_issue_from_spec(self, spec):
        summary = "Skipped issue"
        current_state = spec.get('current', 'New')
        return self._create_issue_data(spec, summary, current_state)

    def _create_passed_issue_from_spec(self, spec, i):
        context_prefix = self._extract_context_prefix_from_spec(spec)
        current_state = spec.get('current', 'New')
        expected_state = current_state
        summary = self._generate_summary(context_prefix, current_state, expected_state, i)
        return self._create_issue_data(spec, summary, current_state)

    def _create_failed_issue_from_spec(self, spec, i):
        context_prefix = self._extract_context_prefix_from_spec(spec)
        current_state = spec.get('current', 'New')
        expected_state = spec.get('expected', 'Done')
        if current_state == expected_state:  # Ensure they're different to trigger assertion failure
            expected_state = 'Ready' if current_state == 'New' else 'Done'
        summary = self._generate_summary(context_prefix, current_state, expected_state, i)
        return self._create_issue_data(spec, summary, current_state)

    def _create_scenario_with_issues_from_assertion_specs(self, mock_jira_class, issue_specs):
        issue_data_list = []
        
        for i, spec in enumerate(issue_specs):
            # Handle assert_result logic
            assert_result = spec.get('assert_result')
            if assert_result == 'Skip':
                issue_data_list.append(self._create_skipped_issue_from_spec(spec))
            elif assert_result == 'Pass':
                issue_data_list.append(self._create_passed_issue_from_spec(spec, i))
            else:  # assume 'Failed' or None
                issue_data_list.append(self._create_failed_issue_from_spec(spec, i))
        
        mock_jira_instance = Mock()
        mock_jira_instance.get_issues_by_label.return_value = issue_data_list
        mock_jira_instance.connect.return_value = True
        mock_jira_class.return_value = mock_jira_instance
        return mock_jira_instance

    def _generate_summary(self, context_prefix, current_state, expected_state, index):
        """Randomize the summary to use all possible valid evaluatable summary structures."""
        if index % 2 == 1:
            return f"{context_prefix}I was in {current_state} - expected to be in {expected_state}"
        else:
            return f"{context_prefix}starting in {current_state} - expected to be in {expected_state}"


class TestHierarchicalFailureOrganization(TestTestFixtureAssert):

    # =============================================================================
    # PUBLIC TEST METHODS (sorted alphabetically)
    # =============================================================================

    @pytest.mark.parametrize("test_name,issue_specs,expected_specs", [
        ("issue_type_category_sorting", [
            {'key': 'EPIC-1',   'issue_type': 'Epic',     'rank': RANKS.HIGH.value},
            {'key': 'STORY-11', 'issue_type': 'Story',    'rank': RANKS.LOW.value},
            {'key': 'SUBT-111', 'issue_type': 'Sub-task', 'rank': RANKS.MID.value}
        ], [
            {'line_with_key': 'EPIC-1'},
            {'line_with_key': 'SUBT-111'},
            {'line_with_key': 'STORY-11'}
        ]),
        ("epics_rank_sorting", [
            {'key': 'PROJ-1', 'issue_type': 'Epic', 'rank': RANKS.LOW.value},
            {'key': 'PROJ-2', 'issue_type': 'Epic', 'rank': RANKS.HIGH.value},
            {'key': 'PROJ-3', 'issue_type': 'Epic', 'rank': RANKS.MID.value}
        ], [
            {'line_with_key': 'PROJ-2'},
            {'line_with_key': 'PROJ-3'},
            {'line_with_key': 'PROJ-1'}
        ]),
        ("orphaned_evaluable_items", [
            {'key': 'PROJ-1', 'issue_type': 'Sub-task', 'parent_key': None, 'rank': RANKS.HIGH.value}
        ], [
            {'line_with_key': 'PROJ-1', 'contains': ['[FAIL]', '[Sub-task]']}
        ]),
        ("color_tags_epic", [
            {'key': 'TAPS-215', 'issue_type': 'Epic'}
        ], [
            {'line_with_key': 'TAPS-215', 'contains': ['[FAIL]', '[Epic]']}
        ]),
        ("color_tags_story", [
            {'key': 'TAPS-210', 'issue_type': 'Story'}
        ], [
            {'line_with_key': 'TAPS-210', 'contains': ['[FAIL]', '[Story]']}
        ]),
        ("color_tags_subtask", [
            {'key': 'TAPS-211', 'issue_type': 'Sub-task'}
        ], [
            {'line_with_key': 'TAPS-211', 'contains': ['[FAIL]', '[Sub-task]']}
        ]),
        ("mixed_pass_fail_assertions", [
            {'key': 'PROJ-1', 'current': 'In Progress', 'expected': 'Done'},
            {'key': 'PROJ-2', 'current': 'Done', 'expected': 'Done'}
        ], [
            {'line_with_key': 'PROJ-1', 'contains': ['[FAIL]']}
        ]),
        ("stories_within_epic_sorted_by_rank", [
            {'key': 'EPIC-1', 'issue_type': 'Epic', 'rank': RANKS.HIGH.value, 'parent_key': None},
            {'key': 'STORY-3', 'issue_type': 'Story', 'rank': RANKS.LOW.value, 'parent_key': 'EPIC-1'},
            {'key': 'STORY-1', 'issue_type': 'Story', 'rank': RANKS.HIGH.value, 'parent_key': 'EPIC-1'},
            {'key': 'STORY-2', 'issue_type': 'Story', 'rank': RANKS.MID.value, 'parent_key': 'EPIC-1'}
        ], [
            {'line_with_key': 'EPIC-1'},
            {'line_with_key': 'STORY-1'},
            {'line_with_key': 'STORY-2'},
            {'line_with_key': 'STORY-3'}
        ]),
        ("mixed_epics_and_orphaned_items", [
            {'key': 'PROJ-1', 'issue_type': 'Epic', 'rank': RANKS.HIGH.value, 'parent_key': None},
            {'key': 'PROJ-2', 'issue_type': 'Story', 'rank': RANKS.MID.value, 'parent_key': 'PROJ-1'},
            {'key': 'PROJ-3', 'issue_type': 'Sub-task', 'rank': RANKS.LOW.value, 'parent_key': None}
        ], [
            {'line_with_key': 'PROJ-1'},
            {'line_with_key': 'PROJ-2'},
            {'line_with_key': 'PROJ-3'}
        ]),
        ("multiple_epics_with_children", [
            {'key': 'PROJ-1', 'issue_type': 'Epic', 'rank': RANKS.LOW.value, 'parent_key': None},
            {'key': 'PROJ-2', 'issue_type': 'Story', 'rank': RANKS.MID.value, 'parent_key': 'PROJ-1'},
            {'key': 'PROJ-3', 'issue_type': 'Epic', 'rank': RANKS.HIGH.value, 'parent_key': None},
            {'key': 'PROJ-4', 'issue_type': 'Story', 'rank': RANKS.LOWER.value, 'parent_key': 'PROJ-3'}
        ], [
            {'line_with_key': 'PROJ-3'},
            {'line_with_key': 'PROJ-4'},
            {'line_with_key': 'PROJ-1'},
            {'line_with_key': 'PROJ-2'}
        ]),
        ("children_found_before_parents", [
            {'key': 'PROJ-2', 'issue_type': 'Story', 'rank': RANKS.MID.value, 'parent_key': 'PROJ-1'},
            {'key': 'PROJ-1', 'issue_type': 'Epic', 'rank': RANKS.HIGH.value, 'parent_key': None}
        ], [
            {'line_with_key': 'PROJ-1'},
            {'line_with_key': 'PROJ-2'}
        ])
    ])
    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_failures_sorting_behavior(self, mock_jira_class, test_name, issue_specs, expected_specs):
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, issue_specs)
        mock_print = self._execute_JiraUtil_with_args('tf', 'a', '--tsl', 'test-label')
        self._assert_issues_in_summary_section(mock_print, expected_specs)








    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_failures_displays_epic_with_non_evaluated_story_and_subtask(self, mock_jira_class):
        """Test 3-level hierarchy: Epic (non-evaluated) -> Story (non-evaluated) -> Subtask (failing)."""
        # Given: Epic with non-evaluated story and failing subtask (3-level hierarchy)
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, [
            {'key': 'PROJ-1', 'issue_type': 'Epic', 'rank': RANKS.HIGH.value, 'parent_key': None, 'summary': 'Epic without assertion pattern', 'current': 'Closed', 'assert_result': 'Skip'},
            {'key': 'PROJ-2', 'issue_type': 'Story', 'rank': RANKS.MID.value, 'parent_key': 'PROJ-1', 'summary': 'Story without assertion pattern', 'current': 'Closed', 'assert_result': 'Skip'},
            {'key': 'PROJ-3', 'issue_type': 'Sub-task', 'rank': RANKS.LOW.value, 'parent_key': 'PROJ-2', 'current': 'New', 'expected': 'Ready'}
        ])
        
        # When: Assert CLI command is executed
        mock_print = self._execute_JiraUtil_with_args('tf', 'a', '--tsl', 'test-label')
        
        # Then: All three levels should appear in CLI output in hierarchical order
        # Note: PROJ-1 and PROJ-2 appear in both the hierarchical structure and "Not evaluated" section
        # We only verify the hierarchical structure part
        clean_output = self._strip_ansi_codes(mock_print)
        clean_output_str = '\n'.join(clean_output)
        
        # Verify hierarchical structure: Epic -> Story -> Subtask
        assert 'PROJ-1' in clean_output_str, "Epic PROJ-1 should appear in output"
        assert 'PROJ-2' in clean_output_str, "Story PROJ-2 should appear in output" 
        assert 'PROJ-3' in clean_output_str, "Sub-task PROJ-3 should appear in output"
        
        # Verify the hierarchical indentation structure
        assert '- [INFO] [Epic] PROJ-1:' in clean_output_str, "Epic should appear with proper indentation"
        assert '  - [INFO] [Story] PROJ-2:' in clean_output_str, "Story should appear indented under Epic"
        assert '    - [FAIL] [Sub-task] PROJ-3:' in clean_output_str, "Sub-task should appear indented under Story"


    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_failures_skips_orphaned_non_evaluable_items(self, mock_jira_class):
        """Test that orphaned non-evaluable items are currently skipped and not included in issues_to_report."""
        # Given: An orphaned Sub-task without assertion pattern (non-evaluable)
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, [
            {'key': 'PROJ-1', 'issue_type': 'Sub-task', 'parent_key': None, 'assert_result': 'Skip'}
        ])
        
        # When: Assert CLI command is executed
        mock_print = self._execute_JiraUtil_with_args('tf', 'a', '--tsl', 'test-label')
        
        # Then: The orphaned non-evaluable item should be skipped and not appear in failure report
        clean_output = self._strip_ansi_codes(mock_print)
        clean_output_str = '\n'.join(clean_output)
        
        # Verify the item is processed but skipped
        assert 'Asserting PROJ-1:' in clean_output_str, "Item should be processed"
        assert "Skipping - summary doesn't match expected pattern" in clean_output_str, "Item should be skipped due to non-evaluable pattern"
        
        # Verify it appears in "Not evaluated" section but not in failures
        assert 'Not evaluated: PROJ-1' in clean_output_str, "Item should appear in not evaluated list"
        assert 'Failures:' not in clean_output_str or 'PROJ-1' not in clean_output_str.split('Failures:')[1], "Item should not appear in failures section"
        
        # Verify counts
        assert 'Assertions failed: 0' in clean_output_str, "Should have 0 failed assertions"
        assert 'Not evaluated: 1' in clean_output_str, "Should have 1 not evaluated"

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_failures_displays_orphaned_with_real_jira_format(self, mock_jira_class):
        """Test that orphaned item with real Jira format appears in issues_to_report."""
        # Given: An orphaned Sub-task with real Jira summary format (like TAPS-211)
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, [
            {'key': 'TAPS-211', 'issue_type': 'Sub-task', 'parent_key': None, 'summary': 'I was in SIT/LAB VALIDATED - expected to be in CLOSED', 'current': 'SIT/LAB Validated', 'expected': 'CLOSED'}
        ])
        
        # When: Assert CLI command is executed
        mock_print = self._execute_JiraUtil_with_args('tf', 'a', '--tsl', 'test-label')
        
        # Then: The orphaned item with real Jira format should appear in failures
        self._assert_issues_in_summary_section(mock_print, [
            {'line_with_key': 'TAPS-211', 'contains': ['[FAIL]', '[Sub-task]']}
        ])
        
        # Verify counts
        clean_output = self._strip_ansi_codes(mock_print)
        clean_output_str = '\n'.join(clean_output)
        assert 'Assertions failed: 1' in clean_output_str, "Should have 1 failed assertion"
        assert 'Not evaluated: 0' in clean_output_str, "Should have 0 not evaluated"

    def test_evaluated_subtask_with_non_evaluated_parent_story_missing_from_failures(self):
        """Test 2-level hierarchy: Story TAPS-210 -> Subtask TAPS-211 using real production code."""
        # Given: A story with a failing subtask (2-level hierarchy)
        mock_jira_manager = create_mock_manager()
        mock_issues = [
            create_mock_issue(
                key='TAPS-210',
                summary='When parent is CLOSED -> also close the children',
                status='Closed',
                issue_type='Story',
                rank=RANKS.HIGHER.value
            ),
            create_mock_issue(
                key='TAPS-211',
                summary='I was in SIT/LAB VALIDATED - expected to be in CLOSED',
                status='SIT/LAB Validated',
                issue_type='Sub-task',
                parent_key='TAPS-210',
                rank=DEFAULT_RANK_VALUE
            )
        ]
        
        # When: The assert operation is executed
        results = execute_assert_testfixture_issues(mock_jira_manager, mock_issues)
        
        # Then: The story should appear but subtask should be missing (current bug)
        issues_to_report = results['issues_to_report']
        verify_issue_in_report(issues_to_report, 'TAPS-210', "TAPS-210 should appear in issues_to_report")
        
        # BUG: TAPS-211 should appear in issues_to_report (the failing subtask) but currently doesn't
        # This test documents the current behavior - TAPS-211 is processed but not included in issues_to_report
        # TODO: Fix the production code to include failing subtasks in issues_to_report
        issue_keys = extract_issue_keys_from_report(issues_to_report)
        assert 'TAPS-211' not in issue_keys, f"BUG: TAPS-211 should appear in issues_to_report but currently doesn't. Actual: {issue_keys}"
        
        # Verify counts
        assert results['failed'] == 1, f"Should have 1 failed assertion (TAPS-211). Actual: {results['failed']}"
        assert results['not_evaluated'] == 1, f"Should have 1 not evaluated (TAPS-210). Actual: {results['not_evaluated']}"

    def test_real_world_bug_three_level_hierarchy(self):
        """Test 3-level hierarchy: Epic TAPS-215 -> Story TAPS-210 -> Subtask TAPS-211."""
        # Given: 3-level hierarchy with real production data
        mock_jira_manager = create_mock_manager()
        mock_issues = [
            create_mock_issue(
                key='TAPS-215',
                summary='Standard workflow',
                status='Closed',
                issue_type='Epic',
                parent_key=None,
                rank='0|g0000:'
            ),
            create_mock_issue(
                key='TAPS-210',
                summary='When parent is CLOSED -> also close the children',
                status='Closed',
                issue_type='Story',
                parent_key='TAPS-215',
                rank='0|h0000:'
            ),
            create_mock_issue(
                key='TAPS-211',
                summary='I was in SIT/LAB VALIDATED - expected to be in CLOSED',
                status='SIT/LAB Validated',
                issue_type='Sub-task',
                parent_key='TAPS-210',
                rank='0|i0000:'
            )
        ]
        
        # When: The assert operation is executed
        results = execute_assert_testfixture_issues(mock_jira_manager, mock_issues)
        
        # Then: All three levels should appear in hierarchical order
        issues_to_report = results['issues_to_report']
        
        verify_issue_in_report(issues_to_report, 'TAPS-215', "Epic TAPS-215 should appear in issues_to_report")
        verify_issue_in_report(issues_to_report, 'TAPS-210', "Story TAPS-210 should appear in issues_to_report")
        verify_issue_in_report(issues_to_report, 'TAPS-211', "Subtask TAPS-211 should appear in issues_to_report")
        
        verify_issue_order(issues_to_report, 'TAPS-215', 'TAPS-210', "Epic should appear before Story")
        verify_issue_order(issues_to_report, 'TAPS-210', 'TAPS-211', "Story should appear before Subtask")
        
        assert results['failed'] == 1, f"Should have 1 failed assertion (TAPS-211). Actual: {results['failed']}"
        assert results['not_evaluated'] == 2, f"Should have 2 not evaluated (TAPS-215, TAPS-210). Actual: {results['not_evaluated']}"

    def test_trace_issue_processing_through_assertion_pipeline(self):
        """Test that traces how issues are processed through the entire assertion pipeline."""
        # Given: 2-level hierarchy with non-evaluable parent and failing child
        mock_jira_manager = create_mock_manager()
        mock_issues = [
            create_mock_issue(
                key='TAPS-210',
                summary='When parent is CLOSED -> also close the children',
                status='Closed',
                issue_type='Story',
                parent_key=None,
                rank=RANKS.HIGHER.value
            ),
            create_mock_issue(
                key='TAPS-211',
                summary='I was in SIT/LAB VALIDATED - expected to be in CLOSED',
                status='SIT/LAB Validated',
                issue_type='Sub-task',
                parent_key='TAPS-210',
                rank=DEFAULT_RANK_VALUE
            )
        ]
        
        # When: The assert operation is executed
        results = execute_assert_testfixture_issues(mock_jira_manager, mock_issues)
        
        # Then: Processing should complete with expected counts
        assert results['success'] == True, "Processing should be successful"
        assert results['processed'] == 2, "Should process 2 issues"
        assert results['failed'] == 1, "Should have 1 failed assertion (TAPS-211)"
        assert results['not_evaluated'] == 1, "Should have 1 not evaluated (TAPS-210)"
        
        # And: Issues should appear in the report
        issues_to_report = results['issues_to_report']
        assert len(issues_to_report) > 0, "issues_to_report should not be empty"
        
        verify_issue_in_report(issues_to_report, 'TAPS-210', "TAPS-210 should appear in issues_to_report")
        # BUG: TAPS-211 should be in issues_to_report but currently isn't for 2-level hierarchies
        issue_keys = extract_issue_keys_from_report(issues_to_report)
        assert 'TAPS-211' not in issue_keys, f"BUG: TAPS-211 should be in issues_to_report but currently isn't for 2-level hierarchies. Actual: {issue_keys}"

    # =============================================================================
    # PRIVATE HELPER METHODS (sorted alphabetically)
    # =============================================================================


    def _create_children_before_parents_scenario(self):
        story = self._create_story_failing_assertion("PROJ-2", RANKS.MID.value, "PROJ-1")
        epic = self._create_epic_failing_assertion("PROJ-1", RANKS.HIGH.value)
        return create_mock_manager([story, epic])

    def _create_epic_failing_assertion(self, key, rank):
        return self._create_issue_assertion("Epic", key, rank, evaluable=True)

    def _create_epic_non_evaluated(self, key, rank):
        return self._create_issue_assertion("Epic", key, rank, evaluable=False)

    def _create_epic_with_child_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", RANKS.HIGH.value)
        story = self._create_story_failing_assertion("PROJ-2", RANKS.MID.value, "PROJ-1")
        return create_mock_manager([epic, story])

    def _create_epic_with_children_grouping_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", RANKS.HIGH.value)
        story1 = self._create_story_failing_assertion("PROJ-2", RANKS.LOW.value, "PROJ-1")
        story2 = self._create_story_failing_assertion("PROJ-3", RANKS.MID.value, "PROJ-1")
        return create_mock_manager([epic, story1, story2])

    def _create_epic_with_multiple_children_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", RANKS.HIGH.value)
        story1 = self._create_story_failing_assertion("PROJ-2", RANKS.MID.value, "PROJ-1")
        story2 = self._create_story_failing_assertion("PROJ-3", RANKS.LOW.value, "PROJ-1")
        return create_mock_manager([epic, story1, story2])

    def _create_epic_with_non_evaluated_parent_scenario(self):
        epic = self._create_epic_non_evaluated("PROJ-1", RANKS.HIGH.value)
        story = self._create_story_failing_assertion("PROJ-2", RANKS.MID.value, "PROJ-1")
        return create_mock_manager([epic, story])

    def _create_epic_with_non_evaluated_story_and_subtask_scenario(self):
        epic = self._create_epic_non_evaluated("PROJ-1", RANKS.HIGH.value)
        story = self._create_story_non_evaluated("PROJ-2", RANKS.MID.value, "PROJ-1")
        subtask = self._create_subtask_failing_assertion("PROJ-3", RANKS.LOW.value, "PROJ-2")
        return create_mock_manager([epic, story, subtask])

    def _create_epic_with_story_and_subtask_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", RANKS.HIGH.value)
        story = self._create_story_failing_assertion("PROJ-2", RANKS.MID.value, "PROJ-1")
        subtask = self._create_subtask_failing_assertion("PROJ-3", RANKS.LOW.value, "PROJ-2")
        return create_mock_manager([epic, story, subtask])

    def _create_issue_assertion(self, issue_type, key, rank, parent_key=None, evaluable=True, status_override=None):
        """Generic method to create issue assertions with different configurations."""
        if evaluable:
            summary = "I was in In Progress - expected to be in CLOSED"
        else:
            summary = f"{issue_type} summary without assertion pattern"
        
        scenario = create_assert_scenario(issue_type, key, summary, rank)
        issue = scenario.get_issues_by_label.return_value[0]
        issue['status'] = status_override or 'In Progress'
        
        if parent_key is not None:
            issue['parent_key'] = parent_key
        
        return issue

    def _create_mixed_epics_and_orphaned_scenario(self):
        epic = self._create_epic_failing_assertion("PROJ-1", RANKS.HIGH.value)
        story = self._create_story_failing_assertion("PROJ-2", RANKS.MID.value, "PROJ-1")
        orphaned = self._create_orphaned_failing_assertion("PROJ-3", RANKS.LOW.value)
        return create_mock_manager([epic, story, orphaned])

    def _create_multiple_epics_with_children_scenario(self):
        epic1 = self._create_epic_failing_assertion("PROJ-1", RANKS.HIGH.value)
        story1 = self._create_story_failing_assertion("PROJ-2", RANKS.MID.value, "PROJ-1")
        epic2 = self._create_epic_failing_assertion("PROJ-3", RANKS.LOW.value)
        story2 = self._create_story_failing_assertion("PROJ-4", RANKS.NO_RANK.value, "PROJ-3")
        return create_mock_manager([epic1, story1, epic2, story2])

    def _create_orphaned_evaluable_scenario(self):
        # Orphaned item with failing assertion (like TAPS-211 Sub-task)
        orphaned = self._create_orphaned_failing_assertion("PROJ-1", RANKS.HIGH.value)
        return create_mock_manager([orphaned])

    def _create_orphaned_failing_assertion(self, key, rank):
        return self._create_issue_assertion("Sub-task", key, rank, evaluable=True)

    def _create_orphaned_non_evaluable(self, key, rank):
        return self._create_issue_assertion("Sub-task", key, rank, evaluable=False)

    def _create_orphaned_non_evaluable_scenario(self):
        # Orphaned item without assertion pattern (like TAPS-211 Sub-task)
        orphaned = self._create_orphaned_non_evaluable("PROJ-1", RANKS.HIGH.value)
        return create_mock_manager([orphaned])

    def _create_orphaned_real_jira_format(self, key, rank):
        # Special case for real Jira format
        summary = "I was in SIT/LAB VALIDATED - expected to be in CLOSED"
        scenario = create_assert_scenario(issue_type="Sub-task", issue_key=key, summary=summary, rank=rank)
        orphaned = scenario.get_issues_by_label.return_value[0]
        orphaned['status'] = 'SIT/LAB VALIDATED'
        return orphaned

    def _create_orphaned_real_jira_format_scenario(self):
        # Orphaned item with real Jira summary format (like TAPS-211)
        orphaned = self._create_orphaned_real_jira_format("TAPS-211", RANKS.HIGH.value)
        return create_mock_manager([orphaned])

    def _create_story_failing_assertion(self, key, rank, parent_key):
        return self._create_issue_assertion("Story", key, rank, parent_key, evaluable=True)

    def _create_story_non_evaluated(self, key, rank, parent_key):
        return self._create_issue_assertion("Story", key, rank, parent_key, evaluable=False)

    def _create_subtask_failing_assertion(self, key, rank, parent_key):
        return self._create_issue_assertion("Sub-task", key, rank, parent_key, evaluable=True)

    def _create_three_failing_epics_scenario(self, first_rank, second_rank, third_rank):
        epic1 = self._create_epic_failing_assertion("PROJ-1", first_rank)
        epic2 = self._create_epic_failing_assertion("PROJ-2", second_rank)
        epic3 = self._create_epic_failing_assertion("PROJ-3", third_rank)
        return create_mock_manager([epic1, epic2, epic3])

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

    def _verify_epic_with_non_evaluated_story_and_subtask_displayed(self, output, epic_key, story_key, subtask_key):
        # Verify epic appears (non-evaluated but has children)
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify story appears indented under epic
        assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"
        
        # Verify subtask appears indented under story
        assert f'    - [Sub-task] {subtask_key}:' in output, f"Subtask {subtask_key} not found indented under story"

    def _verify_epic_with_story_and_subtask_displayed(self, output, epic_key, story_key, subtask_key):
        # Verify epic appears
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify story appears indented under epic
        assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"
        
        # Verify subtask appears indented under story
        assert f'    - [Sub-task] {subtask_key}:' in output, f"Subtask {subtask_key} not found indented under story"

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

    def _verify_mixed_epics_and_orphaned_displayed(self, output, epic_key, story_key, orphaned_key):
        # Verify epic with child appears first
        assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"
        
        # Verify orphaned item appears after epic with children
        epic_pos = output.find(f'[Epic] {epic_key}:')
        orphaned_pos = output.find(f'[Sub-task] {orphaned_key}:')
        assert orphaned_pos > epic_pos, f"Orphaned item {orphaned_key} should appear after epic {epic_key}"

    def _verify_multiple_epics_with_children_displayed(self, output, epic_keys, story_keys):
        # Verify all epics appear
        for epic_key in epic_keys:
            assert f'[Epic] {epic_key}:' in output, f"Epic {epic_key} not found in output"
        
        # Verify all stories appear indented under their epics
        for story_key in story_keys:
            assert f'  - [Story] {story_key}:' in output, f"Story {story_key} not found indented under epic"

    def _verify_orphaned_evaluable_displayed(self, output, orphaned_key):
        # Verify orphaned evaluable item appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output, f"Orphaned evaluable item {orphaned_key} not found in output"

    def _verify_orphaned_non_evaluable_displayed(self, output, orphaned_key):
        # Verify orphaned non-evaluable item appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output, f"Orphaned non-evaluable item {orphaned_key} not found in output"

    def _verify_orphaned_real_jira_format_displayed(self, output, orphaned_key):
        # Verify orphaned item with real Jira format appears in failures
        assert f'[Sub-task] {orphaned_key}:' in output, f"Orphaned item {orphaned_key} with real Jira format not found in output"

    # =============================================================================
    # NEW TESTS USING assert_testfixture_issues WITH MOCK JIRA DATA
    # =============================================================================

    def test_assert_testfixture_issues_two_level_hierarchy_with_mock_jira(self):
        """Test 2-level hierarchy: Story TAPS-210 -> Subtask TAPS-211 using mock Jira data."""
        # Given: 2-level hierarchy with non-evaluable parent and failing child
        mock_jira_manager = create_mock_manager()
        mock_issues = [
            create_mock_issue(
                key='TAPS-210',
                summary='When parent is CLOSED -> also close the children',
                status='Closed',
                issue_type='Story',
                parent_key=None,
                rank=RANKS.HIGHER.value
            ),
            create_mock_issue(
                key='TAPS-211',
                summary='I was in SIT/LAB VALIDATED - expected to be in CLOSED',
                status='SIT/LAB Validated',
                issue_type='Sub-task',
                parent_key='TAPS-210',
                rank=DEFAULT_RANK_VALUE
            )
        ]
        
        # When: The assert operation is executed
        results = execute_assert_testfixture_issues(mock_jira_manager, mock_issues)
        
        # Then: Parent should appear but child should be missing (current bug)
        issues_to_report = results['issues_to_report']
        
        verify_issue_in_report(issues_to_report, 'TAPS-210', "TAPS-210 should appear in issues_to_report (has failing child)")
        
        # BUG: TAPS-211 should appear in issues_to_report but currently doesn't for 2-level hierarchies
        issue_keys = extract_issue_keys_from_report(issues_to_report)
        assert 'TAPS-211' not in issue_keys, f"BUG: TAPS-211 should appear in issues_to_report but currently doesn't. Actual: {issue_keys}"
        
        assert results['failed'] == 1, f"Should have 1 failed assertion (TAPS-211). Actual: {results['failed']}"
        assert results['not_evaluated'] == 1, f"Should have 1 not evaluated (TAPS-210). Actual: {results['not_evaluated']}"

    def test_assert_testfixture_issues_three_level_hierarchy_with_mock_jira(self):
        """Test 3-level hierarchy: Epic TAPS-215 -> Story TAPS-210 -> Subtask TAPS-211 using mock Jira data."""
        # Given: 3-level hierarchy with real production data
        mock_jira_manager = create_mock_manager()
        mock_issues = [
            create_mock_issue(
                key='TAPS-215',
                summary='Standard workflow',
                status='Closed',
                issue_type='Epic',
                parent_key=None,
                rank='0|g0000:'
            ),
            create_mock_issue(
                key='TAPS-210',
                summary='When parent is CLOSED -> also close the children',
                status='Closed',
                issue_type='Story',
                parent_key='TAPS-215',
                rank='0|h0000:'
            ),
            create_mock_issue(
                key='TAPS-211',
                summary='I was in SIT/LAB VALIDATED - expected to be in CLOSED',
                status='SIT/LAB Validated',
                issue_type='Sub-task',
                parent_key='TAPS-210',
                rank='0|i0000:'
            )
        ]
        
        # When: The assert operation is executed
        results = execute_assert_testfixture_issues(mock_jira_manager, mock_issues)
        
        # Then: All three levels should appear in hierarchical order
        issues_to_report = results['issues_to_report']
        
        verify_issue_in_report(issues_to_report, 'TAPS-215', "Epic TAPS-215 should appear in issues_to_report")
        verify_issue_in_report(issues_to_report, 'TAPS-210', "Story TAPS-210 should appear in issues_to_report")
        verify_issue_in_report(issues_to_report, 'TAPS-211', "Subtask TAPS-211 should appear in issues_to_report")
        
        verify_issue_order(issues_to_report, 'TAPS-215', 'TAPS-210', "Epic should appear before Story")
        verify_issue_order(issues_to_report, 'TAPS-210', 'TAPS-211', "Story should appear before Subtask")
        
        assert results['failed'] == 1, f"Should have 1 failed assertion (TAPS-211). Actual: {results['failed']}"
        assert results['not_evaluated'] == 2, f"Should have 2 not evaluated (TAPS-215, TAPS-210). Actual: {results['not_evaluated']}"

    def test_assert_testfixture_issues_trace_processing_with_mock_jira(self):
        """Test that traces how issues are processed through the entire assertion pipeline using mock Jira data."""
        # Given: 2-level hierarchy with non-evaluable parent and failing child
        mock_jira_manager = create_mock_manager()
        mock_issues = [
            create_mock_issue(
                key='TAPS-210',
                summary='When parent is CLOSED -> also close the children',
                status='Closed',
                issue_type='Story',
                parent_key=None,
                rank=RANKS.HIGHER.value
            ),
            create_mock_issue(
                key='TAPS-211',
                summary='I was in SIT/LAB VALIDATED - expected to be in CLOSED',
                status='SIT/LAB Validated',
                issue_type='Sub-task',
                parent_key='TAPS-210',
                rank=DEFAULT_RANK_VALUE
            )
        ]
        
        # When: The assert operation is executed
        results = execute_assert_testfixture_issues(mock_jira_manager, mock_issues)
        
        # Then: Processing should complete with expected counts
        assert results['success'] == True, "Processing should be successful"
        assert results['processed'] == 2, "Should process 2 issues"
        assert results['failed'] == 1, "Should have 1 failed assertion (TAPS-211)"
        assert results['not_evaluated'] == 1, "Should have 1 not evaluated (TAPS-210)"
        
        # And: Issues should appear in the report
        issues_to_report = results['issues_to_report']
        assert len(issues_to_report) > 0, "issues_to_report should not be empty"
        
        verify_issue_in_report(issues_to_report, 'TAPS-210', "TAPS-210 should appear in issues_to_report")
        # BUG: TAPS-211 should be in issues_to_report but currently isn't
        issue_keys = extract_issue_keys_from_report(issues_to_report)
        assert 'TAPS-211' not in issue_keys, f"BUG: TAPS-211 should be in issues_to_report but currently isn't. Actual: {issue_keys}"

    # =============================================================================
    # PRIVATE HELPER METHODS (sorted alphabetically)
    # =============================================================================

    def _assert_issues_in_summary_section(self, mock_print, issue_specs, in_order=True):
        """
        Assert that issues appear in the summary section with expected tags and order.
        
        Args:
            mock_print: Mock print object from CLI execution
            issue_specs: List of dicts with 'line_with_key' and optional 'contains'
                        If 'contains' is provided, verifies tags are on same line as key
                        If multiple specs provided, 
                            by default it verifies they appear in the given order
                            unless 'in_order' is set to false, then just verify existence 
            in_order: default: True
        """

        summary_lines = self._extract_summary_section(mock_print)
        
        # Extract issue keys and their lines from summary section
        issue_data = {}
        for line in summary_lines:
            for spec in issue_specs:
                key = spec['line_with_key']
                if key in line and key not in issue_data:
                    issue_data[key] = line
                    break
        
        # Verify all expected issues appear in summary section
        expected_keys = [spec['line_with_key'] for spec in issue_specs]
        missing_keys = [key for key in expected_keys if key not in issue_data]
        assert not missing_keys, f"Issues missing from summary section: {missing_keys}"
        
        # Verify each issue appears exactly once
        for key in expected_keys:
            count = sum(1 for line in summary_lines if key in line)
            assert count == 1, f"Issue {key} should appear exactly once in summary section, found {count} times"
        
        # Verify contains if provided
        for spec in issue_specs:
            key = spec['line_with_key']
            contains = spec.get('contains', [])
            if contains:
                line = issue_data[key]
                for tag in contains:
                    assert tag in line, f"Line containing {key} should contain '{tag}'. Line: {line}"
        
        # Verify order if requested
        if in_order:
            issue_keys = []
            seen_keys = set()
            for line in summary_lines:
                for spec in issue_specs:
                    key = spec['line_with_key']
                    if key in line and key not in seen_keys:
                        issue_keys.append(key)
                        seen_keys.add(key)
                        break
            
            expected_order = [spec['line_with_key'] for spec in issue_specs]
            assert issue_keys == expected_order, f"Issues appear in processing order. Expected: {expected_order}, Actual: {issue_keys}"


    def _extract_summary_section(self, mock_print):
        clean_lines = self._strip_ansi_codes(mock_print)

        # Find the summary section (after "Assertion process completed:")
        summary_start = self._find_summary_section_start(clean_lines)

        assert summary_start is not None, "Summary section not found in output"
        return clean_lines[summary_start:]
 

    def _find_summary_section_start(self, lines):
        # Find the line index where the summary section begins after "Assertion process completed:"
        for i, line in enumerate(lines):
            if "Assertion process completed:" in line:
                return i
        return None


    def _strip_ansi_codes(self, mock_print):
        # Join all printed lines 
        # to remove ANSI escape sequences in one go
        # which makes assertions easier

        printed_output = '\n'.join([call[0][0] for call in mock_print.call_args_list if call[0]])

        import re
        lines = re.sub(r'\x1b\[[0-9;]*m', '', printed_output)

        return lines.split('\n')




if __name__ == "__main__":
    pytest.main([__file__])