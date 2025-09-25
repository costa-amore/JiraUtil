"""
Shared test data fixtures to eliminate duplication across test files.
"""

# Test fixture issue data
TEST_FIXTURE_ISSUES = [
    {
        'key': 'PROJ-1',
        'summary': 'I was in To Do - expected to be in In Progress',
        'status': 'In Progress'  # Needs update to To Do
    },
    {
        'key': 'PROJ-2',
        'summary': 'Bug fix - starting in In Progress - expected to be in Done',
        'status': 'Done'  # Needs update to In Progress
    },
    {
        'key': 'PROJ-3',
        'summary': 'starting in To Do - expected to be in In Progress',
        'status': 'To Do'  # Already in target status
    }
]

# Test fixture issues for assert tests (different statuses for pass/fail scenarios)
TEST_FIXTURE_ASSERT_ISSUES = [
    {
        'key': 'PROJ-1',
        'summary': 'I was in To Do - expected to be in In Progress',
        'status': 'In Progress'  # Matches expected status
    },
    {
        'key': 'PROJ-2',
        'summary': 'starting in In Progress - expected to be in Done',
        'status': 'To Do'  # Does not match expected status
    }
]

# Valid pattern test cases
VALID_PATTERNS = [
    ("I was in To Do - expected to be in In Progress", "To Do", "In Progress"),
    ("I was in In Progress - expected to be in Done", "In Progress", "Done"),
    ("Bug fix - starting in To Do - expected to be in In Progress", "To Do", "In Progress"),
    ("starting in To Do - expected to be in In Progress", "To Do", "In Progress"),
    ("i was in to do - expected to be in in progress", "to do", "in progress"),
    ("BUG FIX - STARTING IN TO DO - EXPECTED TO BE IN IN PROGRESS", "TO DO", "IN PROGRESS"),
]

# Invalid pattern test cases
INVALID_PATTERNS = [
    "Regular issue summary",
    "I was in To Do",
    "Expected to be in In Progress",
    "I was in To Do expected to be in In Progress",
    "I was To Do - expected to be in In Progress",
    "I was in - expected to be in In Progress",
    "",
]

# Mock manager setup helpers
def create_mock_manager(issues=None, connect_success=True, update_success=True):
    """Create a mock JiraInstanceManager with standard configuration."""
    from unittest.mock import Mock
    from jira_manager import JiraInstanceManager
    
    mock_manager = Mock(spec=JiraInstanceManager)
    mock_manager.jira = None  # Always None so connect() will be called
    mock_manager.connect.return_value = connect_success
    mock_manager.get_issues_by_label.return_value = issues or []
    mock_manager.update_issue_status.return_value = update_success
    
    return mock_manager

# Test result helpers
def create_reset_result(processed=0, updated=0, skipped=0, errors=None, success=True):
    """Create a standard reset result dictionary."""
    return {
        'success': success,
        'processed': processed,
        'updated': updated,
        'skipped': skipped,
        'errors': errors or []
    }

def create_assert_result(processed=0, passed=0, failed=0, not_evaluated=0, failures=None, not_evaluated_keys=None, success=True):
    """Create a standard assert result dictionary."""
    return {
        'success': success,
        'processed': processed,
        'passed': passed,
        'failed': failed,
        'not_evaluated': not_evaluated,
        'failures': failures or [],
        'not_evaluated_keys': not_evaluated_keys or []
    }
