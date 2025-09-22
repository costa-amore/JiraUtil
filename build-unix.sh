#!/bin/bash
# Build Executables Script for macOS and Linux
# This script compiles the JiraUtil project into standalone executables

set -e

PLATFORM="all"
CLEAN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--platform windows|macos|linux|all] [--clean]"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo "🔨 Building JiraUtil Executables"
echo "Platform: $PLATFORM"

# Handle versioning
echo "📋 Managing version..."
python version-manager.py increment
VERSION=$(python version-manager.py get)
echo "✅ Version: $VERSION"

# Create version info file
python create-version-info.py

# Update development README with version
python update-dev-version.py

# Check if PyInstaller is installed
echo "📦 Checking PyInstaller installation..."
if ! python3 -m PyInstaller --version >/dev/null 2>&1; then
    echo "❌ PyInstaller not found. Installing..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install PyInstaller"
        exit 1
    fi
    echo "✅ PyInstaller installed successfully"
else
    VERSION=$(python3 -m PyInstaller --version)
    echo "✅ PyInstaller version: $VERSION"
fi

# Clean build directories if requested
if [ "$CLEAN" = true ]; then
    echo "🧹 Cleaning build directories..."
    rm -rf dist build
    # Don't remove .spec files as they're needed for building
fi

# Create build directory structure
BUILD_DIR="build-executables"
if [ -d "$BUILD_DIR" ]; then
    rm -rf "$BUILD_DIR"
fi
mkdir -p "$BUILD_DIR"

# Function to build for a specific platform
build_executable() {
    local platform_name="$1"
    local target_os="$2"
    
    echo ""
    echo "🔨 Building for $platform_name..."
    
    local output_dir="$BUILD_DIR/$platform_name"
    mkdir -p "$output_dir"
    
    # Use the spec file for more control
    local pyinstaller_cmd=(
        "python3" "-m" "PyInstaller"
        "JiraUtil.spec"
        "--distpath" "$output_dir"
        "--workpath" "build"
        "--noconfirm"
    )
    
    # Execute PyInstaller
    echo "Running: ${pyinstaller_cmd[*]}"
    "${pyinstaller_cmd[@]}"
    
    if [ $? -eq 0 ]; then
        echo "✅ $platform_name build completed successfully"
        
               # Copy additional files
               cp jira_config_example.env "$output_dir/jira_config.env" 2>/dev/null || true
               
               # Create versioned README files
               sed "1a\\
\\
**Version: $VERSION**" docs/user-guide.md > "$output_dir/README.md"
               
               sed "1a\\
\\
**Version: $VERSION**" docs/command-reference.md > "$output_dir/command-reference.md"
               
               sed "1a\\
\\
**Version: $VERSION**" docs/troubleshooting.md > "$output_dir/troubleshooting.md"
               
               # Copy shared documentation folder
               cp -r docs/shared "$output_dir/" 2>/dev/null || true
        
        # Create a simple launcher script
        cat > "$output_dir/run.sh" << 'EOF'
#!/bin/bash
echo "JiraUtil - Jira Administration Tool"
echo "==================================="
echo ""
echo "Edit jira_config.env with your Jira credentials, then run the tool."
echo ""
read -p "Press Enter to continue..."
./JiraUtil "$@"
EOF
        chmod +x "$output_dir/run.sh"
        
        # Get executable size
        local exe_path="$output_dir/JiraUtil"
        if [ -f "$exe_path" ]; then
            local size=$(stat -f%z "$exe_path" 2>/dev/null || stat -c%s "$exe_path" 2>/dev/null || echo "0")
            local size_mb=$(echo "scale=2; $size / 1024 / 1024" | bc 2>/dev/null || echo "0")
            echo "📦 Executable size: ${size_mb} MB"
        fi
        
        return 0
    else
        echo "❌ $platform_name build failed"
        return 1
    fi
}

# Build for requested platforms
declare -A build_results

if [ "$PLATFORM" = "all" ] || [ "$PLATFORM" = "macos" ]; then
    if build_executable "macOS" "macos"; then
        build_results["macOS"]="success"
    else
        build_results["macOS"]="failed"
    fi
fi

if [ "$PLATFORM" = "all" ] || [ "$PLATFORM" = "linux" ]; then
    if build_executable "Linux" "linux"; then
        build_results["Linux"]="success"
    else
        build_results["Linux"]="failed"
    fi
fi

# Summary
echo ""
echo "📊 Build Summary"
echo "==============="

for platform in "${!build_results[@]}"; do
    if [ "${build_results[$platform]}" = "success" ]; then
        echo "$platform: ✅ Success"
    else
        echo "$platform: ❌ Failed"
    fi
done

# Show output directories
echo ""
echo "📁 Output Directories:"
for dir in "$BUILD_DIR"/*; do
    if [ -d "$dir" ]; then
        echo "  - $(basename "$dir"): $dir"
    fi
done

# Create distribution packages
echo ""
echo "📦 Creating distribution packages..."

for dir in "$BUILD_DIR"/*; do
    if [ -d "$dir" ]; then
        platform_name=$(basename "$dir")
        zip_path="$BUILD_DIR/JiraUtil-$platform_name.zip"
        
        echo "Creating $zip_path..."
        cd "$dir"
        zip -r "../JiraUtil-$platform_name.zip" . >/dev/null
        cd - >/dev/null
        
        if [ -f "$zip_path" ]; then
            zip_size=$(stat -f%z "$zip_path" 2>/dev/null || stat -c%s "$zip_path" 2>/dev/null || echo "0")
            zip_size_mb=$(echo "scale=2; $zip_size / 1024 / 1024" | bc 2>/dev/null || echo "0")
            echo "✅ Created $zip_path (${zip_size_mb} MB)"
        else
            echo "❌ Failed to create $zip_path"
        fi
    fi
done

echo ""
echo "🎉 Build process completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Test the executables in the build-executables directory"
echo "2. Distribute the ZIP files to target systems"
echo "3. Users should extract and configure jira_config.env"
echo "4. Run the executable or launcher script"
echo ""
echo "💡 Usage Examples:"
echo "macOS/Linux: ./JiraUtil --help"
