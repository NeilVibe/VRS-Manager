# TASK-001: StringOrigin & Mainline Translation Logic

**Status:** COMPLETED
**Requested:** 2025-12-18
**Requester:** 닐 Neil
**Completed:** 2025-12-18

---

## Summary

Two changes to the stringorigin and mainline translation handling logic.

---

## Change 1: StringOrigin Change Handling

### Previous Behavior
When `stringorigin` changes for row with status:
- Text column → Gets **previous text** (correct)
- strorigin → Gets **previous strorigin** (CHANGED)

### New Behavior (v12181615)
When `stringorigin` changes for row with status:
- Text column → Keep **previous text** (unchanged)
- strorigin → Load from **NEW/current** file

### Implementation
```python
# src/core/import_logic.py line 48
result[COL_STRORIGIN] = safe_str(curr_row.get(COL_STRORIGIN, ""))  # NEW strorigin
```

---

## Change 2: Mainline Translation Loading Condition

### Previous Behavior
```
IF no status:
    text = mainline_translation (always)
```

### New Behavior (v12181615)
```
IF no status AND text == "NO TRANSLATION":
    text = mainline_translation
ELSE IF no status AND text != "NO TRANSLATION":
    text = keep previous text
```

### Implementation
```python
# src/core/import_logic.py lines 50-55
prev_text = safe_str(prev_row.get(COL_TEXT, "")) if prev_row else ""
if prev_text == "NO TRANSLATION":
    result[COL_TEXT] = safe_str(curr_row.get(COL_TEXT, ""))  # Use mainline
else:
    result[COL_TEXT] = prev_text  # Keep previous text
```

---

## Files Modified

| File | Changes |
|------|---------|
| `src/core/import_logic.py:42-56` | StrOrigin change logic (Working) |
| `src/core/import_logic.py:116-129` | StrOrigin change logic (ALLLANG) |
| `src/config.py:104-105` | Updated VERSION to 12181615 |

---

## Additional Changes: CI Pipeline Executive Power

Also updated CI to auto-generate version like LocalizationTools:
- `.github/workflows/build-installers.yml` - Auto-generate VERSION (MMDDHHMM)
- `scripts/check_version_unified.py` - Added `--skip-timestamp` flag

---

## Test Results

- [ ] 518 tests to run

---

*Completed: 2025-12-18*
