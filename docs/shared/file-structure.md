# File Structure Reference

🏠 [Home](../../README.md)

## Executable Package Structure

```text
JiraUtil/
├── JiraUtil.exe          # Main executable (Windows)
├── run.bat               # Windows launcher script
├── jira_config.env       # Configuration file (ready to edit)
├── README.md             # User guide
└── docs/                 # Documentation folder
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
JiraUtil/
├── # Entry Points
├── JiraUtil.py           # Main CLI entry point
├── ju.py                 # Short alias
├── run.ps1               # PowerShell runner
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── jira_config_example.env # Configuration template
├──
├── # Development & Testing
├── tests/                # Test files
├── tools/                # Development tools
│   ├── debug-helper.py   # Debug helper
│   ├── set-version.py    # Version management
│   └── ...
├──
├── # Environment Management
├── setup-environment.ps1 # Environment setup
├──
├── # Build System
├── scripts/              # Build and release scripts
│   ├── build-windows.ps1 # Windows build script
│   ├── build.ps1         # Generic build script
│   ├── release.ps1       # Release script
│   └── ...
├── docker/               # Docker configuration
├──
├── # Source Code
├── src/                  # Main source code
│   ├── cli/              # CLI components
│   ├── auth/             # Authentication
│   ├── config/           # Configuration
│   ├── csv_utils/        # CSV processing
│   ├── testfixture/      # Test fixture management
│   └── ...
├── docs/                 # Documentation
│   ├── shared/           # Shared documentation
│   └── ...
├──
├── # Build Output
├── build/                # PyInstaller build files
├── build-executables/    # Generated executables
└── .venv/                # Virtual environment
```

## Key Files

### Entry Points

- **`JiraUtil.py`** - Main CLI entry point
- **`ju.py`** - Short alias for JiraUtil
- **`run.ps1`** - PowerShell runner script

### Development & Testing

- **`tests/run_tests.py`** - Comprehensive test runner
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
- **`requirements.txt`** - Python package dependencies (includes build deps)

## File Naming Conventions

- **Executables**: `JiraUtil.exe` (Windows), `JiraUtil` (Unix)
- **Scripts**: `setup-environment.ps1`, `build-windows.ps1`, `tests/run_tests.py`
- **Configuration**: `jira_config.env`, `jira_config_example.env`
- **Documentation**: `docs/user-guide.md`, `docs/command-reference.md`, `docs/troubleshooting.md`
