# Change Types Reference

**Version:** v11202116
**Last Updated:** 2025-01-24

This document serves as the **single source of truth** for all change detection in VRS Manager.

---

## Overview

VRS Manager uses a **10-Key Pattern Matching + TWO-PASS Algorithm** to detect changes between previous and current VRS files. This system identifies 9 core change types, plus combinations, for precise change tracking.

---

## Core Change Types (Standalone)

### 1. Primary Field Changes

These are the 4 core fields used in the 10-key matching system:

| Change Type | Field Changed | Detection | Impact | Color |
|-------------|--------------|-----------|---------|-------|
| **StrOrigin Change** | Dialogue text content | Text differs between PREV/CURR | High - needs re-translation | Yellow (#FFD580) |
| **EventName Change** | Event identifier | EventName differs | Medium - event reorganization | Light Yellow (#FFFF99) |
| **SequenceName Change** | Sequence identifier | SequenceName differs | Medium - scene reorganization | Light Blue (#B3E5FC) |
| **CastingKey Change** | Voice actor assignment | CharacterKey/DialogVoice/GroupKey/DialogType combo differs | High - voice actor reassignment | Orange (#FFB347) |

### 2. Metadata Field Changes

These provide timing, context, and classification information:

| Change Type | Field Changed | Detection | Impact | Color |
|-------------|--------------|-----------|---------|-------|
| **TimeFrame Change** | StartFrame/EndFrame | Timing values differ | Medium - may need re-recording | Red-Orange (#FF9999) |
| **Desc Change** | Description field | Desc text differs | Low - context/direction update | Purple (#E1D5FF) |
| **DialogType Change** | Dialogue type classification | DialogType differs (e.g., dialogue→narration) | Medium - classification changed | (Composite only) |
| **Group Change** | Group assignment | Group differs | Low - organizational change | (Composite only) |

### 3. Character Metadata Changes

| Change Type | Fields Changed | Detection | Impact | Color |
|-------------|---------------|-----------|---------|-------|
| **Character Group Change** | Tribe, Age, Gender, Job, or Region | Any character attribute differs | Medium - may affect voice casting | Light Sky Blue (#87CEFA) |

---

## System State Classifications

| Classification | Meaning | Detection | Color |
|---------------|---------|-----------|-------|
| **No Change** | Perfect 4-key match | Sequence + Event + StrOrigin + CastingKey all identical | Light Gray (#E8E8E8) |
| **New Row** | Row in CURRENT not in PREVIOUS | All 10 keys missing from PREVIOUS | Green (#90EE90) |
| **Deleted Row** | Row in PREVIOUS not in CURRENT | Not matched during TWO-PASS algorithm | Red |
| **No Relevant Change** | Changes only in non-Korean text | System ignores non-Korean StrOrigin changes | Dark Gray (#D3D3D3) |

---

## Composite Change Types

When multiple fields change together, the system creates composite labels (e.g., "StrOrigin+Desc Change").

### Common Composites

| Composite Type | Fields Changed | Example Scenario | Color |
|---------------|---------------|------------------|-------|
| **StrOrigin+Desc Change** | Text + Description | Dialogue and context both updated | Light Salmon (#FFA07A) |
| **StrOrigin+TimeFrame Change** | Text + Timing | Dialogue changed and timing shifted | Light Pink (#FFB6C1) |
| **EventName+CastingKey Change** | Event + Actor | Event renamed AND voice actor changed | Yellow-Orange (#FFD966) |
| **StrOrigin+Desc+TimeFrame Change** | Text + Desc + Timing | Major revision (all content fields) | Light Coral (#F08080) |
| **DialogType+Group Change** | Type + Group | Classification and organization changed | (Composite) |

**Note:** The system can create 100+ valid composite combinations. Colors follow a gradient scheme based on the primary change type.

---

## Detection by Processor

This table shows which processors detect which change types:

| Change Type | RAW | WORKING | ALLLANG | MASTER |
|-------------|-----|---------|---------|--------|
| **StrOrigin** | ✅ | ✅ | ✅ | N/A¹ |
| **EventName** | ✅ | ✅ | ✅ | N/A¹ |
| **SequenceName** | ✅ | ✅ | ✅ | N/A¹ |
| **CastingKey** | ✅ | ✅ | ✅ | N/A¹ |
| **TimeFrame** | ✅ | ❌ BUG | ❌ BUG | ⚠️² |
| **Desc** | ✅ | ❌ BUG | ❌ BUG | N/A¹ |
| **DialogType** | ✅ | ⚠️³ | ❌ BUG | N/A¹ |
| **Group** | ✅ | ⚠️³ | ❌ BUG | N/A¹ |
| **Character Groups** | ✅ | ❌ BUG | ❌ BUG | N/A¹ |
| **No Change** | ✅ | ✅ | ✅ | N/A¹ |
| **New Row** | ✅ | ✅ | ✅ | ✅ |
| **Deleted Row** | ✅ | ✅ | ✅ | ✅ |
| **Composites** | ✅ | ⚠️⁴ | ❌ BUG | N/A¹ |

**Legend:**
- ✅ = Fully detected during pattern matching
- ❌ BUG = Not detected (needs fix)
- ⚠️ = Partially working (see notes)
- N/A = Different purpose (not applicable)

**Notes:**
1. **MASTER:** Pass-through processor - receives CHANGES from SOURCE (Working Process), doesn't detect changes itself
2. **MASTER TimeFrame:** Preserves TARGET TimeFrame when StrOrigin unchanged (preservation logic, not detection)
3. **WORKING DialogType/Group:** Detected in post-processing only (after pattern matching), may miss some composite scenarios
4. **WORKING Composites:** Partial - only StrOrigin/EventName/SequenceName/CastingKey combos work

---

## Detection Logic Details

### Pattern Matching Flow (TWO-PASS Algorithm)

**PASS 1: Certainties (Priority)**
1. **Perfect Match (4-key):** All of Sequence + Event + StrOrigin + CastingKey match → "No Change"
2. **Complete Miss (10-key):** All 10 keys missing → "New Row"

**PASS 2: Pattern Matching (Uses UNMARKED rows only)**

**Level 1 - 3-Key Matches (One field changed):**
- SEO match (Sequence + Event + StrOrigin) → Check CastingKey → "CastingKey Change"
- SEC match (Sequence + Event + CastingKey) → Check StrOrigin → "StrOrigin Change" *(+ check Desc, TimeFrame)*
- SOC match (Sequence + StrOrigin + CastingKey) → Check EventName → "EventName Change"
- EOC match (Event + StrOrigin + CastingKey) → Check SequenceName → "SequenceName Change"

**Level 2 - 2-Key Matches (Two+ fields changed):**
- SE match (Sequence + Event) → Check StrOrigin, CastingKey → Composites *(+ check Desc, TimeFrame, Character Groups)*
- OC match (StrOrigin + CastingKey) → Check Sequence, EventName → "SequenceName+EventName Change"
- EC match (Event + CastingKey) → Check Sequence, StrOrigin → Composites
- SC match (Sequence + CastingKey) → "EventName+StrOrigin Change"
- SO match (Sequence + StrOrigin) → Check EventName, CastingKey → Composites
- EO match (Event + StrOrigin) → "SequenceName Change"

### Field-Level Detection (During Pattern Matching)

When a match is found, the system checks for additional field changes:

**RAW Processor (src/core/comparison.py):**
```python
# After SEC match (lines 216-244) or SE match (lines 274-318)
differences = [col for col in common_cols if curr[col] != prev[col]]

important_changes = ["StrOrigin"]  # Base change
if COL_DESC in differences:
    important_changes.append("Desc")
if COL_STARTFRAME in differences:
    important_changes.append("TimeFrame")
if COL_DIALOGTYPE in differences:
    important_changes.append("DialogType")
if COL_GROUP in differences:
    important_changes.append("Group")

change_label = "+".join(important_changes) + " Change"
```

**Character Group Detection (RAW only):**
```python
# During SE match (lines 289-294)
char_group_diffs = [col for col in differences if col in CHAR_GROUP_COLS]
if char_group_diffs:
    change_label = "Character Group Change"
```

**WORKING/ALLLANG Processors:** ❌ **Missing these checks** (BUG)

---

## Import Logic by Change Type

### Working Process & All Language Process

| Change Type | STATUS | Text | Desc | FREEMEMO | PreviousData | Logic |
|-------------|--------|------|------|----------|--------------|-------|
| **No Change** | ✅ PREV | ✅ PREV | ✅ PREV | ✅ PREV | ✅ Generated | Full import |
| **StrOrigin Change** | ✅ PREV* | ❌ CURR | ✅ PREV | ✅ PREV | ✅ Generated | Preserve work, update text |
| **Desc Change** | ✅ PREV | ✅ PREV | ❌ CURR | ✅ PREV | ✅ Generated | Update desc only |
| **TimeFrame Change** | ✅ PREV | ✅ PREV | ✅ PREV | ✅ PREV | ✅ Generated | Full import (timing only) |
| **EventName Change** | ✅ PREV | ✅ PREV | ✅ PREV | ✅ PREV | ✅ Generated | Full import |
| **SequenceName Change** | ✅ PREV | ✅ PREV | ✅ PREV | ✅ PREV | ✅ Generated | Full import |
| **CastingKey Change** | ✅ PREV | ✅ PREV | ✅ PREV | ✅ PREV | ✅ Generated | Full import |
| **DialogType Change** | ✅ PREV | ✅ PREV | ✅ PREV | ✅ PREV | ✅ Generated | Full import |
| **Group Change** | ✅ PREV | ✅ PREV | ✅ PREV | ✅ PREV | ✅ Generated | Full import |
| **Character Group Change** | ✅ PREV | ✅ PREV | ✅ PREV | ✅ PREV | ✅ Generated | Full import |
| **Composites** | Depends on StrOrigin | Depends | Depends | ✅ PREV | If StrOrigin changed | Follow StrOrigin rule |
| **New Row** | ❌ None | ❌ CURR | ❌ CURR | ❌ None | ❌ None | No import (new content) |

**Special Rule:** If PREVIOUS STATUS is after-recording (RECORDED, FINAL, etc.), **always preserve STATUS** regardless of change type.

**PreviousData Format:** `"{PreviousStrOrigin} | {PreviousSTATUS} | {PreviousFREEMEMO}"`

### Master File Update

MASTER is a **pass-through processor** - it receives CHANGES from SOURCE and applies these rules:

**High Importance Rows:**
- EventName matches TARGET → Update TARGET with SOURCE data, preserve CHANGES from SOURCE
- EventName not in TARGET → Add new row, preserve CHANGES from SOURCE
- **TimeFrame Preservation:** If TimeFrame changed BUT StrOrigin did NOT change → Keep TARGET TimeFrame

**Low Importance Rows:**
- Skipped entirely (not processed)

**Deleted Rows:**
- EventName in TARGET but not in SOURCE → Keep row, set CHANGES = "Deleted"

---

## Implementation Files

### Change Detection
- **RAW:** `src/core/comparison.py` - Full detection (gold standard)
- **WORKING:** `src/core/working_comparison.py` - Partial detection (missing 5 types)
- **ALLLANG:** `src/core/alllang_helpers.py` (process_alllang_comparison_twopass) - Partial detection
- **MASTER:** `src/processors/master_processor.py` - No detection (pass-through)

### Import Logic
- **Common:** `src/core/import_logic.py` (apply_import_logic)
- **All Language:** `src/core/alllang_helpers.py` (apply_import_logic_alllang_lang)

### Color Coding
- **Formatting:** `src/io/formatters.py` (apply_direct_coloring)
- **Definitions:** Lines 64-109 (40+ change type colors)

### Configuration
- **Column Names:** `src/config.py` (COL_*)
- **Character Groups:** `src/config.py` (CHAR_GROUP_COLS)

---

## Testing & Validation

### Test Files
- **Performance:** `tests/test_5000_perf.py`
- **Accuracy:** `tests/test_accuracy.py`
- **Math Verification:** `tests/test_math_verify.py`

### Expected Behavior
1. **Row Count Conservation:** CURRENT rows = sum of all change type counts
2. **No Duplicates:** Each CURRENT row classified exactly once
3. **Deleted Detection:** PREVIOUS rows - Matched rows = Deleted rows
4. **Composite Logic:** Multiple field changes create composite labels (e.g., "StrOrigin+Desc Change")

---

## Known Issues (As of v11202116)

### WORKING Processor Bugs
1. ❌ **TimeFrame** changes not detected
2. ❌ **Desc** changes not detected
3. ⚠️ **DialogType/Group** detected in post-processing only (may miss composites)
4. ❌ **Character Group** changes not detected

### ALLLANG Processor Bugs
1. ❌ **TimeFrame** changes not detected
2. ❌ **Desc** changes not detected
3. ❌ **DialogType** changes not detected
4. ❌ **Group** changes not detected
5. ❌ **Character Group** changes not detected

**Impact:** These changes exist in the data but are invisible to users. Import logic for these types exists but is never triggered.

**Fix Required:** Add field-level checking during pattern matching (similar to RAW processor).

---

## Examples

### Example 1: StrOrigin Change
```
PREVIOUS: StrOrigin = "Hello"
CURRENT:  StrOrigin = "Hello there"
RESULT:   "StrOrigin Change"
IMPORT:   STATUS from PREV, Text from CURR, Desc from PREV
```

### Example 2: TimeFrame Change (should detect but WORKING/ALLLANG don't)
```
PREVIOUS: StartFrame = "100"
CURRENT:  StartFrame = "150"
RESULT:   "TimeFrame Change" (RAW ✅) or "No Change" (WORKING ❌)
IMPORT:   Full import from PREV (STATUS, Text, Desc, FREEMEMO)
```

### Example 3: Composite Change
```
PREVIOUS: StrOrigin = "Hello", Desc = "Greeting", StartFrame = "100"
CURRENT:  StrOrigin = "Hi", Desc = "Casual greeting", StartFrame = "150"
RESULT:   "StrOrigin+Desc+TimeFrame Change" (RAW ✅) or "StrOrigin+Desc Change" (WORKING ⚠️)
```

### Example 4: Character Group Change
```
PREVIOUS: Gender = "Male", Age = "Adult"
CURRENT:  Gender = "Female", Age = "Adult"
RESULT:   "Character Group Change" (RAW ✅) or "No Change" (WORKING ❌)
```

---

## Version History

### v11202116 (Current)
- ✅ Word-Level Diff Enhancement for StrOrigin Analysis
- ❌ Known bugs in WORKING/ALLLANG (TimeFrame, Desc, DialogType, Group, Character Groups)

### v1118.X
- ✅ Super Group Word Analysis
- ✅ BERT-based StrOrigin similarity detection
- ✅ TimeFrame preservation in MASTER processor

### v1117.X
- ✅ 10-Key TWO-PASS algorithm
- ✅ Comprehensive composite change detection (RAW only)
- ✅ Character Group Change detection (RAW only)

---

## References

- **Main Documentation:** `README.md`, `WIKI_CONFLUENCE.md`
- **Roadmap:** `roadmap.md`
- **Developer Guide:** `docs/DEVELOPER_GUIDE.md`
- **Archive:** `ARCHIVE/PHASE2_EXTRACTION_SUMMARY.md`, `ARCHIVE/COMPOSITE_CHANGE_BUG_ANALYSIS.md`
