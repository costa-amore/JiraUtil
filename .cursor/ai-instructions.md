# AI Development Instructions

This document contains specific instructions for AI assistants working on this project. Follow these guidelines to ensure consistent, high-quality development practices.

**IMPORTANT**: Ignore `.cursor/human-commands.md` - that file is for human developers to give better instructions to AI assistants, not for AI assistants to follow.

## Quick Reference Files

- **Core Instructions**: `.cursor/ai-instructions-core.md` - Essential rules and commands
- **Testing Guide**: `.cursor/ai-instructions-testing.md` - Test execution and structure
- **Refactoring Guide**: `.cursor/ai-instructions-refactoring.md` - Making code testable
- **Checklist**: `.cursor/ai-instructions-checklist.md` - Step-by-step process

## Quick Commands

- **Bug Fix**: Follow the 6-step process in core instructions (ROLLBACK → ADD TEST → RUN TEST → FIX → RUN ALL → CLEAN UP)
- **New Feature**: Follow TDD process in core instructions
- **Test Execution**: Always use `.\run.ps1` - never direct python commands

## MANDATORY: Read Core Instructions First

**Before starting any work, read `.cursor/ai-instructions-core.md`**

## Development Process

### TDD Process

**See `.cursor/ai-instructions-core.md` for the complete TDD process.**

### Bug Fix Process

1. **ROLLBACK** - Undo recent changes to restore broken state
2. **ADD TEST** - Create test that detects the problem (should fail initially)
3. **RUN TEST** - Execute test to prove it detects the problem
4. **FIX ISSUE** - Implement minimal fix needed
5. **RUN ALL TESTS** - Verify fix works and nothing else broke
6. **CLEAN UP** - Remove temporary files or debug code

### Test Execution

- **Individual files**: `.\run.ps1 tests\test_file.py`
- **All tests**: `.\run.ps1 tests\run_tests.py`
- **Categories**: `.\run.ps1 tests\run_tests.py testfixture`
- **NEVER use** `python -m pytest` directly

### Test File Structure

When creating new test files, follow the existing patterns:

- **Class-based tests**: Use `class TestFeatureName:` (no unittest.TestCase inheritance)
- **Parametrized tests**: Use `@pytest.mark.parametrize` with `pytest.main([__file__])` at bottom
- **Assertions**: Use `assert` statements, not `self.assert*` methods
- **GWT comments**: Keep Given/When/Then structural comments for clarity
- **Helper methods**: Use `_` prefix for private helper methods
- **Constants**: Define test constants at class level
- **Imports**: Follow existing import patterns in other test files

### Test Categories

- `testfixture` - Test fixture operations
- `csv` - CSV export functionality
- `cli` - Command line interface
- `build` - Build system tests
- `functional` - End-to-end functionality tests

## Code Quality Guidelines

### Implementation Rules

- **NEVER implement more than needed for current test to pass**
- **NEVER add CLI integration until function works**
- **NEVER add multiple features in one step**
- **ALWAYS verify test fails for functional reasons before implementing**

### Command Execution

- **IMMEDIATELY acknowledge successful commands** (exit code 0)
- **Don't wait after clear success signals** - commit completions, test passes, etc.
- **Ask "what's next" or summarize accomplishments** instead of waiting
- **Only wait when explicitly requested** or when command output is unclear

### Code Organization

- **ALWAYS group public functions at top, private at bottom**
- **ALWAYS sort both groups alphabetically**
- **Extract large functions** (>10 lines) and classes (>50 lines)
- **Split large files** (>100 lines) into single-purpose files

### Test Consistency

- **ALWAYS follow same mocking pattern** for similar tests
- **ALWAYS mock all external dependencies** in every test
- **ALWAYS use consistent decorator order** and parameter names
- **NEVER mix mocked and unmocked calls** in same test file

## Documentation Standards

### General Rules

- **NEVER create duplicate content** within or across files
- **ALWAYS check for existing duplication** before adding new content
- **Use IDE linter feedback** with `read_lints` tool for real-time feedback
- **Fix linter issues immediately** after editing files

### Markdown Formatting

- **ALWAYS add blank lines** before and after lists, code blocks, headers
- **Use consistent list formatting** within sections
- **Use proper heading hierarchy** (H1 → H2 → H3)
- **NEVER add trailing spaces** - always trim whitespace

### PowerShell Scripting

- **NEVER use `$args`** as variable name (conflicts with PowerShell automatic variable)
- **Use descriptive variable names** like `$arguments`, `$parameters`
- **Always validate script parameters** before using them
- **NEVER use emojis** in script output (causes encoding issues)

## Commit Message Standards

### Prefixes

- `feat`: Enhancement of functionality (may include test code)
- `fix`: Repair functionality that was released
- `test`: Enhancement of test coverage
- `refactor`: Change to code structure without changing functionality
- `release`: Commit that triggers CI to release
- `chore`: Changes to dev, build, release scripts or configurations

### Guidelines

- **Focus on WHY** the change was made, not WHAT changed
- **Keep concise** - avoid repeating details visible in diff
- **Check recent history** for consistent style

## Release Process

- Use: `.\scripts\release.ps1 -Platform windows`
- Automatically runs tests, builds executables, bumps version, commits, pushes, creates GitHub release
- **Use IDE linter feedback** before release: `read_lints` tool
- **Fix issues** before running release script again
