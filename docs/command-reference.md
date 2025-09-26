# Command Reference

🏠 [Home](../README.md)

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
| `csv-export remove-newlines` | `ce rn` | Remove newline characters from CSV fields |
| `csv-export extract-to-comma-separated-list` | `ce ecl` | Extract field values to comma-separated text file |
| `csv-export fix-dates-eu` | `ce fd` | Convert dates for European Excel format |

### Test Fixture Commands

| Command | Short | Description |
|---------|-------|-------------|
| `test-fixture reset` | `tf r` | Reset test fixture issues based on summary pattern |
| `test-fixture assert` | `tf a` | Assert test fixture issues are in expected status |
| `test-fixture trigger` | `tf t` | Trigger automation rules by toggling a label on a specific issue |

### Utility Commands

| Command | Short | Description |
|---------|-------|-------------|
| `list` | `ls` | Show all available commands |
| `status` | `st` | Show tool status and information |

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

### csv-export remove-newlines

**Usage:**

```bash
JiraUtil csv-export remove-newlines <input> [--output <file>]
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

### csv-export extract-to-comma-separated-list

**Usage:**

```bash
JiraUtil csv-export extract-to-comma-separated-list <field_name> <input>
JiraUtil ce ecl <field_name> <input>
```

**Arguments:**

- `field_name` - Name of field to extract (e.g., "Assignee", "Status")
- `input` - Path to input CSV file

**Example:**

```bash
JiraUtil ce ecl "Assignee" data.csv
```

### csv-export fix-dates-eu

**Usage:**

```bash
JiraUtil csv-export fix-dates-eu <input> [--output <file>]
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

### test-fixture reset

**Usage:**

```bash
JiraUtil test-fixture reset [label] [--jira-url <url>] [--username <user>] [--password <pass>]
JiraUtil tf r [label] [--jira-url <url>] [--username <user>] [--password <pass>]
```

**Arguments:**

- `label` - Jira label to search for (default: "rule-testing")

**Options:**

- `--jira-url` - Jira instance URL
- `--username` - Jira username
- `--password` - Jira password/API token

**Example:**

```bash
JiraUtil tf r my-test-label
```

### test-fixture assert

**Usage:**

```bash
JiraUtil test-fixture assert [label] [--jira-url <url>] [--username <user>] [--password <pass>]
JiraUtil tf a [label] [--jira-url <url>] [--username <user>] [--password <pass>]
```

**Arguments:**

- `label` - Jira label to search for (default: "rule-testing")

**Options:**

- `--jira-url` - Jira instance URL
- `--username` - Jira username
- `--password` - Jira password/API token

**Example:**

```bash
JiraUtil tf a my-test-label
```

### test-fixture trigger

**Usage:**

```bash
JiraUtil test-fixture trigger -l <label> [-k <issue_key>] [--jira-url <url>] [--username <user>] [--password <pass>]
JiraUtil tf t -l <label> [-k <issue_key>] [--jira-url <url>] [--username <user>] [--password <pass>]
```

**Arguments:**

- `-l`, `--label` - Label(s) to trigger automation rules (comma-separated for multiple labels) (required)
- `-k`, `--key` - Issue key to trigger (default: "TAPS-212")

**Options:**

- `--jira-url` - Jira instance URL
- `--username` - Jira username
- `--password` - Jira password/API token

**Description:**

Triggers automation rules by setting labels on a specific issue. For single labels, it toggles the label (removes if present, then adds it back). For multiple comma-separated labels, it replaces all existing labels with the new ones in a single operation.

**Examples:**

```bash

# Trigger with single label (default issue key)
JiraUtil tf t -l "TransitionSprintItems"

# Trigger with multiple labels
JiraUtil tf t -l "TransitionSprintItems,CloseEpic,UpdateStatus"

# Trigger with specific issue key
JiraUtil tf t -l "TransitionSprintItems" -k "PROJ-123"

# Trigger multiple labels with specific issue key
JiraUtil tf t -l "TransitionSprintItems,CloseEpic" -k "PROJ-123"

# Trigger with custom Jira credentials
JiraUtil tf t -l "MyRule" -k "PROJ-456" --jira-url "https://mycompany.atlassian.net" --username "user@company.com" --password "token"
```

**Logging:**

- `INFO`: When label is removed from issue (single label mode)
- `INFO`: When label is set on issue (single label mode)
- `INFO`: When labels are set on issue (multiple labels mode)
- `ERROR`: When no valid labels are provided
- `FATAL ERROR`: When issue is not found

### list

**Usage:**

```bash
JiraUtil list
JiraUtil ls
```

**Description:** Show all available commands and their descriptions.

**Example:**

```bash
JiraUtil ls
```

### status

**Usage:**

```bash
JiraUtil status
JiraUtil st
```

**Description:** Show tool status and information including version and configuration.

**Example:**

```bash
JiraUtil st
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

---

[🏠 Home](../README.md) | [← Release and Versioning](release-and-versioning.md) | [Troubleshooting →](troubleshooting.md)
