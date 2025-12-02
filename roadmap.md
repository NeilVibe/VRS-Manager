# VRS Manager - Development Roadmap

## 📋 Current Status

**Version:** v12021745 (December 2, 2025)
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
