# Change Types Reference

**Version:** v12021800
**Last Updated:** 2025-11-28

This document serves as the **single source of truth** for all change detection in VRS Manager.

---

## ✅ Current Status: UNIFIED DETECTION SYSTEM

**All change detection now uses a single, unified function:** `detect_all_field_changes()` in `src/core/change_detection.py`

This unified system:
- Detects ALL 9 change types consistently
- Creates composite labels dynamically (e.g., `CharacterGroup+EventName+StrOrigin Change`)
- Works identically for RAW and WORKING processors
- **Tested with 518 test cases covering all possible combinations**

---

## Overview

VRS Manager uses a **10-Key Pattern Matching + TWO-PASS Algorithm** to detect changes between previous and current VRS files. This system identifies 9 core change types, plus combinations, for precise change tracking.

---

## Unified Detection Function

**Location:** `src/core/change_detection.py`

```python
def detect_all_field_changes(curr_row, prev_row, df_curr, df_prev, require_korean=None):
    """
    Universal change detection - detects ALL field differences.

    Canonical Order:
        CharacterGroup → EventName → StrOrigin → SequenceName →
        CastingKey → Desc → TimeFrame → DialogType → Group

    Returns: change_label (str) - e.g., "CharacterGroup+EventName+StrOrigin Change"
    """
    # 1. Find ALL differences between current and previous rows
    differences = [col for col in common_cols if curr[col] != prev[col]]

    # 2. Build change list in CANONICAL ORDER
    important_changes = []

    # CharacterGroup (Tribe, Age, Gender, Job, Region)
    if any(col in differences for col in CHAR_GROUP_COLS):
        important_changes.append("CharacterGroup")

    # Core keys
    if COL_EVENTNAME in differences:
        important_changes.append("EventName")
    if COL_STRORIGIN in differences:
        important_changes.append("StrOrigin")
    if COL_SEQUENCE in differences:
        important_changes.append("SequenceName")
    if COL_CASTINGKEY in differences:
        important_changes.append("CastingKey")

    # Metadata fields
    if COL_DESC in differences:
        important_changes.append("Desc")
    if COL_STARTFRAME in differences:
        important_changes.append("TimeFrame")
    if COL_DIALOGTYPE in differences:
        important_changes.append("DialogType")
    if COL_GROUP in differences:
        important_changes.append("Group")

    # 3. Build and return the change label
    return "+".join(important_changes) + " Change" if important_changes else "No Change"
```

### Key Points

1. **No special treatment for CharacterGroup** - It's included in composite labels just like any other change type
2. **Canonical order is fixed** - Ensures consistent label formatting across all scenarios
3. **All processors use this function** - RAW and WORKING produce identical results

---

## Core Change Types (9 Types)

### Primary Field Changes (4 Core Keys)

| Change Type | Field Changed | Detection | Impact |
|-------------|--------------|-----------|--------|
| **StrOrigin Change** | Dialogue text content | Text differs | High - needs re-translation |
| **EventName Change** | Event identifier | EventName differs | Medium - event reorganization |
| **SequenceName Change** | Sequence identifier | SequenceName differs | Medium - scene reorganization |
| **CastingKey Change** | Voice actor assignment | CharacterKey/DialogVoice combo differs | High - voice actor reassignment |

### Metadata Field Changes

| Change Type | Field Changed | Detection | Impact |
|-------------|--------------|-----------|--------|
| **TimeFrame Change** | StartFrame/EndFrame | Timing values differ | Medium - may need re-recording |
| **Desc Change** | Description field | Desc text differs | Low - context/direction update |
| **DialogType Change** | Dialogue type | DialogType differs | Medium - classification changed |
| **Group Change** | Group assignment | Group differs | Low - organizational change |

### Character Metadata Changes

| Change Type | Fields Changed | Detection | Impact |
|-------------|---------------|-----------|--------|
| **CharacterGroup Change** | Tribe, Age, Gender, Job, or Region | Any character attribute differs | Medium - may affect voice casting |

---

## System State Classifications

| Classification | Meaning | Detection |
|---------------|---------|-----------|
| **No Change** | Perfect 4-key match | Sequence + Event + StrOrigin + CastingKey all identical |
| **New Row** | Row in CURRENT not in PREVIOUS | No lookup finds a match (too many core keys changed) |
| **Deleted Row** | Row in PREVIOUS not in CURRENT | Not matched during TWO-PASS algorithm |
| **No Relevant Change** | Changes only in non-Korean text | System filters non-Korean StrOrigin changes |

---

## Composite Change Types

When multiple fields change together, the system creates composite labels dynamically.

### Examples

| Fields Changed | Composite Label |
|---------------|-----------------|
| StrOrigin + Desc | `StrOrigin+Desc Change` |
| EventName + StrOrigin + TimeFrame | `EventName+StrOrigin+TimeFrame Change` |
| CharacterGroup + EventName + StrOrigin | `CharacterGroup+EventName+StrOrigin Change` |
| All 9 fields | `CharacterGroup+EventName+StrOrigin+SequenceName+CastingKey+Desc+TimeFrame+DialogType+Group Change` |

**Total possible combinations:** 511 (2^9 - 1)

---

## Detection by Processor

### Current Status (v12021800) - ALL FIXED

| Change Type | RAW | WORKING | Notes |
|-------------|-----|---------|-------|
| **StrOrigin** | ✅ | ✅ | |
| **EventName** | ✅ | ✅ | |
| **SequenceName** | ✅ | ✅ | |
| **CastingKey** | ✅ | ✅ | |
| **TimeFrame** | ✅ | ✅ | |
| **Desc** | ✅ | ✅ | |
| **DialogType** | ✅ | ✅ | |
| **Group** | ✅ | ✅ | |
| **CharacterGroup** | ✅ | ✅ | Included in composites |
| **No Change** | ✅ | ✅ | |
| **New Row** | ✅ | ✅ | |
| **Deleted Row** | ✅ | ✅ | |
| **All Composites** | ✅ | ✅ | 511 combinations tested |

**Both RAW and WORKING processors now produce identical change detection results.**

---

## 10-Key Lookup System

The system uses 10 lookup dictionaries to find matches:

### 4-Key (Perfect Match)
- **SEOC:** Sequence + Event + StrOrigin + CastingKey → "No Change"

### 3-Key Matches
- **SEO:** Sequence + Event + StrOrigin → CastingKey changed
- **SEC:** Sequence + Event + CastingKey → StrOrigin changed
- **SOC:** Sequence + StrOrigin + CastingKey → EventName changed
- **EOC:** Event + StrOrigin + CastingKey → SequenceName changed

### 2-Key Matches
- **SE:** Sequence + Event → Multiple fields changed
- **SO:** Sequence + StrOrigin → Multiple fields changed
- **SC:** Sequence + CastingKey → Multiple fields changed
- **EO:** Event + StrOrigin → Multiple fields changed
- **EC:** Event + CastingKey → Multiple fields changed
- **OC:** StrOrigin + CastingKey → Multiple fields changed

### New Row Detection
When NO lookup finds a match (3+ core keys changed), the row is classified as "New Row".

---

## Implementation Files

### Change Detection (Unified)
- **Single Source:** `src/core/change_detection.py` - `detect_all_field_changes()`

### Processors
- **RAW:** `src/core/comparison.py` - Uses unified detection
- **WORKING:** `src/core/working_comparison.py` - Uses unified detection
- **ALLLANG:** `src/core/alllang_helpers.py` - Uses unified detection
- **MASTER:** `src/processors/master_processor.py` - Pass-through (receives CHANGES from source)

### Configuration
- **Column Names:** `src/config.py` (COL_*)
- **Character Groups:** `src/config.py` (CHAR_GROUP_COLS = ["Tribe", "Age", "Gender", "Job", "Region"])

---

## Testing & Validation

### Primary Test File
- **`tests/test_unified_change_detection.py`** - Comprehensive test with 518 test cases

### What It Tests
- All 9 standalone change types
- All 502 composite combinations (2-9 fields)
- 5 CharacterGroup field variations
- New Row detection
- No Change control cases

### How It Works
1. Creates PREVIOUS/CURRENT Excel files with TRUE VoiceRecordSheet structure
2. Injects KNOWN changes at specific rows
3. Runs **exact production code** (imports from `src/`)
4. Validates each row produces the exact expected change label

### Running the Test
```bash
python3 tests/test_unified_change_detection.py
```

Expected output:
```
✅ RAW: 518/518 (100.0%)
✅ WORKING: 518/518 (100.0%)
```

---

## Examples

### Example 1: Standalone Change
```
PREVIOUS: StrOrigin = "안녕하세요"
CURRENT:  StrOrigin = "안녕하세요 반갑습니다"
RESULT:   "StrOrigin Change"
```

### Example 2: Composite Change
```
PREVIOUS: StrOrigin = "안녕", EventName = "event_001", Gender = "남성"
CURRENT:  StrOrigin = "안녕하세요", EventName = "event_002", Gender = "여성"
RESULT:   "CharacterGroup+EventName+StrOrigin Change"
```

### Example 3: New Row (Too Many Keys Changed)
```
PREVIOUS: StrOrigin = "안녕", EventName = "event_001", SequenceName = "seq_001", CastingKey = "char_001"
CURRENT:  StrOrigin = "다른텍스트", EventName = "event_999", SequenceName = "seq_999", CastingKey = "char_999"
RESULT:   "New Row" (no lookup can match when all 4 core keys change)
```

---

## Version History

### v12021800 (Current)
- ✅ Unified change detection system implemented
- ✅ CharacterGroup treated equally (no special early return)
- ✅ All 518 test cases passing for RAW and WORKING
- ✅ Test infrastructure cleaned up (old tests archived)

### v11241313
- Initial unified detection function
- Phase 3.1.1b bug fixes

### v1118.X
- Super Group Word Analysis
- BERT-based StrOrigin similarity detection

### v1117.X
- 10-Key TWO-PASS algorithm introduced
- Initial composite change detection

---

## References

- **Main Documentation:** `README.md`, `CLAUDE.md`
- **Roadmap:** `roadmap.md`
- **Test File:** `tests/test_unified_change_detection.py`
- **Archive:** `tests/archive/` (old tests), `ARCHIVE/` (old documentation)
