# VRS Manager - Packaging & Release Guide

**Complete guide for building, packaging, and releasing VRS Manager**
**Documenting all critical issues solved during development**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Critical Issues We Solved](#critical-issues-we-solved)
5. [PyInstaller Configuration](#pyinstaller-configuration)
6. [Inno Setup Configuration](#inno-setup-configuration)
7. [GitHub Actions CI/CD](#github-actions-cicd)
8. [Git LFS for Large Files](#git-lfs-for-large-files)
9. [Version Management](#version-management)
10. [Build Process](#build-process)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## Overview

### What We Build

VRS Manager has **TWO distinct versions**:

| Version | Size | Dependencies | Use Case |
|---------|------|-------------|----------|
| **LIGHT** | ~150 MB | pandas, openpyxl, numpy | Fast, lightweight, core VRS features |
| **FULL** | ~2.6 GB | LIGHT + PyTorch + BERT (447MB) | AI-powered semantic analysis |

### Build Output

Each version produces:
1. **PyInstaller executable** (`dist_light/` or `dist_full/`)
2. **Inno Setup installer** (`.exe` with wizard)
3. **GitHub Release** (automatic artifact upload)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ BUILD TRIGGER (BUILD_TRIGGER.txt)                   │
│ - Push to main triggers GitHub Actions              │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ GITHUB ACTIONS (.github/workflows/build-*.yml)      │
│ - Parallel builds: LIGHT + FULL                     │
│ - Windows runners (windows-latest)                  │
└─────────────┬──────────────┬────────────────────────┘
              │              │
        LIGHT │              │ FULL
              ▼              ▼
┌──────────────────┐  ┌──────────────────┐
│ 1. Install Deps  │  │ 1. Install Deps  │
│    (minimal)     │  │    (full)        │
├──────────────────┤  ├──────────────────┤
│ 2. PyInstaller   │  │ 2. Verify BERT   │
│    (light.spec)  │  │    from Git LFS  │
├──────────────────┤  ├──────────────────┤
│ 3. Verify .exe   │  │ 3. PyInstaller   │
├──────────────────┤  │    (full.spec)   │
│ 4. Inno Setup    │  ├──────────────────┤
│    (light.iss)   │  │ 4. Verify .exe   │
├──────────────────┤  ├──────────────────┤
│ 5. Upload        │  │ 5. Inno Setup    │
│    Artifact      │  │    (full.iss)    │
└──────────────────┘  ├──────────────────┤
                      │ 6. Upload        │
                      │    Artifact      │
                      └──────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │ CREATE GITHUB RELEASE    │
              │ - Download artifacts     │
              │ - Create tag             │
              │ - Upload both installers │
              └──────────────────────────┘
```

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose | Install Command |
|------|---------|---------|----------------|
| **Python** | 3.10 | Application runtime | `python --version` |
| **PyInstaller** | Latest | Compile Python → .exe | `pip install pyinstaller` |
| **Inno Setup** | 6.0+ | Create Windows installers | [Download](https://jrsoftware.org/isdl.php) |
| **Git LFS** | Latest | Handle large BERT model | `git lfs install` |
| **Windows** | 10/11 | Build environment | Required for Inno Setup |

### GitHub Setup

```bash
# Enable Git LFS (one-time setup)
git lfs install

# Track large model files
# Already configured in .gitattributes:
# models/**/*.safetensors filter=lfs diff=lfs merge=lfs -text
# models/**/*.bin filter=lfs diff=lfs merge=lfs -text

# Workflow permissions (set in GitHub repo settings)
# Settings → Actions → General → Workflow permissions
# ✓ Read and write permissions
# ✓ Allow GitHub Actions to create and approve pull requests
```

---

## Critical Issues We Solved

### Build #1: Initial Setup Failures

**Problem:** PyInstaller couldn't find hidden imports, missing dependencies
**Error:** `ModuleNotFoundError` for numpy, pandas, openpyxl
**Solution:**
```python
# In .spec file, explicitly declare ALL hiddenimports
hiddenimports=[
    'numpy.core._multiarray_umath',  # Critical for numpy
    'pandas.io.formats.excel',        # Critical for pandas
    'openpyxl.cell._writer',          # Critical for openpyxl
    # ... (see spec files for complete list)
]
```

### Build #2: Model Format Mismatch

**Problem:** Workflow checked for `pytorch_model.bin`, but BERT uses `model.safetensors`
**Error:** `❌ Missing required file: pytorch_model.bin`
**Solution:**
```powershell
# Updated workflow verification (line 126 in build-installers.yml)
$requiredFiles = @("config.json", "model.safetensors")  # NOT pytorch_model.bin!
```

**Commit:** `e2f3388` - Fix Build #2 failures

### Build #3: Inno Setup Pascal Line Limit ⚠️ PAINFUL

**Problem:** Inno Setup Pascal has a **HARD 127-character line limit** (obscure and undocumented in most places!)
**Error:** `Line too long (more than 127 characters)`

**Why This Was So Bad:**
- Error message doesn't tell you WHICH line!
- No line numbers in the error output
- Had to manually count characters in every line
- Modern code editors don't show this limit by default
- Easy to exceed with Windows constants like `{autoprograms}\{#MyAppName}\...`

**What We Tried (That Failed):**
```pascal
; Attempt 1: Descriptive shortcut names (TOO LONG - 145 chars)
Name: "{autoprograms}\{#MyAppName}\Open Documentation Folder and User Guide for VRS Manager Application"; Filename: "{app}\docs"

; Attempt 2: Slightly shorter (STILL TOO LONG - 132 chars)
Name: "{autoprograms}\{#MyAppName}\Documentation and User Guides"; Filename: "{app}\docs\VRS_Manager_Process_Guide_EN.xlsx"

; Attempt 3: Line continuation with + (SYNTAX ERROR - Pascal doesn't support this)
Name: "{autoprograms}\{#MyAppName}\Documentation " +
      "and User Guides"; Filename: "{app}\docs"
```

**What Actually Worked:**
```pascal
; CORRECT - Ultra concise (68 chars)
Name: "{autoprograms}\{#MyAppName}\Documentation"; Filename: "{app}\docs"

; CORRECT - Split into multiple shortcuts if needed
Name: "{autoprograms}\{#MyAppName}\Documentation"; Filename: "{app}\docs"
Name: "{autoprograms}\{#MyAppName}\Uninstall"; Filename: "{uninstallexe}"
```

**Time Lost:** ~3 hours debugging, rebuilding, discovering the limit wasn't documented clearly

**Commit:** `a429ea6` - Fix Build #3

### Build #4: Custom Wizard Page Failures 💀 NIGHTMARE

**Problem:** Custom Inno Setup wizard pages with Pascal code caused cryptic compilation errors

**Error Messages We Got:**
```
Line 145, Column 12: Syntax error
Identifier expected
Undeclared identifier: 'InfoPage'
Type mismatch
Incompatible types: 'String' and 'TOutputMsgMemoPage'
```

**What We Were Trying To Do:**
Create a custom wizard page showing LIGHT vs FULL version differences:
```pascal
[Code]
var
  InfoPage: TOutputMsgMemoPage;

procedure InitializeWizard();
var
  InfoText: String;
begin
  // Attempted to create custom info page
  InfoPage := CreateOutputMsgMemoPage(
    wpWelcome,
    'Version Information',
    'Choose the right version for you',
    'LIGHT Version: 150MB, basic features...'  // Line too long here too!
  );

  // More Pascal code that kept failing...
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  // Custom validation logic
  Result := True;
  if CurPageID = InfoPage.ID then begin
    // More code that broke...
  end;
end;
```

**Why This Was A NIGHTMARE:**
1. **Pascal is picky** - Semicolons, `begin/end` blocks, type mismatches
2. **No debugger** - Only way to test is compile → fail → read error → repeat
3. **Documentation is sparse** - Inno Setup examples are old and incomplete
4. **Modern wizards don't need this** - Spent hours on unnecessary customization
5. **Unicode issues** - Korean text in Pascal strings caused encoding errors
6. **Build time** - Each failed compile took 2-3 minutes in CI

**Failed Attempts:**
- ❌ Custom info page → Syntax errors
- ❌ Custom progress messages → Type mismatches
- ❌ Multi-language wizard text → Unicode encoding errors
- ❌ Simplified version → Still breaking

**The Breakthrough Realization:**
**WE DON'T NEED CUSTOM WIZARD PAGES AT ALL!**

Inno Setup's default wizard already handles:
- ✅ Welcome screen
- ✅ License agreement (if needed)
- ✅ Installation directory selection
- ✅ Start Menu shortcuts
- ✅ Progress display
- ✅ Finish screen with "Launch app" option

**Final Solution (That Actually Works):**
```pascal
[Code]
procedure InitializeWizard();
begin
  // Literally nothing!
  // Default wizard is perfect
  // Don't overthink it
end;
```

**Alternative Approach (If You Really Need Info):**
Put version info in the **release notes** instead of the wizard:
- Users read GitHub release page before downloading
- Can use rich markdown formatting
- No Pascal syntax to fight
- Easier to maintain

**Time Lost:** ~6 hours across multiple build attempts, plus CI wait time

**Key Learning:**
> **KISS Principle:** When packaging software, the standard installer wizard is there for a reason.
> Custom wizard pages add complexity with minimal user benefit.
> Put your effort into clear release notes instead!

**Commit:** `723155e` - Temporarily disable custom wizard pages

### Build #5: GitHub Actions Permissions

**Problem:** Release creation failed with `403 Forbidden`
**Error:** `Resource not accessible by integration`
**Solution:**
```yaml
# Add to workflow file (line 10-11)
permissions:
  contents: write  # CRITICAL for creating releases!
```

**Commit:** `58bfd35` - Fix Build #5 - Add workflow permissions

### Build #6: Git LFS Not Enabled

**Problem:** BERT model (447MB) not checked out in GitHub Actions
**Error:** `❌ BERT model directory not found`
**Solution:**
```yaml
- name: Checkout code
  uses: actions/checkout@v3
  with:
    lfs: true  # CRITICAL! Enables Git LFS checkout
```

**Commit:** `5e20bed` - Fix workflow for LFS model

### Build #7: PyInstaller Output Structure

**Problem:** Inno Setup couldn't find files - wrong path assumptions
**Error:** `Source file not found: dist\VRSManager.exe`
**Root Cause:** Used `--onedir` (COLLECT), not `--onefile`
**Solution:**
```python
# In .spec file:
exe = EXE(
    # ...
    exclude_binaries=True,  # Use COLLECT mode (--onedir)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name='VRSManager',  # Creates dist/VRSManager/VRSManager.exe
)
```

```pascal
; In .iss file - Match the actual output structure
Source: "..\dist_light\VRSManager\VRSManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist_light\VRSManager\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs
```

**Commit:** `b767949` - Fix PyInstaller output structure

### Build #8: Artifact Actions Deprecation

**Problem:** `actions/upload-artifact@v3` deprecated
**Warning:** `Node.js 12 actions are deprecated`
**Solution:**
```yaml
# Update to v4 (current stable)
- name: Upload LIGHT installer
  uses: actions/upload-artifact@v4  # v3 → v4
  with:
    name: VRSManager_Light_Setup
    path: installer_output/VRSManager_v1.120.0_Light_Setup.exe
    retention-days: 90
```

**Commit:** `681e7de` - CRITICAL FIX: deprecated artifact actions

### Build #9: Version Hardcoding

**Problem:** Version numbers scattered across 10+ files, easy to forget one
**Impact:** User sees mismatched versions (v1.119 in app, v1.120 in docs)
**Solution:** Created version checklist in `CLAUDE.md` and `roadmap.md`

Files that MUST be updated together:
1. `src/config.py` - VERSION and VERSION_FOOTER
2. `main.py` - Docstring + print statements
3. `README.md`, `README_EN.md`, `README_KR.md`
4. `roadmap.md` - Current Status + Version History
5. `update_excel_guides.py` - VERSION + content
6. `WIKI_CONFLUENCE.md`
7. `CLAUDE.md`
8. `src/processors/master_processor.py`
9. **Inno Setup scripts** - `#define MyAppVersion`
10. **GitHub workflow** - Installer filenames

**Verification:**
```bash
grep -r "1.120.0" --include="*.py" --include="*.md" --include="*.iss" --include="*.yml"
```

---

## PyInstaller Configuration

### Understanding .spec Files

PyInstaller `.spec` files define how Python code compiles to executables.

**Key Sections:**

```python
# 1. Analysis - What to include
a = Analysis(
    ['main.py'],                    # Entry point
    datas=[...],                    # Data files (Excel, images, models)
    hiddenimports=[...],            # Modules PyInstaller can't auto-detect
    excludes=[...],                 # Explicitly exclude packages
)

# 2. PYZ - Python bytecode archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 3. EXE - The executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # Use COLLECT mode (--onedir)
    name='VRSManager',
    console=True,                   # Show console window
    icon='images/vrsmanager.ico',
)

# 4. COLLECT - Bundle everything in a folder
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name='VRSManager',              # Output: dist/VRSManager/
)
```

### LIGHT vs FULL Configuration

**LIGHT Version (`VRSManager_light.spec`):**

```python
datas=[
    # NO BERT model
],
hiddenimports=[
    'numpy', 'pandas', 'openpyxl',  # Core only
    # NO torch, transformers, sentence_transformers
],
excludes=[
    'torch',                         # Explicitly exclude
    'transformers',
    'sentence_transformers',
]
```

**FULL Version (`VRSManager.spec`):**

```python
datas=[
    ('models/kr-sbert', 'models/kr-sbert'),  # 447MB BERT model
],
hiddenimports=[
    'numpy', 'pandas', 'openpyxl',           # Core
    'torch', 'transformers',                 # ML
    'sentence_transformers',
],
excludes=[
    'matplotlib',  # Don't need plotting
]
```

### Critical hiddenimports

```python
hiddenimports=[
    # Numpy (CRITICAL - app crashes without these)
    'numpy.core._multiarray_umath',
    'numpy.core._multiarray_tests',
    'numpy.random.common',
    'numpy.random.bounded_integers',
    'numpy.random.entropy',

    # OpenPyXL (Excel handling)
    'openpyxl.cell._writer',
    'openpyxl.styles.stylesheet',
    'openpyxl.worksheet._reader',

    # Pandas (data processing)
    'pandas.io.formats.excel',
    'pandas._libs.tslibs.timedeltas',

    # PyTorch (FULL version only)
    'torch._C',
    'torch.nn',

    # BERT (FULL version only)
    'sentence_transformers.models',
    'sentence_transformers.util',
]
```

**How to find missing imports:**
1. Build executable: `pyinstaller VRSManager.spec`
2. Run it: `dist/VRSManager/VRSManager.exe`
3. If crash: Check error message for `ModuleNotFoundError: No module named 'xxx'`
4. Add `'xxx'` to `hiddenimports=[]`
5. Repeat until it works

---

## Inno Setup Configuration

### ⚠️ WARNING: Inno Setup Will Test Your Patience

**Before you proceed, know these pain points:**

Inno Setup is powerful but has quirks that will eat hours of your time if you don't know them:

| Issue | Impact | Our Time Lost |
|-------|--------|---------------|
| **127-character line limit** | Cryptic error, no line numbers | 3 hours |
| **Pascal syntax requirements** | No debugger, compile-fail-repeat cycle | 6 hours |
| **Unicode encoding issues** | Korean text breaks compilation | 2 hours |
| **No IDE support** | Text editor only, manual syntax checking | Ongoing pain |
| **Sparse documentation** | Most examples are 10+ years old | 4 hours research |

**TOTAL TIME LOST TO INNO SETUP ISSUES: ~15 hours across 3 build failures**

**Golden Rules (Learn From Our Pain):**
1. ✅ **Keep lines under 120 chars** - The 127 limit is real and brutal
2. ✅ **Use default wizard** - Don't write custom Pascal code unless absolutely necessary
3. ✅ **Test locally first** - Compile on Windows before pushing to CI
4. ✅ **Copy working examples** - From this guide, don't improvise
5. ✅ **Put info in release notes** - Not in wizard pages
6. ❌ **DON'T use fancy wizard customization** - Not worth it!
7. ❌ **DON'T assume line continuations work** - Pascal doesn't support `+` for string concat in directives
8. ❌ **DON'T trust online tutorials** - Most are outdated

> **If you only remember one thing:** Keep your `.iss` files SIMPLE. Copy from working examples (ours!) and make minimal changes.

---

### Understanding .iss Files

Inno Setup scripts define Windows installer behavior.

**Key Sections:**

```pascal
; 1. Setup metadata
[Setup]
AppName={#MyAppName} (LIGHT)
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\{#MyAppName}
OutputDir=..\installer_output
OutputBaseFilename=VRSManager_v{#MyAppVersion}_Light_Setup
Compression=lzma2/ultra64
ArchitecturesAllowed=x64

; 2. Files to include
[Files]
Source: "..\dist_light\VRSManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

; 3. Start Menu shortcuts
[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

; 4. Run after install
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch"; Flags: nowait postinstall skipifsilent

; 5. Custom code (optional)
[Code]
procedure InitializeWizard();
begin
  // Keep it simple!
end;
```

### LIGHT vs FULL Configuration

**Key Differences:**

| Setting | LIGHT | FULL |
|---------|-------|------|
| **AppId** | `{8A7B3C4D-...}` | `{9B8C4D5E-...}` (different!) |
| **AppName** | `VRS Manager (LIGHT)` | `VRS Manager (FULL)` |
| **Source** | `dist_light\` | `dist_full\` |
| **OutputBaseFilename** | `..._Light_Setup` | `..._Full_Setup` |

**Critical:** Different AppIds allow both versions to be installed side-by-side!

### Output Directory Structure

```pascal
; Output paths
OutputDir=..\installer_output                      ; Relative to .iss file location
OutputBaseFilename=VRSManager_v{#MyAppVersion}_Light_Setup

; Result:
; vrsmanager/installer_output/VRSManager_v1.120.0_Light_Setup.exe
```

### Compression Settings

```pascal
; Maximum compression (slower build, smaller file)
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; Result: LIGHT ~150MB, FULL ~2.6GB (from 3GB+ uncompressed)
```

### Installation Paths

```pascal
; Install to Program Files
DefaultDirName={autopf}\{#MyAppName}    ; C:\Program Files\VRS Manager\

; Start Menu
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

; Desktop (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
```

### Critical Files Section

```pascal
[Files]
; Main executable
Source: "..\dist_light\VRSManager\VRSManager.exe"; DestDir: "{app}"; Flags: ignoreversion

; ALL dependencies (PyInstaller bundles these)
Source: "..\dist_light\VRSManager\_internal\*"; DestDir: "{app}\_internal";
  Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "..\docs\*"; DestDir: "{app}\docs";
  Flags: ignoreversion recursesubdirs createallsubdirs

; Working folders (AllLang processor needs these)
Source: "..\Current\README.txt"; DestDir: "{app}\Current"; Flags: ignoreversion
Source: "..\Previous\README.txt"; DestDir: "{app}\Previous"; Flags: ignoreversion
```

**Critical Flags:**
- `ignoreversion` - Always overwrite on reinstall
- `recursesubdirs` - Include all nested files
- `createallsubdirs` - Create directory structure

### Line Length Limit (127 chars!)

```pascal
; ✗ WRONG - Line too long
Name: "{autoprograms}\{#MyAppName}\Documentation and User Guide for VRS Manager Application"; Filename: "{app}\docs"

; ✓ CORRECT
Name: "{autoprograms}\{#MyAppName}\Documentation"; Filename: "{app}\docs"
```

**Pascal Compiler Error:** `Line too long (more than 127 characters)`

### Testing Locally

```powershell
# Compile installer manually
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\vrsmanager_light.iss

# Check output
ls installer_output\
# Should see: VRSManager_v1.120.0_Light_Setup.exe
```

---

## GitHub Actions CI/CD

### Workflow Structure

**File:** `.github/workflows/build-installers.yml`

```yaml
name: Build LIGHT and FULL Installers

on:
  push:
    branches: [ main ]
    paths:
      - 'BUILD_TRIGGER.txt'  # Only trigger on this file change
  workflow_dispatch:           # Allow manual trigger

permissions:
  contents: write              # CRITICAL for release creation!

jobs:
  build-light:    # Job 1 - LIGHT version
  build-full:     # Job 2 - FULL version (runs in parallel)
  create-release: # Job 3 - Waits for both builds
```

### Job: build-light

```yaml
build-light:
  runs-on: windows-latest  # Must use Windows for Inno Setup!

  steps:
    - name: Checkout code
      uses: actions/checkout@v3
      with:
        lfs: true  # CRITICAL for Git LFS

    - name: Setup Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        cache: 'pip'  # Cache dependencies for faster builds

    - name: Install LIGHT dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pandas openpyxl numpy  # Minimal deps
        pip install pyinstaller

    - name: Build LIGHT .exe
      run: |
        pyinstaller VRSManager_light.spec --clean --noconfirm --distpath dist_light

    - name: Verify LIGHT build
      run: |
        if (!(Test-Path "dist_light\VRSManager\VRSManager.exe")) {
          Write-Error "Build failed"
          exit 1
        }
        Write-Host "✓ Build successful"

    - name: Install Inno Setup
      run: |
        choco install innosetup -y

    - name: Compile LIGHT installer
      run: |
        & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\vrsmanager_light.iss

    - name: Upload LIGHT installer
      uses: actions/upload-artifact@v4
      with:
        name: VRSManager_Light_Setup
        path: installer_output/VRSManager_v1.120.0_Light_Setup.exe
        retention-days: 90
```

### Job: build-full

**Key Differences from LIGHT:**

```yaml
    - name: Install FULL dependencies
      run: |
        pip install -r requirements.txt  # ALL dependencies
        pip install pyinstaller

    - name: Verify BERT model (from LFS)
      run: |
        if (!(Test-Path "models\kr-sbert")) {
          Write-Error "BERT model not found"
          exit 1
        }
        # Check for model.safetensors (NOT pytorch_model.bin!)
        $requiredFiles = @("config.json", "model.safetensors")
        foreach ($file in $requiredFiles) {
          if (!(Test-Path "models\kr-sbert\$file")) {
            Write-Error "Missing: $file"
            exit 1
          }
        }

    - name: Build FULL .exe
      run: |
        pyinstaller VRSManager.spec --clean --noconfirm --distpath dist_full
```

### Job: create-release

```yaml
create-release:
  needs: [build-light, build-full]  # Wait for both builds
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'

  steps:
    - name: Download LIGHT installer
      uses: actions/download-artifact@v4
      with:
        name: VRSManager_Light_Setup
        path: ./artifacts/light

    - name: Download FULL installer
      uses: actions/download-artifact@v4
      with:
        name: VRSManager_Full_Setup
        path: ./artifacts/full

    - name: Extract version from BUILD_TRIGGER.txt
      id: version
      run: |
        VERSION=$(grep "Build v" BUILD_TRIGGER.txt | head -1 | sed 's/.*Build v//' | cut -d' ' -f1)
        echo "version=$VERSION" >> $GITHUB_OUTPUT

    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        tag_name: v${{ steps.version.outputs.version }}
        name: VRS Manager v${{ steps.version.outputs.version }}
        body: |
          # Release notes here (markdown formatted)
        files: |
          artifacts/light/VRSManager_v1.120.0_Light_Setup.exe
          artifacts/full/VRSManager_v1.120.0_Full_Setup.exe
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Common Workflow Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `403 Forbidden` | Missing permissions | Add `permissions: contents: write` |
| `Model not found` | Git LFS not enabled | Add `lfs: true` to checkout |
| `Artifact not found` | Name mismatch | Match upload/download artifact names exactly |
| `ISCC.exe not found` | Inno Setup not installed | Use `choco install innosetup -y` |
| `File not found: dist\VRSManager.exe` | Wrong path | Check `--distpath` matches .iss Source paths |

---

## Git LFS for Large Files

### Why Git LFS?

**Problem:** BERT model is **447MB** - exceeds GitHub's 100MB file limit
**Solution:** Git Large File Storage (LFS) stores large files separately

### Setup (One-Time)

```bash
# 1. Install Git LFS
git lfs install

# 2. Configure .gitattributes (already done)
cat .gitattributes
# models/**/*.safetensors filter=lfs diff=lfs merge=lfs -text
# models/**/*.bin filter=lfs diff=lfs merge=lfs -text

# 3. Add BERT model
git add models/kr-sbert/
git commit -m "Add BERT model with Git LFS"
git push origin main
```

### Verification

```bash
# Check if file is tracked by LFS
git lfs ls-files
# Should show: models/kr-sbert/model.safetensors

# Check file size
ls -lh models/kr-sbert/model.safetensors
# Should show: ~447M

# If it shows a tiny file (<1KB), it's just the LFS pointer!
# Run: git lfs pull
```

### GitHub Actions Integration

```yaml
- name: Checkout code
  uses: actions/checkout@v3
  with:
    lfs: true  # CRITICAL! Without this, you get LFS pointers, not actual files
```

**What happens:**
- `lfs: false` → Gets tiny pointer file (1KB)
- `lfs: true` → Downloads actual model (447MB)

### Common LFS Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Model file is 1KB" | LFS not pulled | `git lfs pull` |
| "Model not found in CI" | Missing `lfs: true` | Add to checkout step |
| "LFS bandwidth exceeded" | Free quota limit | Upgrade GitHub plan or host elsewhere |

---

## Version Management

### The Version Consistency Problem

**Problem:** Version numbers scattered across 10+ files
**Impact:** User sees v1.119 in app but v1.120 in docs → Confusion!

### Files That MUST Match

Create a checklist and update ALL together:

```bash
# 1. Source code
src/config.py                       # VERSION = "1.120.0"
main.py                             # Docstring + print statements

# 2. Documentation
README.md                           # Version badge
README_EN.md                        # English docs
README_KR.md                        # Korean docs
roadmap.md                          # Current Status + Version History
CLAUDE.md                           # Quick reference

# 3. Build configuration
installer/vrsmanager_light.iss      # #define MyAppVersion "1.120.0"
installer/vrsmanager_full.iss       # #define MyAppVersion "1.120.0"
.github/workflows/build-installers.yml  # Installer filenames

# 4. Excel guides
update_excel_guides.py              # VERSION + content updates

# 5. Other
WIKI_CONFLUENCE.md                  # Version references
src/processors/master_processor.py  # Comment header
```

### Version Update Process

```bash
# 1. Update version in ALL files above
NEW_VERSION="1.121.0"

# 2. Verify consistency
grep -r "1.120.0" --include="*.py" --include="*.md" --include="*.iss" --include="*.yml" | wc -l
# Should return 0 (all updated to 1.121.0)

# 3. Update Excel guides
python3 update_excel_guides.py

# 4. Commit everything
git add .
git commit -m "Version bump to v${NEW_VERSION}"
git push origin main
```

### Automated Verification Script

Create `check_version.sh`:

```bash
#!/bin/bash
EXPECTED="1.120.0"
FILES=(
    "src/config.py"
    "main.py"
    "README.md"
    "installer/vrsmanager_light.iss"
    "installer/vrsmanager_full.iss"
)

for file in "${FILES[@]}"; do
    if ! grep -q "$EXPECTED" "$file"; then
        echo "❌ $file missing version $EXPECTED"
        exit 1
    fi
done
echo "✓ All versions consistent: $EXPECTED"
```

---

## Build Process

### Step-by-Step: Triggering a Build

```bash
# 1. Update BUILD_TRIGGER.txt
echo "Build v1.120.1 - Bug fix release" >> BUILD_TRIGGER.txt

# 2. Commit and push to main
git add BUILD_TRIGGER.txt
git commit -m "Trigger build v1.120.1"
git push origin main

# 3. Monitor GitHub Actions
# https://github.com/NeilVibe/VRS-Manager/actions

# 4. Wait for completion (~10-15 minutes)
# - LIGHT build: ~2 minutes
# - FULL build: ~8 minutes
# - Release creation: ~1 minute

# 5. Check release
# https://github.com/NeilVibe/VRS-Manager/releases
```

### Local Testing (Before Pushing)

**Test LIGHT build:**

```bash
# Install dependencies
pip install pandas openpyxl numpy pyinstaller

# Build
pyinstaller VRSManager_light.spec --clean --noconfirm --distpath dist_light

# Test
cd dist_light/VRSManager
./VRSManager.exe

# Compile installer (Windows only)
cd ../..
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\vrsmanager_light.iss

# Verify
ls installer_output\VRSManager_v1.120.0_Light_Setup.exe
```

**Test FULL build:**

```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Verify BERT model
ls -lh models/kr-sbert/model.safetensors
# Should be ~447MB, NOT 1KB!

# Build
pyinstaller VRSManager.spec --clean --noconfirm --distpath dist_full

# Test
cd dist_full/VRSManager
./VRSManager.exe
# Try StrOrigin Analysis - should show similarity %

# Compile installer
cd ../..
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\vrsmanager_full.iss
```

### Build Time Estimates

| Stage | LIGHT | FULL |
|-------|-------|------|
| Dependency install | 30s | 2m |
| PyInstaller build | 1m | 5m |
| Inno Setup compile | 20s | 1m |
| **Total** | **~2m** | **~8m** |

### Manual Build (Emergency Fallback)

If GitHub Actions fails:

```bash
# 1. Clone repo (with LFS!)
git clone https://github.com/NeilVibe/VRS-Manager.git
cd VRS-Manager
git lfs pull  # Get BERT model

# 2. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 3. Build both versions
pyinstaller VRSManager_light.spec --clean --noconfirm --distpath dist_light
pyinstaller VRSManager.spec --clean --noconfirm --distpath dist_full

# 4. Compile installers (Windows)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\vrsmanager_light.iss
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\vrsmanager_full.iss

# 5. Upload to GitHub Releases manually
# Go to: https://github.com/NeilVibe/VRS-Manager/releases/new
# Upload: installer_output/*.exe
```

---

## Troubleshooting

### Build Failures

#### "ModuleNotFoundError: No module named 'X'"

**Cause:** PyInstaller didn't detect hidden import
**Solution:**
1. Add to `.spec` file `hiddenimports=[...]`
2. Rebuild: `pyinstaller <spec_file> --clean`

#### "BERT model not found"

**Cause:** Git LFS not pulled
**Solution:**
```bash
# Local
git lfs pull

# GitHub Actions
# Verify checkout has: lfs: true
```

#### "VRSManager.exe not found"

**Cause:** Wrong `--distpath` or `.spec` output configuration
**Solution:**
```bash
# Check where PyInstaller actually put files
ls -R dist_light/

# Match paths in .iss file:
Source: "..\dist_light\VRSManager\VRSManager.exe"
```

### Inno Setup Errors

These are THE WORST to debug because Inno Setup gives minimal error information!

#### "Line too long (more than 127 characters)"

**Cause:** Pascal compiler's hard limit on line length (a remnant from 1990s compilers!)
**Why It's Frustrating:**
- ❌ Error doesn't tell you WHICH line
- ❌ No line numbers in output
- ❌ Have to manually count every line
- ❌ Modern editors don't warn about this

**How to Find the Offending Line:**
```bash
# PowerShell - Find lines over 127 chars
Get-Content installer\vrsmanager_light.iss |
  Where-Object { $_.Length -gt 127 } |
  ForEach-Object { Write-Host "TOO LONG ($($_.Length) chars): $_" }

# Linux/Mac - Find lines over 127 chars
awk 'length > 127 {print "Line " NR " (" length " chars): " $0}' installer/vrsmanager_light.iss
```

**Common Culprits:**
```pascal
; 1. Long shortcut names in [Icons]
Name: "{autoprograms}\{#MyAppName}\Open Documentation Folder and User Guide"; Filename: "{app}\docs"
;     ^ 138 characters - TOO LONG!

; Fix: Be ultra concise
Name: "{autoprograms}\{#MyAppName}\Documentation"; Filename: "{app}\docs"
;     ^ 68 characters - Perfect!

; 2. Long paths in [Files]
Source: "..\dist_full\VRSManager\_internal\torch\lib\torch_cuda_cu118_backend.dll"; DestDir: "{app}\_internal\torch\lib"
;       ^ Use wildcards instead!

Source: "..\dist_full\VRSManager\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
;       ^ 95 characters - Much better!

; 3. Long comments
; This is a very detailed comment explaining every single thing about what this section does and why we need it
; ^ 127+ chars - Even comments count!

; Be concise in comments too
; Installer configuration
```

**Solution Strategy:**
1. Use shorter variable/shortcut names
2. Use `recursesubdirs` wildcards instead of listing every file
3. Split one long line into multiple shorter lines
4. Keep comments brief

#### "Syntax error" / "Identifier expected"

**Cause:** Pascal syntax error in `[Code]` section
**Why It's Frustrating:**
- ❌ Error messages are cryptic ("Column 12" but doesn't show the line)
- ❌ No syntax highlighting in most editors for `.iss` files
- ❌ No debugger - only way to test is full compile

**Common Mistakes:**
```pascal
; WRONG - Missing semicolon
Name: "{autoprograms}\{#MyAppName}" Filename: "{app}\VRSManager.exe"

; CORRECT
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\VRSManager.exe"
;                                   ^ Don't forget!

; WRONG - Inconsistent quotes
Source: "..\dist_light\*'; DestDir: "{app}"

; CORRECT - Match your quotes
Source: "..\dist_light\*"; DestDir: "{app}"
;                       ^                  ^

; WRONG - Pascal code without proper structure
[Code]
InfoPage := CreateOutputMsgMemoPage(wpWelcome, 'Info', 'Description', 'Text');

; CORRECT - Need var declaration and procedure
[Code]
var
  InfoPage: TOutputMsgMemoPage;

procedure InitializeWizard();
begin
  InfoPage := CreateOutputMsgMemoPage(wpWelcome, 'Info', 'Description', 'Text');
end;
```

**Best Solution:** Just don't write custom Pascal code! Use simple `.iss` directives only.

#### "Source file not found"

**Cause:** Path mismatch between PyInstaller output and .iss Source paths
**Why It's Frustrating:** Relative paths work differently in `.iss` files vs normal code

**The Mental Model:**
```
Your project structure:
vrsmanager/
├── installer/
│   ├── vrsmanager_light.iss    ← .iss file is HERE
│   └── vrsmanager_full.iss
├── dist_light/
│   └── VRSManager/
│       └── VRSManager.exe       ← Trying to reference THIS
└── dist_full/

Relative path FROM installer/ TO dist_light/:
..                                ← Go up one level to vrsmanager/
  \dist_light                     ← Enter dist_light/
    \VRSManager                   ← Enter VRSManager/
      \VRSManager.exe             ← Found it!

Result: ..\dist_light\VRSManager\VRSManager.exe
```

**Common Mistakes:**
```pascal
; WRONG - Missing the ".." to go up one level
Source: "dist_light\VRSManager\VRSManager.exe"; DestDir: "{app}"
; Looking in: installer\dist_light\VRSManager\VRSManager.exe (doesn't exist!)

; WRONG - Too many ".."
Source: "..\..\dist_light\VRSManager\VRSManager.exe"; DestDir: "{app}"
; Looking in: parent_of_vrsmanager\dist_light\... (wrong!)

; CORRECT
Source: "..\dist_light\VRSManager\VRSManager.exe"; DestDir: "{app}"
```

**Debug Technique:**
```pascal
; Add OutputDir to [Setup] and check absolute paths
[Setup]
OutputDir=..\installer_output

; Then during compile, Inno Setup shows:
; "Output directory: C:\Users\...\vrsmanager\installer_output"
; So you know the base is: C:\Users\...\vrsmanager\installer\
; And dist_light is at: C:\Users\...\vrsmanager\dist_light\
; Confirm the relative path: ..\dist_light\ ✓
```

#### "Unable to create output filename"

**Cause:** `OutputDir` path doesn't exist or is wrong
**Solution:**
```pascal
; WRONG - Absolute path (won't work in CI)
OutputDir=C:\Users\YourName\vrsmanager\installer_output

; WRONG - No parent directory (..)
OutputDir=installer_output  ; Creates: installer\installer_output (weird!)

; CORRECT - Relative path one level up
OutputDir=..\installer_output  ; Creates: vrsmanager\installer_output
```

#### "Internal error: unable to load wizard"

**Cause:** Corrupted custom wizard code or incompatible Pascal functions
**Our Experience:** Spent 6 hours debugging custom wizard pages that kept causing this
**Solution:** Delete all custom wizard code and use the default wizard:

```pascal
[Code]
procedure InitializeWizard();
begin
  // Keep it empty - default wizard is perfect!
end;
```

#### Unicode/Encoding Errors

**Problem:** Korean text (or other Unicode) in Pascal strings causes compilation failure
**Error:** `Invalid character` or encoding warnings

**What We Tried (That Failed):**
```pascal
[Code]
procedure InitializeWizard();
var
  InfoText: String;
begin
  InfoText := '라이트 버전: 150MB...';  // ← Korean text breaks compile!
end;
```

**Solution:** Put multilingual text in external files or release notes, NOT in `.iss` code:
```pascal
; Use English only in .iss
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\VRSManager.exe"

; Put Korean/multilingual info in:
; - README.md (bundled with installer)
; - GitHub release notes
; - Separate language pack files
```

### GitHub Actions Errors

#### "403 Forbidden" on release creation

**Cause:** Missing workflow permissions
**Solution:**
```yaml
permissions:
  contents: write  # Add this at workflow root level
```

#### "Resource not accessible by integration"

**Cause:** Token permissions
**Solution:** Check GitHub repo settings:
```
Settings → Actions → General → Workflow permissions
✓ Read and write permissions
```

#### "Artifact not found"

**Cause:** Name mismatch between upload/download
**Solution:**
```yaml
# MUST match exactly
- name: Upload LIGHT installer
  with:
    name: VRSManager_Light_Setup  # This name...

- name: Download LIGHT installer
  with:
    name: VRSManager_Light_Setup  # ...must match this
```

### Runtime Errors

#### "Application failed to start (0xc000007b)"

**Cause:** 32-bit/64-bit mismatch
**Solution:**
```python
# In .spec file:
exe = EXE(
    # ...
    target_arch='x64',  # Force 64-bit
)
```

```pascal
; In .iss file:
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
```

#### "DLL load failed: The specified module could not be found"

**Cause:** Missing dependency (numpy, torch)
**Solution:** Add to `hiddenimports` in .spec file

#### "StrOrigin Analysis shows 'N/A'"

**Cause:** BERT model not loaded
**Solution:**
```python
# Check model path in compiled app
import sys
model_path = os.path.join(sys._MEIPASS, 'models', 'kr-sbert')
print(f"Looking for model at: {model_path}")
```

---

## Best Practices

### 1. Version Consistency

- **Create a checklist** of all files with version numbers
- **Update ALL together** - never push partial version updates
- **Automate verification** with grep script
- **Test installers** to verify version in UI matches filenames

### 2. Git LFS Management

- **Always use `lfs: true`** in GitHub Actions checkout
- **Test locally first:** `git lfs pull` before building
- **Verify file sizes:** 447MB model, not 1KB pointer
- **Plan bandwidth:** Free tier has limits for large files

### 3. Build Configuration

- **Keep it simple:** Don't overcomplicate wizards
- **Test locally first:** Build + run before pushing
- **Separate LIGHT/FULL:** Different specs, different dependencies
- **Document changes:** Update this guide when you solve new issues

### 4. CI/CD Hygiene

- **Use BUILD_TRIGGER.txt:** Prevents accidental builds on every commit
- **Parallel builds:** LIGHT + FULL run simultaneously (faster)
- **Verify steps:** Check file existence before proceeding
- **Retention policy:** Keep artifacts 90 days

### 5. Error Handling

- **Fail fast:** Exit with error code 1 on missing files
- **Print diagnostics:** Show file listings, sizes, paths
- **Keep logs:** GitHub Actions logs are gold for debugging

### 6. User Experience

- **Clear naming:** `_Light_Setup.exe` vs `_Full_Setup.exe`
- **Different AppIds:** Allow side-by-side installation
- **Rich release notes:** Explain LIGHT vs FULL clearly
- **Portable option:** Document how to zip/transfer installed app

### 7. Security

- **Admin privileges:** Required for Program Files installation
- **Dialog override:** `PrivilegesRequiredOverridesAllowed=dialog`
- **Clean uninstall:** Delete generated Excel files
- **No telemetry:** 100% offline operation

### 8. Performance

- **Ultra compression:** `lzma2/ultra64` for smallest installers
- **Parallel threads:** `LZMANumBlockThreads=4`
- **Solid compression:** Groups similar files together
- **UPX compression:** `upx=True` in PyInstaller

### 9. Documentation

- **Update this guide:** Every issue solved = new section
- **Keep examples:** Working code snippets are invaluable
- **Git commit messages:** Reference build numbers (Build #5, #6, etc.)
- **Link to commits:** `Commit: a429ea6` for traceability

### 10. Testing Checklist

Before pushing a build trigger:

```bash
# Pre-flight checklist
[ ] Version numbers updated in ALL 10 files
[ ] Local LIGHT build works
[ ] Local FULL build works
[ ] BERT model present (447MB, not 1KB)
[ ] Excel guides updated
[ ] BUILD_TRIGGER.txt has clear description
[ ] Workflow permissions enabled (contents: write)
[ ] Git LFS enabled (lfs: true in checkout)
[ ] .iss files have correct version
[ ] No lines >127 chars in .iss files
```

---

## Appendix: Command Reference

### PyInstaller

```bash
# Build from spec
pyinstaller VRSManager.spec --clean --noconfirm --distpath dist_full

# Flags:
# --clean          Remove build cache before building
# --noconfirm      Replace output directory without asking
# --distpath DIR   Output directory for bundled application

# Debug mode (show what PyInstaller is doing)
pyinstaller VRSManager.spec --clean --log-level DEBUG
```

### Inno Setup

```bash
# Compile installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\vrsmanager_light.iss

# Check syntax only (no compile)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /? installer\vrsmanager_light.iss

# Verbose output
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /V5 installer\vrsmanager_light.iss
```

### Git LFS

```bash
# Install LFS (one-time)
git lfs install

# Track file types
git lfs track "models/**/*.safetensors"

# Check tracked files
git lfs ls-files

# Pull large files
git lfs pull

# Show LFS storage usage
git lfs env
```

### GitHub CLI (gh)

```bash
# View workflow runs
gh run list

# Watch live workflow
gh run watch

# Download artifacts
gh run download <run-id>

# View releases
gh release list

# Create release manually
gh release create v1.120.0 installer_output/*.exe --title "VRS Manager v1.120.0"
```

---

## Summary

This guide documented **every issue we solved** while building VRS Manager's dual-version installer system:

1. ✅ PyInstaller hidden imports (numpy, pandas, PyTorch)
2. ✅ BERT model format (safetensors, not bin)
3. ✅ Inno Setup line length limit (127 chars)
4. ✅ Custom wizard pages (simplified to default)
5. ✅ GitHub workflow permissions (contents: write)
6. ✅ Git LFS integration (447MB model handling)
7. ✅ PyInstaller COLLECT structure (onedir, not onefile)
8. ✅ Artifact actions deprecation (v3 → v4)
9. ✅ Version consistency (10+ files to update)

**Key Takeaways:**

- **Test locally first** - Don't debug in CI
- **Keep wizards simple** - Standard Inno Setup is best
- **Document everything** - Future you will thank you
- **Fail fast** - Verify files exist before proceeding
- **Version consistency** - Use checklists!

**Result:** Production-ready build system that creates ~150MB LIGHT and ~2.6GB FULL Windows installers in ~10 minutes, fully automated via GitHub Actions. 🚀

---

**Document Version:** 1.0
**Last Updated:** 2025-01-20
**Maintainer:** Neil Schmitt / Claude Code
**Repository:** https://github.com/NeilVibe/VRS-Manager
