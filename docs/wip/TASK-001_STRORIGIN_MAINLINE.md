# TASK-001: StringOrigin & Mainline Translation Logic

**Status:** COMPLETED
**Requested:** 2025-12-18
**Requester:** 닐 Neil
**Completed:** 2025-12-18
**Version:** v12181815+

---

## Summary

Two changes to the stringorigin and mainline translation handling logic, applied to both WORKING and ALLLANG processors.

---

## Change 1: StrOrigin uses NEW value

**When:** StringOrigin change + row has status

| Field | Before | After |
|-------|--------|-------|
| text | previous | previous (unchanged) |
| strorigin | **previous** | **NEW (from curr_row)** |

### Implementation
```python
# src/core/import_logic.py - Line 55 (WORKING)
result[COL_STRORIGIN] = safe_str(curr_row.get(COL_STRORIGIN, ""))  # NEW strorigin
```

---

## Change 2: NO TRANSLATION override (ALL change types)

**When:** Previous text = "NO TRANSLATION" (ANY change type, not just StrOrigin)

| Condition | Before | After |
|-----------|--------|-------|
| prev_text = "NO TRANSLATION" | Only on StrOrigin change | **ALL change types** |

### Logic
```
IF prev_text == "NO TRANSLATION":
    text = CURRENT (nothing to preserve)
    return early (skip other logic)
```

### Implementation
```python
# src/core/import_logic.py
# Lines 42-46 (WORKING) and Lines 120-123 (ALLLANG)
# NO TRANSLATION override: always bring current text (nothing to preserve)
if prev_text == "NO TRANSLATION":
    result[COL_TEXT] = safe_str(curr_row.get(COL_TEXT, ""))
    result[COL_DESC] = safe_str(prev_row.get(COL_DESC, "")) if prev_row else ""
    return result
```

---

## Files Modified

| File | Lines | Changes |
|------|-------|---------|
| `src/core/import_logic.py` | 41-56 | WORKING processor |
| `src/core/import_logic.py` | 116-129 | ALLLANG processor |

---

## Test Results

- **518/518 tests passed** (100%)

---

## Additional: CI Pipeline Executive Power

Also implemented auto-version generation (copied from LocalizationTools):

| File | Change |
|------|--------|
| `.github/workflows/build-installers.yml` | Auto-generate version MMDDHHMM |
| `scripts/check_version_unified.py` | Added `--skip-timestamp` flag |

---

*Completed: 2025-12-18*
