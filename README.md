# JIRA utility

A Python utility for supporting Jira admins.

## 🚀 Quick Start

1. **Setup**: Run `./setup-environment.ps1` to create the environment and install dependencies
2. **Configure**: Edit `.venv\jira_config.env` with your Jira credentials
3. **Run**: Use `./run.ps1 .\JiraUtil.py --help` or `./run.ps1 .\ju.py --help` to see all available commands

## 📋 Available Commands

### CSV Export File Support

- **CsvExport remove-newline** (`ju.py ce rn`): Clean CSV fields from newline characters
- **CsvExport extract-to-comma-separated-list** (`ju.py ce ecl`): Extract specific field values to comma-separated lists
- **CsvExport fix-dates-eu** (`ju.py ce fd`): Convert dates for European Excel format

### Jira Automations Support

- **ResetTestFixture** (`ju.py rt`): Update issue status based on summary patterns
- **AssertExpectations** (`ju.py ae`): Assert that issues are in their expected status based on summary patterns

## 📚 Documentation

- **[Setup Guide](docs/setup.md)** - Detailed installation and configuration
- **[CSV Export Commands](docs/csv_export-commands.md)** - CSV processing functionality
- **[Jira Commands](docs/jira-commands.md)** - Jira integration features
- **[Project Structure](docs/project-structure.md)** - Code organization
- **[Testing](docs/testing.md)** - Running tests and development
- **[Building Executables](docs/building-executables.md)** - Creating standalone executables

## 🛠️ Development

- **Tests**: `python test-runner.py`
- **Debug**: Use `python debug-helper.py` for debugging any command
- **Rebuild**: `./setup-environment.ps1` to update dependencies
- **Build Executables**: `./build-windows.ps1` (Windows) or `./build-unix.sh` (macOS/Linux)

## 📁 Project Structure

```text
Jira_csv_helper/
├── # Entry Points
├── JiraUtil.py             # Main CLI entry point
├── ju.py                   # Short alias
├── run.ps1                 # PowerShell runner
├── 
├── # Development & Testing
├── test-runner.py          # Test runner
├── debug-helper.py         # Debug helper
├── 
├── # Environment Management
├── setup-environment.ps1   # Environment setup
├── 
├── # Build System
├── build-windows.ps1       # Windows build script
├── build-unix.sh           # Unix build script
├── JiraUtil.spec           # PyInstaller spec
├── 
├── # Source Code
├── src/                    # Main source code
├── tests/                  # Test files
├── docs/                   # Documentation
└── .venv/                  # Virtual environment
```

---

*For detailed information, see the [documentation](docs/) folder.*
