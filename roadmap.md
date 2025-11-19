# VRS Manager - Development Roadmap

## 📝 Version Update Checklist (IMPORTANT!)

**After completing any code work that changes the version, update ALL of these files:**

- [ ] `src/config.py` → `VERSION` constant and `VERSION_FOOTER`
- [ ] `main.py` → Docstring (line 5) and all print statements (lines 12-15)
- [ ] `README.md` → Version number (line 3) and status line (line 5)
- [ ] `README_EN.md` → Version number (line 3) and status line (line 5)
- [ ] `README_KR.md` → Version number (line 3) and status line (line 5)
- [ ] `roadmap.md` → Current Status header (below) and add to Version History section

**Don't forget to commit all documentation updates together!**

---

## 🎯 Current Status: v1119.1 (Building)

### ✅ All Core Features Complete
- 10-Key Pattern Matching System
- TWO-PASS Algorithm (1-to-1 Row Matching)
- TimeFrame Preservation Logic
- Group Word Count Analysis & Super Group Aggregation
- StrOrigin Change Analysis (Punctuation + BERT Semantic Similarity)
- Master File Update Simplification
- Translation Tracking & Migration Details

### 🚧 Current Build: v1119.1
- Bundling BERT model + PyTorch (~3GB .exe)
- Full offline operation
- Zero setup for users

---

## 📋 Next Priority: Phase 3.0 - Professional Installer System

### Overview

Replace single 3GB .exe with professional installer offering **LIGHT** and **FULL** versions.

**Problem with current approach:**
- ❌ 3GB download is large and unprofessional
- ❌ Users who don't need AI must download BERT anyway
- ❌ No flexibility for different use cases

**Solution: Two installation options**
- ✅ LIGHT (~150MB): Core features + punctuation detection
- ✅ FULL (~2.6GB): Everything + BERT AI analysis
- ✅ Professional setup experience
- ✅ Start Menu integration + proper uninstaller

---

### Distribution Strategy: Two Offline Installers (RECOMMENDED)

#### Why Offline?

**User Requirements:**
1. Company computers often have **NO internet** (isolated networks)
2. Need to **transfer to offline PCs** via USB/network
3. Predictable installation (no failed downloads mid-install)
4. **Portable after installation** (zip folder → use anywhere)

#### Distribution Plan

**GitHub Releases provides two installers:**

```
VRSManager_v1120_Light_Setup.exe       (~150MB download)
VRSManager_v1120_Full_Setup.exe        (~2.6GB download)
```

**Both installers work 100% offline** - no internet required during installation.

---

### Installation Workflow

#### **LIGHT Installer (~150MB)**

**Bundles:**
- ✅ VRS Manager Core
- ✅ Python runtime
- ✅ Data processing (pandas, openpyxl, numpy)
- ✅ All VRS Check features
- ❌ NO PyTorch
- ❌ NO sentence-transformers
- ❌ NO BERT model

**User Experience:**
```
1. Download VRSManager_v1120_Light_Setup.exe (150MB)
2. Run installer → Select install location
3. Install completes → Start Menu shortcut created
4. Run VRS Manager → All core features work

StrOrigin Analysis behavior:
- Punctuation/Space detection: ✅ Works
- If NOT punctuation-only: Shows "Content Change" (no %)
- Fast, lightweight processing
```

**Installed Size:** ~200MB

**After Installation - Portability:**
```
C:\Program Files\VRSManager\
├── VRSManager.exe
├── _internal/
│   ├── python310.dll
│   ├── pandas/
│   ├── openpyxl/
│   └── ... (core packages)

User can:
1. Zip this folder → VRSManager_Light.zip
2. Copy to offline PC
3. Extract anywhere
4. Run VRSManager.exe ✅ Works offline!
```

---

#### **FULL Installer (~2.6GB)**

**Bundles:**
- ✅ Everything in LIGHT version
- ✅ PyTorch (~2GB)
- ✅ sentence-transformers
- ✅ BERT model (kr-sbert, 447MB)
- ✅ scipy, scikit-learn
- ✅ All ML dependencies

**User Experience:**
```
1. Download VRSManager_v1120_Full_Setup.exe (2.6GB)
2. Run installer → Select install location
3. Install completes → Start Menu shortcut created
4. Run VRS Manager → All features including AI work

StrOrigin Analysis behavior:
- Punctuation/Space detection: ✅ Works
- If NOT punctuation-only: Shows "XX.X% similar" (BERT)
- Complete semantic similarity analysis
```

**Installed Size:** ~3.5GB

**After Installation - Portability:**
```
C:\Program Files\VRSManager\
├── VRSManager.exe
├── _internal/
│   ├── python310.dll
│   ├── torch/               ← PyTorch
│   ├── models/kr-sbert/     ← BERT model
│   └── ... (all packages)

User can:
1. Zip this folder → VRSManager_Full.zip (3.5GB)
2. Copy to offline PC via USB/network
3. Extract anywhere
4. Run VRSManager.exe ✅ Works offline with full AI!
```

---

### Code Modifications Required

#### **File: `src/utils/strorigin_analysis.py`**

**Current behavior:**
- Tries BERT import → Crashes if not available

**New behavior:**
- Gracefully handle missing BERT packages
- Return appropriate message based on availability

**Changes:**

```python
class StrOriginAnalyzer:
    """
    Analyzer with LIGHT/FULL version support.

    LIGHT: Punctuation/Space detection only
    FULL: Punctuation + BERT semantic similarity
    """

    def __init__(self):
        self.model = None
        self.bert_available = self._check_bert_available()

    def _check_bert_available(self) -> bool:
        """Check if BERT packages are available (FULL version)"""
        try:
            import torch
            import sentence_transformers
            return True
        except ImportError:
            return False

    def analyze(self, prev_text: str, curr_text: str) -> str:
        """
        Analyze StrOrigin change.

        Returns:
        - LIGHT & FULL: "Punctuation/Space Change" (if applicable)
        - FULL only: "XX.X% similar" (BERT analysis)
        - LIGHT only: "Content Change" (if not punctuation-only)
        """
        # First Pass: Punctuation/Space check (works in both versions)
        if is_punctuation_space_change_only(prev_text, curr_text):
            return "Punctuation/Space Change"

        # Second Pass: BERT similarity (FULL version only)
        if self.bert_available:
            # Load model and calculate similarity
            self._load_model()
            similarity = calculate_semantic_similarity(prev_text, curr_text, self.model)
            similarity_pct = similarity * 100
            return f"{similarity_pct:.1f}% similar"
        else:
            # LIGHT version: Can't calculate similarity
            return "Content Change"
```

**Result:**
- LIGHT version: Shows "Punctuation/Space Change" OR "Content Change"
- FULL version: Shows "Punctuation/Space Change" OR "XX.X% similar"

---

#### **File: `src/processors/working_processor.py`**

**Current behavior:**
- Catches FileNotFoundError only (model file missing)
- Doesn't handle ImportError (packages missing)

**New behavior:**
- Handle both ImportError and FileNotFoundError
- Create StrOrigin Analysis sheet in BOTH versions
- Different output based on version

**Changes:**

```python
def create_strorigin_analysis_sheet(self):
    """
    Create StrOrigin Change Analysis sheet.

    Works in both LIGHT and FULL versions:
    - LIGHT: Punctuation/Space + "Content Change"
    - FULL: Punctuation/Space + BERT similarity %
    """
    try:
        # Filter rows with StrOrigin changes
        changes_col = "CHANGES"
        if changes_col not in self.df_result.columns:
            log("  ℹ️  No CHANGES column found - skipping StrOrigin analysis")
            return None

        mask = self.df_result[changes_col].astype(str).str.contains(
            "StrOrigin", case=False, na=False
        )
        df_strorigin_changes = self.df_result[mask].copy()

        if df_strorigin_changes.empty:
            log("  ℹ️  No StrOrigin changes found - skipping analysis sheet")
            return None

        log(f"  → Found {len(df_strorigin_changes)} rows with StrOrigin changes")

        # Initialize analyzer (handles LIGHT/FULL automatically)
        try:
            analyzer = StrOriginAnalyzer()
            if analyzer.bert_available:
                log("  → Running FULL analysis (Punctuation + BERT similarity)...")
            else:
                log("  → Running LIGHT analysis (Punctuation + Content Change marker)...")

        except Exception as e:
            log(f"  ⚠️  Analyzer initialization failed: {e}")
            log(f"  ℹ️  Skipping StrOrigin Analysis sheet creation")
            return None

        # Analyze each row
        analysis_results = []
        for idx, row in df_strorigin_changes.iterrows():
            curr_strorigin = safe_str(row.get(COL_STRORIGIN, ""))

            # Extract previous StrOrigin from PreviousData
            prev_strorigin = ""
            if COL_PREVIOUSDATA in row and pd.notna(row[COL_PREVIOUSDATA]):
                previous_data = str(row[COL_PREVIOUSDATA])
                parts = previous_data.split(" | ")
                if len(parts) >= 1:
                    prev_strorigin = parts[0]

            if not prev_strorigin:
                analysis_results.append("N/A - No previous data")
                continue

            # Analyze (automatically uses LIGHT or FULL logic)
            result = analyzer.analyze(prev_strorigin, curr_strorigin)
            analysis_results.append(result)

        # Add "StrOrigin Analysis" column
        changes_col_index = df_strorigin_changes.columns.get_loc(changes_col)
        df_strorigin_changes.insert(
            changes_col_index + 1,
            "StrOrigin Analysis",
            analysis_results
        )

        log(f"  ✓ StrOrigin analysis complete")
        return df_strorigin_changes

    except Exception as e:
        log(f"  ⚠️  Error creating StrOrigin analysis sheet: {e}")
        import traceback
        traceback.print_exc()
        return None
```

---

### Installer Implementation (Inno Setup)

#### File: `installer/vrsmanager_light.iss`

```inno
; VRS Manager LIGHT Installer Script

[Setup]
AppName=VRS Manager (LIGHT)
AppVersion=1.120.0
AppPublisher=Neil Schmitt
DefaultDirName={autopf}\VRS Manager
OutputDir=installer_output
OutputBaseFilename=VRSManager_v1120_Light_Setup
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\VRSManager.exe

[Files]
; Core application (LIGHT version - no BERT)
Source: "dist_light\VRSManager.exe"; DestDir: "{app}"
Source: "dist_light\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "docs\*"; DestDir: "{app}\docs"; Flags: recursesubdirs
Source: "images\*"; DestDir: "{app}\images"
Source: "Current\README.txt"; DestDir: "{app}\Current"
Source: "Previous\README.txt"; DestDir: "{app}\Previous"

[Icons]
Name: "{autoprograms}\VRS Manager"; Filename: "{app}\VRSManager.exe"
Name: "{autodesktop}\VRS Manager"; Filename: "{app}\VRSManager.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\VRSManager.exe"; Description: "Launch VRS Manager"; Flags: postinstall nowait skipifsilent
```

#### File: `installer/vrsmanager_full.iss`

```inno
; VRS Manager FULL Installer Script

[Setup]
AppName=VRS Manager (FULL)
AppVersion=1.120.0
AppPublisher=Neil Schmitt
DefaultDirName={autopf}\VRS Manager
OutputDir=installer_output
OutputBaseFilename=VRSManager_v1120_Full_Setup
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\VRSManager.exe

[Files]
; Full application (includes BERT + PyTorch)
Source: "dist_full\VRSManager.exe"; DestDir: "{app}"
Source: "dist_full\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "docs\*"; DestDir: "{app}\docs"; Flags: recursesubdirs
Source: "images\*"; DestDir: "{app}\images"
Source: "Current\README.txt"; DestDir: "{app}\Current"
Source: "Previous\README.txt"; DestDir: "{app}\Previous"

[Icons]
Name: "{autoprograms}\VRS Manager"; Filename: "{app}\VRSManager.exe"
Name: "{autodesktop}\VRS Manager"; Filename: "{app}\VRSManager.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\VRSManager.exe"; Description: "Launch VRS Manager"; Flags: postinstall nowait skipifsilent
```

---

### Build Process

#### Step 1: Build Two .exe Versions

**LIGHT build:**
```bash
# Temporary: Remove BERT from VRSManager.spec
# Remove: models/kr-sbert from datas
# Remove: torch, transformers from hiddenimports

pyinstaller VRSManager.spec --clean --noconfirm --distpath dist_light
# Result: dist_light/VRSManager.exe (~150MB)
```

**FULL build:**
```bash
# Use full VRSManager.spec (current - includes BERT)
pyinstaller VRSManager.spec --clean --noconfirm --distpath dist_full
# Result: dist_full/VRSManager.exe (~3GB)
```

#### Step 2: Compile Installers

```bash
# Install Inno Setup (Windows)
iscc installer/vrsmanager_light.iss
# Output: VRSManager_v1120_Light_Setup.exe (~150MB)

iscc installer/vrsmanager_full.iss
# Output: VRSManager_v1120_Full_Setup.exe (~2.6GB)
```

#### Step 3: Upload to GitHub Releases

```
GitHub Release v1120.0:
Assets:
- VRSManager_v1120_Light_Setup.exe (150MB)
- VRSManager_v1120_Full_Setup.exe (2.6GB)
- Source code (zip)
- Source code (tar.gz)
```

---

### GitHub Actions Workflow Update

**New workflow: `.github/workflows/build-installers.yml`**

```yaml
name: Build LIGHT and FULL Installers

on:
  push:
    branches: [ main ]
    paths:
      - 'BUILD_TRIGGER.txt'

jobs:
  build-light:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install LIGHT dependencies
        run: |
          pip install pandas openpyxl numpy
          pip install pyinstaller

      - name: Build LIGHT .exe
        run: |
          # Modify spec to exclude BERT temporarily
          python scripts/prepare_light_spec.py
          pyinstaller VRSManager_light.spec --clean --noconfirm --distpath dist_light

      - name: Install Inno Setup
        run: choco install innosetup -y

      - name: Compile LIGHT installer
        run: iscc installer/vrsmanager_light.iss

      - name: Upload LIGHT installer
        uses: actions/upload-artifact@v3
        with:
          name: VRSManager_Light_Setup
          path: installer_output/VRSManager_v1120_Light_Setup.exe

  build-full:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install FULL dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Download BERT model
        run: python scripts/download_bert_model.py

      - name: Build FULL .exe
        run: pyinstaller VRSManager.spec --clean --noconfirm --distpath dist_full

      - name: Install Inno Setup
        run: choco install innosetup -y

      - name: Compile FULL installer
        run: iscc installer/vrsmanager_full.iss

      - name: Upload FULL installer
        uses: actions/upload-artifact@v3
        with:
          name: VRSManager_Full_Setup
          path: installer_output/VRSManager_v1120_Full_Setup.exe

  release:
    needs: [build-light, build-full]
    runs-on: ubuntu-latest
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: v1.120.0
          files: |
            VRSManager_Light_Setup/VRSManager_v1120_Light_Setup.exe
            VRSManager_Full_Setup/VRSManager_v1120_Full_Setup.exe
```

---

### User Documentation Updates

#### README.md

```markdown
## Download

Choose your version:

### 🪶 LIGHT Version (150 MB) - Recommended for:
- Fast download needed
- Basic StrOrigin analysis (punctuation/space detection)
- Limited disk space

**[Download LIGHT Installer](https://github.com/NeilVibe/VRS-Manager/releases/latest/download/VRSManager_v1120_Light_Setup.exe)**

### 🚀 FULL Version (2.6 GB) - Recommended for:
- Complete AI-powered analysis
- Semantic similarity percentage
- Offline use (all features included)

**[Download FULL Installer](https://github.com/NeilVibe/VRS-Manager/releases/latest/download/VRSManager_v1120_Full_Setup.exe)**

---

## Installation

1. Download your preferred version (LIGHT or FULL)
2. Run the installer (VRSManager_vXXXX_Setup.exe)
3. Follow installation wizard
4. Launch from Start Menu

**Both versions work 100% offline after installation.**

## Portable Use (Offline Computers)

After installation, you can copy the installed folder to any computer:

1. Install on a computer (online or offline)
2. Go to: `C:\Program Files\VRS Manager\`
3. Zip the entire folder
4. Transfer to offline computer via USB/network
5. Extract anywhere and run `VRSManager.exe`

Works completely offline! ✅
```

---

## Summary: LIGHT vs FULL Comparison

| Feature | LIGHT | FULL |
|---------|-------|------|
| **Download Size** | 150 MB | 2.6 GB |
| **Installed Size** | ~200 MB | ~3.5 GB |
| **Internet Required** | ❌ No | ❌ No |
| **All VRS Check Features** | ✅ Yes | ✅ Yes |
| **Punctuation/Space Detection** | ✅ Yes | ✅ Yes |
| **BERT Semantic Similarity** | ❌ No | ✅ Yes |
| **StrOrigin Analysis Output** | "Punctuation/Space Change"<br>"Content Change" | "Punctuation/Space Change"<br>"XX.X% similar" |
| **Portable (Zip & Transfer)** | ✅ Yes | ✅ Yes |
| **Offline Operation** | ✅ Yes | ✅ Yes |
| **Best For** | Fast download, basic needs | Complete analysis, offline AI |

---

## Implementation Checklist

### Phase 3.0: Professional Installer System

**Code Changes:**
- [ ] Modify `src/utils/strorigin_analysis.py`:
  - [ ] Add `_check_bert_available()` method
  - [ ] Update `analyze()` to return "Content Change" in LIGHT version
  - [ ] Test graceful degradation

- [ ] Modify `src/processors/working_processor.py`:
  - [ ] Update `create_strorigin_analysis_sheet()` error handling
  - [ ] Handle both ImportError and FileNotFoundError
  - [ ] Test LIGHT and FULL versions

**Build Infrastructure:**
- [ ] Create `installer/` folder
- [ ] Write `vrsmanager_light.iss` (Inno Setup script)
- [ ] Write `vrsmanager_full.iss` (Inno Setup script)
- [ ] Create `scripts/prepare_light_spec.py` (removes BERT from spec)
- [ ] Create `VRSManager_light.spec` (LIGHT build config)
- [ ] Test LIGHT build locally
- [ ] Test FULL build locally

**GitHub Actions:**
- [ ] Create `.github/workflows/build-installers.yml`
- [ ] Add Inno Setup compilation step
- [ ] Test workflow (dry run)
- [ ] Verify artifact uploads

**Testing:**
- [ ] Test LIGHT installer on clean Windows VM
- [ ] Test FULL installer on clean Windows VM
- [ ] Verify StrOrigin Analysis in both versions
- [ ] Test portability (zip → transfer → extract → run)
- [ ] Test offline operation

**Documentation:**
- [ ] Update README.md with two download links
- [ ] Update BERT_MODEL_SETUP.md (explain LIGHT vs FULL)
- [ ] Add installation guide
- [ ] Add portability guide

**Release:**
- [ ] Update version to v1120.0
- [ ] Build both installers via GitHub Actions
- [ ] Create GitHub Release
- [ ] Upload both installers
- [ ] Announce release

---

## Version History

### v1120.0 (Planned - Phase 3.0)
- **NEW**: Professional installer system
- **NEW**: LIGHT version (150MB) - Core features only
- **NEW**: FULL version (2.6GB) - Complete with BERT
- **IMPROVED**: StrOrigin Analysis works in both versions
- **IMPROVED**: Portable installation (zip & transfer)
- **IMPROVED**: Start Menu integration
- **IMPROVED**: Proper Windows uninstaller

### v1119.1 (Current - Building)
- **BUNDLED**: BERT model + PyTorch in single 3GB .exe
- **IMPROVED**: Full offline operation
- **IMPROVED**: Zero setup required

### v1119.0 (Production Ready)
- **Phase 2.3 COMPLETED**: StrOrigin Change Analysis
  - NEW: "StrOrigin Change Analysis" sheet in Working VRS Check
  - NEW: Punctuation/Space-only detection
  - NEW: BERT semantic similarity (Korean SBERT)
  - NEW: Results: "Punctuation/Space Change" or "XX.X% similar"
- **OFFLINE**: Model runs locally, no internet needed
- **FILES ADDED**:
  - `src/utils/strorigin_analysis.py`
  - `scripts/download_bert_model.py`
  - `scripts/download_model.bat`

### v1118.6 (Reorganization Complete)
- **REORGANIZED**: Project structure
  - Moved tests → `tests/`
  - Moved docs → `docs/`
  - Moved archives → `ARCHIVE/`
  - Created `scripts/` for build/setup scripts
- **Phase 2.2.1 COMPLETED**: Super Group Analysis Improvements
  - Removed "Others" category
  - Reordered super groups
  - Added migration tracking table
  - Renamed "Untranslated" → "Not Translated"

### v1118.5 and earlier
- See git history for complete version details
- All core VRS Check features implemented
- 10-Key matching, TWO-PASS algorithm, TimeFrame preservation
