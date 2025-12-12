# VRS Manager - Roadmap Archive

**Archived:** Dec 12, 2025 | **Last Version:** v12051348

---

## Version History

| Version | Date | Key Features |
|---------|------|--------------|
| v12051348 | Dec 5, 2025 | Settings toggle, Super Group improvements, timestamp validation |
| v12031417 | Dec 3, 2025 | Priority CHANGES, DETAILED_CHANGES, PreviousEventName |
| v12021800 | Dec 2, 2025 | Unified change detection (518 tests) |
| v1121 | Nov 21, 2025 | Word-level diff, StrOrigin Analysis |
| v1118 | Nov 18, 2025 | Super Group Analysis, BERT semantic similarity |
| v1117 | Nov 17, 2025 | TimeFrame preservation logic |
| v1116 | Nov 16, 2025 | TWO-PASS algorithm, 10-Key matching |

---

## v12051348 Details

- SETTINGS button - Toggle Priority Change ON/OFF
  - ON: Priority CHANGES + colors (new behavior)
  - OFF: DETAILED_CHANGES only + colors (legacy behavior)
- Super Group Analysis improvements
  - Add Narration Dialog tracking (from DialogType column)
  - Add "Item" to Other super group cluster
  - Main Chapters: keyword-based (chapter/intro/prolog/epilog)
  - NET CHANGE explanation added below table
  - Custom table order (not alphabetical)
- Build Safety: Timestamp validation (KST to UTC)
- Case-insensitive matching for all super group lookups

---

## Architecture Notes (Historical)

### TWO-PASS Algorithm
- PASS 1: Detect No Change / New rows (certainties)
- PASS 2: Detect partial changes using unmarked previous rows

### 10-Key Matching System
Keys: SE, SO, SC, EO, EC, OC, SEO, SEC, SOC, EOC
(S=Sequence, E=Event, O=StrOrigin, C=CastingKey)

### 9 Change Types
StrOrigin, Desc, CastingKey, TimeFrame, Group, EventName, SequenceName, DialogType, CharacterGroup
