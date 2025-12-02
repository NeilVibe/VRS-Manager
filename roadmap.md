# VRS Manager - Development Roadmap

## 📋 Current Status

**Version:** v11272210 (December 2, 2025)
**Status:** Production Ready - All Phase 3.1 Complete

---

## 📋 Next Priority: Phase 4 - User Requested Features

**Status:** Planning
**Requested by:** 닐님, 레베카 (Rebecca)
**Date:** 2025-12-02

---

### Feature 4.1: PreviousEventName Column

**Requestor:** 닐님
**Description:** When EventName changes, show the old EventName value.

**When to populate:** Only when change type includes "EventName Change"

**Implementation:**
- Add `PreviousEventName` column to output
- Only populate when change type includes "EventName Change"
- Place column on far right, near other Previous data columns

**Files to modify:**
- `src/core/working_comparison.py` - Extract and store previous EventName
- `src/io/excel_writer.py` - Add column to output

---

### Feature 4.2: Priority CHANGES Column

**Requestor:** 레베카 (Rebecca)
**Description:** Simplified priority-based change label at current CHANGES position. Move detailed changes to far right.

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

**Note:** "New Row" and "No Change" are never composites - they display as-is.

**Implementation:**
- Create `get_priority_change()` function - extracts highest priority from composite
- Add `CHANGES` column at current position (column N) - shows priority label only
- Rename current detailed changes to `DETAILED_CHANGES` - move to far right
- Reuse existing standalone color assignments for highlighting

**Example:**
```
Composite detected: "EventName+StrOrigin+Desc Change"
Priority label:     "StrOrigin Change" (rank 2 beats rank 7 and 3)
```

**Files to modify:**
- `src/core/change_detection.py` - Add `get_priority_change()` function
- `src/io/excel_writer.py` - Column positioning and naming
- `src/processors/*.py` - Update column output order

---

### Feature 4.3: PreviousText Column

**Requestor:** 레베카 (Rebecca)
**Description:** Extract previous Text/Translation into its own column.

**When to populate:** Always (any matched row, regardless of change type)

**Implementation:**
- Add `PreviousText` column to output
- Always populate for matched rows (not "New Row")
- Place column on far right, near other Previous data columns

**Files to modify:**
- `src/core/working_comparison.py` - Store previous text separately
- `src/io/excel_writer.py` - Add column to output

---

### Output Column Order (After Phase 4)

**Front columns (existing + new):**
```
... [existing columns] ...
CHANGES          ← NEW: Priority label only (was detailed)
... [existing columns] ...
```

**Far right columns (grouped):**
```
... [existing columns] ...
PreviousData     ← Existing
PreviousText     ← NEW: Extracted text
PreviousEventName ← NEW: When EventName changed
DETAILED_CHANGES ← MOVED: Full composite label
```

---

### Implementation Order & Plan of Action

**Phase 4.1 - PreviousEventName** (simplest, isolated change)
```
Step 1: Add PreviousEventName extraction in working_comparison.py
Step 2: Add column to excel_writer.py output (far right)
Step 3: Test with WORKING process
```

**Phase 4.3 - PreviousText** (similar pattern to 4.1)
```
Step 1: Add PreviousText extraction in working_comparison.py
Step 2: Add column to excel_writer.py output (far right, next to PreviousEventName)
Step 3: Test with WORKING process
```

**Phase 4.2 - Priority CHANGES** (requires column reorg + new function)
```
Step 1: Add PRIORITY_RANKING dict and get_priority_change() in change_detection.py
Step 2: Rename current CHANGES → DETAILED_CHANGES, move to far right
Step 3: Add new CHANGES column at current position with priority label
Step 4: Update excel_writer.py column ordering
Step 5: Update all processors to use new column structure
Step 6: Test all 9 standalone + composite scenarios
```

**Final Column Order (far right):**
```
PreviousData → PreviousText → PreviousEventName → DETAILED_CHANGES
```

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
