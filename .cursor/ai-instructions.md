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

## Code Quality Guidelines

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
- **Always run linter check when updating markdown files**: `.\scripts\lint-markdown.ps1`

## Version and Release Management

### Release Process
- Use the release script: `.\scripts\release.ps1 -Platform windows`
- The release script automatically:
  - Bumps version (minor for features, patch for fixes)
  - Commits version changes
  - Pushes to remote repository
  - Creates GitHub release with feature description
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
- Fix release script to commit linter auto-fixes
- The release script runs markdown linting and auto-fixes files
- These auto-fixed files are not included in the release commit
- Need to modify `scripts/release.ps1` to commit any files modified by linter
- This prevents leaving uncommitted changes after release
