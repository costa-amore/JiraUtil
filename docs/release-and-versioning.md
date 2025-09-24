# Release and Versioning Guide

🏠 [Home](../README.md)

This guide covers the versioning system and release workflow for JiraUtil.

## 🎯 Overview

JiraUtil uses a **smart versioning system** that automatically increments build numbers only when code changes are detected, combined with a **controlled release workflow** that separates development, testing, and release phases.

## 📋 Version Format

Versions follow **M.m.b.l** format:

- **M** = Major version (manually set)
- **m** = Minor version (manually set)
- **b** = Build number (incremented on releases and CI builds)
- **l** = Local build number (incremented on local builds)

**Key Rules**:

- Only major.minor versions can be set manually
- Build and local numbers are always auto-managed and reset to 0 when you manually set a version
- Local builds increment the local number (4th component)
- Releases increment the build number (3rd component) and reset local to 0

Examples: `1.0` (manual) → `1.0.0.0` → `1.0.0.1` (local build) → `1.0.1.0` (release)

## 🔧 Version Management

### Manual Version Setting

**⚠️ Never edit `scripts/version.json` manually!** Use the dev-friendly command:

```bash
# Set version to 1.0 (build and local numbers will be 0)
.\run.ps1 tools\set-version.py 1.0

# Set version to 2.1 (build and local numbers will be 0)
.\run.ps1 tools\set-version.py 2.1

# Check current version
.\run.ps1 tools\set-version.py --current
```

### Automatic Version Incrementing

**Build numbers** (3rd component) increment on releases and CI builds (always increments, regardless of code changes).

**Local build numbers** (4th component) increment on local builds only when code changes are detected.

Local build numbers increment when changes are detected in:

- `src/` directory files
- `docs/` directory files
- `README.md` (functional changes, not version updates)
- Build scripts (`run.ps1`, `scripts/build-windows.ps1`, etc.)
- Configuration files (`JiraUtil.spec`, etc.)

Local build numbers don't increment for:

- Version number updates only
- Build output files
- Cache files
- No actual code changes

**Note**: Build numbers (3rd component) always increment on releases, regardless of code changes.

## 🚀 Release Workflow

### Development Phase

- **Command**: `.\scripts\build-windows.ps1`
- **Purpose**: Local development and testing
- **Behavior**: Builds executables, runs tests, increments local build number, no git changes

### Release Phase

- **Command**: `.\scripts\release.ps1 -Platform windows`
- **Purpose**: Create official release
- **Behavior**: Increments build number, commits changes, pushes to git (including tags)
- **Prerequisites**: All code changes must be committed first

### CI Build & Release Phase

- **Triggered by**: Git push and tag push (from release script)
- **Purpose**: Build artifacts and create GitHub release
- **Behavior**: CI automatically builds and creates GitHub release with artifacts

## 📝 Common Workflows

### Starting a New Major Version

```bash
.\run.ps1 tools\set-version.py 2.0    # Set to 2.0.0.0
.\scripts\build-windows.ps1           # Build with local increment (2.0.0.1)
```

### Hotfix Release

```bash
.\run.ps1 tools\set-version.py 1.0    # Set to 1.0.0.0
.\scripts\build-windows.ps1           # Build with local increment (1.0.0.1)
```

### Development Build

```bash
# Make code changes, then:
.\scripts\build-windows.ps1           # Will auto-increment local build if changes detected
```

### Creating a Release

```bash
# 1. Commit all changes first
git add .
git commit -m "Your commit message"

# 2. Create the release
.\scripts\release.ps1 -Platform windows  # Increments build number, commits, pushes, and triggers CI
```

**⚠️ Important**: The release script will fail if there are uncommitted changes. The release script will push all commits and trigger CI automatically.

## 🔄 GitHub Actions

- **Build Job**: Triggers on push from release script (based on the tag it commits), runs tests and builds, creates GitHub release with artifacts
- **Release Job**: Triggers on manual dispatch, creates GitHub release with artifacts
- **Note**: CI never pushes to git - it only builds and creates GitHub releases

## 📁 Key Files

- `scripts/version.json` - Master version file (DO NOT EDIT)
- `tools/set-version.py` - Manual version setting
- `tools/version_manager.py` - Version management logic
- `tools/code_change_detector.py` - Change detection system

## 🔍 Troubleshooting

### Version Not Incrementing

```bash
# Check if files are tracked
.\run.ps1 tools\code_change_detector.py changed

# Check if changes are detected
.\run.ps1 tools\code_change_detector.py check

# Force version update completion
python -c "import sys; sys.path.insert(0, 'tools'); from version_manager import VersionManager; VersionManager('scripts/version.json').mark_version_update_complete()"
```

### Manual Version Reset Issues

```bash
# Reset to known good version
.\run.ps1 tools\set-version.py 1.0

# Mark as complete
python -c "import sys; sys.path.insert(0, 'tools'); from version_manager import VersionManager; VersionManager('scripts/version.json').mark_version_update_complete()"
```

### Version Mismatch

```bash
# Check current version
.\run.ps1 tools\version_manager.py get --version-file scripts/version.json

# Update all files
.\run.ps1 tools\update-dev-version.py
```

## 🎯 Best Practices

1. **Always use `tools/set-version.py`** instead of editing `scripts/version.json`
2. **Set only major.minor versions manually** (e.g., `1.0`, `2.1`) - build numbers are auto-managed
3. **Let build numbers auto-increment** during development
4. **Use development builds** for testing without affecting versions
5. **Use release builds** only when ready to publish
6. **Remember**: Manual version setting resets build number to 0

## 🚨 Warnings

- **Never edit `scripts/version.json` manually**
- **Don't try to set build numbers manually** - they are always auto-managed
- **Don't delete `.code_hash`** - stores file change detection data
- **Don't edit generated files** - they're updated automatically

## 📊 Commands Reference

| Command | Purpose | Version Change | Git Changes | CI Trigger |
|---------|---------|----------------|-------------|------------|
| `.\scripts\build-windows.ps1` | Local development | ❌ No | ❌ No | ❌ No |
| `git add . && git commit` | Prepare for release | ❌ No | ✅ Yes | ❌ No |
| `.\scripts\release.ps1` | Create release | ✅ Yes | ✅ Yes | ✅ Build + Release |

**Notes**:

- The release script requires all changes to be committed first (but not pushed)
- The release script handles the git push and triggers CI automatically
- CI never pushes to git - it only builds and creates GitHub releases

---

*This guide provides everything you need to manage versions and create releases for JiraUtil.*

[🏠 Home](../README.md) | [← Building Executables](building-executables.md) | [Command Reference →](command-reference.md)
