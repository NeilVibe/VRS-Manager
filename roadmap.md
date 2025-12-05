# VRS Manager - Development Roadmap

**Version:** v12051348 | **Status:** Production Ready

---

## 🌳 VERSION TREE

```
CURRENT: v12051348 (Dec 5, 2025) ← YOU ARE HERE
│
├── 🎯 THIS RELEASE
│   ├── SETTINGS button - Toggle Priority Change ON/OFF
│   │   ├── ON: Priority CHANGES + colors (new behavior)
│   │   └── OFF: DETAILED_CHANGES only + colors (legacy behavior)
│   ├── Super Group Analysis improvements
│   │   ├── Add Narration Dialog tracking (from DialogType column)
│   │   ├── Add "Item" to Other super group cluster
│   │   ├── Main Chapters: keyword-based (chapter/intro/prolog/epilog)
│   │   ├── NET CHANGE explanation added below table
│   │   └── Custom table order (not alphabetical)
│   ├── Build Safety: Timestamp validation (KST→UTC)
│   └── Case-insensitive matching for all super group lookups
│
├── 📈 EVOLUTION
│   ├── v12031417 ... Priority CHANGES, DETAILED_CHANGES, PreviousEventName
│   ├── v12021800 ... Unified change detection (518 tests)
│   ├── v1121 ....... Word-level diff, StrOrigin Analysis
│   ├── v1118 ....... Super Group Analysis, BERT semantic similarity
│   ├── v1117 ....... TimeFrame preservation logic
│   └── v1116 ....... TWO-PASS algorithm, 10-Key matching
│
└── 🔗 RELATED DOCS
    ├── CLAUDE.md .............. Documentation hub
    ├── docs/CHANGE_TYPES_REFERENCE.md ... All 9 change types
    └── docs/BUILD.md .......... Build & release process
```

---

## 🔧 Quick Commands

```bash
python3 tests/test_unified_change_detection.py  # 518 tests
python3 tests/test_phase4_comprehensive.py      # 48 tests
python3 scripts/check_version_unified.py        # Version check
```

---

## 🔗 Links

- **Latest Release:** https://github.com/NeilVibe/VRS-Manager/releases/latest
- **Build Status:** https://github.com/NeilVibe/VRS-Manager/actions
