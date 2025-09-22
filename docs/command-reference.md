# Command Reference

Quick reference for all JiraUtil commands and options.

## Command Structure

```bash
JiraUtil <command> [subcommand] [options] [arguments]
```

## Available Commands

### CSV Export Commands

| Command | Short | Description |
|---------|-------|-------------|
| `CsvExport remove-newline` | `ce rn` | Remove newline characters from CSV fields |
| `CsvExport extract-to-comma-separated-list` | `ce ecl` | Extract field values to comma-separated text file |
| `CsvExport fix-dates-eu` | `ce fd` | Convert dates for European Excel format |

### Jira Commands

| Command | Short | Description |
|---------|-------|-------------|
| `ResetTestFixture` | `rt` | Update issue status based on summary pattern |
| `AssertExpectations` | `ae` | Assert issues are in expected status |

## Command Details

### CsvExport remove-newline

**Usage:**
```bash
JiraUtil CsvExport remove-newline <input> [--output <file>]
JiraUtil ce rn <input> [--output <file>]
```

**Arguments:**
- `input` - Path to input CSV file

**Options:**
- `--output`, `-o` - Output file path (default: `<input-stem>-no-newlines.csv`)

**Example:**
```bash
JiraUtil ce rn data.csv --output clean-data.csv
```

### CsvExport extract-to-comma-separated-list

**Usage:**
```bash
JiraUtil CsvExport extract-to-comma-separated-list <field_name> <input>
JiraUtil ce ecl <field_name> <input>
```

**Arguments:**
- `field_name` - Name of field to extract (e.g., "Assignee", "Status")
- `input` - Path to input CSV file

**Example:**
```bash
JiraUtil ce ecl "Assignee" data.csv
```

### CsvExport fix-dates-eu

**Usage:**
```bash
JiraUtil CsvExport fix-dates-eu <input> [--output <file>]
JiraUtil ce fd <input> [--output <file>]
```

**Arguments:**
- `input` - Path to input CSV file

**Options:**
- `--output`, `-o` - Output file path (default: `<input-stem>-eu-dates.csv`)

**Example:**
```bash
JiraUtil ce fd data.csv --output eu-data.csv
```

### ResetTestFixture

**Usage:**
```bash
JiraUtil ResetTestFixture [label] [--jira-url <url>] [--username <user>] [--password <pass>]
JiraUtil rt [label] [--jira-url <url>] [--username <user>] [--password <pass>]
```

**Arguments:**
- `label` - Jira label to search for (default: "rule-testing")

**Options:**
- `--jira-url` - Jira instance URL
- `--username` - Jira username
- `--password` - Jira password/API token

**Example:**
```bash
JiraUtil rt my-test-label
```

### AssertExpectations

**Usage:**
```bash
JiraUtil AssertExpectations [label] [--jira-url <url>] [--username <user>] [--password <pass>]
JiraUtil ae [label] [--jira-url <url>] [--username <user>] [--password <pass>]
```

**Arguments:**
- `label` - Jira label to search for (default: "rule-testing")

**Options:**
- `--jira-url` - Jira instance URL
- `--username` - Jira username
- `--password` - Jira password/API token

**Example:**
```bash
JiraUtil ae my-test-label
```

## Global Options

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message |
| `--jira-url <url>` | Override Jira URL from config |
| `--username <user>` | Override Jira username from config |
| `--password <pass>` | Override Jira password from config |

## Configuration

The tool looks for credentials in this order:
1. Command line options (`--jira-url`, `--username`, `--password`)
2. `jira_config.env` file in the same directory as the executable
3. Environment variables (`JIRA_URL`, `JIRA_USERNAME`, `JIRA_PASSWORD`)
4. Interactive prompts

## Test Fixture Pattern

For Jira test fixture commands, issue summaries must match:

```
I was in <status1> - expected to be in <status2>
```

**ResetTestFixture** uses `<status1>` as the target status.
**AssertExpectations** uses `<status2>` as the expected status.

## Exit Codes

- `0` - Success
- `1` - Error (invalid arguments, connection failed, etc.)

## Examples

### Complete Workflow

```bash
# 1. Process CSV file
JiraUtil ce rn raw-data.csv --output clean-data.csv

# 2. Extract assignees
JiraUtil ce ecl "Assignee" clean-data.csv

# 3. Reset test fixtures
JiraUtil rt rule-testing

# 4. Verify expectations
JiraUtil ae rule-testing
```

### Using Short-hand Commands

```bash
# CSV processing
JiraUtil ce rn data.csv
JiraUtil ce ecl "Status" data.csv
JiraUtil ce fd data.csv

# Jira operations
JiraUtil rt
JiraUtil ae
```

### With Custom Credentials

```bash
JiraUtil rt --jira-url https://mycompany.atlassian.net --username me@company.com --password my_token
```
