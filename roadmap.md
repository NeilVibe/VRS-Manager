# VRS Manager - Development Roadmap

## 📋 Current Status

**Version:** v12031411 (December 2, 2025)
**Status:** Production Ready - Phase 4 Complete

---

## ✅ Phase 4 - User Requested Features (COMPLETED)

**Status:** ✅ Complete
**Requested by:** 닐님, 레베카 (Rebecca)
**Date:** 2025-12-02

---

### Feature 4.1: PreviousEventName Column ✅

**Requestor:** 닐님
**Description:** When EventName changes, show the old EventName value.
**When to populate:** Only when change type includes "EventName Change"
**Status:** ✅ Implemented in RAW, WORKING, ALLLANG processors

---

### Feature 4.2: Priority CHANGES Column ✅

**Requestor:** 레베카 (Rebecca)
**Description:** Simplified priority-based change label at current CHANGES position. Full composite moved to DETAILED_CHANGES (far right).

**Priority Ranking (for composites only):**
```
1. StrOrigin Change      (highest priority)
2. Desc Change
3. CastingKey Change
4. TimeFrame Change
5. Group Change
6. EventName Change
7. SequenceName Change
8. DialogType Change
9. CharacterGroup Change (lowest priority)
```

**Example:**
```
Composite detected: "EventName+StrOrigin+Desc Change"
CHANGES:          "StrOrigin Change" (priority label)
DETAILED_CHANGES: "EventName+StrOrigin+Desc Change" (full composite)
```

**Status:** ✅ Implemented with `get_priority_change()` function

---

### Feature 4.3: PreviousText Column ✅

**Requestor:** 레베카 (Rebecca)
**Description:** Extract previous Text/Translation into its own column.
**When to populate:** Always for matched rows (not "New Row")
**Status:** ✅ Implemented in RAW, WORKING, ALLLANG processors

---

### Phase 4 Test Results

- ✅ **518/518** unified tests pass (RAW processor)
- ✅ **518/518** unified tests pass (WORKING processor)
- ✅ **48/48** Phase 4 specific tests pass
- ✅ All 3 processors unified (RAW, WORKING, ALLLANG)

### Phase 4 Files Modified

- `src/core/change_detection.py` - Added `get_priority_change()` and `PRIORITY_RANKING`
- `src/core/working_comparison.py` - Added Phase 4 columns
- `src/core/alllang_helpers.py` - Added Phase 4 columns
- `src/processors/raw_processor.py` - Added Phase 4 columns
- `src/config.py` - Added column constants, updated OUTPUT_COLUMNS
- `tests/test_phase4_comprehensive.py` - New comprehensive test (48 cases)

---

## ✅ Phase 4.5 - CastingKey Validation (COMPLETED)

**Status:** ✅ Complete
**Date:** 2025-12-03

### Feature 4.5.1: CastingKey Source Column Validation ✅

**Problem:** CastingKey is generated from source columns. Missing columns cause false positives.

**Solution:**
1. **Terminal Warning:** Log missing columns with clear explanation
2. **Error Label:** "CastingKey Change" → "CastingKey Error" when data incomplete

**Status:** ✅ Implemented

### Feature 4.5.2: CastingKey Case Normalization ✅

**Problem:** Different branches returned different cases (original vs lowercase).

**Solution:** All branches now return lowercase for consistent comparison.

**Status:** ✅ Fixed

### Feature 4.5.3: Speaker|CharacterGroupKey from CURRENT Only ✅ (CRITICAL)

**Problem:** `Speaker|CharacterGroupKey` may not exist or be reliable in PREVIOUS file.

**Solution - CRITICAL CHANGE:**
- `Speaker|CharacterGroupKey` is read **ONLY from CURRENT file**
- This same value is used to generate CastingKey for **BOTH** PREVIOUS and CURRENT rows
- Lookup by (SequenceName, EventName) to match PREVIOUS rows to CURRENT's Speaker|CharacterGroupKey

**CastingKey Column Requirements:**

| Column | PREVIOUS | CURRENT | Notes |
|--------|----------|---------|-------|
| CharacterKey | ✅ Required | ✅ Required | From each file |
| DialogVoice | ✅ Required | ✅ Required | From each file |
| DialogType | ✅ Required | ✅ Required | From each file |
| Speaker\|CharacterGroupKey | ❌ Not needed | ✅ Required | **CURRENT only, used for BOTH** |

**Output Columns:**
- `Speaker|CharacterGroupKey` is **NOT** in output columns (used internally only)
- `CastingKey` **IS** in output columns (the generated result)

**Files Modified:**
- `src/core/casting.py` - Updated validation with `is_current` parameter
- `src/processors/raw_processor.py` - Build lookup from CURRENT, use for BOTH
- `src/processors/working_processor.py` - Build lookup from CURRENT, use for BOTH

**Test File:** `tests/test_castingkey_speaker_gk.py` (6 test cases)

**Status:** ✅ Implemented and tested (518/518 + 48/48 + 6/6 tests pass)

---

## ✅ CI/CD Safety Checks (Dec 2025)

**Inspired by:** LocalizationTools CI/CD patterns

Build now includes mandatory safety checks before proceeding:

```
┌─────────────────────────────────────────────────────────────┐
│  SAFETY CHECKS (must pass or build is blocked)              │
├─────────────────────────────────────────────────────────────┤
│  1. Version Unification Check                               │
│     → All 12 files must have same version                   │
│     → Blocks build on mismatch                              │
│                                                             │
│  2. Core Tests (518 test cases)                             │
│     → RAW processor tests                                   │
│     → WORKING processor tests                               │
│                                                             │
│  3. Phase 4 Tests (48 test cases)                           │
│     → Priority ranking validation                           │
│     → All 9 change types tested                             │
│                                                             │
│  4. Security Audit (pip-audit)                              │
│     → Checks for vulnerable dependencies                    │
│     → Informational only (doesn't block)                    │
└─────────────────────────────────────────────────────────────┘
```

**Build blocked if:**
- Version mismatch detected
- Any test fails

---

## ✅ Completed Work

### Phase 3.1 - Unified Change Detection (Nov 2025)
- Single source of truth: `src/core/change_detection.py`
- All 9 change types + 502 composites working
- 518 test cases passing (RAW, WORKING, ALLLANG)
- Code cleanup: removed ~290 lines dead code

### Phase 3.0 - Professional Installer System (Nov 2025)
- LIGHT installer (~150MB, no BERT)
- FULL installer (~2.6GB, with BERT)
- Modular GitHub Actions build

### Phase 2.x - Core Features (Oct-Nov 2025)
- TWO-PASS algorithm (prevents 1-to-many matching)
- 10-Key matching system
- Word-level diff highlighting
- Version unification check script

### Phase 1.x - Foundation (Earlier)
- Core VRS Check functionality
- RAW/WORKING/ALLLANG processors
- Excel import/export

---

## Quick Links

- **Latest Release:** https://github.com/NeilVibe/VRS-Manager/releases/latest
- **Change Types Reference:** `docs/CHANGE_TYPES_REFERENCE.md`
- **Primary Test:** `tests/test_unified_change_detection.py`
- **Version Check:** `python3 scripts/check_version_unified.py`
