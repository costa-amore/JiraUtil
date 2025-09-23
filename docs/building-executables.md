# Building Executables

This guide explains how to build standalone executables for the JiraUtil project that can run on Windows, macOS, and Linux systems without requiring Python to be installed.

## Prerequisites

- Python 3.8 or higher
- All project dependencies installed
- PyInstaller (installed automatically by build scripts)

## Quick Start

**Important**: The build process runs tests first and will abort if any tests fail. This ensures only working code gets built into executables.

### Windows

```powershell
# Build for all platforms

# Build for specific platform
./build-windows.ps1 -Platform windows

# Clean build before building
./build-windows.ps1 -Clean
```

### macOS/Linux

```bash
# Build for all platforms

# Build for specific platform
./build.sh --platform macos
./build.sh --platform linux

# Clean build before building
./build.sh --clean
```

## Build Options

### Platform Options

- `windows` - Windows executable (.exe)
- `macos` - macOS universal binary (Intel + Apple Silicon)
- `linux` - Linux executable
- `all` - Build for all platforms (default)

### Build Scripts

1. **`build-windows.ps1`** - PowerShell script for Windows
2. **`build-unix.sh`** - Bash script for macOS/Linux
3. **`JiraUtil.spec`** - PyInstaller configuration file

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
   - macOS/Linux: Run `./JiraUtil` or `./run.sh`

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
pip install -r requirements-build.txt
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

```bash
# Run tests before building (good practice - although the build process runs the tests as well )
python tests/run_tests.py

# Test the built executables
# Windows
.\JiraUtil.exe --help

# macOS/Linux
./JiraUtil --help
```

### Performance Considerations

- **One-file vs One-dir**: One-file is easier to distribute but slower to start
- **UPX compression**: Enabled by default, can be disabled if causing issues
- **Console window**: Kept for debugging, can be removed for GUI apps

## Cross-Platform Building

### Building on Different Platforms

- **Windows**: Can build Windows and Linux executables
- **macOS**: Can build macOS and Linux executables  
- **Linux**: Can build Linux executables

### Docker Build (Optional)

For consistent builds across platforms, you can use Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install pyinstaller

RUN python -m PyInstaller --onefile JiraUtil.py

CMD ["cp", "dist/JiraUtil", "/output/"]
```

## File Sizes

Typical executable sizes:

- **Windows**: ~15-25 MB
- **macOS**: ~20-30 MB (universal binary)
- **Linux**: ~15-25 MB

Sizes may vary depending on included dependencies and compression settings.

## Security Considerations

- Executables are not digitally signed
- Consider code signing for production distribution
- Scan executables with antivirus software before distribution
- Test on clean systems to ensure compatibility

---

[🏠 Home](../README.md) | [← Testing](testing.md) | [Versioning →](versioning.md)
