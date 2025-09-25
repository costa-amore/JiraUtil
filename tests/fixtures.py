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

# CLI test helpers
def create_temp_config_file(content, suffix='.env'):
    """Create a temporary config file for testing."""
    import tempfile
    from pathlib import Path
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    temp_file.write(content)
    temp_file.close()
    return Path(temp_file.name)

def create_temp_env_file(url, username, password, comment_prefix="# Jira Configuration", suffix='.env'):
    """Create a temporary environment file with given credentials."""
    content = generate_env_content(url, username, password, comment_prefix)
    return create_temp_config_file(content, suffix)

# CLI test data - using functions from production code
from config.validator import TEMPLATE_PATTERNS
from auth.credentials import (CREDENTIAL_TEMPLATE_PATTERNS, JIRA_ENV_VARS, 
                             generate_env_file_content, create_template_env_content)

# Re-export production functions for convenience
generate_env_content = generate_env_file_content
create_template_config_content = create_template_env_content

def create_configured_config_content():
    """Create configured config content with real-looking values."""
    return generate_env_file_content(
        url="https://mycompany.atlassian.net",
        username="john.doe@mycompany.com",
        password="abc123def456ghi789"
    )

# Template generators for different scenarios using production function
def create_empty_config_content():
    """Create empty config content (no values)."""
    return generate_env_file_content("", "", "")

def create_partial_config_content():
    """Create config content with only URL set."""
    return generate_env_file_content("https://partial.atlassian.net", "", "")

def create_invalid_config_content():
    """Create config content with invalid values."""
    return generate_env_file_content("not-a-url", "invalid-email", "short")

# Pre-generated config content for convenience
TEMPLATE_CONFIG_CONTENT = create_template_config_content()
CONFIGURED_CONFIG_CONTENT = create_configured_config_content()

# CLI command test cases
CSV_EXPORT_COMMANDS = [
    (['csv-export', 'remove-newlines', 'input.csv'], 'csv-export', 'remove-newlines', 'input.csv'),
    (['ce', 'rn', 'input.csv'], 'ce', 'rn', 'input.csv'),
    (['csv-export', 'extract-to-comma-separated-list', 'Status', 'input.csv'], 'csv-export', 'extract-to-comma-separated-list', 'input.csv'),
    (['csv-export', 'fix-dates-eu', 'input.csv', '--output', 'output.csv'], 'csv-export', 'fix-dates-eu', 'input.csv'),
]

TEST_FIXTURE_COMMANDS = [
    (['test-fixture', 'reset', 'custom-label'], 'test-fixture', 'reset', 'custom-label'),
    (['tf', 'r'], 'tf', 'r', 'rule-testing'),
    (['test-fixture', 'assert', 'custom-label'], 'test-fixture', 'assert', 'custom-label'),
    (['tf', 'a'], 'tf', 'a', 'rule-testing'),
]

UTILITY_COMMANDS = [
    (['list'], 'list'),
    (['ls'], 'ls'),
    (['status'], 'status'),
    (['st'], 'st'),
]

# CSV test helpers and data
def create_temp_csv_file(content, suffix='.csv'):
    """Create a temporary CSV file for testing."""
    import tempfile
    from pathlib import Path
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    temp_file.write(content)
    temp_file.close()
    return Path(temp_file.name)

# CSV test data
CSV_WITH_NEWLINES = '''Issue key,Summary,Description,Status
PROJ-1,"Task with newlines
in summary","Description with
multiple lines",Done
PROJ-2,"Normal task","Single line description",In Progress
PROJ-3,"Task with\r\nWindows newlines","Mixed\r\nline endings",To Do'''

CSV_FIELD_EXTRACTION = '''Issue key,Summary,Parent key,Status,Assignee
PROJ-1,Task 1,EPIC-1,Done,John Doe
PROJ-2,Task 2,EPIC-1,In Progress,Jane Smith
PROJ-3,Task 3,EPIC-2,To Do,John Doe
PROJ-4,Task 4,EPIC-1,Done,Bob Wilson'''

CSV_WITH_DATES = '''Issue key,Summary,Created,Updated,Status
PROJ-1,Task 1,2024-01-15 10:30:00,2024-01-20 14:45:00,Done
PROJ-2,Task 2,2024-02-01 09:15:00,2024-02-05 16:20:00,In Progress
PROJ-3,Task 3,2024-03-10 11:00:00,2024-03-10 11:00:00,To Do'''

CSV_EMPTY = ""
