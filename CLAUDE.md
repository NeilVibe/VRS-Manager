# Claude Code Reference - VRS Manager

**Version:** v12121619

---

## Navigation

| What | Where |
|------|-------|
| **Active tasks** | `roadmap.md` → `WIP/` |
| **Version history** | `history/` |
| **Change types** | `docs/CHANGE_TYPES_REFERENCE.md` |
| **Build/CI** | `docs/BUILD.md` |

---

## Source Code

```
src/core/
├── change_detection.py ... Detection + priority
├── working_comparison.py . WORKING processor
├── comparison.py ......... RAW processor
├── alllang_helpers.py .... ALLLANG processor
└── import_logic.py ....... Import rules

src/config.py ............. Column names, constants
src/settings.py ........... User settings
```

---

## Commands

```bash
python3 tests/test_unified_change_detection.py  # Tests
python3 scripts/check_version_unified.py        # Version check
```

---

## Critical Pattern

```python
value = safe_str(row.get(COL_NAME, ""))  # ALWAYS
value = row[COL_NAME]                     # NEVER - dict errors
```
