# Test Fixture Pattern Reference

🏠 [Home](../../README.md)

## Pattern Format

For Jira test fixture management, issue summaries must match one of these patterns:

**Format 1 (Original):**

```text
[<optional context> - ]I was in <status1> - expected to be in <status2>
```

**Format 2 (Starting Pattern):**

```text
[<optional context> - ]starting in <status1> - expected to be in <status2>
```

## Examples

**Valid issue summary patterns (Format 1):**

- `I was in To Do - expected to be in In Progress`
- `I was in In Progress - expected to be in Done`
- `I was in SIT/LAB VALIDATED - expected to be in CLOSED`
- `I was in CLOSED - expected to be in CLOSED`

**Valid issue summary patterns (Format 2):**

- `starting in To Do - expected to be in In Progress` (without context)
- `Bug fix - starting in To Do - expected to be in In Progress` (with context)
- `Feature request - starting in In Progress - expected to be in Done` (with context)
- `Hotfix - starting in SIT/LAB VALIDATED - expected to be in CLOSED` (with context)
- `Enhancement - starting in CLOSED - expected to be in CLOSED` (with context)

**Invalid issue summary patterns:**

- `I was in To Do` (missing expected part)
- `Expected to be in In Progress` (missing I was in part)
- `I was in To Do expected to be in In Progress` (missing " - ")
- `I was To Do - expected to be in In Progress` (missing "in")
- `I was in - expected to be in In Progress` (empty status)
- `Context - starting in To Do expected to be in In Progress` (missing " - " in context format)

## Command Behavior

### ResetTestFixture

- **Purpose**: Update issue status based on summary pattern
- **Uses**: `<status1>` as the target status
- **Action**: Changes issue status to `<status1>`
- **Skip**: If already in target status

### AssertExpectations

- **Purpose**: Verify issues are in expected status
- **Uses**: `<status2>` as the expected status
- **Action**: Compares current status with `<status2>`
- **Result**: Reports pass/fail for each issue

## Status Name Requirements

- Use exact Jira status names (case-sensitive)
- Avoid extra spaces or special characters
- Check status names in your Jira instance
- Common statuses: "To Do", "In Progress", "Done", "Closed"

## Pattern Matching Rules

- Case-insensitive matching for the pattern structure
- Exact matching for status names
- Whitespace around status names is trimmed
- Pattern must be complete and well-formed

## Troubleshooting Pattern Issues

### "Summary doesn't match expected pattern"

1. Check the exact format: `I was in <status1> - expected to be in <status2>`
2. Verify status names match your Jira instance exactly
3. Ensure no extra spaces or characters
4. Check the issue summary is not empty or malformed

### "Status not found" or transition errors

1. Verify the status name exists in your Jira workflow
2. Check you have permission to transition to that status
3. Ensure the status is available for that issue type
4. Try with a different, known status name
