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

### 1. **Quadruple-Key Validation System (4-Tier)**
The tool uses a 4-key matching system for robust change detection:

```
Key 1 (CW): (SequenceName, EventName)
Key 2 (CG): (SequenceName, StrOrigin)
Key 3 (ES): (EventName, StrOrigin)
Key 4 (CS): (CastingKey, SequenceName)
```

**Why 4 keys?**
- **Key 1**: Handles direct matches (same sequence + event)
- **Key 2**: Catches EventName changes (same sequence + dialogue)
- **Key 3**: Catches SequenceName changes (same event + dialogue)
- **Key 4**: Prevents duplicate StrOrigin false matches (unique character identification)
- Prevents false positives when common phrases appear across multiple characters
- Example: "안녕하세요" (Hello) spoken by 100 different characters

**NEW ROW Detection**: ALL 4 keys missing from TARGET
**DELETED ROW Detection**: ALL 4 keys missing from SOURCE

**Why CastingKey?**
- CastingKey = `{CharacterKey}_{DialogVoice}_{GroupKey}_{DialogType}`
- **Unique per character** within a sequence
- Differentiates speakers even with identical dialogue
- Critical for handling common dialogue phrases
- **Purpose**: Verification helper for Key 2 (not a standalone identifier)

**Staged Matching Logic (4-Tier System):**

The system uses a cascading match strategy:

```
Stage 1: Direct match (Key 1)
  ↓ If match → Compare fields for changes
  ↓ If no match → Continue to Stage 2

Stage 2: StrOrigin+Sequence match (Key 2) → VERIFY with Key 4
  ↓ If Key 2 matches AND Key 4 matches:
      → Same character → EventName Change
  ↓ If Key 2 matches BUT Key 4 doesn't match:
      → Different character → New Row (duplicate StrOrigin case)
  ↓ If Key 2 doesn't match → Continue to Stage 3

Stage 3: EventName+StrOrigin match (Key 3)
  ↓ If match → SequenceName Change
  ↓ If no match → Continue to Stage 4

Stage 4: No keys match
  → New Row
```

**Critical Innovation - Stage 2 Verification:**

The 4th key (CastingKey + SequenceName) is used exclusively in Stage 2 to verify character identity:

- **Scenario**: 100 different characters all say "안녕하세요" (Hello) in the same scene
- **Without Key 4** (v1114v2): All marked as "EventName Change" ❌
- **With Key 4** (v1114v3): Correctly marked as "New Row" ✅

**Example:**
```
PREVIOUS:
  Row A: Seq="Scene1", Event="E123", StrOrigin="Hello", CastingKey="Hero_Male_A"

CURRENT:
  Row B: Seq="Scene1", Event="E456", StrOrigin="Hello", CastingKey="NPC_Female_B"

Matching Process:
  Stage 1: Key1 (Scene1, E123) vs (Scene1, E456) → NO MATCH
  Stage 2: Key2 (Scene1, Hello) → MATCH!
           Key4 (Hero_Male_A, Scene1) vs (NPC_Female_B, Scene1) → NO MATCH
           → Different character → NEW ROW ✅
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
**Purpose**: Update Master File with Working Process output using 3-Key Copy-Paste

**Input**:
- SOURCE: Working Process output file (new updates)
- TARGET: Master File (existing master data to update)

**Output**:
- Updated Master File with:
  - Main Sheet (High): All high-importance rows
  - Low Importance: All low-importance rows
  - Deleted Rows: Rows removed from SOURCE (3-key validated)

**Process Logic**:

#### Current Behavior:
1. **Separate by Importance**: Split SOURCE into High/Low
2. **Build 3-Key Lookups**: Create lookups for SOURCE High/Low + TARGET
3. **Match & Classify**: Use 3-key system to determine change type
4. **Copy Data**: Copy SOURCE data to output with change classification
5. **Handle Deletions**: Find rows in TARGET missing from all SOURCE keys

#### Special Handling:
- **TimeFrame Changes**: Preserve TARGET timeframes (StartFrame, EndFrame)
- **EventName+TimeFrame Changes**: Preserve TARGET timeframes
- **SequenceName Changes**: Detected via 3rd key (ES)

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

**Branch**: `vrs-manager-dev` (active development)
**Remote**: `git@github.com:NeilVibe/VRS-Manager.git`
**Status**: Phase 2 Complete - Modular Architecture
**Date**: November 15, 2024

## Current Version

**Version**: 1114v3 (Modular Architecture - Production Ready)

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

**v1114v3 Features** (CURRENT - MODULAR):
- ✅ **Modular Architecture** - 31 Python files, clean separation of concerns
- ✅ **4-Tier Key System** (CW, CG, ES, CS)
- ✅ **Stage 2 Verification** with Key 4 (CastingKey-based)
- ✅ **Duplicate StrOrigin handling** for common phrases
- ✅ **Enhanced NEW/DELETED row detection** (all 4 keys)
- ✅ **Character identity verification** in all processes
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
