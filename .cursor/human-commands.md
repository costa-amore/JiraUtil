# Human Commands - Short Commands

> **⚠️ IMPORTANT FOR AI: This file contains HUMAN instructions for using short commands in this project. Do NOT use this file as instructions for how to run tests or other commands. Always refer to the actual documentation (README.md, run_tests.py) for correct command syntax.**

## Short Command Patterns

### Commits

- `"commit this"` → Auto-detect appropriate prefix (`feat`, `fix`, `refactor`, `chore`, `test`, `release`) based on changes
- `"commit as feat"` → Force specific prefix
- `"commit with message: custom message"` → Override auto-detection

### Testing

- `"test this"` → Run appropriate test command (see README.md for correct syntax)
- `"test all"` → Run all tests (see README.md for correct syntax)
- `"test first"` → Run first/scaffolding test (see README.md for correct syntax)

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

- If working on specific test file → run appropriate test command (see README.md)
- If working on testfixture feature → run appropriate test command (see README.md)
- If working on csv feature → run appropriate test command (see README.md)
- If no context → run all tests (see README.md)

**IMPORTANT**: Always refer to README.md for correct test command syntax!

## Ambiguous Instructions

When instructions don't match well enough, respond with:
**"Do you mean: [assumption] from the dev-instructions?"**

This helps clarify intent and ensures we're on the same page.
