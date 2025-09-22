# JiraUtil - User Guide

A powerful command-line tool for Jira administrators and power users.

## 🚀 Quick Start

1. **Download** the appropriate ZIP file for your platform
2. **Extract** the ZIP file to a folder
3. **Edit** `jira_config.env` with your Jira credentials
4. **Run** the tool:
   - Windows: Double-click `JiraUtil.exe` or run `run.bat`
   - macOS/Linux: Run `./JiraUtil` or `./run.sh`

## 📋 Available Commands

### CSV Export File Support

- **CsvExport remove-newline** (`ce rn`): Clean CSV fields from newline characters
- **CsvExport extract-to-comma-separated-list** (`ce ecl`): Extract specific field values to comma-separated lists
- **CsvExport fix-dates-eu** (`ce fd`): Convert dates for European Excel format

### Jira Test Fixture Management

- **ResetTestFixture** (`rt`): Update issue status based on summary patterns
- **AssertExpectations** (`ae`): Assert that issues are in their expected status based on summary patterns

## ⚙️ Configuration

Edit `jira_config.env` with your Jira credentials:

```env
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_PASSWORD=your_api_token_here
```

**Security Note**: Use Jira API tokens instead of passwords for better security.

## 📖 Command Examples

### CSV Processing

```bash
# Remove newlines from CSV file
JiraUtil CsvExport remove-newline input.csv

# Extract assignee names to text file
JiraUtil CsvExport extract-to-comma-separated-list "Assignee" input.csv

# Convert dates for European Excel
JiraUtil CsvExport fix-dates-eu input.csv
```

### Jira Test Fixtures

```bash
# Reset test fixture issues (default label: rule-testing)
JiraUtil ResetTestFixture

# Reset with custom label
JiraUtil ResetTestFixture my-test-label

# Assert expectations for test fixtures
JiraUtil AssertExpectations

# Assert with custom label
JiraUtil AssertExpectations my-test-label
```

### Short-hand Commands

```bash
# CSV commands
JiraUtil ce rn input.csv
JiraUtil ce ecl "Assignee" input.csv
JiraUtil ce fd input.csv

# Jira commands
JiraUtil rt
JiraUtil ae
```

## 🔧 Command Line Options

### Global Options

- `--help` - Show help message
- `--jira-url URL` - Override Jira URL
- `--username USER` - Override Jira username
- `--password PASS` - Override Jira password

### CSV Export Options

- `--output FILE` - Specify output file path

## 🎯 Test Fixture Pattern

For Jira test fixture management, issues should have summaries matching this pattern:

```
I was in <status1> - expected to be in <status2>
```

**Examples:**
- `I was in To Do - expected to be in In Progress`
- `I was in In Progress - expected to be in Done`

### ResetTestFixture Behavior

- Finds issues with the specified label (default: "rule-testing")
- Parses summary to extract `<status1>`
- Updates issue status to `<status1>`
- Skips if already in target status

### AssertExpectations Behavior

- Finds issues with the specified label (default: "rule-testing")
- Parses summary to extract `<status2>` (expected status)
- Verifies current status matches expected status
- Reports pass/fail results

## 🚨 Troubleshooting

### Common Issues

1. **"Failed to connect to Jira"**
   - Verify your Jira URL is correct
   - Check your API token is valid
   - Ensure you have permission to access the issues

2. **"No issues found"**
   - Check the label name is correct
   - Verify issues exist with that label
   - Ensure you have permission to view the issues

3. **"Template values detected"**
   - Edit `jira_config.env` with your real credentials
   - The tool will prompt you if template values are detected

### Getting Help

- Run `JiraUtil --help` for general help
- Run `JiraUtil <command> --help` for command-specific help
- Check the configuration file format matches the example

## 📁 File Structure

```
JiraUtil/
├── JiraUtil.exe          # Main executable (Windows)
├── JiraUtil              # Main executable (macOS/Linux)
├── run.bat               # Windows launcher
├── run.sh                # Unix launcher
├── jira_config.env       # Configuration file
├── README.md             # This file
└── docs/                 # Additional documentation
```

---

*For developers and advanced users, see the full documentation in the `docs/` folder.*
