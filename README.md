# JIRA utility

A Python utility for supporting Jira admins.

## Version

Version: 1.0.2

## 🚀 Quick Start

1. **Setup**: Run `./setup-environment.ps1` to create the environment and install dependencies
2. **Configure**: Edit `.venv\jira_config.env` with your Jira credentials
3. **Run**: Use `./run.ps1 .\JiraUtil.py --help` or `./run.ps1 .\ju.py --help` to see all available commands
4. **Version**: Use `./run.ps1 .\ju.py --version` or `./run.ps1 .\ju.py -v` to check the current version

## 🔢 Version Management

JiraUtil uses smart versioning that automatically increments build numbers only when code changes are detected.

**Quick Commands:**

```bash
python set-version.py 1.0.0          # Set version to 1.0.0
python set-version.py --current      # Show current version
```

**⚠️ Never edit `version.json` manually!** Use `set-version.py` instead.

📖 **[Complete Versioning Guide](docs/versioning.md)** - Detailed documentation on how versioning works

## 📋 Available Commands

### CSV Export File Support

- **csv-export remove-newlines** (`ju.py ce rn`): Clean CSV fields from newline characters
- **csv-export extract-to-comma-separated-list** (`ju.py ce ecl`): Extract specific field values to comma-separated lists
- **csv-export fix-dates-eu** (`ju.py ce fd`): Convert dates for European Excel format

### Test Fixture Management

- **test-fixture reset** (`ju.py tf r`): Reset test fixture issues based on summary patterns
- **test-fixture assert** (`ju.py tf a`): Assert that test fixture issues are in expected status

### Utility Commands

- **list** (`ju.py ls`): Show all available commands
- **status** (`ju.py st`): Show tool status and information

## 📚 Documentation

### For Users

- **[User Guide](docs/user-guide.md)** - Complete user guide for executable users
- **[Command Reference](docs/command-reference.md)** - Quick command reference
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

### For Developers

- **[Setup Guide](docs/setup.md)** - Development environment setup
- **[Project Structure](docs/project-structure.md)** - Code organization
- **[Testing](docs/testing.md)** - Running tests and development
- **[Building Executables](docs/building-executables.md)** - Creating standalone executables
- **[Detailed Commands](docs/csv_export-commands.md)** - CSV processing details
- **[Jira Integration](docs/jira-commands.md)** - Jira integration details

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
