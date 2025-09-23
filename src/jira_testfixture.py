"""
Jira test fixture management functionality.

This module provides functionality to manage issues used as test fixtures,
primarily for verifying correct execution of automation rules. It uses the
generic Jira management capabilities from jira_manager.py.

This module now serves as a compatibility layer that imports from the
new modular structure.
"""

# Import from the new modular structure
from testfixture import run_TestFixture_Reset, run_assert_expectations, DEFAULT_TEST_FIXTURE_LABEL
from auth import get_jira_credentials