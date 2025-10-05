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

### ALWAYS keep the tests green when refactoring - run them regularly

### When not refactoring

#### NEVER change code unless a test shows you need it

### When creating a todo list for a feature (ask for review after each step)

1. **Create a short list of GWT examples** to finetune the specs
2. **Determine 1st GWT to create test for** (simplest context)
3. **Find a test to update** if we're adjusting existing behavior
4. **or Write a scaffolding test** for new behavior (to help us design and write testable code)
5. **Run the tests** to prove that we can catch this behavior not being there
6. **Change / add as little code as possible** to make the test pass
7. **Add more tests or make it a parametrized test** to prove more examples
8. **Refactoring**: when all examples have been proven to work, check the 4 rules of simple design:
   8.1 **Keep all tests green** during these steps
   8.2 **All changed code expresses intent**
   8.3 **No duplication of concepts** (check changed files and the structures they are part of)
       8.3.1 **List design smells**
       8.3.2 **Propose design patterns** that could be appropriate
   8.4 **Reduce the nr of elements** as much as possible
       8.4.1 **Reduce test coupled to implementation** by removing scaffolding tests that cover behavior already tested by API tests
       8.4.2 **Extract code into it's own module** when API tests would become too complex or slow to cover the same behavior as the scaffolding tests. Promote the scaffolding tests to API tests
9. **Review & update the list of GWTs**

## MANDATORY: Bug Fix Process (When Asked to 'Fix')

**Follow this EXACT sequence - no shortcuts:**

1. **ROLLBACK** - Undo any recent changes to restore the broken state
2. **ADD TEST** - Create a test that detects the problem (should fail initially)
3. **RUN TEST** - Execute the test to prove it detects the problem (test fails for right reasons)
4. **FIX ISSUE** - Implement the minimal fix needed
5. **RUN ALL TESTS** - Verify the fix works and nothing else broke
6. **CLEAN UP** - Remove any temporary files or debug code

**Why this works:** Rollback ensures you're fixing the actual problem, test-driven approach proves the fix works, minimal changes reduce risk.

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

## Instruction File Maintenance

- **ALWAYS review instruction files** after making changes to them
- **Check for consistency** - same concepts should use same wording
- **Check for conciseness** - remove redundant or verbose content
- **Check for duplications** - eliminate repeated information across files
- **Verify linter compliance** - use `read_lints` tool on instruction files
- **Keep single source of truth** - reference rather than repeat information
