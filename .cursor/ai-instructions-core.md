# Core AI Instructions

## MANDATORY: Test Execution

**ALWAYS use `.\run.ps1` for tests - NEVER use `python -m pytest`**

```bash

# Individual test files
.\run.ps1 tests\test_file.py

# All tests
.\run.ps1 tests\run_tests.py

# Test categories
.\run.ps1 tests\run_tests.py testfixture
```

## MANDATORY: TDD Process

1. **Write ONE test first** - must fail for functional reasons (missing behavior)
2. **Run test with `.\run.ps1`** - verify it fails for right reasons
3. **If fails for technical reasons** (imports, syntax) → suggest refactoring first
4. **If fails for functional reasons** → implement minimal code to pass
5. **Repeat with next test**

## MANDATORY: Start with Scaffolding Test

- Write ONE test that demonstrates core expected behavior
- Test must fail for functional reasons, not technical reasons
- If technical failure → suggest refactoring to make code testable

## Common Refactoring for Testability

- Extract pure functions (no I/O)
- Use dependency injection
- Separate business logic from I/O
- Return data instead of printing

## When Uncertain

- **Ask for clarification** rather than making assumptions
- **Test commands** to verify they work before using them
- **Don't guess** - it's better to ask than to implement incorrectly

## Commit Messages

- **Use prefixes** with clear meanings:
  - `feat`: Enhancement of functionality (may include test code)
  - `fix`: Repair functionality that was released
  - `test`: Enhancement of test coverage
  - `refactor`: Change to code structure without changing functionality
  - `release`: Commit that triggers CI to release
  - `chore`: Changes to dev, build, release scripts or configurations
- **Focus on WHY** the change was made, not WHAT changed
- **Keep concise** - avoid repeating details visible in diff
- **Check recent history** for consistent style

## Linter Guidelines

- **Use IDE linter feedback**: Check `read_lints` tool for real-time feedback
- **Fix issues immediately** after editing files
- **Avoid automated linters** that may introduce unwanted changes
- **Always verify** no linter errors before committing changes
