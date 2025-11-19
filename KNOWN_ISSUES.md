# Known Issues - VRS Manager

## Issue #1: NEW/DELETED Row Count Math Discrepancy (2025-11-15)

### Problem Description
The math for NEW and DELETED rows doesn't add up correctly. There's a small discrepancy between the expected and actual row counts.

### Test Case
```
PREVIOUS rows: 71,094
CURRENT rows:  71,824
NEW ROWS:      1,250
DELETED ROWS:  529

Expected: CURRENT = PREVIOUS + NEW - DELETED
Expected: 71,824 = 71,094 + 1,250 - 529
Expected: 71,824 = 71,815

ACTUAL:   71,824
DISCREPANCY: 9 rows
```

**9 rows are missing from the calculation.**

### Possible Causes

#### 1. Stage 2 Fallback "New Row" (comparison.py:175-179)
```python
else:
    change_label = "New Row"
    prev_row = None
```

When `key_cg` matches in `prev_lookup_cg`, but the lookup for the old EventName fails, we mark it as "New Row". This might be creating duplicate "New Row" classifications.

**Question:** Should these be "New Row" or something else?

#### 2. Rows Marked as Changes Instead of "New Row"
Some rows that should be "New Row" might be caught by Stage 2 or Stage 3 and labeled as change types instead (e.g., "EventName+CastingKey Change").

#### 3. Deleted Rows Not Caught by 4-Key Check
Some deleted rows might have 1-3 keys still matching (but not all 4), so they're not counted as deleted.

**Deleted logic (comparison.py:380-384):**
```python
if (key_cw not in curr_keys_cw) and \
   (key_cg not in curr_keys_cg) and \
   (key_es not in curr_keys_es) and \
   (key_cs not in curr_keys_cs):
    deleted_rows.append(row.to_dict())
```

### Investigation Steps

1. **Check change type distribution:**
   - Look at Summary Report in output Excel
   - Sum ALL change type counts (should equal CURRENT rows: 71,824)
   - Identify which change types have the "missing" 9 rows

2. **Verify "New Row" count:**
   - Count rows where CHANGES = "New Row"
   - Should be 1,250, but might be 1,241 or 1,259

3. **Check Stage 2 fallback cases:**
   - Find rows where `key_cg` matched but EventName lookup failed
   - Are these truly new rows or misclassified?

4. **Audit deleted row logic:**
   - Are there rows in PREVIOUS that should be deleted but have 1-3 keys matching?
   - Should DELETED logic be stricter or more lenient?

### Files Involved

- `src/core/comparison.py` - RAW processor NEW/DELETED logic
- `src/core/working_comparison.py` - WORKING processor logic
- `src/processors/master_processor.py` - MASTER processor logic
- `src/core/alllang_helpers.py` - ALLLANG processor logic

### Current Status
- **Status:** OPEN - Needs investigation
- **Impact:** Low (9-row discrepancy in ~71k rows = 0.01% error)
- **Priority:** Medium (math should be exact)

### Next Steps
1. Run test with change type counts output
2. Identify where the 9 rows are classified
3. Determine if it's a NEW row issue or DELETED row issue
4. Fix the logic accordingly
5. Re-test with same files to verify fix

---

## Composite Change Detection Status

### ✅ Completed (2025-11-15)
- Implemented comprehensive composite change detection
- Added 30+ color definitions for change types
- Simplified logic (removed early returns)
- NEW row logic: Only when all 3 primary keys fail (Stage 4)
- DELETED row logic: Only when all 4 keys missing
- Applied consistently across RAW, WORKING, MASTER, ALLLANG processors

### Current Branch
`claude/composite-detection-01QLHXfUtkB2ppE9AY3Em4ft`

**Commit:** "Implement comprehensive composite change detection across all processors"
