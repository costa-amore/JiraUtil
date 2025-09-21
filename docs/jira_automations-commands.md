# Jira Commands

Commands for interacting directly with Jira instances.

## ResetTestFixture

Process issues with a specified label and update their status based on summary patterns.

### Pattern Matching

The tool looks for issues with summaries matching this pattern (case-insensitive):
```
"I was in <status1> - expected to be in <status2>"
```

When found, it updates the issue status to `<status1>`.

### Usage

#### Basic Usage (default "rule-testing" label)
```powershell
./run.ps1 .\JiraUtil.py ResetTestFixture
```

#### Custom Label
```powershell
./run.ps1 .\JiraUtil.py ResetTestFixture my-custom-label
```

#### With Credentials
```powershell
./run.ps1 .\JiraUtil.py ResetTestFixture --jira-url "https://yourcompany.atlassian.net" --username "your.email@company.com" --password "your_api_token"
```

### Examples

```powershell
# Process "rule-testing" issues (default)
./run.ps1 .\JiraUtil.py ResetTestFixture

# Process "bug-fix" issues
./run.ps1 .\JiraUtil.py ResetTestFixture bug-fix

# Process "feature-request" issues
./run.ps1 .\JiraUtil.py ResetTestFixture feature-request

# Process with custom credentials
./run.ps1 .\JiraUtil.py ResetTestFixture --jira-url "https://company.atlassian.net" --username "user@company.com" --password "token"
```

### Configuration

The tool automatically loads credentials from:
1. `.venv\jira_config.env` (recommended)
2. Environment variables: `JIRA_URL`, `JIRA_USERNAME`, `JIRA_PASSWORD`
3. Interactive prompts (fallback)

### How It Works

1. **Connects** to your Jira instance
2. **Searches** for issues with the specified label
3. **Analyzes** each issue's summary for the pattern
4. **Updates** the issue status to the first status mentioned
5. **Reports** results (processed, updated, skipped, errors)

### Status Transition Matching

The tool searches for transitions that contain the target status name in quotes:
- `Jump to "IMPLEMENT"`
- `Jump back to "CLOSED"`
- `To "READY for SIT/LAB"`

### Output Example

```
Starting process for issues with label 'rule-testing'...
Connecting to Jira at: https://company.atlassian.net
Processing TAPS-211: I was in SIT/LAB VALIDATED - expected to be in CLOSED
  Current status: SIT/LAB Validated
  Parsed: was in 'SIT/LAB VALIDATED', expected to be in 'CLOSED'
  Skipping - current status 'SIT/LAB Validated' already matches target status 'SIT/LAB VALIDATED'

Rule-testing process completed:
  Issues processed: 42
  Issues updated: 5
  Issues skipped: 37
```

### Debugging

Use the debug script for development:
```powershell
python debug_all_commands.py
```

---

[← CSV Export Commands](csv_export-commands.md) | [Project Structure →](project-structure.md)
