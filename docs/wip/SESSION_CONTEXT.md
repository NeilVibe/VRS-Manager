# Session Context - Claude Handoff Document

**Last Updated:** 2025-12-22
**Version:** v12181615 (production)
**Status:** TASK-002 ready for implementation

---

## Current State

| Item | Status |
|------|--------|
| Production | Stable (v12181615) |
| Git | Clean, up to date with origin/main |
| New Task | TASK-002 - Customizable Columns |

---

## Active Task: TASK-002 Customizable Output Columns

**WIP File:** [TASK-002-CUSTOMIZABLE-COLUMNS.md](TASK-002-CUSTOMIZABLE-COLUMNS.md)

### Colleague Request (Korean conversation summary)

1. **HasAudio Column** - Add to output next to Mainline Translation
2. **Customizable Columns** - Let users choose which columns appear in WORK output

### Key Decisions Confirmed

- **Mandatory columns** - Core identification + VRS logic (cannot disable)
- **Auto-generated columns** - Created by VRS logic (user can toggle)
- **Optional columns** - From source files (user can toggle)
- **Persistence** - Save to JSON so users don't reset each session
- **Column source** - User can choose CURRENT or PREVIOUS for each optional column
- **HasAudio placement** - After Mainline Translation
- **Defaults** - All optional columns ON by default, user deactivates if wanted

### Status

Ready for implementation - all decisions confirmed

---

## Column Classification Summary

**MANDATORY (10):** SequenceName, EventName, StrOrigin, CharacterKey, CharacterName, CastingKey, DialogVoice, Text, STATUS, CHANGES

**AUTO-GENERATED (6):** PreviousData, PreviousText, PreviousEventName, DETAILED_CHANGES, Previous StrOrigin, Mainline Translation

**OPTIONAL (17+):** Desc, FREEMEMO, SubTimelineName, StartFrame, EndFrame, DialogType, Group, UpdateTime, Tribe, Age, Gender, Job, Region, HasAudio, UseSubtitle, Record, isNew

---

## Previous Session (2025-12-18)

### Completed Changes
- StrOrigin uses NEW value on StringOrigin changes
- NO TRANSLATION override applies to ALL change types
- CI auto-version pipeline

### Files Modified (previous session)
```
src/core/import_logic.py      # Core logic changes
src/config.py                 # VERSION update
.github/workflows/*.yml       # CI auto-version
```

---

## Quick Commands

```bash
# Run tests
python3 tests/test_unified_change_detection.py

# Check version
python3 scripts/check_version_unified.py

# Git status
git status
```

---

*This document is the source of truth for session handoff.*
