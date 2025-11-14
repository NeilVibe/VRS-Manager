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
- Unique per character within a sequence
- Differentiates speakers even with identical dialogue
- Critical for handling common dialogue phrases

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

## Current Version

**Version**: 1114v2 (Stable) / 1114v3 (In Development)

**v1114v2 Features**:
- 3-Key System (SequenceName + EventName + StrOrigin)
- SequenceName Change Detection
- Master File LOW importance logic fix
- Multi-language support (KR/EN/CN)
- Update history tracking
- Intelligent import logic
- Color-coded change visualization
- Word count statistics

**v1114v3 (Planned)**:
- 4-Tier Key System (adds CastingKey + SequenceName)
- Duplicate StrOrigin handling for common phrases
- Enhanced NEW/DELETED row detection
- Character Change detection
- All features from v1114v2
