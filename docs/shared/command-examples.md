# Command Examples Reference

## Basic Command Structure

```bash
JiraUtil <command> [subcommand] [options] [arguments]
```


## CSV Processing Examples

### Remove Newlines
```bash
# Basic usage
JiraUtil CsvExport remove-newline input.csv

# With custom output
JiraUtil CsvExport remove-newline input.csv --output clean-data.csv

# Short-hand
JiraUtil ce rn input.csv
```


### Extract Field Values
```bash
# Extract assignees
JiraUtil CsvExport extract-to-comma-separated-list "Assignee" input.csv

# Extract status values
JiraUtil CsvExport extract-to-comma-separated-list "Status" input.csv

# Short-hand
JiraUtil ce ecl "Assignee" input.csv
```


### Fix Dates for European Excel
```bash
# Basic usage
JiraUtil CsvExport fix-dates-eu input.csv

# With custom output
JiraUtil CsvExport fix-dates-eu input.csv --output eu-data.csv

# Short-hand
JiraUtil ce fd input.csv
```


## Jira Test Fixture Examples

### ResetTestFixture
```bash
# Default label (rule-testing)
JiraUtil ResetTestFixture

# Custom label
JiraUtil ResetTestFixture my-test-label

# With custom credentials
JiraUtil ResetTestFixture --jira-url https://company.atlassian.net --username user@company.com --password token

# Short-hand
JiraUtil rt my-test-label
```


### AssertExpectations
```bash
# Default label (rule-testing)
JiraUtil AssertExpectations

# Custom label
JiraUtil AssertExpectations my-test-label

# With custom credentials
JiraUtil AssertExpectations --jira-url https://company.atlassian.net --username user@company.com --password token

# Short-hand
JiraUtil ae my-test-label
```


## Help Commands

```bash
# General help
JiraUtil --help

# Command-specific help
JiraUtil CsvExport --help
JiraUtil ResetTestFixture --help
JiraUtil AssertExpectations --help

# Short-hand help
JiraUtil ce --help
JiraUtil rt --help
JiraUtil ae --help
```


## Complete Workflow Examples

### CSV Processing Workflow
```bash
# 1. Clean the data
JiraUtil ce rn raw-data.csv --output clean-data.csv

# 2. Extract specific fields
JiraUtil ce ecl "Assignee" clean-data.csv
JiraUtil ce ecl "Status" clean-data.csv

# 3. Fix dates for European Excel
JiraUtil ce fd clean-data.csv --output final-data.csv
```


### Jira Test Fixture Workflow
```bash
# 1. Reset test fixtures to initial state
JiraUtil rt rule-testing

# 2. Run your automation/tests here
# (manual step or external process)

# 3. Verify expectations
JiraUtil ae rule-testing
```


### Development Workflow
```bash
# 1. Setup environment
./setup-environment.ps1

# 2. Run tests
python test-runner.py

# 3. Debug specific command
python debug-helper.py

# 4. Build executable
./build-windows.ps1
```


## Short-hand Command Reference

| Full Command | Short | Description |
|--------------|-------|-------------|
| `CsvExport remove-newline` | `ce rn` | Remove newlines from CSV |
| `CsvExport extract-to-comma-separated-list` | `ce ecl` | Extract field values |
| `CsvExport fix-dates-eu` | `ce fd` | Fix dates for EU Excel |
| `ResetTestFixture` | `rt` | Reset test fixtures |
| `AssertExpectations` | `ae` | Assert expectations |


## Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--help`, `-h` | Show help | `JiraUtil --help` |
| `--output`, `-o` | Output file | `--output result.csv` |
| `--jira-url` | Jira URL | `--jira-url https://company.atlassian.net` |
| `--username` | Jira username | `--username user@company.com` |
| `--password` | Jira password/token | `--password my_token` |
