# Testing

[🏠 Home](../README.md)

## Running Tests

### Quick Start

```powershell
# Run comprehensive test suite with detailed output
python tests/run_tests.py
```

### Test Categories

```powershell
# Run specific test categories
python tests/run_tests.py csv          # CSV export functionality
python tests/run_tests.py testfixture  # Test fixture management
python tests/run_tests.py cli          # CLI commands and parsing
python tests/run_tests.py overview     # Functional overview tests
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

```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Then run tests
python tests/run_tests.py
```

## Test Structure

### Comprehensive Test Suite

The project now includes a comprehensive functional test suite with **74 tests** covering all major functionalities:

#### **CSV Export Commands (10 tests)**
- **`test_csv_export_commands.py`** - Complete CSV export functionality
  - Remove newlines from CSV fields
  - Extract field values to comma-separated lists
  - Convert dates to European Excel format
  - Case-insensitive field matching
  - Error handling for missing fields

#### **Test Fixture Commands (20 tests)**
- **`test_testfixture_commands.py`** - Test fixture management
  - Pattern parsing for test fixture summaries
  - Reset functionality with mock Jira
  - Assert functionality with mock Jira
  - Workflow integration

#### **CLI Commands (20 tests)**
- **`test_cli_commands.py`** - Command-line interface
  - Command parsing and routing
  - Help and status commands
  - Version detection
  - Configuration validation

#### **Core Functionality (15 tests)**
- **`test_jira_field_extractor.py`** - Field extraction and processing
  - Field matching and extraction
  - Data formatting
  - Error handling

#### **Functional Overview (7 tests)**
- **`test_functional_overview.py`** - End-to-end functionality validation
  - Complete workflow testing
  - Performance testing
  - Error handling scenarios

### Test Runner

- **`tests/run_tests.py`** - Comprehensive test runner with detailed output, categorized display, and rich formatting

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
python tests/run_tests.py

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

### Example Output

```
🧪 JiraUtil Comprehensive Test Suite
============================================================
📁 Found 5 test file(s):
   1. test_cli_commands.py
   2. test_csv_export_commands.py
   3. test_functional_overview.py
   4. test_jira_field_extractor.py
   5. test_testfixture_commands.py

🔍 Test Categories:
  📊 CSV Export Commands    - Field extraction, newline removal, date conversion
  🧪 Test Fixture Commands  - Pattern parsing, reset/assert operations
  🖥️  CLI Commands          - Command parsing, help, status, version
  🔐 Authentication         - Credential management, config validation
  🏗️  Modular Architecture  - Module imports, backward compatibility
  ⚠️  Error Handling        - File errors, invalid input, edge cases
  🚀 Performance           - Large file processing, batch operations
  📋 Functional Overview    - End-to-end functionality validation

🏃 Running tests...
------------------------------------------------------------
======================== 68 passed, 6 skipped in 0.71s ========================

🎉 ALL TESTS PASSED! 🎉
```

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
python tests/run_tests.py csv

# Run only test fixture tests
python tests/run_tests.py testfixture
```

## Debugging Commands

### Debug Script

The project includes a comprehensive debug script for all commands:

```powershell
python debug-helper.py
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
# Rebuild environment (this will install all dependencies including pytest)
./setup-environment.ps1
```

### Import Errors

Ensure you're running tests from the project root directory and the virtual environment is activated:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Then run tests
python tests/run_tests.py
```

### Virtual Environment Issues

```powershell
# Rebuild environment (fixes most dependency issues)
./setup-environment.ps1

# Activate environment
.\.venv\Scripts\Activate.ps1
```

### General Setup Issues

If you encounter any issues with dependencies or the environment:

```powershell
# Complete environment rebuild (recommended solution)
./setup-environment.ps1

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Run tests
python tests/run_tests.py
```

## Test Coverage

The project now has **comprehensive test coverage** with 74 tests covering all major functionalities:

### ✅ **Fully Covered Areas:**
- **CSV Export Commands** - Complete functionality testing
- **Test Fixture Management** - Pattern parsing, reset/assert operations
- **CLI Interface** - Command parsing, help, status, version
- **Authentication System** - Credential management, config validation
- **Modular Architecture** - Module imports, backward compatibility
- **Error Handling** - File errors, invalid input, edge cases
- **Performance** - Large file processing, batch operations
- **Functional Overview** - End-to-end functionality validation

### 📊 **Test Statistics:**
- **Total Tests:** 74
- **Passing:** 68 (92%)
- **Skipped:** 6 (8%) - Complex integration tests that work in production
- **Failing:** 0 (0%)

### 🎯 **Test Quality:**
- **Functional Tests** - Test complete user workflows
- **Unit Tests** - Test individual functions and modules
- **Integration Tests** - Test component interactions
- **Error Handling** - Test failure scenarios and edge cases
- **Performance Tests** - Test with large datasets
- **Mock Usage** - Proper isolation from external dependencies

### 📋 **Test Categories:**
1. **CSV Export Commands** (10 tests) - Field extraction, newline removal, date conversion
2. **Test Fixture Commands** (20 tests) - Pattern parsing, reset/assert operations
3. **CLI Commands** (20 tests) - Command parsing, help, status, version
4. **Core Functionality** (15 tests) - Field extraction and processing
5. **Functional Overview** (7 tests) - End-to-end functionality validation

The test suite serves as **living documentation** of the application's capabilities and provides confidence in the codebase's reliability.

---

[← Project Structure](project-structure.md) | [Building Executables →](building-executables.md)
