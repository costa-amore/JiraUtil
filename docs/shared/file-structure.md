# File Structure Reference

## Executable Package Structure

```text
JiraUtil/
├── JiraUtil.exe          # Main executable (Windows)
├── JiraUtil              # Main executable (macOS/Linux)
├── run.bat               # Windows launcher script
├── run.sh                # Unix launcher script
├── jira_config.env       # Configuration file (ready to edit)
├── README.md             # User guide
├── command-reference.md  # Quick command reference
├── troubleshooting.md    # Common issues and solutions
└── shared/               # Shared documentation references
    ├── configuration.md
    ├── test-fixture-pattern.md
    ├── file-structure.md
    └── command-examples.md
```

## Development Structure

```text
Jira_csv_helper/
├── # Entry Points
├── JiraUtil.py           # Main CLI entry point
├── ju.py                 # Short alias
├── run.ps1               # PowerShell runner
├── 
├── # Development & Testing
├── test-runner.py        # Test runner
├── debug-helper.py       # Debug helper
├── 
├── # Environment Management
├── setup-environment.ps1 # Environment setup
├── 
├── # Build System
├── build-windows.ps1     # Windows build script
├── build-unix.sh         # Unix build script
├── JiraUtil.spec         # PyInstaller spec
├── 
├── # Source Code
├── src/                  # Main source code
├── tests/                # Test files
├── docs/                 # Documentation
└── .venv/                # Virtual environment
```

## Key Files

### Entry Points
- **`JiraUtil.py`** - Main CLI entry point
- **`ju.py`** - Short alias for JiraUtil
- **`run.ps1`** - PowerShell runner script


### Development & Testing
- **`test-runner.py`** - Test runner
- **`debug-helper.py`** - Debug helper for all commands


### Environment Management
- **`setup-environment.ps1`** - One-command environment setup/rebuild


### Build System
- **`build-windows.ps1`** - Windows build script
- **`build-unix.sh`** - Unix build script
- **`JiraUtil.spec`** - PyInstaller configuration


### Configuration
- **`jira_config_example.env`** - Template for Jira credentials
- **`.venv/jira_config.env`** - Actual credentials (created by setup)
- **`requirements.txt`** - Python package dependencies
- **`requirements-build.txt`** - Build-specific dependencies


## File Naming Conventions

- **Executables**: `JiraUtil.exe` (Windows), `JiraUtil` (Unix)
- **Scripts**: `setup-environment.ps1`, `build-windows.ps1`, `test-runner.py`
- **Configuration**: `jira_config.env`, `jira_config_example.env`
- **Documentation**: `user-guide.md`, `command-reference.md`, `troubleshooting.md`
