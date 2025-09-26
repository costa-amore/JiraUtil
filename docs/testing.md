# Testing

[🏠 Home](../README.md)

## Running Tests

### Quick Start

**First time setup:**

```powershell

# Create virtual environment and install dependencies
.\setup-environment.ps1
```

**Run tests:**

```powershell

# Run comprehensive test suite with detailed output
.\run.ps1 tests\run_tests.py
```

### Test-First Build Process

The build system automatically runs tests before building executables:

```powershell

# Build process (runs tests first, then builds if tests pass)
.\build-windows.ps1
```

**Important**: The build process will abort if any tests fail, ensuring only working code gets built into executables.

### Test Categories

```powershell

# Run specific test categories
.\run.ps1 tests\run_tests.py csv          # CSV export functionality
.\run.ps1 tests\run_tests.py testfixture  # Test fixture management
.\run.ps1 tests\run_tests.py cli          # CLI commands and parsing
.\run.ps1 tests\run_tests.py overview     # Functional overview tests

# Run specific test files or patterns
.\run.ps1 tests\run_tests.py test_testfixture_trigger.py  # Specific file
.\run.ps1 tests\run_tests.py test_trigger_operation       # Pattern matching
```

## Test Structure

### Comprehensive Test Suite

The project includes a comprehensive functional test suite covering all major functionalities:

- **CSV Export Commands** - Field extraction, newline removal, date conversion
- **Test Fixture Commands** - Pattern parsing, reset/assert operations
- **CLI Commands** - Command parsing, help, status, version
- **Core Functionality** - Field extraction and processing
- **Functional Overview** - End-to-end functionality validation

### Test Runner

- **`tests\run_tests.py`** - Comprehensive test runner with detailed output, categorized display, and rich formatting

## Adding New Tests

### 1. Create Test File

Create a new file in `tests/` with the pattern `test_*.py`:

```python

# tests/test_my_module.py
import pytest
from src.my_module import my_function

def test_my_function():
    assert my_function("input") == "expected_output"
```

### 2. Test Discovery

The test runner automatically discovers files matching `test_*.py` pattern.

### 3. Run Tests

See the [Test Categories](#test-categories) section above for how to run tests.

## Test Dependencies

Tests use `pytest` which is installed via `requirements.txt`:

```text
pytest==8.0.0
```

## Test Output

The comprehensive test runner provides detailed output including:

- **Test Categories** - Organized by functional area
- **Progress Indicators** - Real-time test execution status
- **Summary Report** - Overall test results and coverage
- **Error Details** - Clear failure information when tests fail
- **Performance Metrics** - Test execution timing

**Run `.\run.ps1 tests\run_tests.py` to see the current test output.**

## Debugging Tests

Use the test runner capabilities described in the [Test Categories](#test-categories) section above.

## Debugging Commands

### Debug Script

The project includes a comprehensive debug script for all commands:

```powershell
.\run.ps1 debug-helper.py
```

### VS Code Debugging

Use the Debug panel (`Ctrl+Shift+D`) and select:

- **"Debug All Commands"** - Debug any command

### Custom Debug Commands

Edit `debug-helper.py` to test specific commands:

```python

# Uncomment the command you want to debug:
debug_command(["JiraUtil.py", "CsvExport", "remove-newline", "test.csv"])
debug_command(["JiraUtil.py", "ResetTestFixture", "rule-testing"])
debug_command(["JiraUtil.py", "AssertExpectations", "rule-testing"])
debug_command(["JiraUtil.py", "CsvExport", "extract-to-comma-separated-list", "Parent key", "test.csv"])
debug_command(["JiraUtil.py", "CsvExport", "fix-dates-eu", "test.csv"])
```

### Available Commands to Debug

- **CSV**: `remove-newline`, `extract-to-comma-separated-list`, `fix-dates-eu`
- **Jira**: `ResetTestFixture`, `AssertExpectations`
- **Help**: `--help`

## Troubleshooting

### pytest Not Found

```powershell

# Rebuild environment (installs all dependencies including pytest)
.\setup-environment.ps1
```

### Import Errors

If you get import errors, rebuild the environment:

```powershell

# Rebuild environment (fixes import issues and activates venv)
.\setup-environment.ps1
```

### Virtual Environment Issues

```powershell

# Rebuild environment (fixes most dependency issues)
.\setup-environment.ps1
```

### General Setup Issues

If you encounter any issues with dependencies or the environment:

```powershell

# Complete environment rebuild (fixes most issues and activates venv)
.\setup-environment.ps1
```

## Test Coverage

The project has comprehensive test coverage with 72 tests covering all major functionalities. Run `.\run.ps1 tests\run_tests.py` to see the current test status and detailed results.

---

[← Project Structure](project-structure.md) | [Building Executables →](building-executables.md)
