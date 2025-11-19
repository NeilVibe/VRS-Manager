# VRS Manager Installer Scripts

This folder contains Inno Setup scripts for creating professional Windows installers.

## Files

- `vrsmanager_light.iss` - LIGHT version installer script
- `vrsmanager_full.iss` - FULL version installer script

## Versions

### LIGHT Version (~150MB)
**Includes:**
- All VRS Check features
- Punctuation/Space detection
- Core dependencies only

**Excludes:**
- PyTorch
- BERT model
- ML dependencies

**StrOrigin Analysis output:**
- "Punctuation/Space Change" OR "Content Change"

### FULL Version (~2.6GB)
**Includes:**
- Everything in LIGHT
- PyTorch (~2GB)
- Korean BERT model (447MB)
- All ML dependencies

**StrOrigin Analysis output:**
- "Punctuation/Space Change" OR "XX.X% similar"

## Build Process (Manual)

### Prerequisites

1. **Windows OS** (Inno Setup is Windows-only)
2. **Inno Setup 6.0+**: Download from https://jrsoftware.org/isinfo.php
3. **Python 3.10+**
4. **PyInstaller**: `pip install pyinstaller`

### Step 1: Build LIGHT .exe

```bash
# Install LIGHT dependencies only
pip install pandas openpyxl numpy pyinstaller

# Build LIGHT .exe
pyinstaller VRSManager_light.spec --clean --noconfirm --distpath dist_light
```

**Result:** `dist_light/VRSManager.exe` (~150MB)

### Step 2: Build FULL .exe

```bash
# Install ALL dependencies
pip install -r requirements.txt
pip install pyinstaller

# Download BERT model
python scripts/download_bert_model.py

# Build FULL .exe
pyinstaller VRSManager.spec --clean --noconfirm --distpath dist_full
```

**Result:** `dist_full/VRSManager.exe` (~3GB)

### Step 3: Compile Installers

```bash
# Compile LIGHT installer
iscc installer/vrsmanager_light.iss

# Compile FULL installer
iscc installer/vrsmanager_full.iss
```

**Output:**
- `installer_output/VRSManager_v1.120.0_Light_Setup.exe` (~150MB)
- `installer_output/VRSManager_v1.120.0_Full_Setup.exe` (~2.6GB)

## Automated Build (GitHub Actions)

The `.github/workflows/build-installers.yml` workflow automates this process:

1. Builds both LIGHT and FULL .exe files in parallel
2. Compiles both installers
3. Uploads to GitHub Releases

**Trigger:** Push to main when `BUILD_TRIGGER.txt` changes

## Testing

After building installers:

1. **Test on clean Windows VM:**
   - Install LIGHT version
   - Run VRS Manager
   - Process file with StrOrigin changes
   - Verify: Shows "Content Change" for non-punctuation changes

2. **Test FULL version:**
   - Install FULL version
   - Run VRS Manager
   - Process file with StrOrigin changes
   - Verify: Shows "XX.X% similar" for content changes

3. **Test portability:**
   - After installation, zip `C:\Program Files\VRS Manager\`
   - Transfer to another PC
   - Extract and run
   - Verify: Works offline

## Installer Features

Both installers include:
- ✅ Professional installation wizard
- ✅ Start Menu shortcuts
- ✅ Optional desktop shortcut
- ✅ Proper Windows uninstaller
- ✅ Custom welcome screen with version info
- ✅ Admin privileges for Program Files installation
- ✅ Ultra compression (LZMA2)

## File Structure After Installation

```
C:\Program Files\VRS Manager\
├── VRSManager.exe
├── _internal/
│   ├── python310.dll
│   ├── pandas/
│   ├── openpyxl/
│   └── ... (FULL: also includes torch/, models/kr-sbert/)
├── docs/
│   ├── VRS_Manager_Process_Guide_EN.xlsx
│   └── VRS_Manager_Process_Guide_KR.xlsx
├── images/
│   └── vrsmanager.ico
├── Current/
│   └── README.txt
├── Previous/
│   └── README.txt
├── BERT_MODEL_SETUP.md
└── README.md
```

## Size Comparison

| Component | LIGHT | FULL |
|-----------|-------|------|
| Download size | 150 MB | 2.6 GB |
| Installed size | ~200 MB | ~3.5 GB |
| Compression ratio | ~75% | ~15% |

## Notes

- Both installers are **100% offline** - no internet required
- Both create **fully portable** installations (can zip and transfer)
- LIGHT version gracefully handles missing BERT packages
- FULL version includes everything for complete offline operation
