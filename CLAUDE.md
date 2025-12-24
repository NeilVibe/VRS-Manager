# CLAUDE.md - VRS Manager Navigation Hub

**Version:** v12242254 | **Status:** Production | **Tasks:** 1 active

> **KEEP THIS FILE COMPACT.** Details in linked docs.

---

## Quick Navigation

| Need | Go To |
|------|-------|
| **Current task?** | [roadmap.md](roadmap.md) |
| **Session context?** | [docs/wip/SESSION_CONTEXT.md](docs/wip/SESSION_CONTEXT.md) |
| **Active WIP?** | [docs/wip/](docs/wip/) |
| **Change types?** | [docs/CHANGE_TYPES_REFERENCE.md](docs/CHANGE_TYPES_REFERENCE.md) |
| **Build/CI?** | [docs/BUILD.md](docs/BUILD.md) |
| **History?** | [history/](history/) |

---

## Glossary

| Term | Meaning |
|------|---------|
| **RM** | roadmap.md - global priorities |
| **WIP** | docs/wip/*.md - active task files |
| **SC** | SESSION_CONTEXT.md - Claude handoff |
| **strorigin** | String origin column (source of text) |
| **mainline** | Main translation file reference |
| **WORKING** | Processor for working files |
| **RAW** | Processor for raw comparison |

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

## Versioning (Executive Power)

**CI auto-generates version on every build - DO NOT manually update!**

- Format: `vMMDDHHMM` (KST timezone)
- CI updates all 12 files automatically
- CI commits: `build: Auto-version vXXXX [skip ci]`
- Installer filename matches: `VRSManager_vXXXX_Light_Setup.exe`

See [docs/BUILD.md](docs/BUILD.md) for details.

---

## Quick Commands

```bash
# Run tests (518 tests)
python3 tests/test_unified_change_detection.py

# Check version (informational only - CI handles this)
python3 scripts/check_version_unified.py
```

---

## Critical Pattern

```python
value = safe_str(row.get(COL_NAME, ""))  # ALWAYS
value = row[COL_NAME]                     # NEVER - dict errors
```

---

## New Session Checklist

1. Read [roadmap.md](roadmap.md)
2. Read [SESSION_CONTEXT.md](docs/wip/SESSION_CONTEXT.md)
3. Check [docs/wip/](docs/wip/) for active tasks
4. Ask user what to do

---

## Claude Behavior

1. **Be frank** - Bad idea? Say so
2. **Independent** - Give honest opinions
3. **Optimal first** - Best approach first
4. **Don't command** - Present info, user decides

---

*Last updated: 2025-12-24 | Hub file - details in linked docs*
