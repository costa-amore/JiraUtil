# Building Executables

This guide explains how to build standalone executables for the JiraUtil project that can run on Windows, macOS, and Linux systems without requiring Python to be installed.

## Prerequisites

- Python 3.8 or higher
- All project dependencies installed
- PyInstaller (installed automatically by build scripts)

## Quick Start

### Windows

```powershell
# Build for all platforms
./build-windows.ps1

# Build for specific platform
./build-windows.ps1 -Platform windows

# Clean build before building
./build-windows.ps1 -Clean
```

### macOS/Linux

```bash
# Build for all platforms
./build-unix.sh

# Build for specific platform
./build-unix.sh --platform macos
./build-unix.sh --platform linux

# Clean build before building
./build-unix.sh --clean
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

After building, you'll find:

```
build-executables/
├── Windows/
│   ├── JiraUtil.exe
│   ├── run.bat
│   ├── jira_config_example.env
│   ├── README.md
│   └── docs/
├── macOS/
│   ├── JiraUtil
│   ├── run.sh
│   ├── jira_config_example.env
│   ├── README.md
│   └── docs/
├── Linux/
│   ├── JiraUtil
│   ├── run.sh
│   ├── jira_config_example.env
│   ├── README.md
│   └── docs/
├── JiraUtil-Windows.zip
├── JiraUtil-macOS.zip
└── JiraUtil-Linux.zip
```

## Distribution

### For End Users

1. **Download** the appropriate ZIP file for your platform
2. **Extract** the ZIP file to a folder
3. **Edit** `jira_config.env` with your Jira credentials (file is ready to use)
4. **Run** the executable:
   - Windows: Double-click `JiraUtil.exe` or run `run.bat`
   - macOS/Linux: Run `./JiraUtil` or `./run.sh`

### Configuration

Users need to edit `jira_config.env`:

```env
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_PASSWORD=your_api_token_here
```

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
   - Or install manually: `pip install pyinstaller`

2. **Missing dependencies**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check `hiddenimports` in `JiraUtil.spec`

3. **Large executable size**
   - Use `--exclude-module` to remove unused modules
   - Consider using `--onedir` instead of `--onefile` for smaller size

4. **Import errors in executable**
   - Add missing modules to `hiddenimports` in `JiraUtil.spec`
   - Test the executable thoroughly

### Build Verification

Test the built executables:

```bash
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

[🏠 Home](../README.md) | [← Project Structure](project-structure.md) | [Testing →](testing.md)
