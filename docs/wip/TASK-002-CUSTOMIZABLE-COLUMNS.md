# TASK-002: Customizable Output Columns + HasAudio

**Created:** 2025-12-22 | **Status:** COMPLETE | **Priority:** High
**Completed:** 2025-12-24

---

## Summary

Two requests from colleague:
1. Add `HasAudio` column to WORK output (next to Mainline Translation)
2. Allow users to customize which optional columns appear in output

**Scope:** MAIN TAB only (within WORKING processor). Other tabs in WORKING processor not affected.

---

## V5 IMPLEMENTATION (COMPLETE - 2025-12-24)

### What Was Implemented

1. **Backend: KEY-based PREVIOUS Column Extraction** ✅
   - `src/core/working_comparison.py`: Added V5 PREVIOUS column extraction
   - Uses existing 10-KEY matching system (SequenceName+EventName+StrOrigin+CastingKey)
   - For each CURRENT row, extracts selected columns from matched PREVIOUS row
   - New rows (no KEY match) get empty PREVIOUS values

2. **Data Processing: V5 Column Filtering** ✅
   - `src/utils/data_processing.py`: Updated `filter_output_columns()`
   - Includes V5 auto-generated, current, and previous columns in output

3. **UI: Dual File Upload** ✅ (Already existed)
   - `src/ui/main_window.py`: V5 dual upload boxes
   - CURRENT file box (green) and PREVIOUS file box (blue)
   - Previous_ prefix added to PREVIOUS columns in display

4. **Settings: V5 Schema** ✅ (Already existed)
   - `src/settings.py`: V5 functions
   - `get_v5_column_settings()`, `set_v5_current_file()`, `set_v5_previous_file()`
   - `get_v5_enabled_columns()` returns Previous_ prefixed columns

5. **Tests: V5 Test Suite** ✅
   - `tests/test_column_classification.py`: 6 new V5 tests (21 total)
   - All tests pass

### Key Technical Details

```python
# In working_comparison.py:
# Get V5 settings once (outside loop for performance)
v5_cols = get_v5_enabled_columns()
selected_previous_cols = v5_cols.get("previous", [])  # e.g., ["Previous_FREEMEMO"]

# For each row in the processing loop:
for prefixed_col in selected_previous_cols:
    if prefixed_col.startswith("Previous_"):
        original_col = prefixed_col[9:]  # "FREEMEMO"
        if prev_row_dict and change_type != "New Row":
            # KEY-matched: extract from matched PREVIOUS row
            curr_dict[prefixed_col] = safe_str(prev_row_dict.get(original_col, ""))
        else:
            curr_dict[prefixed_col] = ""  # New Row - no match
```

### V5 UI Design

```
┌────────────────────────────────────────────────────────────────────────────┐
│ COLUMN SETTINGS                                               [X]          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│ FIXED COLUMNS (Always Included)                                            │
│ ┌────────────────────────────────────────────────────────────────────────┐ │
│ │ ✓ MANDATORY (10): SequenceName, EventName, StrOrigin, CharacterKey... │ │
│ │ ✓ VRS CONDITIONAL (10): Desc, DialogType, Group, StartFrame...        │ │
│ └────────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│ AUTO-GENERATED (Toggle ON/OFF)                                             │
│ ☑ PreviousData  ☑ PreviousText  ☑ DETAILED_CHANGES  ☐ Mainline...        │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│ OPTIONAL COLUMNS                                          [RESET ALL]      │
│                                                                            │
│  ┌─── FROM CURRENT FILE ───────┐    ┌─── FROM PREVIOUS FILE ──────┐       │
│  │ myfile_v2.xlsx ✓            │    │ myfile_v1.xlsx ✓            │       │
│  │                             │    │                             │       │
│  │ ☑ FREEMEMO                  │    │ ☐ Previous_FREEMEMO         │       │
│  │ ☑ HasAudio                  │    │ ☐ Previous_HasAudio         │       │
│  │ ☐ Record                    │    │ ☐ Previous_Record           │       │
│  │                             │    │                             │       │
│  │ [Upload] [All] [None]       │    │ [Upload] [All] [None]       │       │
│  └─────────────────────────────┘    └─────────────────────────────┘       │
│                                                                            │
│ ℹ️ PREVIOUS columns matched by KEY (Seq+Event+StrOrigin+CastingKey).       │
│   New Rows will have empty PREVIOUS values.                                │
│                                                                            │
│                                              [Back]    [Save]              │
└────────────────────────────────────────────────────────────────────────────┘
```

### V5 Key Features

| Feature | Description |
|---------|-------------|
| **Dual upload** | Separate CURRENT and PREVIOUS file upload buttons |
| **Empty by default** | No example/hardcoded columns - boxes empty until file uploaded |
| **Auto-prefix** | PREVIOUS columns automatically get "Previous_" prefix |
| **Single RESET** | One button clears both uploads and all selections |
| **Compact FIXED** | MANDATORY + VRS_CONDITIONAL condensed to 2 lines |
| **KEY-based matching** | PREVIOUS columns pulled from matched row, not by index |
| **Clear visual separation** | Two distinct boxes for CURRENT vs PREVIOUS |

### Implementation Tasks

1. [x] Update UI with dual upload boxes (empty by default)
2. [x] Add RESET ALL button
3. [x] Compact the FIXED columns section
4. [x] Implement PREVIOUS column extraction during processing
5. [x] Add "Previous_" prefix to PREVIOUS columns in output
6. [x] Update settings save/load for V5 schema
7. [x] Add tests for KEY-based PREVIOUS column matching

---

## V5 UI FIXES (2025-12-24)

### All 6 Issues Fixed

| Issue | Problem | Fix |
|-------|---------|-----|
| **V5-001** | FIXED columns truncated ("...10 total") | Show full comma-separated list with text wrapping |
| **V5-002** | PREVIOUS checkboxes showed "Previous_FREEMEMO" | Removed prefix - user sees original column name |
| **V5-003** | Info text "New Rows..." unclear | Clarified: "Rows that only exist in CURRENT..." |
| **V5-004** | Previous_ prefix on ALL PREVIOUS columns | Only add prefix on CONFLICT (same column in both files) |
| **V5-005** | Dialog too small, buttons compressed | Increased to 950x850 / minsize 850x750 |
| **V5-006** | Upload freezes UI | Threading + progress feedback |

### Key Code Changes

```python
# Fix 1: Full column list (main_window.py)
mandatory_text = ", ".join(MANDATORY_COLUMNS)  # Was [:4] + "..."

# Fix 2: No prefix in checkbox (main_window.py)
text=col,  # Was f"Previous_{col}"

# Fix 4: Prefix only on CONFLICT (settings.py)
for col in selected_previous:
    if col in enabled_current:
        enabled_previous.append(f"Previous_{col}")  # CONFLICT
    else:
        enabled_previous.append(col)  # NO CONFLICT

# Fix 5: Larger dialog (main_window.py)
dialog.geometry("950x850")
dialog.minsize(850, 750)

# Fix 6: Threaded upload (main_window.py)
def upload_current_file():
    current_status.config(text=f"⏳ Analyzing {filename}...", fg="#FF9800")
    thread = threading.Thread(target=analyze_in_thread, daemon=True)
    thread.start()
```

### Column Selection Persistence
- Settings saved to `~/.vrsmanager_settings.json`
- Analyzed file is for DISCOVERY only
- Settings apply to ALL future WORKING processor runs
- RESET ALL + REUPLOAD to change configuration

---

## V4 IMPLEMENTATION COMPLETE (2025-12-23)

### 4-Tier Column Classification System

| Category | Count | Behavior |
|----------|-------|----------|
| **MANDATORY** | 10 | Always included, cannot disable |
| **VRS_CONDITIONAL** | 10 | Used in change detection, always from CURRENT |
| **AUTO_GENERATED** | 6 | Created by VRS logic, toggleable |
| **OPTIONAL** | 7 | Extra metadata only, toggleable |

### Key Changes
- Removed dual-file upload (columns now predefined)
- Column Settings dialog: 1000x900, spacious 4-section layout
- Priority Mode dialog: 600x550 (Back/Save visible)
- VRS logic columns (Group, Desc, Age, etc.) now VRS_CONDITIONAL, not optional
- 15 new tests for column classification

### Files Modified
```
src/config.py                # VRS_CONDITIONAL_COLUMNS added
src/settings.py              # get_vrs_conditional_columns()
src/ui/main_window.py        # 4-section dialog
src/utils/data_processing.py # Always include VRS_CONDITIONAL
tests/test_column_classification.py  # 15 new tests
```

### Build Status
✅ V4 Column Classification System - Success (2m24s)

---

## V2 IMPLEMENTATION - UI FIX NEEDED (2025-12-23)

### What Was Built
1. **Nested Settings UI** - Settings → Priority Mode / Column Settings
2. **File Analysis** - Upload Excel, extract columns automatically
3. **Dynamic Selection** - Only columns from analyzed file shown
4. **Graceful Fallback** - Missing columns skipped without error
5. **Bug Fix** - V1 defaults no longer pollute V2 settings

### Files Modified
```
src/settings.py              # V2 functions + load_settings() fix
src/ui/main_window.py        # show_settings_dialog(), show_column_settings_dialog_v2()
src/utils/data_processing.py # filter_output_columns() V2 logic
```

### Tests
- All 518 tests pass
- V2 logic verified: analysis, selection, filtering all work

---

## V2.1 FIXES IMPLEMENTED (2025-12-23)

All issues fixed:
- **Dialog size**: 700x750 → 880x800
- **Resizable**: Now `resizable(True, True)` with `minsize(800, 600)`
- **Threading**: File analysis runs in background thread
- **Console logging**: Added via `log()` function
- **Shortened help text**: Prevents cut-off
- **Dynamic scrolling**: Canvas width adjusts with window

---

## V2.1 Issues (RESOLVED)

### Problem 1: Text Cut-Off on Windows
1. **Green button cut off** - Only shows "Oly and Sa" (should be "Apply & Save")
2. **Auto-generated help text cut off:**
   - "Combined previous tet..." → should show full text
   - "Text from matched preivou..." → cut off
   - "Previous EventName when..." → cut off
   - "Full composite change type..." → cut off
   - "StrOrigin from previous ro..." → cut off

**Root Cause:** Window width (700px) not enough for help text + checkbox layout on Windows.

**Fix Options:**
1. Increase dialog width to 850-900px
2. Wrap help text to multiple lines
3. Use tooltip (hover) instead of inline text

### Problem 2: GUI Freeze During File Upload
When user uploads Excel file for analysis:
- **GUI freezes** completely
- **No threading** - blocks main thread
- **No progress tracking** in console or UI
- Bad UX - user thinks app crashed

**Fix Required:**
1. Move `analyze_excel_columns()` to background thread
2. Add progress indicator (spinner or progress bar)
3. Console logging: "Analyzing file...", "Found X columns"
4. Disable Upload button during analysis
5. Show "Analyzing..." status in dialog

### Problem 3: No Console Feedback
- File analysis happens silently
- No logging to console
- User has no idea what's happening

**Fix Required:**
Add logging:
```python
log("Analyzing file: {filename}")
log("Found {n} columns")
log("Optional columns: {list}")
```

### Problem 4: Optional Columns Not All Visible
After file analysis:
- Shows "14 columns found" but only 10 visible
- No scrolling in optional columns section
- Grid cuts off remaining columns

**Fix Required:**
1. Add scrollbar to optional columns grid
2. Or increase window height dynamically
3. Show column count: "Showing X of Y columns"

### Problem 5: Window Not Adaptive
- Fixed 700x750 size not enough
- Not resizable (or poorly resizable)
- Content gets clipped on smaller screens

**Fix Required:**
1. Make dialog resizable: `dialog.resizable(True, True)`
2. Set minimum size: `dialog.minsize(700, 600)`
3. Use grid weights for proper expansion
4. Canvas should expand with window

---

## Automated Testing Plan

### Constraint: Tkinter ≠ Electron
VRS Manager uses **tkinter** (native Python GUI), NOT Electron.
- CDP (Chrome DevTools Protocol) does NOT work with tkinter
- Node.js injection does NOT work
- Need different testing approach

### Options for Tkinter Testing

| Option | Pros | Cons |
|--------|------|------|
| **pyautogui** | Cross-platform, screenshots + clicks | Needs display, slower |
| **Self-test mode** | Built-in, reliable | Needs code changes |
| **PowerShell** | Native Windows, no deps | Windows only |

### Recommended: Self-Test Mode
Add `--screenshot-test` flag to VRS Manager:
```bash
VRSManager.exe --screenshot-test
```

This mode:
1. Opens main window
2. Opens Settings dialog
3. Takes screenshot → `screenshots/01_settings.png`
4. Opens Column Settings
5. Takes screenshot → `screenshots/02_column_settings.png`
6. Loads test Excel file
7. Takes screenshot → `screenshots/03_columns_analyzed.png`
8. Exits with report

### Playground Path (Created)
```
Windows: C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject\Playground\VRSManager
WSL:     /mnt/c/NEIL_PROJECTS_WINDOWSBUILD/VRSManagerProject/Playground/VRSManager
```

### Testing Toolkit Created

```
testing_toolkit/
├── VRS_MANAGER_TEST_PROTOCOL.md    # Full testing protocol
├── requirements.txt                 # pyautogui, pillow, pygetwindow
├── scripts/
│   ├── launch_and_test.py          # Main test runner
│   ├── playground_install.ps1      # PowerShell installer
│   └── playground_install.sh       # WSL wrapper
└── screenshots/                     # Test output
```

### Running Tests

**From Windows PowerShell:**
```powershell
cd C:\NEIL_PROJECTS_WINDOWSBUILD\VRSManagerProject
pip install pyautogui pillow pygetwindow
python testing_toolkit\scripts\launch_and_test.py
```

**From WSL:**
```bash
cd /home/neil1988/vrsmanager
./testing_toolkit/scripts/playground_install.sh --test
```

### Test Cases Covered
- TC-001: Main Window Loads
- TC-002: Settings Dialog Opens
- TC-003: Column Settings Opens
- TC-004: Button Text Visibility
- TC-005: Help Text Visibility

---

## V2 Design (Reference)

### Problems with V1 (Fixed)

1. **Settings window too small** - Fixed: 700x750
2. **Hardcoded column list** - Fixed: file analysis
3. **CURRENT/PREVIOUS selector is pointless** - Fixed: removed
4. **Not nested** - Fixed: Settings → submenu

### Code Review Findings

#### Columns with FIXED source (always from PREVIOUS):
```python
# import_logic.py line 32-33
FREEMEMO  → ALWAYS from PREVIOUS (unconditional)
Text      → Conditionally from PREVIOUS (based on change type + status)
Desc      → Conditionally from PREVIOUS
STATUS    → Conditionally from PREVIOUS
```

#### Columns that are AUTO-GENERATED (not from files):
```
PreviousData        → Generated: PREV Text|STATUS|FREEMEMO
PreviousText        → From matched PREVIOUS row
PreviousEventName   → From matched PREVIOUS row (only when EventName changed)
DETAILED_CHANGES    → Generated by change detection
CHANGES             → Generated from change detection
Mainline Translation → Saved from CURRENT before import
CastingKey          → Generated from components
Previous StrOrigin  → From matched PREVIOUS row
```

#### Pass-through columns (from CURRENT as-is unless import logic overwrites):
```
HasAudio, UseSubtitle, Record, isNew
Tribe, Age, Gender, Job, Region
DialogType, Group, StartFrame, EndFrame
SubTimelineName, UpdateTime, etc.
```

### V2 Design Requirements

1. **Nested Settings UI**
   ```
   [Settings Button] → Opens Settings Modal
       ├── Priority Change Mode → Opens Priority Settings
       └── Column Settings → Opens Column Settings Modal
   ```

2. **File Upload Approach**
   - Upload PREVIOUS or CURRENT file button
   - Analyze first sheet automatically
   - Show clean list of ALL columns found in file
   - Let user select which columns to include in output

3. **Smarter Column Classification**
   - **MANDATORY** (cannot disable): Key columns for matching
   - **AUTO-GENERATED** (toggle): Generated by VRS logic
   - **PASS-THROUGH** (from analysis): Columns from source files
   - Remove CURRENT/PREVIOUS selector (pointless - logic decides source)

4. **Robust Fallback**
   - If selected column not in processed file → skip gracefully
   - Log which columns were requested but missing
   - Don't crash, just omit the column

5. **Bigger Window**
   - Increase dialog size
   - Better layout for many columns
   - Scrollable area for long lists

---

## V2 UI Mockup (Approved)

### Main Settings Modal (nested)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ VRS Manager Settings                                             [X] Close │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────┐                                │   │
│  │  │  🔄 Priority Change Mode            │  ← Click to expand             │   │
│  │  │                                     │                                │   │
│  │  │  Currently: ON (Priority Labels)   │                                │   │
│  │  └─────────────────────────────────────┘                                │   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────┐                                │   │
│  │  │  📋 Column Settings                 │  ← Click to expand             │   │
│  │  │                                     │                                │   │
│  │  │  Configure output columns           │                                │   │
│  │  └─────────────────────────────────────┘                                │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│                                              [Close]                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Column Settings Modal (from file analysis)

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│  📋 Column Settings                                                       [X] Close │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─ STEP 1: Analyze Source File ────────────────────────────────────────────────┐   │
│  │                                                                               │   │
│  │   [📂 Upload PREVIOUS or CURRENT Excel File]                                  │   │
│  │                                                                               │   │
│  │   Status: ✅ Analyzed: "MyFile_v2.xlsx" (47 columns found)                    │   │
│  │                                                                               │   │
│  └───────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  ┌─ MANDATORY COLUMNS (Always Included - Cannot Disable) ───────────────────────┐   │
│  │                                                                               │   │
│  │   🔒 SequenceName   🔒 EventName   🔒 StrOrigin   🔒 CharacterKey             │   │
│  │   🔒 CharacterName  🔒 CastingKey  🔒 DialogVoice 🔒 Text                     │   │
│  │   🔒 STATUS         🔒 CHANGES                                                │   │
│  │                                                                               │   │
│  └───────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  ┌─ AUTO-GENERATED COLUMNS (Created by VRS Logic) ──────────────────────────────┐   │
│  │                                                                               │   │
│  │   [✓] PreviousData          ⓘ Combined prev Text|STATUS|Freememo             │   │
│  │   [✓] PreviousText          ⓘ Text from matched previous row                 │   │
│  │   [✓] PreviousEventName     ⓘ Previous EventName when changed                │   │
│  │   [✓] DETAILED_CHANGES      ⓘ Full composite change type                     │   │
│  │   [✓] Previous StrOrigin    ⓘ StrOrigin from matched previous row            │   │
│  │   [✓] Mainline Translation  ⓘ Original Text before import                    │   │
│  │                                                                               │   │
│  └───────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  ┌─ OPTIONAL COLUMNS (From Analyzed File) ──────────────────────────────────────┐   │
│  │                                                                               │   │
│  │   [Select All] [Deselect All]                                                 │   │
│  │   ─────────────────────────────────────────────────────────────────────────   │   │
│  │                                                                               │   │
│  │   [✓] Desc              [✓] FREEMEMO         [✓] SubTimelineName             │   │
│  │   [✓] StartFrame        [✓] EndFrame         [✓] DialogType                  │   │
│  │   [✓] Group             [✓] UpdateTime       [✓] Tribe                       │   │
│  │   [✓] Age               [✓] Gender           [✓] Job                         │   │
│  │   [✓] Region            [✓] HasAudio         [✓] UseSubtitle                 │   │
│  │   [✓] Record            [✓] isNew            [ ] CustomColumn1               │   │
│  │   [ ] CustomColumn2     [ ] CustomColumn3    [ ] AnotherColumn               │   │
│  │                                                                               │   │
│  │   ℹ️  Columns shown are from analyzed file. If a selected column is not      │   │
│  │       present in processed files, it will be skipped gracefully.             │   │
│  │                                                                               │   │
│  └───────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │  [Reset to Defaults]                           [Cancel]    [Apply & Save]    │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Priority Change Mode Modal

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🔄 Priority Change Mode                                             [X] Close │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                                                                         │   │
│   │   [✓] Use Priority Change Mode                                          │   │
│   │                                                                         │   │
│   │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │   │ ✅ ON:  CHANGES shows priority-based label (recommended)        │   │   │
│   │   │         Example: "StrOrigin Change" instead of full composite   │   │   │
│   │   └─────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                         │   │
│   │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │   │ ⚪ OFF: CHANGES shows full composite label (legacy)              │   │   │
│   │   │         Example: "StrOrigin+EventName+TimeFrame Change"         │   │   │
│   │   └─────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                         │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│                                              [Cancel]    [Save]                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### V2 vs V1 Comparison

| Feature | V1 | V2 |
|---------|----|----|
| **Settings structure** | Separate buttons | Nested (Settings → submenu) |
| **Column list** | Hardcoded | From file analysis |
| **Source selector** | CURRENT/PREVIOUS | Removed (logic decides) |
| **Window size** | 550x700 (too small) | 700x800 (bigger) |
| **File upload** | None | Analyze any Excel file |
| **Fallback** | None | Skip missing columns gracefully |
| **Select All/Deselect All** | None | Added for optional columns |

---

## Column Classification

### MANDATORY Columns (Always Present - Cannot Disable)

These are required for VRS logic to function:

| Column | Purpose |
|--------|---------|
| SequenceName | Row identification key |
| EventName | Row identification key |
| StrOrigin | Row identification key |
| CharacterKey | Character identification |
| CharacterName | Character display name |
| CastingKey | Matching key (auto-generated) |
| DialogVoice | Voice assignment |
| Text | Core content |
| STATUS | Status tracking |
| CHANGES | Change detection result |

### AUTO-GENERATED Columns (VRS Logic Creates These)

User can choose to INCLUDE or EXCLUDE these:

| Column | Description | When Generated |
|--------|-------------|----------------|
| `PreviousData` | Previous Text/Status/Freememo combined | When row matched to previous |
| `PreviousText` | Previous row's Text value | When matched (not New Row) |
| `PreviousEventName` | Previous EventName | Only when EventName changed |
| `DETAILED_CHANGES` | Full composite change type | Always (from detection) |
| `Previous StrOrigin` | Previous row's StrOrigin | When matched |
| `Mainline Translation` | Current Text before import | Always |

### OPTIONAL Columns (From Source Files)

User can choose which to include. Source: CURRENT or PREVIOUS file.

| Column | Default | Source | Notes |
|--------|---------|--------|-------|
| `Desc` | ON | CURRENT/PREVIOUS | Description field |
| `FREEMEMO` | ON | CURRENT/PREVIOUS | Free memo field |
| `SubTimelineName` | ON | CURRENT/PREVIOUS | Timeline info |
| `StartFrame` | ON | CURRENT/PREVIOUS | Frame data |
| `EndFrame` | ON | CURRENT/PREVIOUS | Frame data |
| `DialogType` | ON | CURRENT/PREVIOUS | Dialog classification |
| `Group` | ON | CURRENT/PREVIOUS | Grouping info |
| `UpdateTime` | ON | CURRENT/PREVIOUS | Update timestamp |
| `Tribe` | ON | CURRENT/PREVIOUS | Character attribute |
| `Age` | ON | CURRENT/PREVIOUS | Character attribute |
| `Gender` | ON | CURRENT/PREVIOUS | Character attribute |
| `Job` | ON | CURRENT/PREVIOUS | Character attribute |
| `Region` | ON | CURRENT/PREVIOUS | Character attribute |
| `HasAudio` | ON | CURRENT/PREVIOUS | **NEW - Audio flag** |
| `UseSubtitle` | ON | CURRENT/PREVIOUS | Subtitle flag |
| `Record` | ON | CURRENT/PREVIOUS | Record flag |
| `isNew` | ON | CURRENT/PREVIOUS | New flag |

**All optional columns ON by default. User can choose source: CURRENT or PREVIOUS.**

---

## Settings Schema (JSON)

```json
{
  "use_priority_change": true,
  "output_columns": {
    "auto_generated": {
      "PreviousData": { "enabled": true },
      "PreviousText": { "enabled": true },
      "PreviousEventName": { "enabled": true },
      "DETAILED_CHANGES": { "enabled": true },
      "Previous StrOrigin": { "enabled": true },
      "Mainline Translation": { "enabled": true }
    },
    "optional": {
      "Desc": { "enabled": true, "source": "CURRENT" },
      "FREEMEMO": { "enabled": true, "source": "CURRENT" },
      "SubTimelineName": { "enabled": true, "source": "CURRENT" },
      "StartFrame": { "enabled": true, "source": "CURRENT" },
      "EndFrame": { "enabled": true, "source": "CURRENT" },
      "DialogType": { "enabled": true, "source": "CURRENT" },
      "Group": { "enabled": true, "source": "CURRENT" },
      "UpdateTime": { "enabled": true, "source": "CURRENT" },
      "Tribe": { "enabled": true, "source": "CURRENT" },
      "Age": { "enabled": true, "source": "CURRENT" },
      "Gender": { "enabled": true, "source": "CURRENT" },
      "Job": { "enabled": true, "source": "CURRENT" },
      "Region": { "enabled": true, "source": "CURRENT" },
      "HasAudio": { "enabled": true, "source": "CURRENT" },
      "UseSubtitle": { "enabled": true, "source": "CURRENT" },
      "Record": { "enabled": true, "source": "CURRENT" },
      "isNew": { "enabled": true, "source": "CURRENT" }
    }
  }
}
```

**Source options:** `"CURRENT"` or `"PREVIOUS"`

---

## Implementation Plan

### Phase 1: Add HasAudio (Quick Win)
1. Add `HasAudio` to `OUTPUT_COLUMNS` in `src/config.py`
2. Place after `Mainline Translation`
3. Test with CURRENT file

### Phase 2: Settings Schema
1. Expand `src/settings.py` with column configuration
2. Add default values for all columns
3. Add load/save functions for column settings

### Phase 3: Dynamic Column Filtering
1. Modify `filter_output_columns()` in `src/utils/data_processing.py`
2. Read column settings and filter dynamically
3. Maintain column ORDER (mandatory → auto-generated → optional)

### Phase 4: UI Integration (if GUI exists)
1. Add settings panel for column toggles
2. Group by category (Auto-Generated vs Optional)
3. Add HELP tooltip explaining each auto-generated column

#### UI Mockup (Approved)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Column Settings                                              [X] Close │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ MANDATORY COLUMNS (Always Shown) ─────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  🔒 SequenceName    🔒 EventName    🔒 StrOrigin    🔒 CharacterKey    │ │
│  │  🔒 CharacterName   🔒 CastingKey   🔒 DialogVoice  🔒 Text            │ │
│  │  🔒 STATUS          🔒 CHANGES                                         │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ AUTO-GENERATED COLUMNS ───────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Column                  Show    Info                                   │ │
│  │  ─────────────────────────────────────────                              │ │
│  │  PreviousData            [✓]     ⓘ Combined prev Text|STATUS|Freememo  │ │
│  │  PreviousText            [✓]     ⓘ Text from matched previous row      │ │
│  │  PreviousEventName       [✓]     ⓘ Previous EventName when changed     │ │
│  │  DETAILED_CHANGES        [✓]     ⓘ Full composite change type          │ │
│  │  Previous StrOrigin      [✓]     ⓘ StrOrigin from previous row         │ │
│  │  Mainline Translation    [✓]     ⓘ Original Text before import         │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ OPTIONAL COLUMNS ─────────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Column           Show    Source                                        │ │
│  │  ───────────────────────────────────────────                            │ │
│  │  Desc             [✓]     ( ) CURRENT  (•) PREVIOUS                     │ │
│  │  FREEMEMO         [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  SubTimelineName  [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  StartFrame       [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  EndFrame         [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  DialogType       [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Group            [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  UpdateTime       [ ]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Tribe            [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Age              [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Gender           [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Job              [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Region           [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  HasAudio         [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  UseSubtitle      [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Record           [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  isNew            [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  [Reset to Defaults]                      [Cancel]  [Apply & Save]  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Access:** Button in MAIN TAB toolbar: `[⚙️ Columns]`

### Phase 5: Help System
One-liner explanations for auto-generated columns:

| Column | Help Text |
|--------|-----------|
| PreviousData | "Combined previous Text, STATUS, FREEMEMO (format: Text \| STATUS \| Freememo)" |
| PreviousText | "Text value from matched previous row" |
| PreviousEventName | "Previous EventName when it changed" |
| DETAILED_CHANGES | "Full composite change type (all detected changes)" |
| Previous StrOrigin | "StrOrigin value from matched previous row" |
| Mainline Translation | "Original Text value before import logic applied" |

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/config.py` | Add HasAudio to OUTPUT_COLUMNS |
| `src/settings.py` | Expand with column settings schema |
| `src/utils/data_processing.py` | Dynamic column filtering |
| GUI file (TBD) | Settings panel |

---

## Decisions Confirmed (2025-12-22)

1. **Column source**: User CAN choose CURRENT vs PREVIOUS for each optional column
2. **HasAudio placement**: After Mainline Translation - CONFIRMED
3. **Defaults**: All optional columns ON by default, user deactivates if needed

---

## Testing

- [x] HasAudio appears in output
- [x] Settings persist between sessions
- [x] Disabling column removes it from output
- [x] Mandatory columns cannot be disabled
- [x] Column order is maintained
- [x] V2: File analysis works
- [x] V2: Selected columns included, unselected excluded
- [x] V2: V1 defaults don't pollute V2 settings
- [x] All 518 unified tests pass

---

*Task created from colleague request - see SESSION_CONTEXT for conversation*
