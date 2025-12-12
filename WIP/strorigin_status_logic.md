# WIP: StrOrigin + Status Logic Update

**Task:** Update Working process StrOrigin handling
**Date:** Dec 12, 2025

---

## Requirements

1. **Remove "NEED CHECK"** - Delete all logic that sets STATUS = "NEED CHECK"

2. **StrOrigin preservation**:
   - Previous row has **ANY status** (non-empty) → Keep **PREVIOUS StrOrigin**
   - Previous row has **NO status** (empty) → Use **CURRENT StrOrigin** (mainline)

3. **PICKUP / ISSUE** - No code change needed (already preserved as status values)

---

## Files to Modify

| File | Change |
|------|--------|
| `src/core/import_logic.py` | Remove "NEED CHECK" logic |
| `src/core/alllang_helpers.py` | Remove "NEED CHECK" logic |
| `src/core/working_comparison.py` | Add StrOrigin swap based on status |

---

## Current Logic (import_logic.py:42-53)

```python
if "StrOrigin" in change_type:
    if is_after_recording:
        # Preserve all previous data
        result[COL_TEXT] = prev_row Text
        result[COL_STATUS] = prev_status
    else:
        # Use current text, mark for review
        result[COL_TEXT] = curr_row Text
        result[COL_STATUS] = "NEED CHECK"  # <- REMOVE THIS
```

---

## New Logic

```python
if "StrOrigin" in change_type:
    if prev_status:  # ANY status exists
        # Preserve previous data + StrOrigin
        result[COL_TEXT] = prev_row Text
        result[COL_STATUS] = prev_status
        # Also swap StrOrigin to previous
    else:
        # No status - use current/mainline
        result[COL_TEXT] = curr_row Text
        # No NEED CHECK - leave status empty
```

---

## Test Cases

- [ ] StrOrigin change + status "PICKUP" → keep prev StrOrigin
- [ ] StrOrigin change + status "ISSUE" → keep prev StrOrigin
- [ ] StrOrigin change + status "RECORDED" → keep prev StrOrigin
- [ ] StrOrigin change + status "" (empty) → use current StrOrigin
- [ ] No StrOrigin change → normal behavior
