# VRS Manager - Roadmap

**Version:** v12242254 | **Status:** Production | **Tasks:** TASK-002 COMPLETE

---

## Active Work

| ID | Task | Status | File |
|----|------|--------|------|
| TASK-002 | Customizable Output Columns + HasAudio | **COMPLETE** | [docs/wip/TASK-002-CUSTOMIZABLE-COLUMNS.md](docs/wip/TASK-002-CUSTOMIZABLE-COLUMNS.md) |
| TASK-001 | StringOrigin & Mainline Logic | COMPLETED | [docs/wip/TASK-001_STRORIGIN_MAINLINE.md](docs/wip/TASK-001_STRORIGIN_MAINLINE.md) |

**Session context:** [docs/wip/SESSION_CONTEXT.md](docs/wip/SESSION_CONTEXT.md)
**Issue tracking:** [docs/wip/ISSUELIST.md](docs/wip/ISSUELIST.md)

---

## TASK-002 Summary (COMPLETE - 2025-12-24)

**Requester:** Colleague via Neil (2025-12-22)

### Features Delivered

1. **HasAudio Column** - Now available in output
2. **Customizable Columns** - Full V5 implementation:
   - 4-tier classification (MANDATORY, VRS_CONDITIONAL, AUTO_GENERATED, OPTIONAL)
   - Dual file upload (CURRENT + PREVIOUS)
   - KEY-based PREVIOUS column matching
   - Previous_ prefix only on CONFLICT
   - Settings persist to JSON
   - Threaded uploads with progress feedback

### V5 Issues Fixed (6 total)

| Issue | Problem | Fix |
|-------|---------|-----|
| V5-001 | FIXED columns truncated | Full list with wrapping |
| V5-002 | Previous_ prefix in checkboxes | Removed - original names shown |
| V5-003 | Info text unclear | Clarified wording |
| V5-004 | Prefix on ALL columns | Only on CONFLICT |
| V5-005 | Dialog too small | 950x850 / minsize 850x750 |
| V5-006 | Upload freezes UI | Threading + progress |

### Tests
- **539 tests pass** (518 unified + 21 column classification)

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
python3 tests/test_column_classification.py     # 21 tests
python3 scripts/check_version_unified.py        # Version check
```

---

## Quick Navigation

| Need | Go To |
|------|-------|
| **Session state?** | [docs/wip/SESSION_CONTEXT.md](docs/wip/SESSION_CONTEXT.md) |
| **Issue tracking?** | [docs/wip/ISSUELIST.md](docs/wip/ISSUELIST.md) |
| **WIP tasks?** | [docs/wip/](docs/wip/) |
| **History?** | [history/](history/) |

---

## Links

- **Releases:** https://github.com/NeilVibe/VRS-Manager/releases
- **Build Status:** https://github.com/NeilVibe/VRS-Manager/actions

---

*Last updated: 2025-12-24*
