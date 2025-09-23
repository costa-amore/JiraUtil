# Release Workflow Documentation

## Overview

This document describes the current release workflow strategy for JiraUtil, which provides clean separation between development, testing, and release phases.

## Workflow Strategy

### 🛠️ Development Phase
- **Command**: `.\scripts\build-windows.ps1`
- **Purpose**: Local development and testing
- **Behavior**:
  - ✅ Builds executables
  - ✅ Runs all tests
  - ✅ **No version increment**
  - ✅ **No git changes**
  - ✅ Can be run as many times as needed
- **Use case**: During development, debugging, testing changes

### 📤 Push Phase
- **Command**: `git push`
- **Purpose**: CI testing and build feedback
- **Behavior**:
  - ✅ **Only triggers build job** (no release)
  - ✅ Runs tests in CI environment
  - ✅ Builds executables in CI
  - ✅ **No version increment**
  - ✅ **No release created**
- **Use case**: Getting CI feedback, testing in cloud environment

### 🚀 Release Phase
- **Command**: `.\scripts\release.ps1 -Platform windows`
- **Purpose**: Create official release
- **Behavior**:
  - ✅ **Increments version** (e.g., 1.0.32 → 1.0.33)
  - ✅ **Commits version changes** to git
  - ✅ **Pushes to GitHub**
  - ✅ **Triggers dedicated release workflow**
  - ✅ **Creates GitHub release** with artifacts
  - ✅ **Uploads ZIP files** for download
- **Use case**: When ready to publish a new version

## GitHub Actions Workflow

### Build Job (`build-windows`)
- **Trigger**: Every push to main branch
- **Purpose**: CI testing and build verification
- **Output**: Build artifacts (ZIP files)
- **No release creation**

### Release Job (`create-release`)
- **Trigger**: Only on manual workflow dispatch
- **Purpose**: Create GitHub release
- **Dependencies**: Requires successful build job
- **Output**: GitHub release with download links

## Key Benefits

1. **Clean Separation**: Development, testing, and release are distinct phases
2. **No Accidental Releases**: Releases only happen when explicitly requested
3. **Version Control**: Developer controls when versions increment
4. **CI Feedback**: Build and test feedback on every push
5. **No Conflicts**: Local and CI versions stay synchronized
6. **Flexible Development**: Can build and test locally without affecting versions

## File Structure

```
├── build-windows.ps1          # Local development builds
├── release.ps1               # Release builds with version increment
├── .github/workflows/
│   └── build-and-release.yml # CI workflow configuration
└── docs/
    └── RELEASE_WORKFLOW.md   # This documentation
```

## Commands Reference

| Command | Purpose | Version Change | Git Changes | CI Trigger |
|---------|---------|----------------|-------------|------------|
| `.\build-windows.ps1` | Local development | ❌ No | ❌ No | ❌ No |
| `git push` | CI testing | ❌ No | ❌ No | ✅ Build only |
| `.\release.ps1` | Create release | ✅ Yes | ✅ Yes | ✅ Build + Release |

## Workflow States

### State 1: Development
- Working on code changes
- Running `.\build-windows.ps1` for testing
- No version changes, no git commits

### State 2: CI Testing
- Pushed changes to GitHub
- CI runs build job automatically
- Getting feedback on build/test results
- Still no version changes

### State 3: Release Ready
- Code is stable and tested
- Ready to publish new version
- Run `.\release.ps1` to create release
- Version increments and release is created

## Troubleshooting

### Issue: Unwanted releases created
- **Cause**: Release job triggered on regular pushes
- **Solution**: Ensure release job only runs on `workflow_dispatch`

### Issue: Version conflicts between local and CI
- **Cause**: CI trying to increment version
- **Solution**: CI should only read committed version, not increment

### Issue: Build job not running
- **Cause**: Workflow syntax errors or incorrect triggers
- **Solution**: Check YAML syntax and trigger conditions

## Future Improvements

1. **Automated Testing**: Add more comprehensive CI tests
2. **Release Notes**: Enhance automatic release note generation
3. **Multi-platform**: Re-enable macOS and Linux builds
4. **Version Validation**: Add checks for version format consistency
5. **Rollback Support**: Add ability to rollback releases if needed

---

*This workflow provides a robust, controlled approach to software releases while maintaining development flexibility.*
