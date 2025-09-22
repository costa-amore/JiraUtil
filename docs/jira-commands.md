# Jira Commands

[🏠 Home](../README.md)

> **For users**: See [Command Reference](command-reference.md) for quick command syntax and examples.
> **For developers**: This page provides detailed implementation information.

Commands for interacting directly with Jira instances.

## ResetTestFixture

Process issues with a specified label and update their status based on summary patterns.

### Pattern Matching

The tool looks for issues with summaries matching this pattern (case-insensitive):

```text
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

See [Configuration Reference](shared/configuration.md) for detailed setup instructions.

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

```text
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

## AssertExpectations

Assert that issues with a specified label are in their expected status based on summary patterns.

### Assertion Pattern Matching

The tool looks for issues with summaries matching this pattern (case-insensitive):

```text
"I was in <status1> - expected to be in <status2>"
```

When found, it asserts that the current status matches `<status2>`.

### AssertExpectations Usage

#### AssertExpectations Basic Usage (default "rule-testing" label)

```powershell
./run.ps1 .\JiraUtil.py AssertExpectations
# Short-hand: ./run.ps1 .\ju.py ae
```

#### AssertExpectations Custom Label

```powershell
./run.ps1 .\JiraUtil.py AssertExpectations my-custom-label
# Short-hand: ./run.ps1 .\ju.py ae my-custom-label
```

#### AssertExpectations With Credentials

```powershell
./run.ps1 .\JiraUtil.py AssertExpectations --jira-url "https://yourcompany.atlassian.net" --username "your.email@company.com" --password "your_api_token"
# Short-hand: ./run.ps1 .\ju.py ae --jira-url "https://yourcompany.atlassian.net" --username "your.email@company.com" --password "your_api_token"
```

### AssertExpectations Examples

```powershell
# Assert "rule-testing" issues (default)
./run.ps1 .\JiraUtil.py AssertExpectations
# Short-hand: ./run.ps1 .\ju.py ae

# Assert "bug-fix" issues
./run.ps1 .\JiraUtil.py AssertExpectations bug-fix
# Short-hand: ./run.ps1 .\ju.py ae bug-fix

# Assert with custom credentials
./run.ps1 .\JiraUtil.py AssertExpectations --jira-url "https://company.atlassian.net" --username "user@company.com" --password "token"
# Short-hand: ./run.ps1 .\ju.py ae --jira-url "https://company.atlassian.net" --username "user@company.com" --password "token"
```

### AssertExpectations Configuration

See [Configuration Reference](shared/configuration.md) for detailed setup instructions.

### AssertExpectations How It Works

1. **Connects** to your Jira instance
2. **Searches** for issues with the specified label
3. **Analyzes** each issue's summary for the pattern
4. **Asserts** that the current status matches the expected status (status2)
5. **Reports** results (processed, passed, failed, not evaluated)

### AssertExpectations Output Example

```text
Starting assertion process for issues with label 'rule-testing'...
Connecting to Jira at: https://company.atlassian.net
Asserting TAPS-211: I was in SIT/LAB VALIDATED - expected to be in CLOSED
  Current status: SIT/LAB Validated
  Expected status: CLOSED
  ❌ FAIL - Current status 'SIT/LAB Validated' does not match expected status 'CLOSED'

Asserting TAPS-210: I was in CLOSED - expected to be in CLOSED
  Current status: Closed
  Expected status: CLOSED
  ✅ PASS - Current status matches expected status

Assertion process completed:
  Issues processed: 42
  Assertions passed: 5
  Assertions failed: 10
  Not evaluated: 27
  Failures:
    - TAPS-211: Expected 'CLOSED' but is 'SIT/LAB Validated'
    - TAPS-197: Expected 'CLOSED' but is 'Ready to Validate'
  Not evaluated: TAPS-209, TAPS-208, TAPS-206, TAPS-205, TAPS-203, TAPS-202, TAPS-201, TAPS-199, TAPS-198, TAPS-196, TAPS-195, TAPS-193, TAPS-192, TAPS-190, TAPS-189, TAPS-187, TAPS-186, TAPS-185, TAPS-183, TAPS-182, TAPS-180, TAPS-179, TAPS-178, TAPS-176, TAPS-175, TAPS-174, TAPS-171

============================================================
❌ ASSERTION FAILURES DETECTED! ❌
⚠️  10 out of 15 evaluated issues are NOT in their expected status
============================================================
```

### AssertExpectations Debugging

Use the debug script for development:

```powershell
python debug-helper.py
```

---

[← CSV Export Commands](csv_export-commands.md) | [Project Structure →](project-structure.md)
