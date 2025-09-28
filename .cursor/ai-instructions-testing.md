# Testing Instructions

## Test Execution Commands

See `.cursor/ai-instructions-core.md` for test execution commands.

**Note**: To run specific test methods, edit the test file temporarily or use pytest directly (but this requires virtual environment activation).

## Test Structure Rules

- Use Given-When-Then (GWT) approach
- Extract helper methods for setup
- Keep test methods small and focused
- Group public methods first, private methods last
- Sort methods alphabetically within groups

## Test Failure Types

- **Functional failure**: Missing behavior, wrong output, NotImplementedError
- **Technical failure**: ImportError, SyntaxError, AttributeError on imports

## Before Starting Work

1. Run `.\run.ps1 tests\run_tests.py` - verify all tests pass
2. Write ONE failing test for the feature
3. Verify test fails for functional reasons
4. If technical failure → suggest refactoring first
