# JIRA utility

A Python utility for processing Jira CSV exports and manipulating Jira issues directly.

## 🚀 Quick Start

1. **Setup**: Run `./rebuild-venv.ps1` to create the environment and install dependencies
2. **Configure**: Edit `.venv\jira_config.env` with your Jira credentials
3. **Run**: Use `./run.ps1 .\JiraUtil.py --help` or `./run.ps1 .\ju.py --help` to see all available commands

## 📋 Available Commands

### CSV Export File Support

- **CsvExport remove-newline** (`ju.py ce rn`): Clean CSV fields from newline characters
- **CsvExport extract-to-comma-separated-list** (`ju.py ce ecl`): Extract specific field values to comma-separated lists
- **CsvExport fix-dates-eu** (`ju.py ce fd`): Convert dates for European Excel format

### Jira Automations Support

- **ResetTestFixture** (`ju.py rt`): Update issue status based on summary patterns

## 📚 Documentation

- **[Setup Guide](docs/setup.md)** - Detailed installation and configuration
- **[CSV Export Commands](docs/csv_export-commands.md)** - CSV processing functionality
- **[Jira Commands](docs/jira-commands.md)** - Jira integration features
- **[Project Structure](docs/project-structure.md)** - Code organization
- **[Testing](docs/testing.md)** - Running tests and development

## 🛠️ Development

- **Tests**: `python run_tests.py`
- **Debug**: Use `python debug_all_commands.py` for debugging any command
- **Rebuild**: `./rebuild-venv.ps1` to update dependencies

## 📁 Project Structure

```
Jira_csv_helper/
├── src/                    # Source code
├── tests/                  # Test files
├── docs/                   # Documentation
├── .venv/                  # Virtual environment
├── rebuild-venv.ps1        # Environment setup script
└── run.ps1                 # PowerShell runner
```

---

*For detailed information, see the [documentation](docs/) folder.*
