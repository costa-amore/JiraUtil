# Setup Guide

[🏠 Home](../README.md)

## Prerequisites

- Python 3.x installed
- PowerShell (Windows)
- Access to a Jira instance

## Installation

### 1. Clone or Download

```powershell

# If using git
git clone <repository-url>
cd Jira_csv_helper

# Or download and extract the project files
```

### 2. Environment Setup

```powershell

# Run the setup script (creates virtual environment, installs dependencies, and activates it)
.\setup-environment.ps1
```

This script will:

- Create a new virtual environment (`.venv`)
- Upgrade pip to the latest version (eliminates pip warnings)
- Install all required dependencies
- Copy `jira_config_example.env` to `.venv\jira_config.env`
- **Activate the virtual environment** in the current PowerShell session
- Run tests to verify everything works correctly

### 3. Configuration

Edit `.venv\jira_config.env` with your Jira credentials:

```env
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_PASSWORD=your_api_token_here
```

**Security Note**: Use Jira API tokens instead of passwords for better security.

## Verification

After running the setup script, you can use commands in two ways:

```powershell

# Option 1: Use run script (recommended - always uses venv)
.\run.ps1 .\JiraUtil.py --help
.\run.ps1 tests\run_tests.py

# Option 2: Direct python commands (only works in current session after setup)
python .\JiraUtil.py --help
.\run.ps1 tests\run_tests.py

# 3. Build executables (includes testing and versioning)
.\scripts\build-windows.ps1
```

**Note**: The run script automatically uses the virtual environment and works consistently across all terminal sessions. The setup script activates the venv in the current session, so you can also use `python` commands directly.

## Troubleshooting

### Virtual Environment Issues

If you encounter issues with the virtual environment:

```powershell

# Rebuild everything (automatically activates the environment)
.\setup-environment.ps1
```

### Dependencies Issues

If you update `requirements.txt`:

```powershell

# Rebuild with new dependencies (automatically activates the environment)
.\setup-environment.ps1
```

### General Issues

If you encounter any issues with the environment or dependencies:

```powershell

# Complete rebuild (fixes most issues and activates environment)
.\setup-environment.ps1
```

### New Terminal Sessions

For new terminal sessions, you have two options:

### Option 1: Run the setup script again (recommended)

```powershell

# This will reactivate the environment and run tests
.\setup-environment.ps1
```

### Option 2: Use the run script for any command

```powershell

# This automatically uses the virtual environment
.\run.ps1 tests\run_tests.py
.\run.ps1 .\JiraUtil.py --help
```

### Jira Connection Issues

- Verify your Jira URL is correct
- Check your API token is valid
- Ensure you have permission to access the issues

---

[↑ Back to README](../README.md) | [CSV Export Commands →](csv_export-commands.md)
