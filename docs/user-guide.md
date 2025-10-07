# JiraUtil - User Guide

A powerful command-line tool for Jira administrators and power users.

## 🚀 Quick Start

1. **Download** the appropriate ZIP file for your platform
2. **Extract** the ZIP file to a folder
3. **Edit** `jira_config.env` with your Jira credentials
4. **Run** the tool:
   - Windows: Run `JiraUtil.exe -h` or double-click `run.bat`
   - macOS/Linux: Run `./JiraUtil -h` or `./run.sh`

## 📋 Available Commands

### CSV Export File Support

- **CsvExport remove-newline** (`ce rn`): Clean CSV fields from newline characters
- **CsvExport extract-to-comma-separated-list** (`ce ecl`): Extract specific field values to comma-separated lists
- **CsvExport fix-dates-eu** (`ce fd`): Convert dates for European Excel format

### Jira Test Fixture Management

- **ResetTestFixture** (`rt`): Update issue status based on summary patterns
- **AssertExpectations** (`ae`): Assert that issues are in their expected status based on summary patterns

## ⚙️ Configuration

See [Configuration Reference](shared/configuration.md) for detailed setup instructions.

**Quick Setup:**

1. Edit `jira_config.env` with your Jira credentials
2. Use API tokens instead of passwords for better security
3. The tool will prompt you if template values are detected

## 🔧 Custom Batch Files

The included `run.bat` file provides a simple launcher for JiraUtil. You can create custom batch files for frequently used commands.

### Creating Custom Batch Files

1. **Copy `run.bat`** as a starting template
2. **Rename** your custom files to start with `_` (underscore) so they appear at the top in Windows Explorer
3. **Modify** the command to include your specific parameters

### Examples

**`_reset-test-fixtures.bat`:**
```batch
@echo off
JiraUtil.exe test-fixture reset --tsl my-test-label
pause
```

**`_trigger-automation.bat`:**
```batch
@echo off
JiraUtil.exe test-fixture trigger --tl "automation-label1,automation-label2" -k PROJECT-123
pause
```

**`_csv-cleanup.bat`:**
```batch
@echo off
JiraUtil.exe csv-export remove-newlines "%~1"
pause
```

### Benefits

- **Quick access** to frequently used commands
- **Consistent parameters** without typing them each time
- **Easy sharing** of common workflows with team members
- **File Explorer sorting** with underscore prefix

## 📖 Command Examples

See [Command Examples Reference](shared/command-examples.md) for comprehensive examples and usage patterns.

## 🔧 Command Line Options

### Global Options

- `--help` - Show help message
- `--jira-url URL` - Override Jira URL
- `--username USER` - Override Jira username
- `--password PASS` - Override Jira password

### CSV Export Options

- `--output FILE` - Specify output file path

## 🎯 Test Fixture Pattern

See [Test Fixture Pattern Reference](shared/test-fixture-pattern.md) for detailed pattern requirements and behavior.

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

See [File Structure Reference](shared/file-structure.md) for complete file organization details.

## 📚 Documentation

For detailed information, see the complete documentation:

- **[Command Reference](command-reference.md)** - Complete command syntax and options
- **[Troubleshooting Guide](troubleshooting.md)** - Detailed troubleshooting and error solutions

---

*For developers and advanced users, see the full documentation in the `docs/` folder.*
