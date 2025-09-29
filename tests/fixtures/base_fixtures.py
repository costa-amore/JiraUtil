"""
Base fixtures and shared test data.

This module contains the core test data and helper functions
that are shared across different test contexts.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock


# CSV test data constants
CSV_EMPTY = ""

UTILITY_COMMANDS = [
    (['list'], 'list'),
    (['ls'], 'ls'),
    (['status'], 'status'),
    (['st'], 'st'),
]

# Pre-generated config content for convenience (defined after functions)


# Public functions (sorted alphabetically)
def create_configured_config_content():
    """Create configured config content with real-looking values."""
    return generate_env_content(
        url="https://mycompany.atlassian.net",
        username="john.doe@mycompany.com",
        password="abc123def456ghi789"
    )


def create_field_extractor_rows(rows_data):
    """
    Create field extractor test rows with standard header.
    
    Args:
        rows_data: List of tuples (issue_key, summary, parent_key, status)
        
    Returns:
        List of rows with header + data rows
    """
    header = ["Issue key", "Summary", "Parent key", "Status"]
    data_rows = [list(row) for row in rows_data]
    return [header] + data_rows


def create_mock_code_change_detector(has_changes=True):
    """Create a mock code change detector for testing."""
    from unittest.mock import Mock
    
    mock_detector = Mock()
    mock_detector.has_code_changed.return_value = has_changes
    return mock_detector


def create_mock_manager(issues=None, connect_success=True, update_success=True):
    """Create a mock JiraInstanceManager with standard configuration."""
    # Create a mock without importing the actual class to avoid dependency issues
    mock_manager = Mock()
    mock_manager.jira = None  # Always None so connect() will be called
    mock_manager.connect.return_value = connect_success
    mock_manager.get_issues_by_label.return_value = issues or []
    mock_manager.update_issue_status.return_value = update_success
    
    return mock_manager


def create_mock_manager_with_expected_results(issues, expected_success=True, expected_processed=0, expected_updated=0, expected_skipped=0, expected_errors=None):
    """Create a mock manager with both test data and expected results grouped together."""
    # Setup: Create mock manager with test data
    mock_manager = create_mock_manager(issues=issues, connect_success=expected_success)
    
    # Expectations: Store expected results for assertions
    mock_manager.expected_success = expected_success
    mock_manager.expected_processed = expected_processed
    mock_manager.expected_updated = expected_updated
    mock_manager.expected_skipped = expected_skipped
    mock_manager.expected_errors = expected_errors or []
    
    return mock_manager



def create_template_config_content():
    """Create template config content."""
    return generate_env_content("", "", "")


def create_temp_config_file(content, suffix='.env'):
    """Create a temporary config file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    temp_file.write(content)
    temp_file.close()
    return Path(temp_file.name)


def create_temp_csv_file(content, suffix='.csv'):
    """Create a temporary CSV file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    temp_file.write(content)
    temp_file.close()
    return Path(temp_file.name)


def create_temp_env_file(url, username, password, comment_prefix="# Jira Configuration", suffix='.env'):
    """Create a temporary environment file with given credentials."""
    content = f"""{comment_prefix}
JIRA_URL={url}
JIRA_USERNAME={username}
JIRA_PASSWORD={password}"""
    return create_temp_config_file(content, suffix)


def create_temp_version_file():
    """Create a temporary version file for testing."""
    import os
    temp_dir = tempfile.mkdtemp()
    version_file = os.path.join(temp_dir, "test_version.json")
    return Path(version_file), temp_dir


def create_test_project_structure(temp_dir, project_name="test_project"):
    """Create a complete test project structure for build integration tests."""
    import shutil
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent.parent
    test_project_dir = Path(temp_dir) / project_name
    test_project_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy necessary directories
    dirs_to_copy = ["tools", "scripts", "src", "tests"]
    for dir_name in dirs_to_copy:
        src_dir = project_root / dir_name
        if src_dir.exists():
            shutil.copytree(src_dir, test_project_dir / dir_name)
    
    # Copy individual files
    files_to_copy = [
        "JiraUtil.py", "ju.py", "run.ps1", "setup-environment.ps1",
        "requirements.txt"
    ]
    
    for file_name in files_to_copy:
        src_file = project_root / file_name
        if src_file.exists():
            shutil.copy2(src_file, test_project_dir)
    
    return test_project_dir


def create_version_file_with_version(temp_dir, major=1, minor=0, build=0, local=0):
    """Create a version file with specific version components."""
    import json
    from pathlib import Path
    
    version_file = Path(temp_dir) / "test_version.json"
    version_data = {
        "major": major,
        "minor": minor,
        "build": build,
        "local": local,
        "description": "JiraUtil - Jira Administration Tool"
    }
    
    with open(version_file, 'w') as f:
        json.dump(version_data, f, indent=2)
    
    return version_file


def create_version_manager_with_version(major, minor, build=0, local=0):
    """Create a VersionManager with a specific version."""
    import sys
    from pathlib import Path
    
    # Add tools directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
    from version_manager import VersionManager
    
    version_file, temp_dir = create_temp_version_file()
    manager = VersionManager(str(version_file))
    manager.set_manual_version(major, minor)
    
    # Increment build if needed
    for _ in range(build):
        manager.increment_build()
    
    # Increment local if needed
    for _ in range(local):
        manager.increment_local_build()
    
    return manager, version_file, temp_dir


def generate_env_content(url, username, password, comment_prefix="# Jira Configuration"):
    """Generate environment file content."""
    return f"""{comment_prefix}
JIRA_URL={url}
JIRA_USERNAME={username}
JIRA_PASSWORD={password}"""


def get_version_components(version_file):
    """Get version components from version file."""
    import json
    
    with open(version_file, 'r') as f:
        version_data = json.load(f)
    
    return {
        'major': version_data['major'],
        'minor': version_data['minor'],
        'build': version_data['build'],
        'local': version_data['local']
    }


def get_version_from_file(version_file):
    """Get version string from version file."""
    import json
    
    with open(version_file, 'r') as f:
        version_data = json.load(f)
    
    return f"{version_data['major']}.{version_data['minor']}.{version_data['build']}.{version_data['local']}"


def run_version_command(command, version_file, cwd=None):
    """Run a version manager command and return the result."""
    import subprocess
    from pathlib import Path
    
    if cwd is None:
        cwd = Path(__file__).parent.parent.parent
    
    cmd = ["python", "tools/version_manager.py"] + command + ["--version-file", str(version_file)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


# Pre-generated config content for convenience
TEMPLATE_CONFIG_CONTENT = create_template_config_content()
CONFIGURED_CONFIG_CONTENT = create_configured_config_content()

# Default rank value for test issues
DEFAULT_RANK_VALUE = "0|i0000:"


def create_mock_issue(key, summary, status, issue_type, parent_key=None, rank=DEFAULT_RANK_VALUE):
    """Create a mock issue dictionary with standard structure."""
    return {
        'key': key,
        'summary': summary,
        'status': status,
        'issue_type': issue_type,
        'parent_key': parent_key,
        'rank': rank
    }


def execute_assert_testfixture_issues(mock_jira_manager, mock_issues):
    """Execute assert_testfixture_issues with mock data and return results."""
    from src.testfixture.issue_processor import assert_testfixture_issues
    
    mock_jira_manager.get_issues_by_label.return_value = mock_issues
    return assert_testfixture_issues(mock_jira_manager, "test-label")


def extract_issue_keys_from_report(issues_to_report):
    """Extract issue keys from issues_to_report, handling both dict and string formats."""
    issue_keys = []
    for issue in issues_to_report:
        if isinstance(issue, dict) and 'key' in issue:
            issue_keys.append(issue['key'])
        elif isinstance(issue, str) and '] ' in issue:
            # Handle formatted string like "[Story] TAPS-210: ..."
            key = issue.split('] ')[1].split(':')[0]
            issue_keys.append(key)
    return issue_keys


def verify_issue_in_report(issues_to_report, expected_key, description):
    """Verify that an issue with the expected key appears in the report."""
    issue_keys = extract_issue_keys_from_report(issues_to_report)
    assert expected_key in issue_keys, f"{description}. Actual keys: {issue_keys}"


def verify_issue_order(issues_to_report, first_key, second_key, description):
    """Verify that first_key appears before second_key in the report."""
    issue_keys = extract_issue_keys_from_report(issues_to_report)
    first_index = issue_keys.index(first_key)
    second_index = issue_keys.index(second_key)
    assert first_index < second_index, f"{description}. Order: {issue_keys}"


def verify_context_extraction(issues_to_report, expected_context):
    """Verify that context is correctly extracted from issue summaries."""
    assert len(issues_to_report) > 0, "Should have issues in report"
    issue = issues_to_report[0]
    assert 'context' in issue, "Issue should have context extracted"
    assert issue['context'] == expected_context, f"Expected context '{expected_context}', got '{issue['context']}'"