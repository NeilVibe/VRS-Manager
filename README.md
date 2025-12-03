# VRS Manager

**Version:** 12031417
**Author:** Neil Schmitt
**Status:** Production Ready (TWO-PASS Algorithm + Clean Super Group Tables + Migration Tracking)

[![Build Executables](https://github.com/NeilVibe/VRS-Manager/actions/workflows/build-executables.yml/badge.svg)](https://github.com/NeilVibe/VRS-Manager/actions/workflows/build-executables.yml)
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/NeilVibe/VRS-Manager/releases)

---

## Overview

VRS Manager is a specialized tool for managing Voice Recording Script (VRS) data across multiple languages and versions. It helps track changes, updates, and translations for voice-over content in game development or multimedia projects.

The tool compares previous and current versions of VRS Excel files to detect and classify changes, manage multi-language translations (Korean, English, Chinese), and update master files intelligently based on importance levels.

---

## Key Features

### 🔑 10-Key Pattern Matching + TWO-PASS Algorithm (v1116 - Latest)
- **Ultra-precise change detection** using comprehensive 10-key combinations:
  - **2-Key Combos (6)**: SE, SO, SC, EO, EC, OC
  - **3-Key Combos (4)**: SEO, SEC, SOC, EOC
- **TWO-PASS Algorithm**: Eliminates 1-to-many matching issues
  - **PASS 1**: Detect & mark certainties (No Change, New)
  - **PASS 2**: Pattern match using UNMARKED rows only
  - **After PASS 2**: Detect deleted rows (unmarked PREVIOUS rows)
- **100% accurate NEW/DELETED detection**: Row is NEW/DELETED only when **ALL 10 keys** are missing
- **Handles all duplicates**: Duplicate StrOrigin, blank cells, duplicate CastingKey
- **Cascading pattern matching**: From most specific (3-key) to least specific (2-key)
- **Prevents false positives** when common phrases appear across multiple characters
- **Mathematically correct**: `new_rows - deleted_rows = actual_difference` ✅

### 📊 Group Word Count Analysis (v1118.1 - NEW!)
- **Group-level word tracking**: Track word count changes per Group (chapter/category)
- **Migration detection**: Automatically detect when content moves between groups
- **Detailed metrics per group**:
  - Total words (Previous/Current)
  - Words added (new rows)
  - Words deleted (removed rows)
  - Words changed (StrOrigin modifications)
  - Words migrated in/out (between groups)
  - Net change & percentage
- **Formatted Excel sheet**: "Group Word Analysis" with color-coded changes
- **Perfect for voice actors**: Filter by group to see exactly what changed in their section
- **No impact on accuracy**: Built on top of existing 10-key system (zero changes to core logic)

### 🌍 Multi-Language Support
- **Tri-lingual processing** (Korean, English, Chinese)
- **Flexible updates** - can update just 1, 2, or all 3 languages
- **Auto-detection** of language files from folder structure

### 🎯 Intelligent Import Logic
- **Status-aware** - preserves after-recording data automatically
- **Change-type specific** - different logic for StrOrigin, Desc, TimeFrame changes
- **Importance-based** - High and Low importance rows handled differently

### 📊 Four Main Processes

1. **Raw VRS Check** - Compare PREVIOUS ↔ CURRENT and detect all changes
2. **Working VRS Check** - Import PREVIOUS data into CURRENT with smart logic
3. **All Language Check** - Tri-lingual merge and update (KR/EN/CN)
4. **Master File Update** - Update Master File with 3-key copy-paste validation

### 📈 Update History Tracking
- **Complete audit trail** for all processes
- **JSON-based storage** with timestamps and statistics
- **Viewable via GUI** with rich formatting

---

## Installation

### Option 1: Use Pre-Built Executable (Recommended)

**No Python installation required!**

#### Download from GitHub Actions (Latest Build)
1. Go to [Actions tab](https://github.com/NeilVibe/VRS-Manager/actions)
2. Click latest "Build Executables" workflow
3. Download artifact for your platform:
   - **Windows**: `VRSManager-Windows.zip` → Extract → Run `VRSManager.exe`
   - **Linux**: `VRSManager-Linux.zip` → Extract → `chmod +x VRSManager` → `./VRSManager`
   - **macOS**: `VRSManager-macOS.zip` → Extract → `chmod +x VRSManager` → `./VRSManager`

#### Download from Releases (Stable)
1. Go to [Releases page](https://github.com/NeilVibe/VRS-Manager/releases)
2. Download latest release for your platform
3. Extract and run!

All files (history JSON, Excel outputs) are created in the same folder as the executable.

### Option 2: Run from Source

**Prerequisites:**
- **Python 3.7+**
- **Required packages:**
  ```bash
  pip install -r requirements.txt
  ```

**Steps:**

1. **Clone the repository:**
   ```bash
   git clone git@github.com:NeilVibe/VRS-Manager.git
   cd VRS-Manager
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Option 3: Build Your Own Executable

See **[BUILD.md](BUILD.md)** for detailed build instructions.

**Quick build:**
```bash
# Linux/macOS
chmod +x build_executable.sh
./build_executable.sh

# Windows
python -m PyInstaller VRSManager.spec --clean --noconfirm
```

Executable will be in `dist/` folder.

---

## Project Structure

```
vrs-manager/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── claude.md                        # Project overview for AI
├── roadmap.md                       # Development roadmap
│
├── src/                             # Modular source code
│   ├── config.py                    # Configuration constants
│   │
│   ├── processors/                  # Process orchestrators
│   │   ├── base_processor.py        # Abstract base class
│   │   ├── raw_processor.py         # Raw VRS Check
│   │   ├── working_processor.py     # Working VRS Check
│   │   ├── alllang_processor.py     # All Language Check
│   │   └── master_processor.py      # Master File Update
│   │
│   ├── core/                        # Business logic
│   │   ├── casting.py               # CastingKey generation
│   │   ├── lookups.py               # 4-tier lookup building
│   │   ├── comparison.py            # Change detection
│   │   ├── import_logic.py          # Data import rules
│   │   ├── working_comparison.py    # Working process logic
│   │   ├── working_helpers.py       # Working process helpers
│   │   └── alllang_helpers.py       # All Language helpers
│   │
│   ├── io/                          # File operations
│   │   ├── excel_reader.py          # Excel reading
│   │   ├── excel_writer.py          # Excel writing
│   │   ├── formatters.py            # Cell formatting
│   │   └── summary.py               # Summary sheets
│   │
│   ├── history/                     # Update history
│   │   └── history_manager.py       # History tracking
│   │
│   ├── ui/                          # User interface
│   │   ├── main_window.py           # Main GUI window
│   │   └── history_viewer.py        # History viewer dialog
│   │
│   └── utils/                       # Utilities
│       ├── helpers.py               # Helper functions
│       ├── progress.py              # Progress indicators
│       └── data_processing.py       # Data processing utils
│
├── tests/                           # Unit tests (future)
│
├── docs/                            # Documentation
│
├── ARCHIVE/                         # Old versions
│   ├── vrsmanager1114.py           # v1114 (3-key system)
│   └── vrsmanager1114v2.py         # v1114v2 (3-key + fixes)
│
└── original_monolith/              # Latest monolith
    └── vrsmanager1114v3.py         # v1114v3 (4-tier key system)
```

---

## Usage

### 1. Raw VRS Check

**Purpose:** Compare PREVIOUS ↔ CURRENT and detect all changes

**Steps:**
1. Click **"PROCESS RAW VRS CHECK"**
2. Select PREVIOUS file
3. Select CURRENT file
4. Review the output Excel with color-coded changes

**Output:**
- Change classification for each row
- Previous StrOrigin tracking
- Word counts for translation workload
- Deleted rows in separate sheet

---

### 2. Working VRS Check

**Purpose:** Import PREVIOUS data into CURRENT with intelligent logic

**Steps:**
1. Click **"PROCESS WORKING VRS CHECK"**
2. Select PREVIOUS file (contains completed work)
3. Select CURRENT file (new baseline to update)
4. Review the enriched output

**Output:**
- CURRENT file with imported STATUS, Text, FREEMEMO
- Smart import based on change type and recording status
- PreviousData column for audit trail

---

### 3. All Language Check

**Purpose:** Tri-lingual merge and update (KR/EN/CN)

**Steps:**
1. Click **"PROCESS ALL LANGUAGE CHECK"**
2. Select folder containing `Previous/` and `Current/` subfolders
3. Files auto-detected: `*_KR.xlsx`, `*_EN.xlsx`, `*_CN.xlsx`
4. Review the merged output

**Output:**
- Single file with all 3 languages
- Independent change tracking per language
- Flexible: can update 1, 2, or 3 languages

---

### 4. Master File Update

**Purpose:** Update Master File with Working Process output

**Steps:**
1. Click **"PROCESS MASTER FILE UPDATE"**
2. Select SOURCE file (Working Process output)
3. Select TARGET file (Master File to update)
4. Review the updated Master

**Output:**
- Main Sheet (High): All high-importance rows
- Low Importance: All low-importance rows (preserves TARGET data)
- Deleted Rows: 3-key validated deletions
- Update History: Auto-generated tracking

---

## Change Types

The tool detects and classifies the following change types:

### Core Field Changes

| Change Type | Description | Color |
|-------------|-------------|-------|
| **StrOrigin Change** | Dialogue text changed | Yellow |
| **EventName Change** | EventName identifier changed | Light Yellow |
| **SequenceName Change** | Sequence/scene reorganized | Light Blue |
| **CastingKey Change** | Voice actor assignment changed | Orange |

### Metadata Field Changes

| Change Type | Description | Color |
|-------------|-------------|-------|
| **TimeFrame Change** | StartFrame/EndFrame timing changed | Red-Orange |
| **Desc Change** | Description/context changed | Purple |
| **DialogType Change** | Dialogue type classification changed | (Composite) |
| **Group Change** | Group assignment changed | (Composite) |
| **Character Group Change** | Character attributes changed (Tribe/Age/Gender/Job/Region) | Light Sky Blue |

### System States

| Classification | Description | Color |
|---------------|-------------|-------|
| **New Row** | Row exists in CURRENT but not in PREVIOUS | Green |
| **Deleted Row** | Row exists in PREVIOUS but not in CURRENT | Red |
| **No Change** | Perfect match (all 4 core keys identical) | Light Gray |
| **No Relevant Change** | Changes only in non-Korean text (ignored) | Dark Gray |

### Composite Changes

The system can detect 100+ combinations when multiple fields change together:
- **Example:** "StrOrigin+Desc Change" (text and description both changed)
- **Example:** "EventName+CastingKey Change" (event renamed AND actor changed)
- **Example:** "StrOrigin+Desc+TimeFrame Change" (major revision)

**Note:** See `docs/CHANGE_TYPES_REFERENCE.md` for complete details on all change types, detection logic, and processor compatibility.

---

## Import Logic Rules

### Working Process & All Language

| Change Type | Source for Data | Notes |
|-------------|----------------|-------|
| **No Change** | PREVIOUS | Full import (STATUS, Text, Desc, FREEMEMO) |
| **StrOrigin Change** | PREVIOUS → PreviousData<br>CURRENT → Text | Preserves STATUS, FREEMEMO, Desc from PREVIOUS |
| **Desc Change** | PREVIOUS → PreviousData<br>PREVIOUS → Text | Full import including Text |
| **TimeFrame Change** | PREVIOUS → PreviousData<br>PREVIOUS → full import | Full import of STATUS, Text, Desc, FREEMEMO |
| **EventName Change** | PREVIOUS → full import | Everything from PREVIOUS |
| **SequenceName Change** | PREVIOUS → full import | Everything from PREVIOUS |
| **CastingKey Change** | PREVIOUS → full import | Everything from PREVIOUS |
| **DialogType Change** | PREVIOUS → full import | Everything from PREVIOUS |
| **Group Change** | PREVIOUS → full import | Everything from PREVIOUS |
| **Character Group Change** | PREVIOUS → full import | Everything from PREVIOUS |
| **Composite Changes** | Depends on StrOrigin | If StrOrigin in change → PreviousData created |
| **New Row** | CURRENT only | No import (new content) |

**Special Rule:** If PREVIOUS STATUS is after-recording (RECORDED, FINAL, etc.), always preserve STATUS regardless of change type.

### Master File Update

| Change Type | High Importance | Low Importance |
|-------------|----------------|----------------|
| **Existing Rows** | Copy SOURCE data<br>**Exception:** Preserve TARGET TimeFrame when TimeFrame changed but StrOrigin did NOT change | **Keep TARGET data** |
| **New Rows** | Include in output | **Exclude from output** |
| **Deleted Rows** | Track in "Deleted Rows" sheet | Track in "Deleted Rows" sheet |

**TimeFrame Preservation Rule (High Importance only):**
- **If TimeFrame changed AND StrOrigin changed:** Update TimeFrame (use SOURCE)
- **If TimeFrame changed BUT StrOrigin did NOT change:** Preserve TimeFrame (keep TARGET)
- This ensures TimeFrame updates only apply when accompanied by StrOrigin changes

---

## Configuration

All configuration constants are in `src/config.py`:

- **Column names** (SequenceName, EventName, StrOrigin, etc.)
- **Status categories** (after-recording vs pre-recording)
- **Output column orders** (for each process type)
- **File naming patterns**

---

## Update History

The tool maintains 3 separate JSON history files:
- `working_update_history.json` - Working Process history
- `alllang_update_history.json` - All Language Process history
- `master_update_history.json` - Master File Update history

Each record contains:
- Timestamp
- Process type
- Input/output files
- Statistics (total rows, change counts)

View history via **"📊 View Update History"** button in GUI.

---

## Version History

### v1117.1 (Current - TimeFrame+StrOrigin Logic + Column Robustness)
- ✅ **Column Robustness Fix** - Handles files with different column structures
  - Only compares columns that exist in BOTH files (PREVIOUS and CURRENT)
  - No crashes when optional columns missing (Desc, StartFrame, EndFrame, Text, etc.)
  - Required CORE columns: SequenceName, EventName, StrOrigin, CastingKey components
  - Program gracefully skips change detection for missing optional columns
- ✅ All v1117 features included

### v1117 (Previous - TimeFrame+StrOrigin Logic)
- ✅ **Master File Update TimeFrame Preservation Logic** - Robust and universal implementation
  - If TimeFrame changed AND StrOrigin changed → Update TimeFrame
  - If TimeFrame changed BUT StrOrigin did NOT change → Preserve TimeFrame
  - Works for ANY combination of changes (universal rule)
- ✅ **Documentation Updates** - All guides updated with TimeFrame logic
- ✅ All v1116 features included

### v1116 (Previous - TWO-PASS Algorithm)
- ✅ **TWO-PASS Algorithm** - Eliminates 1-to-many matching issues
  - PASS 1: Detect & mark certainties (No Change, New)
  - PASS 2: Pattern match using UNMARKED rows only
  - After PASS 2: Detect deleted rows (unmarked PREVIOUS rows)
- ✅ **100% Correct Duplicate Handling** - StrOrigin, CastingKey, blank cells
- ✅ **Mathematically Correct Row Counting** - `new - deleted = actual_diff` ✅
- ✅ **Comprehensive Test Suite** - Full duplicate handling validation
- ✅ **Identical Detection Logic** - All 4 processors use same algorithm
- ✅ All 4 core files updated (comparison, working_comparison, alllang_helpers, master_processor)
- ✅ Full duplicate row cleanup before processing
- ✅ 10-Key Pattern Matching System
- ✅ Modular architecture maintained
- ✅ Multi-language support (KR/EN/CN)
- ✅ Update history tracking
- ✅ Intelligent import logic

### v1114v4 (Previous - 10-Key System)
- ✅ **10-Key Pattern Matching System** - Ultra-precise change detection
  - 2-key combinations: SE, SO, SC, EO, EC, OC
  - 3-key combinations: SEO, SEC, SOC, EOC
- ✅ **Bug Fix**: NEW/DELETED detection now 100% accurate
- ✅ **Upfront NEW check**: ALL 10 keys must be missing
- ✅ **Cascading pattern matching**: Most specific to least specific
- ✅ **Correct row count math**: `new_rows - deleted_rows = actual_difference`
- ✅ All 9 core files updated (lookups, comparison, processors)
- ✅ Modular architecture maintained
- ✅ Multi-language support (KR/EN/CN)
- ✅ Update history tracking
- ✅ Intelligent import logic

### v1114v3 (Previous - 4-Tier Key System)
- ✅ **4-Tier Key System** (CW, CG, ES, CS)
- ✅ **Stage 2 Verification** with Key 4 (CastingKey-based)
- ✅ **Duplicate StrOrigin handling** for common phrases
- ✅ **Character identity verification** in all processes
- ✅ **Modular architecture** - 31 Python files, 4,400+ lines
- ✅ **Fully refactored** from 2,700-line monolith
- ✅ Master File LOW importance logic fix
- ✅ Color-coded change visualization

### v1114v2 (Previous Stable)
- 3-Key System (SequenceName + EventName + StrOrigin)
- SequenceName Change Detection
- Master File LOW importance logic fix
- Multi-language support (KR/EN/CN)

### v1114 (Original)
- 2-Key System
- Basic change detection
- Single monolith file

---

## Development

### Running Tests

```bash
# Syntax validation
python3 -m py_compile main.py
python3 -m py_compile src/processors/*.py

# Future: Unit tests
pytest tests/
```

### Contributing

1. Create a feature branch
2. Make changes with clear commit messages
3. Test thoroughly with real data
4. Submit pull request

---

## License

Proprietary - © Neil Schmitt

---

## Support

For issues, questions, or feature requests:
- **GitHub Issues:** https://github.com/NeilVibe/VRS-Manager/issues
- **Email:** (contact info)

---

## Acknowledgments

- **Built with:** Python, pandas, openpyxl, tkinter
- **AI Assistant:** Claude Code (Anthropic)
- **Architecture:** Template Method Pattern, Modular Design

---

**Happy VRS Managing! 🎙️🎬**
