# AI Development Instructions

This document contains specific instructions for AI assistants working on this project. Follow these guidelines to ensure consistent, high-quality development practices.

## Test-Driven Development (TDD) Process

### Requirements Definition

1. **First describe the requirements in terms of examples (try to maintain a GWT style)**
2. **Ask for confirmation before continuing**

### TDD Step-by-Step Process

1. **Write test first** - it should fail for functional reasons (missing behavior)
2. **Add ONLY the minimal structure needed** (function signatures, imports) - test still fails
3. **Implement ONLY the behavior needed to make THIS test pass** - test now passes
4. **Commit this single use-case**
5. **Move to next simplest example and repeat**

### Test Failure Verification

- Tests must fail for functional reasons (missing behavior), not technical reasons (imports, syntax, etc.)
- Examples of functional failures: `NotImplementedError`, missing function, wrong behavior
- Examples of technical failures: `ImportError`, `SyntaxError`, `AttributeError` on imports

## Test Execution

### Running Tests

- **Always use the virtual environment approach**: `.\run.ps1 tests\run_tests.py`
- **For specific test categories**: `.\run.ps1 tests\run_tests.py <category>`
- **For individual test files**: `.\run.ps1 tests\run_tests.py <test_file.py>`
- **For test patterns**: `.\run.ps1 tests\run_tests.py <pattern>`

### Pre-Development Validation

**Before making any changes:**

1. **Run import validation**: `.\run.ps1 scripts\validate-imports.py`
2. **Run all tests**: `.\run.ps1 tests\run_tests.py all`
3. **Verify no failures** before starting work

**After making changes:**

1. **Run import validation**: `.\run.ps1 scripts\validate-imports.py`
2. **Run affected test categories**: `.\run.ps1 tests\run_tests.py <category>`
3. **Run all tests**: `.\run.ps1 tests\run_tests.py all`
4. **Commit only when all tests pass**

### Test Categories

- `testfixture` - Test fixture operations
- `csv` - CSV export functionality
- `cli` - Command line interface
- `build` - Build system tests
- `functional` - End-to-end functionality tests

### Running Scripts

- **Python scripts**: Use `.\run.ps1 <script_path>` to run in virtual environment
- **PowerShell scripts**: Run directly since we're already in PowerShell with venv activated

#### Python Scripts (use .\run.ps1)

- **Markdown linter**: `.\run.ps1 tools\markdown_linter.py --fix <file>`
- **Python linter**: `.\run.ps1 tools\python_linter.py --fix <file>`
- **PowerShell linter**: `.\run.ps1 tools\powershell_linter.py --fix <file>`

#### PowerShell Scripts (run directly)

- **Build script**: `.\scripts\build.ps1 -Platform windows`
- **Release script**: `.\scripts\release.ps1 -Platform windows`
- **Linter wrappers**: `.\scripts\lint-markdown.ps1`, `.\scripts\lint-python.ps1`, `.\scripts\lint-powershell.ps1`
- **All linters**: `.\scripts\lint-all.ps1` (runs all linters together)

### Dependency Management

- **ALWAYS use the setup script for installing dependencies**: `.\setup-environment.ps1`
- **NEVER use pip directly** or other package managers
- **NEVER suggest installing packages manually** - always use the setup script
- The setup script manages the virtual environment and installs from `requirements.txt`

## Code Quality Guidelines

### Refactoring Safety

**When renaming functions or moving code:**

1. **Search for all usages**: `grep -r "old_function_name" tests/ src/`
2. **Update all references** before committing
3. **Run import validation**: `.\run.ps1 scripts\validate-imports.py`
4. **Run all tests**: `.\run.ps1 tests\run_tests.py all`
5. **Verify no old references remain**

**Common refactoring patterns:**

- Function renames: Update all imports and calls
- Module moves: Update all import paths
- Parameter renames: Update all function calls
- Class renames: Update all instantiations

### Minimal Implementation Rules

- **NEVER implement more than needed for the current test to pass**
- **NEVER add CLI integration until you have a working function**
- **NEVER add multiple features in one step**
- **ALWAYS implement behavior only after structure is in place**
- **ALWAYS verify test fails for functional reasons before implementing**

### Code Extraction Criteria

- Large functions: >10 lines
- Large classes: >50 lines
- Use functional domain language (not technical IT language)

### File Splitting Criteria

- Large files: >100 lines
- Split into files with single purpose

### Code Organization Rules

- **ALWAYS group public functions at the top of files/classes**
- **ALWAYS group private functions at the bottom of files/classes**
- **ALWAYS sort both public and private groups alphabetically**
- This makes processing diffs easier and improves code navigation

## Documentation Standards

### Avoid Duplication

- **NEVER create duplicate content within a file**
- **ALWAYS check for existing duplication in sections being edited**
- If adding new capabilities, integrate them into existing sections rather than creating new ones
- Prefer referencing existing sections over repeating information
- Remove outdated or redundant content when making changes
- Keep documentation concise and focused on single source of truth

### Documentation Updates

- Add new commands to `src/cli/commands.py` `show_list()` function
- Add short aliases to the help output
- Update command reference documentation
- Test the actual command line interface to verify help output
- **Linting is now separate from build/release process** due to reliability issues
- **Run linting manually when needed**:
  - All linters: `.\scripts\lint-all.ps1 -Fix`
  - Individual: `.\scripts\lint-markdown.ps1`, `.\scripts\lint-python.ps1 -Fix`, `.\scripts\lint-powershell.ps1 -Fix`
- **Note**: Linters were removed from build process because they caused false positives and build failures

### Markdown Formatting Rules

- **ALWAYS add blank lines before and after lists** (both bullet and numbered lists)
- **ALWAYS add blank lines before and after code blocks**
- **ALWAYS add blank lines before and after headers** (except the first header after a section)
- **Use consistent list formatting** - either all bullet points or all numbered lists within a section
- **Keep line length reasonable** - break long lines at appropriate points
- **Use proper heading hierarchy** - don't skip heading levels (H1 → H2 → H3)
- **Add blank lines around blockquotes and other block elements**
- **Ensure consistent spacing** - one blank line between sections, two blank lines before major sections
- **NEVER add trailing spaces** - always trim whitespace at end of lines
- **Run linting manually** with `.\scripts\lint-all.ps1 -Fix` to catch formatting issues

### PowerShell Scripting Rules

- **NEVER use `$args` as a variable name** - it conflicts with PowerShell's automatic variable
- **Use descriptive variable names** like `$arguments`, `$parameters`, `$options`
- **Always validate script parameters** before using them
- **Use proper error handling** with try-catch blocks
- **Test PowerShell scripts** before committing changes

### Error Message Formatting Rules

- **NEVER use emojis in script output** - not in error messages, success messages, or any other output
- **Emojis don't display consistently** across all terminals and can cause encoding issues
- **Use the colored text enum** from `src/color_system.py` for visual emphasis instead
- **Keep all output clean and professional** - use clear text labels like "Problem:" and "Solution:"
- **Provide actionable solutions** - always include specific examples of correct usage

## Version and Release Management

### Release Process

- Use the release script directly: `.\scripts\release.ps1 -Platform windows`
- The release script automatically:
  - Runs tests first (tests must pass before release)
  - Builds executables (linters removed due to reliability issues)
  - Bumps version (minor for features, patch for fixes)
  - Commits version changes
  - Pushes to remote repository
  - Creates GitHub release with feature description
- Run linting manually before release if desired: `.\scripts\lint-all.ps1 -Fix`
- If tests fail, fix the issues before running release script again
- GitHub Actions are already configured in `.github` folder

## Commit Message Standards

### Commit Message Prefixes

- Use: `feat`, `fix`, `cleanup`, `chore`, `refactor`
- Keep consistent with recent commit history
- Focus on WHY the change was made, not WHAT changed (diffs show the what)
- Keep messages concise and avoid repeating details visible in the diff

### File Tracking

- Keep a list in memory of files added/edited across multiple commits for a feature
- Also create temp file in project (e.g., `.temp/implementation-files.txt`) that's git-ignored
- This helps understand what got updated over multiple commits and may help describe the feature that got added
- Clear the file when the feature is released

## Test Coverage Management

### Test Evolution Strategy

#### Scaffolding vs API Tests

- **Scaffolding Tests**: Implementation-coupled tests used during TDD development
  - Tied to HOW the behavior is implemented
  - Use these to incrementally build the design
  - Essential for TDD red-green-refactor cycles
  - Can be tightly coupled to internal structure

- **API Tests**: Behavior-focused tests for final verification
  - Test WHAT the feature does, not HOW it's implemented
  - Verify expected behavior from user perspective
  - Should be resilient to implementation changes
  - Focus on public interfaces and outcomes

#### Test Evolution Process

1. **During Development**: Use scaffolding tests to drive implementation
   - Write tests that fail for functional reasons (missing behavior)
   - Implement minimal code to make tests pass
   - Refactor while keeping tests green
   - These tests can be tightly coupled to implementation details

2. **Near Completion**: Create or adjust API tests
   - Focus on testing the expected behavior
   - Test public interfaces and user-visible outcomes
   - Make tests as implementation-agnostic as possible

3. **Cleanup Phase**: Evaluate and consolidate tests
   - Identify which scaffolding tests are covered by API tests
   - Remove redundant scaffolding tests
   - Keep only scaffolding tests that provide unique value
   - If scaffolding tests remain valuable, make them implementation-agnostic
   - If many scaffolding tests remain, consider if the module needs its own API

### Test Coverage Duplication Detection

- Detect if more than 1 test verifies the same functional use-case or part of it
- Prefer tests that test the use-case as a whole
- Keep lower level tests only if:
  - Too many meaningful variations that would obfuscate API test intent
  - API test setup/validation becomes too complex
  - In that case, review the design

## Code Review Process

### When Feature is Complete

1. **Review the tests** - detect test coverage duplication
2. **Suggest steps to reduce duplication** favoring API tests
3. **Ask for confirmation** by preparing a commit with a message describing the functionality added

### Code Review

1. **Extract large code blocks** into intent-revealing classes and functions
2. **Review the tracked files** that were added or edited across multiple commits for this feature
3. **Break up large files** into smaller files with a single purpose
4. **Ask for confirmation** by preparing a commit with a message describing the functionality added

## Implementation Details

### Bug Fixes

- (This section will be updated as needed for future bug fixes)
