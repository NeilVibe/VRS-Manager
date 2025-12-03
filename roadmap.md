# VRS Manager - Development Roadmap

## 📋 Current Status

**Version:** v12031417 (December 3, 2025)
**Status:** Production Ready

---

## ✅ Latest Release - v12031417

### Smart Change Classification
- **Priority CHANGES column** - Shows most important change first
- **DETAILED_CHANGES column** - Full composite for complete picture
- **PreviousEventName column** - Track event renames
- **PreviousText column** - See previous translations easily

### Improved Reliability
- CastingKey validation with Speaker|CharacterGroupKey from CURRENT only
- CI/CD safety checks (566 tests must pass before build)
- All documentation updated

---

## ✅ Version History

| Version | Date | Highlights |
|---------|------|------------|
| **v12031417** | Dec 2025 | Priority CHANGES, DETAILED_CHANGES, PreviousEventName, PreviousText |
| v12021800 | Nov 2025 | Unified change detection, 518 test cases |
| v1121 | Nov 2025 | Word-level diff, StrOrigin Analysis sheet |
| v1118 | Nov 2025 | Super Group Analysis, BERT semantic similarity |
| v1117 | Nov 2025 | TimeFrame preservation logic |
| v1116 | Oct 2025 | TWO-PASS algorithm, 10-Key matching |

---

## 🔧 Technical Reference

### Test Suite
```bash
python3 tests/test_unified_change_detection.py  # 518 tests
python3 tests/test_phase4_comprehensive.py      # 48 tests
python3 scripts/check_version_unified.py        # Version check
```

### Key Files
- `src/core/change_detection.py` - Unified detection + priority ranking
- `src/core/comparison.py` - RAW processor logic
- `src/core/working_comparison.py` - WORKING processor logic
- `docs/CHANGE_TYPES_REFERENCE.md` - Complete change type documentation

---

## Quick Links

- **Latest Release:** https://github.com/NeilVibe/VRS-Manager/releases/latest
- **Build Status:** https://github.com/NeilVibe/VRS-Manager/actions
- **Documentation:** `docs/WIKI_CONFLUENCE.md`
