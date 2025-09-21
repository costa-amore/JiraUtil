# Testing

## Running Tests

### Quick Start
```powershell
python run_tests.py
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
python run_tests.py
```

## Test Structure

### Current Tests
- **`test_jira_field_extractor.py`** - Tests for CSV field extraction functionality

### Test Runner
- **`run_tests.py`** - Discovers and runs all test files in the `tests/` directory

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
python run_tests.py
```

## Test Dependencies

Tests use `pytest` which is installed via `requirements.txt`:
```
pytest==8.0.0
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

## Debugging Commands

### Debug Script
The project includes a comprehensive debug script for all commands:

```powershell
python debug_all_commands.py
```

### VS Code Debugging
Use the Debug panel (`Ctrl+Shift+D`) and select:
- **"Debug All Commands"** - Debug any command

### Custom Debug Commands
Edit `debug_all_commands.py` to test specific commands:

```python
# Uncomment the command you want to debug:
debug_command(["JiraUtil.py", "CsvExport", "remove-newline", "test.csv"])
debug_command(["JiraUtil.py", "ResetTestFixture", "rule-testing"])
debug_command(["JiraUtil.py", "CsvExport", "extract-to-comma-separated-list", "Parent key", "test.csv"])
debug_command(["JiraUtil.py", "CsvExport", "fix-dates-eu", "test.csv"])
```

### Available Commands to Debug
- **CSV**: `remove-newline`, `extract-to-comma-separated-list`, `fix-dates-eu`
- **Jira**: `ResetTestFixture`
- **Help**: `--help`

## Troubleshooting

### pytest Not Found
```powershell
# Install pytest
.\.venv\Scripts\python.exe -m pip install pytest

# Or rebuild environment
./rebuild-venv.ps1
```

### Import Errors
Ensure you're running tests from the project root directory.

### Virtual Environment Issues
```powershell
# Rebuild environment
./rebuild-venv.ps1
```

## Test Coverage

Currently, the project has basic test coverage. Consider adding tests for:
- Jira API integration
- CSV processing functions
- Error handling scenarios
- Edge cases

---

[← Project Structure](project-structure.md) | [← Back to README](README.md)
