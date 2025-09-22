# Test Fixture Pattern Reference

## Pattern Format

For Jira test fixture management, issue summaries must match this pattern:

```text
I was in <status1> - expected to be in <status2>
```

## Examples

**Valid patterns:**

- `I was in To Do - expected to be in In Progress`
- `I was in In Progress - expected to be in Done`
- `I was in SIT/LAB VALIDATED - expected to be in CLOSED`
- `I was in CLOSED - expected to be in CLOSED`

**Invalid patterns:**

- `I was in TODO - expected to be in IN PROGRESS` (wrong case)
- `I was in To Do - expected to be in In Progress` (extra spaces)
- `Was in To Do - expected to be in In Progress` (missing "I")
- `I was in To Do expected to be in In Progress` (missing " - ")

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
