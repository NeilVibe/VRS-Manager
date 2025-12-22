# VRS Manager - Roadmap

**Version:** v12181615 | **Status:** Production | **Tasks:** 1 active

---

## Active Work

| ID | Task | Status | File |
|----|------|--------|------|
| TASK-002 | Customizable Output Columns + HasAudio | PLANNING | [docs/wip/TASK-002-CUSTOMIZABLE-COLUMNS.md](docs/wip/TASK-002-CUSTOMIZABLE-COLUMNS.md) |
| TASK-001 | StringOrigin & Mainline Logic | COMPLETED | [docs/wip/TASK-001_STRORIGIN_MAINLINE.md](docs/wip/TASK-001_STRORIGIN_MAINLINE.md) |

**Session context:** [docs/wip/SESSION_CONTEXT.md](docs/wip/SESSION_CONTEXT.md)

---

## TASK-002 Summary (Current)

**Requester:** Colleague via Neil (2025-12-22)

### Feature 1: HasAudio Column
- Add `HasAudio` to WORK output
- Source: Already in CURRENT file
- Place next to Mainline Translation

### Feature 2: Customizable Columns
- Mandatory columns (always shown, cannot disable)
- Auto-generated columns (VRS creates, user can toggle)
- Optional columns (from source files, user can toggle)
- Persist settings to JSON

---

## TASK-001 Summary (Completed)

**Completed:** 2025-12-18

- StrOrigin change → text = previous, strorigin = NEW value
- NO TRANSLATION → always use current text (all change types)

---

## Architecture

- **TWO-PASS algorithm** - Prevents 1-to-many matching
- **10-Key matching** - SE, SO, SC, EO, EC, OC, SEO, SEC, SOC, EOC
- **9 Change Types** - StrOrigin, Desc, CastingKey, TimeFrame, Group, EventName, SequenceName, DialogType, CharacterGroup
- **Priority System** - Shows most important change in CHANGES column

---

## Quick Commands

```bash
python3 tests/test_unified_change_detection.py  # 518 tests
python3 scripts/check_version_unified.py        # Version check
```

---

## Quick Navigation

| Need | Go To |
|------|-------|
| **Session state?** | [docs/wip/SESSION_CONTEXT.md](docs/wip/SESSION_CONTEXT.md) |
| **WIP tasks?** | [docs/wip/](docs/wip/) |
| **History?** | [history/](history/) |

---

## Links

- **Releases:** https://github.com/NeilVibe/VRS-Manager/releases
- **Build Status:** https://github.com/NeilVibe/VRS-Manager/actions

---

*Last updated: 2025-12-22*
