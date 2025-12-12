# WIP: StrOrigin + Status Logic Update

**Task:** Update Working process StrOrigin handling
**Date:** Dec 12, 2025
**Status:** COMPLETED

---

## Requirements

1. **Remove "NEED CHECK"** - Delete all logic that sets STATUS = "NEED CHECK" ✅

2. **StrOrigin preservation**: ✅
   - Previous row has **ANY status** (non-empty) → Keep **PREVIOUS StrOrigin**
   - Previous row has **NO status** (empty) → Use **CURRENT StrOrigin** (mainline)

3. **PICKUP / ISSUE** - No code change needed (already preserved as status values) ✅

---

## Files Modified

| File | Change |
|------|--------|
| `src/core/import_logic.py` | Removed "NEED CHECK", added COL_STRORIGIN swap |
| `src/core/alllang_helpers.py` | Removed "NEED CHECK", added COL_STRORIGIN swap |
| `src/io/formatters.py` | Removed "NEED CHECK" color definition |

---

## Logic Change Summary

**Before:**
```python
if "StrOrigin" in change_type:
    if is_after_recording:  # Only specific statuses
        preserve previous
    else:
        use current + STATUS = "NEED CHECK"
```

**After:**
```python
if "StrOrigin" in change_type:
    if prev_status:  # ANY status exists
        preserve previous Text + Status + StrOrigin
    else:
        use current (no NEED CHECK)
```

---

## Test Results

- 518/518 tests passed ✅
