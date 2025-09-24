# JIRA utility

A Python utility for supporting Jira admins.

## Version

Version: 1.0.44.8

## 🚀 Quick Start

1. **Setup**: Run `.\setup-environment.ps1` to create the environment, install dependencies, and activate the virtual environment
2. **Configure**: Edit `.venv\jira_config.env` with your Jira credentials
3. **Run**: Use `.\run.ps1 .\JiraUtil.py --help` or `.\run.ps1 .\ju.py --help` to see all available commands
4. **Test**: Run `.\run.ps1 tests\run_tests.py` to verify everything works correctly
5. **Build**: Use `.\scripts\build-windows.ps1` to create executables (runs tests first, then versioning and building)
6. **Release**: Use `.\scripts\release.ps1 -Platform windows` to create a new release (increments version and publishes)

**Note**: The run script automatically uses the virtual environment, so it works consistently across all terminal sessions.

**Release Workflow**: See [Release and Versioning](docs/release-and-versioning.md) for detailed information about the development, testing, and release process.

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

- **[User Guide](user-guide.md)** - Complete user guide for executable users
- **[Command Reference](docs/command-reference.md)** - Quick command reference
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

### For Developers

- **[Setup Guide](docs/setup.md)** - Development environment setup
- **[Project Structure](docs/project-structure.md)** - Code organization
- **[Testing](docs/testing.md)** - Running tests and development
- **[Building Executables](docs/building-executables.md)** - Creating standalone executables
- **[Release and Versioning](docs/release-and-versioning.md)** - Version management and release workflow
- **[Detailed Commands](docs/csv_export-commands.md)** - CSV processing details
- **[Jira Integration](docs/jira-commands.md)** - Jira integration details

## 🛠️ Development

### 🧪 **Comprehensive Test Suite**

The project includes a comprehensive functional test suite covering all major functionalities:

```powershell
# Run all tests with detailed output
.\run.ps1 tests\run_tests.py

# Run specific test categories
.\run.ps1 tests\run_tests.py csv          # CSV export functionality
.\run.ps1 tests\run_tests.py testfixture  # Test fixture management
.\run.ps1 tests\run_tests.py cli          # CLI commands and parsing
.\run.ps1 tests\run_tests.py overview     # Functional overview tests
```

**Test Coverage:** Comprehensive functional testing with 72 tests covering all major functionalities

### 🔧 **Development Tools**

- **Tests**: `.\run.ps1 tests\run_tests.py` (always uses virtual environment)
- **Debug**: Use `.\run.ps1 debug-helper.py` for debugging any command
- **Rebuild**: `.\setup-environment.ps1` to update dependencies and reactivate environment
- **Build Executables**: `.\build-windows.ps1` (Windows)

**Note**: The run script automatically uses the virtual environment, so it works consistently across all terminal sessions. After running the setup script, you can also use `python` commands directly in the same session.

## 🔢 Version Management
<!-- Test comment for version increment -->

JiraUtil uses smart versioning that automatically increments build numbers only when code changes are detected.

**Quick Commands:**

```powershell
.\run.ps1 tools\set-version.py 1.0         # Set version to 1.0.0.0 (build and local will be 0)
.\run.ps1 tools\set-version.py --current   # Show current version
```

**⚠️ Important:**

- Never edit `scripts/version.json` manually! Use `tools/set-version.py` instead.
- Only major.minor versions can be set manually (e.g., `1.0`, `2.1`)
- Build and local numbers are always auto-managed and reset to 0 when you set a version manually
- Local builds increment the 4th component (local build number)
- Releases increment the 3rd component (build number) and reset local to 0

📖 **[Complete Release and Versioning Guide](docs/release-and-versioning.md)** - Detailed documentation on versioning and release workflow

## 📁 Project Structure

```text
Jira_csv_helper/
├── # Entry Points
├── JiraUtil.py             # Main CLI entry point
├── ju.py                   # Short alias
├── run.ps1                 # PowerShell runner
├──
├── # Development & Testing
├── debug-helper.py         # Debug helper
├──
├── # Environment Management
├── setup-environment.ps1   # Environment setup
├──
├── # Build System
├── scripts\                # Build and release scripts
├── tools\                  # Development tools
├──
├── # Source Code
├── src\                    # Main source code
├── tests\                  # Test files
├── docs\                   # Documentation
└── .venv\                  # Virtual environment
```

---

*For detailed information, see the [documentation](docs\) folder.*
