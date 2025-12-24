# Issue List - VRS Manager

**Last Updated:** 2025-12-24

---

## Resolved Issues

### V5-001: Fixed columns truncated in UI (RESOLVED)
**Reported:** 2025-12-24
**Status:** FIXED

**Problem:** FIXED COLUMNS section showed truncated list like "SequenceName, EventName, StrOrigin, CharacterKey... (10 total)" instead of full column list.

**Fix:** Changed to show full comma-separated list with wraplength for text wrapping:
```python
# Before
mandatory_text = ", ".join(MANDATORY_COLUMNS[:4]) + f"... ({len(MANDATORY_COLUMNS)} total)"

# After
mandatory_text = ", ".join(MANDATORY_COLUMNS)  # Full list with wraplength=880
```

---

### V5-002: Previous_ prefix shown prematurely in UI (RESOLVED)
**Reported:** 2025-12-24
**Status:** FIXED

**Problem:** When uploading PREVIOUS file, checkboxes showed "Previous_FREEMEMO" etc. This was confusing because:
- User is just selecting which columns to include
- The prefix is an implementation detail (only needed in output)
- Columns aren't conflicting with anything at selection time

**Fix:** Removed prefix from checkbox display. User sees original column name ("FREEMEMO"), prefix is only added in output processing.
```python
# Before
text=f"Previous_{col}",

# After
text=col,  # No prefix - user sees original column name
```

---

### V5-003: Unclear info text about "New Rows" (RESOLVED)
**Reported:** 2025-12-24
**Status:** FIXED

**Problem:** Info text "New Rows will have empty PREVIOUS values" was unclear. User didn't understand what "New Row" means.

**Fix:** Clarified to explain the matching concept:
```
Before: "New Rows will have empty PREVIOUS values"

After: "Output will show as 'Previous_ColumnName'. Rows that only exist in
CURRENT (no match in PREVIOUS) will have empty values."
```

---

## Open Issues

(None currently)

---

*This file tracks UI/UX issues and their resolutions.*
