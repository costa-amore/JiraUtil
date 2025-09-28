# Dev Instructions - Short Commands

## Short Command Patterns

### Commits

- `"commit this"` → Auto-detect appropriate prefix (`feat`, `fix`, `refactor`, `chore`, `test`, `release`) based on changes
- `"commit as feat"` → Force specific prefix
- `"commit with message: custom message"` → Override auto-detection

### Testing

- `"test this"` → Run `.\run.ps1` with appropriate test file
- `"test all"` → Run all tests
- `"test first"` → Run only the first/scaffolding test

### Development

- `"start feature: description"` → Begin TDD with failing test
- `"refactor this"` → Make code more testable
- `"check lints"` → Use `read_lints` tool

### General

- `"show approach"` → List approach and todos without coding
- `"rollback"` → Undo recent changes
- `"status"` → Show current state

## Key Principles

1. **Context matters** - Infer the right action based on what we're working on
2. **Defaults are smart** - Use the most common/reasonable option
3. **Override when needed** - You can always be more specific
4. **One word + context** - "commit", "test", "refactor" work well

## Auto-Detection Rules

### Commit Prefix Detection

- **feat:** New functionality or features
- **fix:** Bug fixes or repairs
- **refactor:** Code structure changes without functionality change
- **chore:** Dev environment, build scripts, configuration changes
- **test:** Test code additions or improvements
- **release:** Version bumps, release preparation

### Test Command Detection

- If working on specific test file → run that file
- If working on feature → run related tests
- If no context → run all tests

## Ambiguous Instructions

When instructions don't match well enough, respond with:
**"Do you mean: <assumption> from the dev-instructions?"**

This helps clarify intent and ensures we're on the same page.
