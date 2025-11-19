# VRS Manager - Project Overview

## What is VRS Manager?

VRS Manager is a specialized tool for managing Voice Recording Script (VRS) data across multiple languages and versions. It helps track changes, updates, and translations for voice-over content in game development or multimedia projects.

## Core Purpose

The tool compares previous and current versions of VRS Excel files to:
- Detect and classify changes (new rows, edits, deletions, sequence changes)
- Manage multi-language translations (Korean, English, Chinese)
- Update master files intelligently based on importance levels
- Maintain complete update history for auditing

## Key Concepts

### 1. **10-Key Pattern Matching System with TWO-PASS Algorithm (v1116 - Latest)**
The tool uses a comprehensive 10-key matching system with TWO-PASS algorithm for ultra-precise change detection:

```
2-Key Combinations (6):
- SE: (SequenceName, EventName)
- SO: (SequenceName, StrOrigin)
- SC: (SequenceName, CastingKey)
- EO: (EventName, StrOrigin)
- EC: (EventName, CastingKey)
- OC: (StrOrigin, CastingKey)

3-Key Combinations (4):
- SEO: (SequenceName, EventName, StrOrigin)
- SEC: (SequenceName, EventName, CastingKey)
- SOC: (SequenceName, StrOrigin, CastingKey)
- EOC: (EventName, StrOrigin, CastingKey)
```

**Why 10 keys + TWO-PASS?**
- **100% accurate NEW/DELETED detection**: Row is NEW/DELETED only when **ALL 10 keys** are missing
- **No false positives**: Prevents incorrect classification when partial matches occur
- **No 1-to-many matching**: TWO-PASS algorithm ensures each PREVIOUS row matches at most ONE CURRENT row
- **Handles all duplicates**: Duplicate StrOrigin, blank cells, duplicate CastingKey
- **Mathematically correct**: `new_rows - deleted_rows = actual_difference` ✅

**NEW ROW Detection**: ALL 10 keys missing from PREVIOUS
**DELETED ROW Detection**: ALL 10 keys missing from CURRENT

**TWO-PASS Algorithm** (Prevents 1-to-many matching):
```
PASS 1 - Detect & Mark Certainties:
  - Perfect match (ALL 10 keys match) → "No Change" → Mark PREVIOUS index
  - No match (ALL 10 keys missing) → "New Row"
  - After all CURRENT processed: Unmarked PREVIOUS rows → "Deleted"

PASS 2 - Detect Changes (using UNMARKED rows only):
  - Pattern match with 10 keys (3-key first, then 2-key)
  - Only use PREVIOUS rows with UNMARKED DataFrame indices
  - First unmarked match wins (deterministic, order-dependent)
  - No unmarked match → "New Row"
```

**Why CastingKey?**
- CastingKey = `{CharacterKey}_{DialogVoice}_{GroupKey}_{DialogType}`
- **Unique per character** within a sequence
- Differentiates speakers even with identical dialogue
- Critical for handling common dialogue phrases
- **Purpose**: Verification helper for Key 2 (not a standalone identifier)

**Pattern Matching Logic (10-Key System):**

The system uses a 2-step approach:

```
STEP 1: NEW ROW Detection (Upfront Check)
  → Check ALL 10 keys
  → If ALL missing from PREVIOUS → NEW ROW ✅
  → If ANY key matches → Continue to STEP 2

STEP 2: Cascading Pattern Matching
  LEVEL 1: 3-Key Matches (Most Specific)
    → SEO match: Only CastingKey changed
    → SEC match: Only StrOrigin changed
    → SOC match: Only EventName changed
    → EOC match: Only SequenceName changed

  LEVEL 2: 2-Key Matches (Less Specific)
    → SE match: StrOrigin and/or CastingKey changed
    → OC match: SequenceName and/or EventName changed
    → EC match: SequenceName and/or StrOrigin changed
    → SC match: EventName and StrOrigin changed
    → SO match: EventName and/or CastingKey changed
    → EO match: SequenceName changed (most common)
```

**Example:**
```
PREVIOUS:
  Row A: Seq="Scene1", Event="E123", StrOrigin="Hello", CastingKey="Hero_Male_A"

CURRENT:
  Row B: Seq="Scene1", Event="E456", StrOrigin="Hello", CastingKey="NPC_Female_B"

Matching Process:
  STEP 1: Check ALL 10 keys
    key_se: (Scene1, E123) vs (Scene1, E456) → NO MATCH
    key_so: (Scene1, Hello) → MATCH! ✓
    key_sc: (Scene1, Hero_Male_A) vs (Scene1, NPC_Female_B) → NO MATCH
    key_eo: (E123, Hello) vs (E456, Hello) → NO MATCH
    key_ec: (E123, Hero_Male_A) vs (E456, NPC_Female_B) → NO MATCH
    key_oc: (Hello, Hero_Male_A) vs (Hello, NPC_Female_B) → NO MATCH
    key_seo: (Scene1, E123, Hello) vs (Scene1, E456, Hello) → NO MATCH
    key_sec: (Scene1, E123, Hero_Male_A) vs (Scene1, E456, NPC_Female_B) → NO MATCH
    key_soc: (Scene1, Hello, Hero_Male_A) vs (Scene1, Hello, NPC_Female_B) → NO MATCH
    key_eoc: (E123, Hello, Hero_Male_A) vs (E456, Hello, NPC_Female_B) → NO MATCH

  Result: Only key_so matches, NOT all keys missing
  → Continue to STEP 2

  STEP 2: Pattern Matching
    → key_so matches → EventName and/or CastingKey changed
    → Check details: E changed (E123→E456), C changed (Hero_Male_A→NPC_Female_B)
    → Classification: "EventName+CastingKey Change" ✅
```

### 2. **Importance Levels**
- **High**: Critical content that requires updates and tracking
- **Low**: Non-critical content with special handling rules

### 3. **Status Categories**
- **Pre-recording**: Empty, "POLISHED", "SPEC-OUT", "CHECK", etc.
- **After-recording**: "RECORDED", "FINAL", "RE-RECORD", "SHIPPED", etc.
  - Includes Korean: "전달 완료", "녹음 완료"
  - Includes Chinese: "已传达", "已录音"

## Main Processes

### 1. **Raw Process**
**Purpose**: Compare PREVIOUS ↔ CURRENT and detect all changes

**Input**:
- PREVIOUS file (baseline)
- CURRENT file (new version)

**Output**:
- Excel file with multiple sheets showing:
  - All rows with CHANGES column indicating type of change
  - Previous StrOrigin tracking
  - Color-coded changes
  - Summary statistics
  - Word counts for translation workload

**Change Types Detected**:
- New Row
- Deleted Rows
- StrOrigin Change
- Desc Change
- TimeFrame Change
- EventName Change
- SequenceName Change
- Combined changes (e.g., "EventName+TimeFrame Change")

---

### 2. **Working Process**
**Purpose**: Import PREVIOUS data into CURRENT with intelligent logic

**Input**:
- PREVIOUS file (contains completed work)
- CURRENT file (new baseline to update)

**Output**:
- CURRENT file enriched with data from PREVIOUS
- Smart import rules based on status and change types

**Import Logic Rules**:

| Change Type | Source for Data | Notes |
|-------------|----------------|-------|
| **No Change** | PREVIOUS | Full import (STATUS, Text, FREEMEMO) |
| **StrOrigin Change** | PREVIOUS → PreviousData<br>CURRENT → Text | Preserves STATUS, FREEMEMO from PREVIOUS |
| **Desc Change** | PREVIOUS → PreviousData<br>PREVIOUS → Text | Full import including Text |
| **TimeFrame Change** | PREVIOUS → PreviousData<br>PREVIOUS → full import | Full import of STATUS, Text, FREEMEMO |
| **EventName Change** | PREVIOUS → full import | Everything from PREVIOUS |
| **SequenceName Change** | PREVIOUS → full import | Everything from PREVIOUS |
| **New Row** | CURRENT only | No import (new content) |
| **Deleted Row** | Appears in separate sheet | Tracked for reference |

**Special Behavior**:
- After-recording status rows: Always preserved
- Pre-recording status rows: Eligible for updates based on change type
- PreviousData column: Created for tracking original StrOrigin on changes

---

### 3. **All Language Process**
**Purpose**: Tri-lingual merge and update (KR/EN/CN)

**Input**:
- PREVIOUS files: KR, EN, CN (optional - can be missing)
- CURRENT files: KR, EN, CN (required)

**Output**:
- Merged file with language-specific updates
- Each language processed independently with same import logic
- Flexible: Can update just 1, 2, or all 3 languages

**Process Flow**:
1. Merge CURRENT KR+EN+CN into single dataframe (by StrOrigin key)
2. Build lookups for each PREVIOUS language file
3. Apply import logic per language with suffix (_KR, _EN, _CN)
4. Classify changes per language independently
5. Output with all languages in single file

**Import Rules**: Same as Working Process, but per language

---

### 4. **Master File Update**
**Purpose**: Update Master File with Working Process output using 10-Key System

**Input**:
- SOURCE: Working Process output file (new updates)
- TARGET: Master File (existing master data to update)

**Output**:
- Updated Master File with:
  - Main Sheet (High): All high-importance rows
  - Low Importance: All low-importance rows
  - Deleted Rows: Rows removed from SOURCE (10-key validated)

**Process Logic**:

#### Current Behavior:
1. **Separate by Importance**: Split SOURCE into High/Low
2. **Build 10-Key Lookups**: Create lookups for SOURCE High/Low + TARGET
3. **Match & Classify**: Use 10-key TWO-PASS system to determine change type
4. **Copy Data**: Copy SOURCE data to output with change classification
5. **Handle Deletions**: Find rows in TARGET missing from all SOURCE keys
6. **TimeFrame Preservation**: Apply smart TimeFrame logic (v1117)

#### Special Handling:
- **TimeFrame Preservation Logic (v1117)**:
  - If StrOrigin changed → Update TimeFrame (use SOURCE)
  - If StrOrigin NOT changed → Preserve TimeFrame (keep TARGET)
  - Works for ANY composite change (universal rule)
  - Applies to High Importance rows only
- **Low Importance**: Preserves TARGET data for existing rows
- **SequenceName Changes**: Detected via 10-key pattern matching

**Sheets Output**:
- Main Sheet (High): All high-importance updates
- Low Importance: All low-importance updates (currently: same as High logic)
- Deleted Rows: Missing from SOURCE (3-key validation)
- Update History: Auto-generated tracking
- Summary Report: Statistics and change counts

---

## Data Structure

### Key Columns:
- **SequenceName**: Scene/sequence identifier
- **EventName**: Event identifier within sequence
- **StrOrigin**: Original Korean text (primary content)
- **Desc**: Description/context
- **StartFrame/EndFrame**: Timing information
- **Text**: Translated text (language-specific)
- **STATUS**: Recording status
- **FREEMEMO**: Free-form notes
- **CharacterKey**: Character identifier
- **CharacterName**: Character display name
- **DialogVoice**: Voice actor/type
- **CastingKey**: Auto-generated key for tracking
- **PreviousData**: Historical StrOrigin tracking
- **Mainline Translation**: Reference translation
- **CHANGES**: Auto-generated change classification
- **Importance**: High/Low priority flag

### Auto-Generated Columns:
- **CastingKey**: `{CharacterKey}_{DialogVoice}_{Speaker|CharacterGroupKey}_{DialogType}`
- **PreviousData**: Previous StrOrigin + STATUS + FREEMEMO (when changed)
- **CHANGES**: Change classification from comparison logic
- **UpdateTime**: Timestamp of processing

---

## Update History Tracking

The tool maintains 3 separate JSON history files:
- `working_update_history.json`: Working Process history
- `alllang_update_history.json`: All Language Process history
- `master_update_history.json`: Master File Update history

Each record contains:
- Timestamp
- Process type
- Input/output files
- Statistics (total rows, change counts)

History is viewable via "📊 View Update History" button in GUI.

---

## Color Coding

Output Excel files use color coding in CHANGES column:
- **Green (#90EE90)**: New Row
- **Yellow (#FFD700)**: StrOrigin Change / SequenceName Change
- **Orange (#FFA500)**: TimeFrame Change
- **Pink (#FFB6C1)**: EventName Change
- **Purple (#DDA0DD)**: Desc Change
- **Cyan (#ADD8E6)**: Combined changes
- **Red (#FF6B6B)**: Deleted Rows

---

## File Naming Convention

Output files follow this pattern:
```
{ProcessType}_{YYYYMMDD_HHMMSS}.xlsx
```

Examples:
- `RawVRS_20241114_143022.xlsx`
- `WorkingVRS_20241114_143145.xlsx`
- `AllLanguageVRS_20241114_143301.xlsx`
- `MasterFile_Updated_20241114_143455.xlsx`

---

## Technical Details

- **Language**: Python 3
- **GUI Framework**: Tkinter
- **Excel Library**: pandas + openpyxl
- **Data Processing**: pandas DataFrames
- **File Format**: Excel (.xlsx, .xlsm, .xls)
- **Encoding**: UTF-8 for all text
- **Threading**: Background processing for UI responsiveness

---

## Repository Information

**Branch**: `main` (REQUIRED - always work on main branch)
**Remote**: `git@github.com:NeilVibe/VRS-Manager.git`
**Status**: Phase 2 Complete - Modular Architecture
**Date**: November 15, 2024

**IMPORTANT**: All development must be done on the `main` branch.

## Current Version

**Version**: 1118.6 (Simplified Master File Update + TimeFrame Preservation - Production Ready)

## Architecture Overview

The VRS Manager has been **fully refactored** from a 2,732-line monolith into a clean, modular architecture:

### Project Structure (Phase 2 Complete ✅)

```
vrs-manager/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # User documentation
├── claude.md                        # This file (AI reference)
├── roadmap.md                       # Development roadmap
│
├── src/                             # Modular source code (31 files)
│   ├── config.py                    # Configuration constants
│   │
│   ├── processors/                  # Process orchestrators (5 files)
│   │   ├── base_processor.py        # Abstract base class
│   │   ├── raw_processor.py         # Raw VRS Check
│   │   ├── working_processor.py     # Working VRS Check
│   │   ├── alllang_processor.py     # All Language Check
│   │   └── master_processor.py      # Master File Update
│   │
│   ├── core/                        # Business logic (8 files)
│   │   ├── casting.py               # CastingKey generation
│   │   ├── lookups.py               # 4-tier lookup building
│   │   ├── comparison.py            # Change detection
│   │   ├── import_logic.py          # Data import rules
│   │   ├── working_comparison.py    # Working process logic
│   │   ├── working_helpers.py       # Working helpers
│   │   └── alllang_helpers.py       # All Language helpers
│   │
│   ├── io/                          # File operations (4 files)
│   │   ├── excel_reader.py          # Excel reading
│   │   ├── excel_writer.py          # Excel writing
│   │   ├── formatters.py            # Cell formatting
│   │   └── summary.py               # Summary sheets
│   │
│   ├── history/                     # Update history (1 file)
│   │   └── history_manager.py       # History tracking
│   │
│   ├── ui/                          # User interface (2 files)
│   │   ├── main_window.py           # Main GUI window
│   │   └── history_viewer.py        # History viewer dialog
│   │
│   └── utils/                       # Utilities (3 files)
│       ├── helpers.py               # Helper functions
│       ├── progress.py              # Progress indicators
│       └── data_processing.py       # Data processing utils
│
├── tests/                           # Unit tests (future expansion)
├── docs/                            # Documentation
├── ARCHIVE/                         # Old versions (v1114, v1114v2)
└── original_monolith/              # Reference (vrsmanager1114v3.py)
```

### Architecture Benefits

| Aspect | Monolith | Modular (Current) |
|--------|----------|-------------------|
| **File Structure** | 1 file, 2,732 lines | 31 files, ~4,400 lines |
| **Largest File** | 2,732 lines | <500 lines each |
| **Testability** | Cannot unit test | Fully unit-testable |
| **Maintainability** | Hard to navigate | Clear module boundaries |
| **Extensibility** | Edit monolith | Add new processor class |
| **Code Reuse** | Lots of duplication | Shared base + utilities |
| **IDE Support** | Limited | Full autocomplete |
| **Collaboration** | Merge conflicts | Independent modules |

**v1117.1 Features** (CURRENT - TimeFrame+StrOrigin Logic + Column Robustness):
- ✅ **Column Robustness** - Handles files with different column structures gracefully (v1117.1)
  - Only compares columns that exist in BOTH files
  - No crashes when optional columns missing (Desc, TimeFrame, Text, etc.)
  - Requires only CORE keys: SequenceName, EventName, StrOrigin, CastingKey components
- ✅ **TimeFrame Preservation Logic** - Preserve TARGET timeframes when StrOrigin unchanged (High Importance only)
- ✅ **Universal Rule**: If StrOrigin NOT part of changes → Preserve TimeFrame (keep TARGET)
- ✅ **TWO-PASS Algorithm** - Eliminates 1-to-many matching issues
- ✅ **10-Key Pattern Matching** - Ultra-precise change detection
- ✅ **100% Correct Duplicate Handling** - StrOrigin, CastingKey, blank cells
- ✅ **Mathematically Correct Row Counting** - `new - deleted = actual_diff`
- ✅ **Modular Architecture** - 31 Python files, clean separation of concerns
- ✅ **Comprehensive Test Suite** - Full duplicate handling validation
- ✅ **Identical Detection Logic** - All 4 processors use same algorithm
- ✅ **5 Processor Classes** (Base + 4 implementations)
- ✅ **Template Method Pattern** for consistent workflow
- ✅ **Fully unit-testable** components
- ✅ Multi-language support (KR/EN/CN)
- ✅ Master File LOW importance logic fix
- ✅ Update history tracking
- ✅ Intelligent import logic
- ✅ Color-coded change visualization
- ✅ Word count statistics
- ✅ **Production-ready** and easy to extend

**v1116 Features** (Previous - TWO-PASS):
- ✅ TWO-PASS Algorithm implementation
- ✅ 10-Key Pattern Matching
- ✅ All features from v1114v3 plus duplicate handling

**v1114v2 Features** (Previous Stable):
- 3-Key System (SequenceName + EventName + StrOrigin)
- SequenceName Change Detection
- Master File LOW importance logic fix
- Multi-language support (KR/EN/CN)
- Update history tracking
- Intelligent import logic
- Color-coded change visualization
- Word count statistics

**Migration from v1114v2 to v1114v3:**
- No data migration required
- Backward compatible with v1114v2 output files
- All processes enhanced with 4-tier key system
- Improved accuracy for duplicate dialogue detection
- **Fully refactored** from monolith to modular architecture
- Original monolith preserved in `original_monolith/vrsmanager1114v3.py`

## Running the Application

### Quick Start
```bash
# Navigate to project directory
cd /home/neil1988/vrsmanager

# Run the application
python main.py
```

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Syntax validation
python3 -m py_compile main.py
python3 -m py_compile src/processors/*.py

# Future: Run unit tests
pytest tests/
```

## Module Reference

### Processors (`src/processors/`)
- **BaseProcessor**: Abstract base class with template method pattern
- **RawProcessor**: Raw VRS Check (PREVIOUS ↔ CURRENT comparison)
- **WorkingProcessor**: Working VRS Check (import with smart logic)
- **AllLangProcessor**: All Language Check (tri-lingual merge)
- **MasterProcessor**: Master File Update (3-key copy-paste)

### Core Logic (`src/core/`)
- **casting.py**: CastingKey and PreviousData generation
- **lookups.py**: 4-tier lookup dictionary building
- **comparison.py**: Row comparison and change classification
- **import_logic.py**: Data import rules (status-aware, change-type specific)
- **working_comparison.py**: Working process comparison orchestration
- **working_helpers.py**: Working process utility functions
- **alllang_helpers.py**: All Language process helpers (file detection, merge, comparison)

### I/O Operations (`src/io/`)
- **excel_reader.py**: Safe Excel reading with normalization
- **excel_writer.py**: Column filtering for output
- **formatters.py**: Cell coloring and formatting (17 change types, 25+ statuses)
- **summary.py**: Summary sheet generation with statistics

### UI Components (`src/ui/`)
- **main_window.py**: Main application window with 4 process buttons
- **history_viewer.py**: Update history viewer with rich formatting

### Utilities (`src/utils/`)
- **helpers.py**: Common helper functions (log, safe_str, contains_korean, etc.)
- **progress.py**: Progress bar utilities for long operations
- **data_processing.py**: Data normalization and cleaning

### Configuration (`src/config.py`)
- All column name constants (COL_SEQUENCE, COL_EVENTNAME, etc.)
- Status categories (AFTER_RECORDING_STATUSES, PRE_RECORDING_STATUSES)
- Output column orders (OUTPUT_COLUMNS, OUTPUT_COLUMNS_RAW, OUTPUT_COLUMNS_MASTER)
- File naming patterns

## Development Workflow

### Adding a New Processor
1. Create new class in `src/processors/` extending `BaseProcessor`
2. Implement required abstract methods:
   - `get_process_name()`
   - `select_files()`
   - `read_files()`
   - `process_data()`
   - `write_output()`
3. Add button in `src/ui/main_window.py`
4. Update `src/processors/__init__.py`

### Adding New Core Logic
1. Create new module in appropriate directory (`src/core/`, `src/io/`, etc.)
2. Add functions with clear docstrings
3. Export from `__init__.py`
4. Use in processor classes

### Testing
- All modules compile successfully with `python3 -m py_compile`
- Unit tests planned for `tests/` directory
- Integration testing with real VRS data recommended
