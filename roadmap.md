# VRS Manager - Development Roadmap

## 📝 Version Update Checklist (IMPORTANT!)

**After completing any code work that changes the version, update ALL of these files:**

- [ ] `src/config.py` → `VERSION` constant and `VERSION_FOOTER`
- [ ] `main.py` → Docstring (line 5) and all print statements (lines 12-15)
- [ ] `README.md` → Version number (line 3) and status line (line 5)
- [ ] `README_KR.md` → Version number (line 3) and status line (line 5)
- [ ] `roadmap.md` → Current Status header (below) and add to Version History section
- [ ] `docs/VRS_Manager_Process_Guide_EN.xlsx` → Version in Overview sheet
- [ ] `docs/VRS_Manager_Process_Guide_KR.xlsx` → Version in Overview sheet (개요)

**Don't forget to commit all documentation updates together!**

---

## 📋 Current Status

**Version:** v11241313 (DateTime Versioning - November 24, 2025 at 1:13 PM)

---

## 🚨 CURRENT PRIORITY: Phase 3.1.1b - Universal Change Detection Fix

**Status:** READY FOR IMPLEMENTATION
**Discovery Date:** 2025-11-27
**Reported By:** Tester (TimeFrame missing in composite changes)

---

### The Problem

When multiple fields change together (e.g., EventName + StrOrigin + TimeFrame), many pattern matches **miss metadata fields** because they use **hardcoded labels** instead of checking actual differences.

**Example Bug:**
```
PREVIOUS: EventName=Event_A, StrOrigin=Hello, TimeFrame=100
CURRENT:  EventName=Event_B, StrOrigin=World, TimeFrame=200

EXPECTED: "EventName+StrOrigin+TimeFrame Change"
ACTUAL:   "EventName+StrOrigin Change"  ← TimeFrame MISSING!
```

---

### Root Cause

**Inconsistent implementation across pattern matches:**

| Pattern Matches | Status | Issue |
|-----------------|--------|-------|
| PASS 1 (4-key perfect match) | ✅ Fixed v11241313 | - |
| SEC match (Seq+Event+CastingKey) | ✅ Always correct | Uses general detection |
| SE match (Seq+Event) | ✅ Always correct | Uses general detection |
| **All other matches (8 types)** | ❌ **BROKEN** | Hardcoded labels or partial checks |

**Bug Count:**
- RAW processor: 8 locations
- WORKING processor: 8 locations
- ALLLANG processor: 18 locations (2 functions)
- **TOTAL: 34 locations need fixing**

---

### The Solution: Universal Helper Function

**Create ONE function that ALL pattern matches will call:**

```python
# NEW FILE: src/core/change_detection.py

def detect_all_field_changes(curr_row, prev_row, df_curr, df_prev, require_korean=None):
    """
    Universal change detection - THE SINGLE SOURCE OF TRUTH.

    Detects ALL field differences between current and previous rows.
    Works for both standalone and composite changes.

    Args:
        curr_row: Current row
        prev_row: Previous row (matched)
        df_curr: Current DataFrame
        df_prev: Previous DataFrame
        require_korean: If provided, return "No Relevant Change" if no Korean

    Returns:
        change_label: e.g., "EventName+StrOrigin+TimeFrame Change"
    """
    # 1. Find ALL differences
    common_cols = [col for col in df_curr.columns if col in df_prev.columns]
    differences = [col for col in common_cols if safe_str(curr_row[col]) != safe_str(prev_row[col])]

    # 2. Character Groups first (special priority)
    char_group_diffs = [col for col in differences if col in CHAR_GROUP_COLS]
    if char_group_diffs:
        return "Character Group Change"

    # 3. Build change list from ACTUAL differences
    important_changes = []
    if COL_STRORIGIN in differences: important_changes.append("StrOrigin")
    if COL_EVENTNAME in differences: important_changes.append("EventName")
    if COL_SEQUENCE in differences: important_changes.append("SequenceName")
    if COL_CASTINGKEY in differences: important_changes.append("CastingKey")
    if COL_DESC in differences: important_changes.append("Desc")
    if COL_STARTFRAME in differences: important_changes.append("TimeFrame")
    if COL_DIALOGTYPE in differences: important_changes.append("DialogType")
    if COL_GROUP in differences: important_changes.append("Group")

    # 4. No changes found
    if not important_changes:
        return "No Change"

    # 5. Korean relevance filter (optional)
    if require_korean is not None and not contains_korean(require_korean):
        return "No Relevant Change"

    return "+".join(important_changes) + " Change"
```

**Why This Works:**
- ✅ **No hardcoding** - Always checks actual differences
- ✅ **Handles standalone** - 1 field changed → "TimeFrame Change"
- ✅ **Handles composite** - 3 fields changed → "EventName+StrOrigin+TimeFrame Change"
- ✅ **Future-proof** - Add new field in ONE place
- ✅ **Easy to maintain** - ONE function, not 34 copies

---

### Implementation Checklist

#### Phase 1: Create Helper Function
- [ ] Create `src/core/change_detection.py`
- [ ] Implement `detect_all_field_changes()` function
- [ ] Add proper imports and exports
- [ ] Write unit tests for the helper function

#### Phase 2: Update RAW Processor
**File:** `src/core/comparison.py`

| Line | Match | Current (WRONG) | Action |
|------|-------|-----------------|--------|
| 202-229 | SEO | Partial check | Add full detection |
| 261-275 | SOC | `"EventName Change"` hardcoded | Replace with helper |
| 277-286 | EOC | `"SequenceName Change"` hardcoded | Replace with helper |
| 335-351 | OC | Only core keys | Replace with helper |
| 353-369 | EC | Only core keys | Replace with helper |
| 371-380 | SC | `"EventName+StrOrigin Change"` hardcoded | Replace with helper |
| 382-403 | SO | Only core keys | Replace with helper |
| 405-414 | EO | `"SequenceName Change"` hardcoded | Replace with helper |

- [ ] Import helper function
- [ ] Update SEO match (lines 202-229)
- [ ] Update SOC match (lines 261-275)
- [ ] Update EOC match (lines 277-286)
- [ ] Update OC match (lines 335-351)
- [ ] Update EC match (lines 353-369)
- [ ] Update SC match (lines 371-380)
- [ ] Update SO match (lines 382-403)
- [ ] Update EO match (lines 405-414)

#### Phase 3: Update WORKING Processor
**File:** `src/core/working_comparison.py`

- [ ] Import helper function
- [ ] Update SEO match (lines 210-223)
- [ ] Update SOC match (lines 260-272)
- [ ] Update EOC match (lines 274-281)
- [ ] Update OC match (lines 326-339)
- [ ] Update EC match (lines 341-354)
- [ ] Update SC match (lines 356-363)
- [ ] Update SO match (lines 365-384)
- [ ] Update EO match (lines 386-393)

#### Phase 4: Update ALLLANG Processor
**File:** `src/core/alllang_helpers.py`

**Old function (lines ~320-410):**
- [ ] Update all pattern matches

**TWO-PASS function (lines ~665-850):**
- [ ] Update all pattern matches

#### Phase 5: Testing & Verification
- [ ] Run `tests/test_composite_timeframe_bug.py` - should PASS
- [ ] Run `tests/test_standalone_changes.py` - should still PASS
- [ ] Run `tests/test_accuracy.py` - should still PASS
- [ ] Run `tests/test_5000_perf.py` - performance check
- [ ] Create comprehensive test for ALL pattern match scenarios

#### Phase 6: Documentation & Release
- [ ] Update version number (all files)
- [ ] Update `docs/CHANGE_TYPES_REFERENCE.md` - remove bug warnings
- [ ] Update this roadmap - move to completed
- [ ] Run `check_version_unified.py`
- [ ] Commit and push
- [ ] Trigger build

---

### Impact Assessment

- **Risk Level:** MEDIUM (touching core detection logic)
- **Files Modified:** 4 (new change_detection.py + 3 processors)
- **Lines Changed:** ~200 lines across all files
- **Breaking Changes:** None (output format unchanged, just more accurate)
- **Testing Required:** Comprehensive - all pattern match scenarios

---

## ✅ Recently Completed

### Phase 3.1.1a - Standalone Change Detection Fix (v11241313)
- Fixed PASS 1 perfect match to detect standalone metadata changes
- Fixed SEC/SE matches in WORKING/ALLLANG (parity with RAW)
- Created `docs/CHANGE_TYPES_REFERENCE.md`

### Phase 3.1.3 - Processor Parity (v11201322)
- Added Super Group Word Analysis to WORKING processor
- Full feature parity between RAW and WORKING

### Phase 3.1.1 - Word-Level Diff (v11201321)
- Word-level diff algorithm for StrOrigin Analysis
- 4-column layout with Diff Detail column
- Progress tracking

### Phase 3.0 - Professional Installer System (v1.120.0)
- LIGHT (~150MB) and FULL (~2.6GB) installers
- 100% offline operation
- GitHub Actions CI/CD

---

## 📋 Future Priorities (After Phase 3.1.1b)

### Phase 3.1.2 - AllLang Process Enhancement
- Add StrOrigin Analysis to AllLang Process

### Phase 3.2 - Self-Monitoring Infrastructure
- ✅ Version unification check script (DONE)
- Additional monitoring tools TBD

---

## Version History

### v11241313 (Released - 2025-11-24) ✅
- **Phase 3.1.1a**: Standalone Change Detection Fix (Partial)
- Fixed PASS 1 standalone detection
- Known issue: PASS 2 composite detection still has bugs (Phase 3.1.1b)

### v11201321 (Released - 2025-11-20) ✅
- **Phase 3.1.1**: Word-Level Diff Enhancement

### v1.120.0 (Released - 2025-11-19) ✅
- **Phase 3.0**: Professional Installer System

### v1.119.0 and earlier
- Core VRS Check features, 10-Key matching, TWO-PASS algorithm

---

## Quick Links

- **Latest Release:** https://github.com/NeilVibe/VRS-Manager/releases/latest
- **Change Types Reference:** `docs/CHANGE_TYPES_REFERENCE.md`
- **Version Check:** `python3 check_version_unified.py`
