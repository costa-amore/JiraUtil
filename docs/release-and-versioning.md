# Release and Versioning Guide

This guide covers the versioning system and release workflow for JiraUtil.

## 🎯 Overview

JiraUtil uses a **smart versioning system** that automatically increments build numbers only when code changes are detected, combined with a **controlled release workflow** that separates development, testing, and release phases.

## 📋 Version Format

Versions follow **M.m.bld** format:

- **M** = Major version (manually set)
- **m** = Minor version (manually set)  
- **bld** = Build number (automatically incremented by build system)

**Key Rule**: Only major.minor versions can be set manually. Build numbers are always auto-managed and reset to 0 when you manually set a version.

Examples: `1.0`, `1.2` (manual) → `1.0.1`, `1.2.3` (after builds)

## 🔧 Version Management

### Manual Version Setting

**⚠️ Never edit `scripts/version.json` manually!** Use the dev-friendly command:

```bash
# Set version to 1.0 (build number will be 0)
.\run.ps1 tools\set-version.py 1.0

# Set version to 2.1 (build number will be 0)
.\run.ps1 tools\set-version.py 2.1

# Check current version
.\run.ps1 tools\set-version.py --current
```

### Automatic Build Incrementing

Build numbers increment automatically when code changes are detected in:

- `src/` directory files
- `docs/` directory files  
- `README.md` (functional changes, not version updates)
- Build scripts (`run.ps1`, `scripts/build-windows.ps1`, etc.)
- Configuration files (`JiraUtil.spec`, etc.)

Build numbers do NOT increment for:

- Version number updates only
- Build output files
- Cache files
- No actual code changes

## 🚀 Release Workflow

### Development Phase

- **Command**: `.\scripts\build-windows.ps1`
- **Purpose**: Local development and testing
- **Behavior**: Builds executables, runs tests, no version increment, no git changes

### CI Testing Phase

- **Command**: `git push`
- **Purpose**: CI testing and build feedback
- **Behavior**: Triggers build job only, no version increment, no release created

### Release Phase

- **Command**: `.\scripts\release.ps1 -Platform windows`
- **Purpose**: Create official release
- **Behavior**: Increments version, commits changes, pushes to GitHub, creates release

## 📝 Common Workflows

### Starting a New Major Version

```bash
.\run.ps1 tools\set-version.py 2.0    # Set to 2.0.0
.\scripts\build-windows.ps1           # Build with auto-increment
```

### Hotfix Release

```bash
.\run.ps1 tools\set-version.py 1.0    # Set to 1.0.0
.\scripts\build-windows.ps1           # Build with auto-increment
```

### Development Build

```bash
# Make code changes, then:
.\scripts\build-windows.ps1           # Will auto-increment if changes detected
```

### Creating a Release

```bash
.\scripts\release.ps1 -Platform windows  # Increments version and publishes
```

## 🔄 GitHub Actions

- **Build Job**: Triggers on every push, runs tests and builds, no release
- **Release Job**: Triggers on manual dispatch, creates GitHub release with artifacts

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
| `git push` | CI testing | ❌ No | ❌ No | ✅ Build only |
| `.\scripts\release.ps1` | Create release | ✅ Yes | ✅ Yes | ✅ Build + Release |

---

*This guide provides everything you need to manage versions and create releases for JiraUtil.*

[🏠 Home](../README.md) | [← Building Executables](building-executables.md) | [Command Reference →](command-reference.md)
