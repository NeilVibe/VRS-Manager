#!/bin/bash
# Build script for VRS Manager executable

echo "=================================="
echo "VRS Manager - Build Executable"
echo "=================================="
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "Building executable with PyInstaller..."
echo ""

# Build using spec file
python3 -m PyInstaller VRSManager.spec --clean --noconfirm

# Check if build succeeded
if [ -f "dist/VRSManager" ] || [ -f "dist/VRSManager.exe" ]; then
    echo ""
    echo "=================================="
    echo "✅ BUILD SUCCESSFUL!"
    echo "=================================="
    echo ""
    echo "Executable location: dist/VRSManager"
    echo ""
    echo "To run:"
    echo "  cd dist"
    echo "  ./VRSManager"
    echo ""
else
    echo ""
    echo "=================================="
    echo "❌ BUILD FAILED"
    echo "=================================="
    echo ""
    echo "Check the output above for errors."
    exit 1
fi
