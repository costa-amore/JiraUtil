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

from src.jira_manager import DEFAULT_RANK_VALUE
from tests.base_test_jira_utils_command import TestJiraUtilsCommand


class RankValues(Enum):
    """Jira rank values used in test fixtures."""
    
    HIGHEST = "0|f0000:"
    HIGHER = "0|h0000:"
    HIGH = "0|i0000:"
    MID = "0|i0001:"
    LOW = "0|i0002:"
    LOWER = "0|i0003:"
    NO_RANK = DEFAULT_RANK_VALUE  # JIRA's actual default rank value


# Convenience access to rank values
RANKS = RankValues


class TestTestFixtureAssert(TestJiraUtilsCommand):
    # =============================================================================
    # PUBLIC TEST METHODS (sorted alphabetically)
    # =============================================================================

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

    # =============================================================================
    # PRIVATE HELPER METHODS (sorted alphabetically)
    # =============================================================================

    def _create_failed_issue_from_spec(self, spec, i):
        context_prefix = self._extract_context_prefix_from_spec(spec)
        current_state = spec.get('current', 'New')
        expected_state = spec.get('expected', 'Done')
        if current_state == expected_state:  # Ensure they're different to trigger assertion failure
            expected_state = 'Ready' if current_state == 'New' else 'Done'
        summary = self._generate_summary(context_prefix, current_state, expected_state, i)
        return self._create_issue_data(spec, summary, current_state)

    def _create_issue_data(self, spec, summary, current_state):
        return {
            'key': spec['key'],
            'summary': summary,
            'status': current_state,
            'issue_type': spec.get('issue_type', 'Story'),
            'parent_key': spec.get('parent_key'),
            'rank': spec.get('rank', '0|i0000:')
        }

    def _create_passed_issue_from_spec(self, spec, i):
        context_prefix = self._extract_context_prefix_from_spec(spec)
        current_state = spec.get('current', 'New')
        expected_state = current_state
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

    def _create_skipped_issue_from_spec(self, spec):
        summary = "Skipped issue"
        current_state = spec.get('current', 'New')
        return self._create_issue_data(spec, summary, current_state)

    def _extract_context_prefix_from_spec(self, spec):
        context = spec.get('context')
        if context is None and spec.get('issue_type') is not None:
            context = f"{spec.get('issue_type')}"
        return f"{context} - " if context else ""

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

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_failures_displays_orphans(self, mock_jira_class):
        """Test that orphaned item with real Jira format appears in issues_to_report."""
        # Given: An orphaned Sub-task with real Jira summary format (like TAPS-211)
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, [
            {'key': 'TAPS-211', 'issue_type': 'Sub-task'}
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

    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_failures_displays_three_level_hierarchy_with_indentation(self, mock_jira_class):
        """Test 3-level hierarchy: Epic (non-evaluated) -> Story (non-evaluated) -> Subtask (failing)."""
        # Given: Epic with non-evaluated story and failing subtask (3-level hierarchy)
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, [
            {'key': 'PROJ-1', 'issue_type': 'Epic',     'rank': RANKS.HIGH.value, 'parent_key': None,       'assert_result': 'Skip'},
            {'key': 'PROJ-2', 'issue_type': 'Story',    'rank': RANKS.MID.value,  'parent_key': 'PROJ-1',   'assert_result': 'Skip'},
            {'key': 'PROJ-3', 'issue_type': 'Sub-task', 'rank': RANKS.LOW.value,  'parent_key': 'PROJ-2',   'current': 'New',        'expected': 'Ready'}
        ])
        
        # When: Assert CLI command is executed
        mock_print = self._execute_JiraUtil_with_args('tf', 'a', '--tsl', 'test-label')
        
        # Then: All three levels should appear in summary section
        # Note: PROJ-1 and PROJ-2 appear in both the hierarchical structure and "Not evaluated" section
        self._assert_issues_in_summary_section(mock_print, [
            {'line_with_key': 'PROJ-1', 'contains': ['[INFO]', '[Epic]'],   'skipped_parent': True},
            {'line_with_key': 'PROJ-2', 'contains': ['[INFO]', '[Story]'],  'skipped_parent': True},
            {'line_with_key': 'PROJ-3', 'contains': ['[FAIL]', '[Sub-task]']}
        ])
        
        # Verify the hierarchical indentation structure in the main output
        clean_output = self._strip_ansi_codes(mock_print)
        clean_output_str = '\n'.join(clean_output)
        assert '- [INFO] [Epic] PROJ-1:' in clean_output_str, "Epic should appear with proper indentation"
        assert '  - [INFO] [Story] PROJ-2:' in clean_output_str, "Story should appear indented under Epic"
        assert '    - [FAIL] [Sub-task] PROJ-3:' in clean_output_str, "Sub-task should appear indented under Story"

    @pytest.mark.skip(reason="TODO: Fix production code - failing subtasks of non-evaluated parents should appear in summary section")
    @patch('testfixture_cli.handlers.JiraInstanceManager')
    def test_assert_failures_displays_two_level_hierarchy(self, mock_jira_class):
        """Test that traces how issues are processed through the entire assertion pipeline using CLI."""
        # Given: 2-level hierarchy with non-evaluable parent and failing child
        mock_jira_instance = self._create_scenario_with_issues_from_assertion_specs(mock_jira_class, [
            {'key': 'TAPS-210', 'issue_type': 'Story',    'rank': RANKS.HIGHER.value, 'parent_key': None,      'assert_result': 'Skip'},
            {'key': 'TAPS-211', 'issue_type': 'Sub-task', 'rank': RANKS.NO_RANK.value, 'parent_key': 'TAPS-210'}
        ])
        
        # When: Assert CLI command is executed
        mock_print = self._execute_JiraUtil_with_args('tf', 'a', '--tsl', 'test-label')
        
        # Verify issues appear in summary
        self._assert_issues_in_summary_section(mock_print, [
            {'line_with_key': 'TAPS-210', 'contains': ['[INFO]', '[Story]'], 'skipped_parent': True},
            {'line_with_key': 'TAPS-211', 'contains': ['[FAIL]', '[Sub-task]']}
        ])

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
            {'key': 'EPIC-1',  'issue_type': 'Epic', 'rank': RANKS.HIGH.value,  'parent_key': None},
            {'key': 'STORY-3', 'issue_type': 'Story', 'rank': RANKS.LOW.value,  'parent_key': 'EPIC-1'},
            {'key': 'STORY-1', 'issue_type': 'Story', 'rank': RANKS.HIGH.value, 'parent_key': 'EPIC-1'},
            {'key': 'STORY-2', 'issue_type': 'Story', 'rank': RANKS.MID.value,  'parent_key': 'EPIC-1'}
        ], [
            {'line_with_key': 'EPIC-1'},
            {'line_with_key': 'STORY-1'},
            {'line_with_key': 'STORY-2'},
            {'line_with_key': 'STORY-3'}
        ]),
        ("mixed_epics_and_orphaned_items", [
            {'key': 'PROJ-1', 'issue_type': 'Epic',     'rank': RANKS.HIGH.value, 'parent_key': None},
            {'key': 'PROJ-2', 'issue_type': 'Story',    'rank': RANKS.MID.value,  'parent_key': 'PROJ-1'},
            {'key': 'PROJ-3', 'issue_type': 'Sub-task', 'rank': RANKS.LOW.value,  'parent_key': None}
        ], [
            {'line_with_key': 'PROJ-1'},
            {'line_with_key': 'PROJ-2'},
            {'line_with_key': 'PROJ-3'}
        ]),
        ("multiple_epics_with_children", [
            {'key': 'PROJ-1', 'issue_type': 'Epic',  'rank': RANKS.LOW.value,   'parent_key': None},
            {'key': 'PROJ-2', 'issue_type': 'Story', 'rank': RANKS.MID.value,   'parent_key': 'PROJ-1'},
            {'key': 'PROJ-3', 'issue_type': 'Epic',  'rank': RANKS.HIGH.value,  'parent_key': None},
            {'key': 'PROJ-4', 'issue_type': 'Story', 'rank': RANKS.LOWER.value, 'parent_key': 'PROJ-3'}
        ], [
            {'line_with_key': 'PROJ-3'},
            {'line_with_key': 'PROJ-4'},
            {'line_with_key': 'PROJ-1'},
            {'line_with_key': 'PROJ-2'}
        ]),
        ("children_found_before_parents", [
            {'key': 'PROJ-2', 'issue_type': 'Story', 'rank': RANKS.MID.value,  'parent_key': 'PROJ-1'},
            {'key': 'PROJ-1', 'issue_type': 'Epic',  'rank': RANKS.HIGH.value, 'parent_key': None}
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


    # =============================================================================
    # PRIVATE HELPER METHODS (sorted alphabetically)
    # =============================================================================

    def _assert_issues_in_summary_section(self, mock_print, issue_specs, in_order=True):
        """
        Assert that issues appear in the summary section with expected tags and order.
        
        Args:
            mock_print: Mock print object from CLI execution
            
            issue_specs: List of dicts 
                'line_with_key' 
                
                'contains' [optional]
                    - if provided, verifies tags are on same line as key
                
                'skipped_parent' [optional] 
                    - if True: verifies issue appears as parent in overview and as not evaluated in summary section
                
                - if multiple specs provided, 
                    by default it verifies they appear in the given order
                    unless 'in_order' is set to false, then just verify existence 

            in_order: default: True
        """
        summary_lines = self._extract_summary_section(mock_print)
        
        # Collect all needed data from summary lines
        collection_result = self._collect_issue_data_from_summary(summary_lines, issue_specs, in_order)
        
        # Verify all expected issues and their properties
        self._verify_issue_properties(collection_result, issue_specs, in_order)

    def _collect_issue_data_from_summary(self, summary_lines, issue_specs, in_order):
        """
        Collect issue data from summary lines in a single pass.
        
        Returns:
            dict: Collection result with 'issue_data', 'issue_counts', 'issue_keys', 'expected_keys'
        """
        issue_data = {}  # For contains verification
        issue_keys = []  # For order verification
        seen_keys = set()  # For order verification
        issue_counts = {}  # For count verification
        expected_keys = [spec['line_with_key'] for spec in issue_specs]  # For order verification
        
        # Single pass through summary lines to collect all needed data
        for line in summary_lines:
            for spec in issue_specs:
                key = spec['line_with_key']
                
                if key in line:
                    # Collect line data (first occurrence only)
                    if key not in issue_data:
                        issue_data[key] = line
                    
                    # Track count for count verification (all occurrences)
                    issue_counts[key] = issue_counts.get(key, 0) + 1
                    
                    # Collect order information if requested (first occurrence only)
                    if in_order and key not in seen_keys:
                        issue_keys.append(key)
                        seen_keys.add(key)
        
        return {
            'issue_data': issue_data,
            'issue_counts': issue_counts,
            'issue_keys': issue_keys,
            'expected_keys': expected_keys
        }

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

    def _verify_issue_properties(self, collection_result, issue_specs, in_order):
        """
        Verify all issue properties including presence, contains, count, and order.
        """
        issue_data = collection_result['issue_data']
        issue_counts = collection_result['issue_counts']
        issue_keys = collection_result['issue_keys']
        expected_keys = collection_result['expected_keys']
        
        # Verify all expected issues appear in summary section and their properties
        for spec in issue_specs:
            key = spec['line_with_key']
            
            # Verify issue appears in summary section
            assert key in issue_data, f"Issue {key} missing from summary section"
            
            # Verify contains if provided
            contains = spec.get('contains', [])
            if contains:
                line = issue_data[key]
                for tag in contains:
                    assert tag in line, f"Line containing {key} should contain '{tag}'. Line: {line}"
            
            # Verify count
            count = issue_counts.get(key, 0)
            skipped_parent = spec.get('skipped_parent', False)
            if skipped_parent:
                assert count == 2, f"Issue {key} should appear as parent in overview and as not evaluated in summary section, found {count} times"
            else:
                assert count == 1, f"Issue {key} should appear exactly once in summary section, found {count} times"
        
        # Verify order if requested
        if in_order:
            assert issue_keys == expected_keys, f"Issues appear in processing order. Expected: {expected_keys}, Actual: {issue_keys}"


if __name__ == "__main__":
    pytest.main([__file__])