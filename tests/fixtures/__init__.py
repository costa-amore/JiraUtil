"""
Test fixtures organized by context.

This package contains focused fixture modules for different test contexts:
- base_fixtures: Core test data and shared helpers
- test_fixture_scenarios: Test fixture automation scenarios
- csv_scenarios: CSV processing scenarios  
- cli_scenarios: CLI command scenarios
"""

# Import commonly used fixtures for backward compatibility
from .base_fixtures import (
    create_mock_manager,
    create_temp_csv_file,
    create_temp_config_file,
    create_temp_env_file,
    create_reset_result,
    create_assert_result,
    create_field_extractor_rows,
    create_temp_version_file,
    create_version_manager_with_version,
    create_test_project_structure,
    create_version_file_with_version,
    create_mock_code_change_detector,
    run_version_command,
    get_version_from_file,
    get_version_components,
    generate_env_content,
    create_template_config_content,
    create_configured_config_content,
    TEMPLATE_CONFIG_CONTENT,
    CONFIGURED_CONFIG_CONTENT,
    CSV_EXPORT_COMMANDS,
    TEST_FIXTURE_SINGLE_COMMANDS,
    TEST_FIXTURE_CHAINED_COMMANDS,
    UTILITY_COMMANDS,
    CSV_EMPTY,
    TEST_FIXTURE_ISSUES,
    TEST_FIXTURE_ASSERT_ISSUES
)

# Import scenario-based fixtures
from .test_fixture_scenarios import (
    create_reset_scenario_with_expectations,
    create_assert_scenario_with_expectations,
    create_empty_scenario_with_expectations,
    create_connection_failure_scenario_with_expectations,
    create_skip_scenario_with_expectations
)

from .csv_scenarios import (
    create_csv_with_embedded_newlines,
    create_csv_for_field_extraction,
    create_csv_with_iso_dates,
    create_newlines_removal_scenario,
    create_field_extraction_scenario,
    create_date_conversion_scenario
)

from .cli_scenarios import (
    create_config_validation_scenarios,
    create_authentication_scenarios,
    create_command_parsing_scenarios,
    create_display_scenarios
)
