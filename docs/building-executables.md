# Building Executables

🏠 [Home](../README.md)

This guide explains how to build standalone executables for the JiraUtil project that can run on Windows systems without requiring Python to be installed.

## Prerequisites

- Python 3.8 or higher
- All project dependencies installed
- PyInstaller (installed automatically by build scripts)

## Code Quality (Optional)

Before building, you may want to run linting to check code quality:

```powershell

# Check for linting issues
.\scripts\lint-all.ps1

# Fix linting issues automatically
.\scripts\lint-all.ps1 -Fix
```

**Note**: Linting is not integrated into the build process due to reliability issues that were causing build failures. The build process focuses on testing and compilation only.

## Quick Start

**Important**: The build process runs tests first and will abort if any tests fail. This ensures only working code gets built into executables.

### Simple Build (Recommended)

```powershell

# Build for Windows (default platform)
.\scripts\build.ps1

# Build with clean (removes previous build)
.\scripts\build.ps1 -Clean

# Build for release (increments version)
.\scripts\build.ps1 -BuildForRelease
```

### Platform-Specific Build Scripts

```powershell

# Windows-specific build script
.\scripts\build-windows.ps1
```

## Build Strategy

The project uses a **dedicated script per platform** approach:

1. **Platform-specific scripts** (e.g., `build-windows.ps1`) - Handle platform-specific details
2. **Generic build script** (`build.ps1`) - Contains the core build logic
3. **Default behavior** - Running `build.ps1` without parameters defaults to Windows

### Build Scripts

- **`scripts/build.ps1`** - Generic build script (defaults to Windows)
- **`scripts/build-windows.ps1`** - Windows-specific convenience script
- **`JiraUtil.spec`** - PyInstaller configuration file (auto-generated)

## Output Structure

See [File Structure Reference](shared/file-structure.md) for complete file organization details.

**Build Output:**

- `build-executables/` - Contains platform-specific folders and ZIP files
- Each platform folder includes executable, launcher scripts, and documentation

## Distribution

### For End Users

1. **Download** the appropriate ZIP file for your platform
2. **Extract** the ZIP file to a folder
3. **Edit** `jira_config.env` with your Jira credentials (file is ready to use)
4. **Run** the executable:
   - Windows: Double-click `JiraUtil.exe` or run `run.bat`

### Configuration

See [Configuration Reference](shared/configuration.md) for detailed setup instructions.

## Advanced Configuration

### Custom PyInstaller Options

Edit `JiraUtil.spec` to customize the build:

```python

# Add custom data files
datas=[
    ('custom_file.txt', '.'),
    ('templates', 'templates'),
],

# Add hidden imports
hiddenimports=[
    'custom_module',
    'another_module',
],

# Exclude unnecessary modules
excludes=[
    'tkinter',
    'matplotlib',
],
```

### Build Dependencies

Install build-specific dependencies:

```bash
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **PyInstaller not found**
   - The build scripts will automatically install PyInstaller
   - Ensure virtual environment is set up: `./setup-environment.ps1`

2. **Missing dependencies**
   - Rebuild virtual environment: `./setup-environment.ps1`
   - Check `hiddenimports` in `JiraUtil.spec`

3. **Large executable size**
   - Use `--exclude-module` to remove unused modules
   - Consider using `--onedir` instead of `--onefile` for smaller size

4. **Import errors in executable**
   - Add missing modules to `hiddenimports` in `JiraUtil.spec`
   - Test the executable thoroughly

### Build Verification

The build process automatically runs tests before building, but you can also verify manually:

```powershell

# Run tests before building (good practice - although the build process runs the tests as well)
.\run.ps1 tests\run_tests.py

# Test the built executables

# Windows
.\build-executables\Windows\JiraUtil.exe --help
```

### Performance Considerations

- **One-file vs One-dir**: One-file is easier to distribute but slower to start
- **UPX compression**: Enabled by default, can be disabled if causing issues
- **Console window**: Kept for debugging, can be removed for GUI apps

## File Sizes

Typical executable sizes:

- **Windows**: ~32 MB (current build)

Sizes may vary depending on included dependencies and compression settings.

## Security Considerations

- Executables are not digitally signed
- Consider code signing for production distribution
- Scan executables with antivirus software before distribution
- Test on clean systems to ensure compatibility

---

[🏠 Home](../README.md) | [← Testing](testing.md) | [Release and Versioning →](release-and-versioning.md)
