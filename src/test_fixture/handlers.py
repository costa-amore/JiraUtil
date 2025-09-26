from jira_manager import JiraInstanceManager
from testfixture import run_TestFixture_Reset, run_assert_expectations


def handle_test_fixture_commands(args, result: dict) -> dict:
    """Handle test-fixture commands."""
    jira_url, username, password = get_jira_credentials(args)
    
    if args.test_command in ["reset", "r"]:
        execute_with_jira_manager(jira_url, username, password, run_TestFixture_Reset, args.label)
        return result
    elif args.test_command in ["assert", "a"]:
        execute_with_jira_manager(jira_url, username, password, run_assert_expectations, args.label)
        return result
    else:
        from cli.parser import build_parser
        parser = build_parser()
        parser.error("Unknown test-fixture command")


def execute_with_jira_manager(jira_url: str, username: str, password: str, workflow_function, *args):
    """Execute a workflow function with a connected Jira manager."""
    manager = JiraInstanceManager(jira_url, username, password)
    manager.connect()
    workflow_function(manager, *args)


def get_jira_credentials(args) -> tuple[str, str, str]:
    """Get Jira credentials from arguments or environment."""
    from auth import get_jira_credentials as get_env_credentials
    
    jira_url = args.jira_url
    username = args.username
    password = args.password
    
    # If not provided via arguments, get from environment or prompt
    if not jira_url or not username or not password:
        env_url, env_username, env_password = get_env_credentials()
        jira_url = jira_url or env_url
        username = username or env_username
        password = password or env_password
    
    return jira_url, username, password
