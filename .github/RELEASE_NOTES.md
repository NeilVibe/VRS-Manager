# VRS Manager Release Notes

## Automated Builds

Every push to `main` and every tag automatically builds executables for:
- ✅ **Windows** - VRSManager.exe (with icon)
- ✅ **Linux** - VRSManager
- ✅ **macOS** - VRSManager

## Download Pre-Built Executables

### Option 1: Latest Builds (main branch)
1. Go to [Actions tab](https://github.com/NeilVibe/VRS-Manager/actions)
2. Click the latest "Build Executables" workflow run
3. Scroll to "Artifacts" section
4. Download:
   - `VRSManager-Windows.zip` (Windows .exe)
   - `VRSManager-Linux.zip` (Linux executable)
   - `VRSManager-macOS.zip` (macOS executable)

### Option 2: Official Releases
1. Go to [Releases page](https://github.com/NeilVibe/VRS-Manager/releases)
2. Download the latest release for your platform
3. Extract and run!

## Creating a New Release

To trigger an official release build:

```bash
# Tag the version
git tag v1.0.0

# Push the tag
git push origin v1.0.0
```

This will:
1. Build executables for all platforms
2. Create ZIP archives
3. Create a GitHub Release with all executables attached
4. Generate release notes automatically

## What's Included

Each executable includes:
- Full VRS Manager application
- All dependencies (pandas, openpyxl, etc.)
- Application icon (Windows/macOS)
- No Python installation required

## File Size

- Windows: ~70-90 MB
- Linux: ~60-80 MB
- macOS: ~80-100 MB

## Running the Executable

### Windows
1. Extract `VRSManager.exe`
2. Double-click to run
3. History JSON files created in same folder

### Linux
1. Extract `VRSManager`
2. Make executable: `chmod +x VRSManager`
3. Run: `./VRSManager`

### macOS
1. Extract `VRSManager`
2. Make executable: `chmod +x VRSManager`
3. Run: `./VRSManager`
4. If blocked by security: Right-click → Open

## Support

For issues with executables, please check:
1. Extract the file first (don't run from ZIP)
2. Run from a writable directory
3. Check antivirus isn't blocking (Windows)

For other issues, see [GitHub Issues](https://github.com/NeilVibe/VRS-Manager/issues)
