# Command Reference

Quick reference for all JiraUtil commands and options.

## Command Structure

```bash
JiraUtil <command> [subcommand] [options] [arguments]
```

## Available Commands

### General Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message and exit |
| `-v`, `--version` | Show program version and exit |

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

### Version Command

```bash
JiraUtil --version
JiraUtil -v
```

**Description**: Display the current version of JiraUtil.

**Output**: Shows version in format `JiraUtil X.Y.Z`

**Examples**:
```bash
# Show version
JiraUtil --version
# Output: JiraUtil 1.0.2

# Short form
JiraUtil -v
# Output: JiraUtil 1.0.2
```

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

See [Configuration Reference](shared/configuration.md) for detailed setup instructions.

## Test Fixture Pattern

See [Test Fixture Pattern Reference](shared/test-fixture-pattern.md) for pattern requirements and behavior.

## Exit Codes

- `0` - Success
- `1` - Error (invalid arguments, connection failed, etc.)

## Examples

See [Command Examples Reference](shared/command-examples.md) for comprehensive examples and usage patterns.
