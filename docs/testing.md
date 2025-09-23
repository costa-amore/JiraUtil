# Testing

[🏠 Home](../README.md)

## Running Tests

### Quick Start

**After running the setup script** (which automatically activates the virtual environment):

```powershell
# Run comprehensive test suite with detailed output
.\run.ps1 tests\run_tests.py
```

**For new terminal sessions**, use one of these options:

```powershell
# Option 1: Run setup script again (recommended)
.\setup-environment.ps1

# Option 2: Use run script (automatically uses venv)
.\run.ps1 tests\run_tests.py
```

### Test-First Build Process

The build system automatically runs tests before building executables:

```powershell
# Build process (runs tests first, then builds if tests pass)
.\build-windows.ps1

# Manual test run (optional - build process does this automatically)
.\run.ps1 tests\run_tests.py
```

**Important**: The build process will abort if any tests fail, ensuring only working code gets built into executables.

### Test Categories

```powershell
# Run specific test categories
.\run.ps1 tests\run_tests.py csv          # CSV export functionality
.\run.ps1 tests\run_tests.py testfixture  # Test fixture management
.\run.ps1 tests\run_tests.py cli          # CLI commands and parsing
.\run.ps1 tests\run_tests.py overview     # Functional overview tests
```

### Alternative Methods

```powershell
# Using pytest directly
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_jira_field_extractor.py -v

# Run with detailed output
python -m pytest tests/ -v -s
```

### Using Virtual Environment

**The setup script automatically activates the virtual environment**, so after running `.\setup-environment.ps1`, you can use `python` commands directly:

```powershell
# After running setup script, virtual environment is already active
.\run.ps1 tests\run_tests.py
```

**For new terminal sessions**, use one of these options:

```powershell
# Option 1: Run setup script again (recommended)
.\setup-environment.ps1

# Option 2: Use run script (automatically uses venv)
.\run.ps1 tests\run_tests.py
```

## Test Structure

### Comprehensive Test Suite

The project includes a comprehensive functional test suite with **72 tests** covering all major functionalities:

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

```powershell
# Run all tests
.\run.ps1 tests\run_tests.py

# Run specific test file
python -m pytest tests/test_my_module.py -v
```

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

### Verbose Output

```powershell
python -m pytest tests/ -v -s
```

### Specific Test

```powershell
python -m pytest tests/test_jira_field_extractor.py::test_specific_function -v
```

### Stop on First Failure

```powershell
python -m pytest tests/ -x
```

### Run Specific Test Category

```powershell
# Run only CSV export tests
.\run.ps1 tests\run_tests.py csv

# Run only test fixture tests
.\run.ps1 tests\run_tests.py testfixture
```

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
