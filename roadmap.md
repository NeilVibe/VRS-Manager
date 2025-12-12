# VRS Manager - Roadmap

**Current:** v12121619 | **Status:** Production

---

## Active Work

No active WIP. See `history/` for completed tasks.

---

## v12121619 Changes

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

## Links

- **Releases:** https://github.com/NeilVibe/VRS-Manager/releases
- **Build Status:** https://github.com/NeilVibe/VRS-Manager/actions
- **History:** `history/`
