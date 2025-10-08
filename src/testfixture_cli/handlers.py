from jira_manager import JiraInstanceManager
from testfixture import run_TestFixture_Reset, run_assert_expectations, run_trigger_operation
from cli.parser import DEFAULT_TEST_FIXTURE_LABEL


# =============================================================================
# PUBLIC METHODS (sorted alphabetically)
# =============================================================================

def handle_test_fixture_commands(args, result: dict) -> dict:
    """Handle test-fixture commands with support for chaining."""
    jira_url, username, password = get_jira_credentials(args)
    
    # Get the test-set-label to use for reset/assert commands
    test_set_label = getattr(args, 'tsl', None) or DEFAULT_TEST_FIXTURE_LABEL
    
    # Process each command in the chain sequentially
    for command in args.commands:
        if command in ["reset", "r"]:
            print(f"[CHAIN] Executing reset with test-set-label: {test_set_label}")
            force_update_via = getattr(args, 'force_update_via', None)
            execute_with_jira_manager(jira_url, username, password, run_TestFixture_Reset, test_set_label, force_update_via)
        elif command in ["assert", "a"]:
            print(f"[CHAIN] Executing assert with test-set-label: {test_set_label}")
            execute_with_jira_manager(jira_url, username, password, run_assert_expectations, test_set_label)
        elif command in ["trigger", "t"]:
            trigger_label = getattr(args, 'tl', None)
            if not trigger_label or not trigger_label.strip():
                print("[FATAL] ERROR: Trigger command requires --tl/--trigger-label argument")
                return result
            
            print(f"[CHAIN] Executing trigger with trigger-label: {trigger_label}, key: {args.key}")
            execute_with_jira_manager(jira_url, username, password, run_trigger_operation, args.key, trigger_label)
        else:
            from cli.parser import build_parser
            parser = build_parser()
            parser.error(f"Unknown test-fixture command: {command}")
    
    return result


# =============================================================================
# PRIVATE METHODS (sorted alphabetically)
# =============================================================================

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