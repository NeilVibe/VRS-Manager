# VRS Manager - Development Roadmap

## 📝 Version Update Checklist

**After completing any code work that changes the version, update ALL of these files:**

```bash
# 1. Run version check FIRST to see current state
python3 scripts/check_version_unified.py

# 2. Update files (see CLAUDE.md for full list)
# 3. Run check again - must pass before commit
```

---

## 📋 Current Status

**Version:** v11272210 (November 27, 2025)
**Status:** Production Ready - Unified Change Detection System

---

## ✅ COMPLETED: Phase 3.1.1b - Unified Change Detection

**Completed:** 2025-11-28
**Status:** ✅ DONE - 518 test cases passing

### What Was Done

1. **Created unified detection function:** `src/core/change_detection.py`
   - Single source of truth: `detect_all_field_changes()`
   - All 9 change types detected consistently
   - CharacterGroup treated equally (no special early return)
   - Canonical order: CharacterGroup → EventName → StrOrigin → SequenceName → CastingKey → Desc → TimeFrame → DialogType → Group

2. **Updated all processors to use unified detection:**
   - RAW processor: ✅
   - WORKING processor: ✅
   - Both produce identical results

3. **Created comprehensive test:**
   - `tests/test_unified_change_detection.py`
   - 518 test cases covering all combinations
   - Uses exact production code (no mocks)
   - Row-by-row validation

4. **Cleaned up test infrastructure:**
   - Archived 13 old/broken test files → `tests/archive/old_tests/`
   - Archived 18 old Excel files → `tests/archive/old_excel_files/`
   - Primary test: `test_unified_change_detection.py`

5. **Updated documentation:**
   - `docs/CHANGE_TYPES_REFERENCE.md` - Complete rewrite
   - `CLAUDE.md` - Updated hub references

### Test Results
```
✅ RAW: 518/518 (100.0%)
✅ WORKING: 518/518 (100.0%)
```

---

## 📋 Next Priority: Phase 3.1.2 - Expand to AllLang Process

**Status:** Not Started

### Scope
- Apply unified detection to ALLLANG processor
- Ensure same 518 test cases pass for ALLLANG

### Files to Update
- `src/core/alllang_helpers.py` - Use `detect_all_field_changes()`

---

## 📋 Future Priorities

### Phase 3.2 - Self-Monitoring Infrastructure
- ✅ Version unification check script (DONE)
- Additional monitoring tools TBD

### Phase 4.0 - TBD
- User feedback driven

---

## Version History

### v11272210 (Current - 2025-11-28) ✅
- **Phase 3.1.1b COMPLETE**: Unified Change Detection
- Single source of truth: `src/core/change_detection.py`
- All 9 change types + 502 composites working
- CharacterGroup included in composites (no special treatment)
- 518 test cases passing for RAW and WORKING
- Test infrastructure cleanup

### v11272115 (2025-11-27) ✅
- **Phase 3.1.1a**: Standalone Change Detection Fix (Partial)
- Fixed PASS 1 standalone detection

### v11201321 (2025-11-20) ✅
- **Phase 3.1.1**: Word-Level Diff Enhancement

### v1.120.0 (2025-11-19) ✅
- **Phase 3.0**: Professional Installer System
- LIGHT (~150MB) and FULL (~2.6GB) installers

### v1.119.0 and earlier
- Core VRS Check features
- 10-Key matching
- TWO-PASS algorithm

---

## Quick Links

- **Latest Release:** https://github.com/NeilVibe/VRS-Manager/releases/latest
- **Change Types Reference:** `docs/CHANGE_TYPES_REFERENCE.md`
- **Primary Test:** `tests/test_unified_change_detection.py`
- **Version Check:** `python3 scripts/check_version_unified.py`
