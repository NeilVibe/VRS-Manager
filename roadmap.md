# VRS Manager - Roadmap

**Version:** v12181615 | **Status:** Production | **Tasks:** 1 active

---

## Active Work

| ID | Task | Status | File |
|----|------|--------|------|
| TASK-001 | StringOrigin & Mainline Logic | IN PROGRESS | [docs/wip/TASK-001_STRORIGIN_MAINLINE.md](docs/wip/TASK-001_STRORIGIN_MAINLINE.md) |

**Session context:** [docs/wip/SESSION_CONTEXT.md](docs/wip/SESSION_CONTEXT.md)

---

## TASK-001 Summary

**Requester:** 닐 Neil (2025-12-18)

### Change 1: StringOrigin Change
- **Current:** strorigin change → text = mainline translation
- **Requested:** strorigin change → text = **previous text**, strorigin = new value

### Change 2: Mainline Loading Condition
- **Current:** no status → use mainline translation
- **Requested:** no status AND text == "NO TRANSLATION" → use mainline

---

## v12121619 Changes (Previous)

- Removed "NEED CHECK" status logic
- StrOrigin preserved when ANY status exists
- Mainline StrOrigin used only when no status

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

*Last updated: 2025-12-18*
