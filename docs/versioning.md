# Versioning System

This document explains how the JiraUtil versioning system works and how to manage versions.

## 🎯 Overview

JiraUtil uses a **smart versioning system** that automatically increments the build number only when actual code changes are detected. This prevents unnecessary version increments when building the same code multiple times.

## 📋 Version Format

Versions follow the format: **M.m.bld**

- **M** = Major version (manually set)
- **m** = Minor version (manually set)  
- **bld** = Build number (automatically incremented)

Examples: `1.0.0`, `1.2.5`, `2.0.12`

## 🔧 Managing Versions

### Setting Version Numbers

**⚠️ IMPORTANT: Never edit `version.json` manually!**

Use the dev-friendly command instead:

```bash
# Set version to 1.0.0
python set-version.py 1.0.0

# Set version to 2.1.0
python set-version.py 2.1.0

# Check current version
python set-version.py --current
```

### Automatic Version Incrementing

The build system automatically increments the build number when:

- ✅ Any file in `src/` directory changes
- ✅ Any file in `docs/` directory changes  
- ✅ `README.md` changes (functional changes, not version updates)
- ✅ Any build scripts change (`run.ps1`, `build-windows.ps1`, etc.)
- ✅ Any configuration files change (`JiraUtil.spec`, etc.)

The build system does NOT increment when:

- ❌ Only version numbers are updated in files
- ❌ Build output files change
- ❌ Cache files change
- ❌ No actual code changes are made

## 🚀 How It Works

### 1. Code Change Detection

The system calculates SHA256 hashes of all tracked files and compares them with stored hashes to detect changes.

**Tracked files:**

- All `.py` files in `src/` and root
- All `.md` files in `docs/` and root
- All `.ps1` and `.sh` build scripts
- Configuration files (`.spec`, `.json`)

**Ignored files:**

- `version.json` (version file itself)
- `version_info.txt` (generated file)
- Build output directories
- Cache directories

### 2. Build Process

```bash
# 1. Check for code changes
python version_manager.py increment-if-changed

# 2. If changes detected:
#    - Increment build number
#    - Update README.md with new version
#    - Update version_info.txt for PyInstaller
#    - Update all documentation files

# 3. If no changes:
#    - Keep current version
#    - Skip file updates

# 4. Build executable with current version
```

### 3. Version Synchronization

All files are kept in sync with the same version number:

- `version.json` - Master version file
- `README.md` - Development documentation
- `version_info.txt` - PyInstaller metadata
- `build-executables/*/README.md` - User documentation
- `build-executables/*/command-reference.md` - Command reference
- `build-executables/*/troubleshooting.md` - Troubleshooting guide
- `JiraUtil.exe` - Executable file properties

## 📝 Common Workflows

### Starting a New Major Version

```bash
# Set new major version
python set-version.py 2.0.0

# Build with new version
.\build-windows.ps1
```

### Hotfix Release

```bash
# Set hotfix version
python set-version.py 1.0.1

# Build hotfix
.\build-windows.ps1
```

### Development Build

```bash
# Make code changes
# ... edit files ...

# Build (will auto-increment)
.\build-windows.ps1
```

### Checking Current Version

```bash
# Show current version
python set-version.py --current

# Or use version manager directly
python version_manager.py get
```

## 🔍 Troubleshooting

### Version Not Incrementing

If the version isn't incrementing when you expect it to:

1. **Check if files are tracked:**

   ```bash
   python code_change_detector.py changed
   ```

2. **Check if changes are detected:**

   ```bash
   python code_change_detector.py check
   ```

3. **Force version update completion:**

   ```bash
   python -c "from version_manager import VersionManager; VersionManager().mark_version_update_complete()"
   ```

### Manual Version Reset Issues

If you manually edited `version.json` and caused issues:

1. **Reset to a known good version:**

   ```bash
   python set-version.py 1.0.0
   ```

2. **Mark as complete:**

   ```bash
   python -c "from version_manager import VersionManager; VersionManager().mark_version_update_complete()"
   ```

### Version Mismatch

If files show different versions:

1. **Check current version:**

   ```bash
   python version_manager.py get
   ```

2. **Update all files:**

   ```bash
   python update-dev-version.py
   ```

## 📁 Files Involved

### Core Versioning Files

- `version.json` - Master version file (DO NOT EDIT MANUALLY)
- `version_manager.py` - Version management logic
- `code_change_detector.py` - Change detection system
- `set-version.py` - Dev-friendly version setting command

### Build Integration Files

- `build-windows.ps1` - Windows build script
- `build-unix.sh` - Unix build script
- `update-dev-version.py` - Updates README.md
- `create-version-info.py` - Creates PyInstaller version info

### Generated Files

- `version_info.txt` - PyInstaller version metadata
- `.code_hash` - File hash storage (auto-generated)

## 🎯 Best Practices

1. **Always use `set-version.py`** instead of editing `version.json`
2. **Set major.minor versions manually** for releases
3. **Let build numbers auto-increment** during development
4. **Check version before important builds** with `--current`
5. **Don't manually edit version-related files** unless you know what you're doing

## 🚨 Warnings

- **Never edit `version.json` manually** - Use `set-version.py` instead
- **Don't delete `.code_hash`** - This stores file change detection data
- **Don't edit generated files** - They're updated automatically during builds
- **Test version changes** - Always verify the version is correct after changes
