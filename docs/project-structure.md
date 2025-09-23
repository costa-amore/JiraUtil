# Project Structure

[🏠 Home](../README.md)

## Directory Layout

```text
Jira_csv_helper/
├── src\                          # Source code
│   ├── __init__.py
│   ├── JiraUtil.py               # Main CLI entry point
│   ├── jira_cleaner.py          # Newline removal functionality
│   ├── jira_dates_eu.py         # European date formatting
│   ├── jira_field_extractor.py  # Field value extraction
│   └── jira_testfixture.py      # Jira integration functionality
├── tests/                        # Test files
│   ├── __init__.py
│   ├── run_tests.py             # Test runner
│   └── test_jira_field_extractor.py
├── docs/                         # Documentation
│   ├── setup.md
│   ├── csv_export-commands.md
│   ├── jira-commands.md
│   ├── project-structure.md
│   └── testing.md
├── .venv/                        # Virtual environment
│   └── jira_config.env          # Jira credentials (not in git)
├── # Entry Points
├── JiraUtil.py                   # Main CLI entry point
├── ju.py                         # Short alias
├── run.ps1                       # PowerShell runner
├── 
├── # Development & Testing
├── debug-helper.py               # Debug helper
├── 
├── # Environment Management
├── setup-environment.ps1         # Environment setup
├── 
├── # Build System
├── build-windows.ps1             # Windows build script
├── build-unix.sh                 # Unix build script
├── JiraUtil.spec                 # PyInstaller spec
├── 
├── # Configuration
├── jira_config_example.env      # Configuration template
├── requirements.txt             # Python dependencies
├── requirements-build.txt       # Build dependencies
└── README.md                    # Project documentation
```

## Key Files

### Entry Points

- **`JiraUtil.py`** - Root entry point that imports from `src\`
- **`src\JiraUtil.py`** - Main CLI implementation with argument parsing

### Core Modules

- **`jira_cleaner.py`** - CSV newline removal
- **`jira_dates_eu.py`** - European date formatting
- **`jira_field_extractor.py`** - Field value extraction
- **`jira_testfixture.py`** - Jira API integration and issue processing

### Configuration

- **`jira_config_example.env`** - Template for Jira credentials
- **`.venv/jira_config.env`** - Actual credentials (created by setup)
- **`requirements.txt`** - Python package dependencies

### Development & Testing

- **`tests/run_tests.py`** - Comprehensive test runner
- **`debug-helper.py`** - Debug helper for all commands

### Environment Management

- **`setup-environment.ps1`** - One-command environment setup/rebuild

### Build System

- **`build-windows.ps1`** - Windows build script (runs tests first)
- **`build.sh`** - Generic Unix build script (runs tests first)
- **`build-macos.ps1`** - macOS convenience script
- **`build-linux.ps1`** - Linux convenience script
- **`build-all.ps1`** - All platforms convenience script
- **`JiraUtil.spec`** - PyInstaller configuration

### Utilities

- **`run.ps1`** - PowerShell wrapper for running Python scripts

### Testing

- **`tests/run_tests.py`** - Test runner that discovers and runs all tests
- **`tests/test_jira_field_extractor.py`** - Unit tests for field extraction

## Module Dependencies

```text
JiraUtil.py (root)
├── src\JiraUtil.py
    ├── jira_cleaner.py
    ├── jira_dates_eu.py
    ├── jira_field_extractor.py
    └── jira_testfixture.py
        └── jira (external library)
```

## Development Workflow

1. **Setup**: `.\setup-environment.ps1`
2. **Develop**: Edit files in `src\`
3. **Test**: `.\run.ps1 tests\run_tests.py`
4. **Debug**: Use `.\run.ps1 debug-helper.py` for debugging any command
5. **Build**: `.\build-windows.ps1` (runs tests first, then builds executables)
6. **Rebuild**: `.\setup-environment.ps1` when dependencies change

## Adding New Features

1. **New CSV command**: Add to `src\JiraUtil.py` CsvExport subparser
2. **New Jira command**: Add to `src\JiraUtil.py` ResetTestFixture or AssertExpectations section
3. **New functionality**: Create new module in `src\`
4. **Tests**: Add test files to `tests\`
5. **Documentation**: Update relevant files in `docs\`

---

[← Jira Commands](jira-commands.md) | [Testing →](testing.md)
