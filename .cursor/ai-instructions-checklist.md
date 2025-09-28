# AI Development Checklist

## Before Starting Any Feature

- [ ] Read the core instructions: `.cursor/ai-instructions-core.md`
- [ ] Follow TDD process from core instructions

## If Test Fails for Technical Reasons

- [ ] Stop implementation
- [ ] Read refactoring guide: `.cursor/ai-instructions-refactoring.md`
- [ ] Suggest specific refactoring to make code testable
- [ ] Wait for user confirmation before proceeding

## If Test Fails for Functional Reasons

- [ ] Follow TDD process from core instructions

## Test Execution Commands

- [ ] See `.cursor/ai-instructions-core.md` for test execution commands

## Common Mistakes to Avoid

- [ ] Don't implement multiple features in one step
- [ ] Don't add CLI integration until function works
- [ ] Don't skip the test-first approach
- [ ] Don't use direct python commands for testing
- [ ] Don't proceed if test fails for technical reasons
- [ ] Don't make assumptions when instructions are unclear
- [ ] Don't guess at command syntax - ask for clarification
- [ ] Don't forget commit message standards - use prefixes and focus on WHY
