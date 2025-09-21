# Setup Guide

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
# Run the setup script (creates virtual environment and installs dependencies)
./rebuild-venv.ps1
```

This script will:
- Create a new virtual environment (`.venv`)
- Install all required dependencies
- Copy `jira_config_example.env` to `.venv\jira_config.env`

### 3. Configuration
Edit `.venv\jira_config.env` with your Jira credentials:

```env
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_PASSWORD=your_api_token_here
```

**Security Note**: Use Jira API tokens instead of passwords for better security.

## Verification

Test your setup:
```powershell
# Check if everything works
./run.ps1 .\JiraCsv.py --help
```

## Troubleshooting

### Virtual Environment Issues
If you encounter issues with the virtual environment:
```powershell
# Rebuild everything
./rebuild-venv.ps1
```

### Dependencies Issues
If you update `requirements.txt`:
```powershell
# Rebuild with new dependencies
./rebuild-venv.ps1
```

### Jira Connection Issues
- Verify your Jira URL is correct
- Check your API token is valid
- Ensure you have permission to access the issues

---

[← Back to README](README.md) | [CSV Export Commands →](csv_export-commands.md)
