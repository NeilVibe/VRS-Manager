# Building VRS Manager Executable

This guide explains how to compile VRS Manager into a standalone executable.

---

## ⚡ Automated Builds (Recommended)

**GitHub Actions automatically builds executables for all platforms!**

### Get Pre-Built Executables

**Option 1: Latest Builds**
1. Go to [Actions tab](https://github.com/NeilVibe/VRS-Manager/actions)
2. Click latest successful "Build Executables" run
3. Download artifacts:
   - `VRSManager-Windows.zip` (Windows .exe with icon)
   - `VRSManager-Linux.zip` (Linux executable)
   - `VRSManager-macOS.zip` (macOS executable)

**Option 2: Tagged Releases**
1. Create a tag: `git tag v1.0.0 && git push origin v1.0.0`
2. Go to [Releases page](https://github.com/NeilVibe/VRS-Manager/releases)
3. Download release for your platform

### What Gets Built Automatically
- ✅ Windows executable with icon (`VRSManager.exe`)
- ✅ Linux executable (`VRSManager`)
- ✅ macOS executable (`VRSManager`)
- ✅ All packaged with README and BUILD.md
- ✅ Triggered on every push to main
- ✅ Creates releases for version tags

---

## 🔧 Manual Build (Local)

If you prefer to build locally:

### Prerequisites

- Python 3.7+
- PyInstaller installed: `pip install pyinstaller`

---

## Quick Build

### Linux / macOS

```bash
# Make build script executable (first time only)
chmod +x build_executable.sh

# Run build
./build_executable.sh
```

### Windows

```cmd
python -m PyInstaller VRSManager.spec --clean --noconfirm
```

---

## Build Output

After successful build:

```
dist/
└── VRSManager         # Standalone executable (Linux/macOS)
    or
    VRSManager.exe     # Standalone executable (Windows)
```

---

## Running the Executable

### Linux / macOS

```bash
cd dist
./VRSManager
```

### Windows

```cmd
cd dist
VRSManager.exe
```

---

## What Gets Bundled

The executable includes:
- All Python code from `src/` modules
- All dependencies (pandas, openpyxl, tkinter, etc.)
- Application icon (`images/vrsmanager.ico`)
- Runtime libraries

**Note:** History JSON files (`*_update_history.json`) are created in the same directory as the executable when you run processes.

---

## File Paths in Executable

The application automatically handles file paths correctly whether running as:
- Python script: Files saved in project root
- Compiled executable: Files saved in same directory as `.exe`

This is handled by `src/utils/helpers.py::get_script_dir()` which detects:
- `sys.frozen = True` → Running as executable
- `sys.frozen = False` → Running as script

---

## Icon Support

- **Windows**: Icon displays on executable and taskbar
- **macOS**: Icon displays on application bundle
- **Linux**: Icon not supported (warning can be ignored)

---

## Troubleshooting

### Build fails with "module not found"

Add missing module to `hiddenimports` in `VRSManager.spec`:

```python
hiddenimports=[
    'your_missing_module',
    # ... existing imports
],
```

### Executable won't run

Check `build/VRSManager/warn-VRSManager.txt` for warnings about missing libraries.

### Files not being created

Ensure you have write permissions in the directory containing the executable.

---

## Build Configuration

The build is configured in `VRSManager.spec`:

- **Entry point**: `main.py`
- **Icon**: `images/vrsmanager.ico`
- **Console**: `False` (GUI mode, no console window)
- **Compression**: UPX enabled
- **One-file**: Yes (single executable)

---

## Distribution

To distribute VRS Manager:

1. Build the executable on the target platform
2. Copy the entire `dist/` folder
3. Share `dist/VRSManager` (or `VRSManager.exe`)

**Note:** The executable is platform-specific:
- Build on Windows for Windows users
- Build on Linux for Linux users
- Build on macOS for macOS users

---

## Build System Details

**Build Tool**: PyInstaller 6.16.0
**Build Time**: ~15-30 seconds
**Executable Size**: ~80-120 MB (includes Python runtime + dependencies)

---

## Clean Build

To force a complete rebuild:

```bash
# Clean all build artifacts
rm -rf build/ dist/ __pycache__/
find . -type d -name "__pycache__" -exec rm -rf {} +

# Rebuild
./build_executable.sh
```

---

**Last Updated**: November 15, 2024
