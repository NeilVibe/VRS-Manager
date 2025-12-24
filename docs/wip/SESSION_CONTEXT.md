# Session Context - Claude Handoff Document

**Last Updated:** 2025-12-24
**Version:** v12231045 (production)
**Status:** TASK-002 V5 IMPLEMENTED - KEY-based PREVIOUS column extraction

---

## Current State

| Item | Status |
|------|--------|
| Production | Stable (v12231045) |
| Git | V4 commits done, V5 code ready |
| TASK-002 | V5 IMPLEMENTED - Ready for testing |

---

## TASK-002: V5 Implementation (COMPLETE)

### What Was Implemented

1. **Backend: KEY-based PREVIOUS Column Extraction**
   - `src/core/working_comparison.py`: Added V5 PREVIOUS column extraction in the processing loop
   - Uses existing KEY-matching (SequenceName+EventName+StrOrigin+CastingKey)
   - For each CURRENT row, extracts selected columns from matched PREVIOUS row
   - New rows (no KEY match) get empty PREVIOUS values

2. **Data Processing: V5 Column Filtering**
   - `src/utils/data_processing.py`: Updated `filter_output_columns()` to include V5 columns
   - Includes V5 auto-generated, current, and previous columns in output

3. **UI: Dual File Upload (Already Existed)**
   - `src/ui/main_window.py`: Already had V5 dual upload boxes implemented
   - CURRENT file box (green) and PREVIOUS file box (blue)
   - Previous_ prefix added to PREVIOUS columns in display

4. **Settings: V5 Schema (Already Existed)**
   - `src/settings.py`: Already had V5 functions
   - `get_v5_column_settings()`, `set_v5_current_file()`, `set_v5_previous_file()`
   - `get_v5_enabled_columns()` returns Previous_ prefixed columns

5. **Tests: V5 Test Suite**
   - `tests/test_column_classification.py`: Added 6 new V5 tests
   - All 21 tests pass

### Key Technical Details

```python
# In working_comparison.py (simplified):
v5_cols = get_v5_enabled_columns()
selected_previous_cols = v5_cols.get("previous", [])  # e.g., ["Previous_FREEMEMO"]

for prefixed_col in selected_previous_cols:
    if prefixed_col.startswith("Previous_"):
        original_col = prefixed_col[9:]  # "FREEMEMO"
        if prev_row_dict and change_type != "New Row":
            # KEY-matched: extract from matched PREVIOUS row
            curr_dict[prefixed_col] = safe_str(prev_row_dict.get(original_col, ""))
        else:
            curr_dict[prefixed_col] = ""  # New Row
```

### Files Modified (This Session)

```
src/core/working_comparison.py   # V5: PREVIOUS column KEY-based extraction
src/utils/data_processing.py     # V5: filter_output_columns includes V5 columns
tests/test_column_classification.py  # V5: 6 new tests (21 total)
```

---

## V5 UI Design (Reference)

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

---

## V4 Implementation (COMPLETE - Reference)

### 4-Tier Column Classification System

| Category | Count | Behavior | UI |
|----------|-------|----------|-----|
| **MANDATORY** | 10 | Always included, cannot disable | Green ✓ info section |
| **VRS_CONDITIONAL** | 10 | Used in change detection, always from CURRENT | Blue ✓ info section |
| **AUTO-GENERATED** | 6 | Created by VRS logic, toggleable | Purple checkboxes |
| **OPTIONAL** | 7 | Extra metadata only, toggleable | Orange checkboxes |

### Column Details

**MANDATORY (10):** SequenceName, EventName, StrOrigin, CharacterKey, CharacterName, CastingKey, DialogVoice, Text, STATUS, CHANGES

**VRS_CONDITIONAL (10):** Desc, DialogType, Group, StartFrame, EndFrame, Tribe, Age, Gender, Job, Region

**AUTO-GENERATED (6):** PreviousData, PreviousText, PreviousEventName, DETAILED_CHANGES, Previous StrOrigin, Mainline Translation

**OPTIONAL (7):** FREEMEMO, SubTimelineName, UpdateTime, HasAudio, UseSubtitle, Record, isNew

---

## Testing

```bash
# Run unified tests (518 tests)
python3 tests/test_unified_change_detection.py

# Run column classification tests (21 tests including V5)
python3 tests/test_column_classification.py

# Check version
python3 scripts/check_version_unified.py
```

All tests pass:
- 518/518 unified tests
- 21/21 column classification tests (including 6 new V5 tests)

---

## Next Steps

1. **Manual Windows test** - Verify Column Settings dialog with dual upload
2. **Build and deploy** - Create new build with V5 functionality
3. **User testing** - Test with real PREVIOUS/CURRENT file pairs

---

## Key Clarifications

- **CURRENT columns**: Extracted by NAME from CURRENT file (simple, direct)
- **PREVIOUS columns**: Extracted by KEY-matching from PREVIOUS file (robust)
- **New Rows**: PREVIOUS columns are empty (no KEY match)
- **Matched Rows**: PREVIOUS columns contain value from matched PREVIOUS row

---

*This document is the source of truth for session handoff.*
