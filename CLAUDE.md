# Claude Code Reference - VRS Manager

## QUICK STATUS
**Version:** v12031417 | **Status:** Production Ready

---

## 📚 DOCUMENTATION HUB

### User Documentation
| Doc | Purpose |
|-----|---------|
| `README.md` | Project overview, features, installation |
| `README_KR.md` | Korean version |
| `docs/WIKI_CONFLUENCE.md` | Complete user guide |
| `docs/QUICK_START.md` | Basic usage |

### Developer Documentation
| Doc | Purpose |
|-----|---------|
| `docs/CHANGE_TYPES_REFERENCE.md` | Change detection logic, all 9 types, composites |
| `docs/DEVELOPER_GUIDE.md` | Developer onboarding |
| `docs/BUILD.md` | Build system, installers, CI/CD |
| `docs/BERT_MODEL_SETUP.md` | Korean BERT setup (FULL build only) |

### Project Status
| Doc | Purpose |
|-----|---------|
| `roadmap.md` | Version history, current status |

---

## 🔧 COMMON TASKS

### Build (Default: LIGHT)
```bash
echo "Trigger LIGHT build v$(date '+%m%d%H%M')" >> BUILD_TRIGGER.txt
git add BUILD_TRIGGER.txt && git commit -m "Trigger LIGHT build" && git push
# Check: https://github.com/NeilVibe/VRS-Manager/actions
```

### Run Tests
```bash
python3 tests/test_unified_change_detection.py  # 518 tests
python3 tests/test_phase4_comprehensive.py      # 48 tests
```

### Version Update (12 files)
```bash
python3 scripts/check_version_unified.py  # Shows all files to update
```

### Update Excel Guides
```bash
python3 scripts/update_excel_guides.py
```

---

## 📁 KEY SOURCE FILES

| File | Purpose |
|------|---------|
| `src/core/change_detection.py` | Unified detection + `get_priority_change()` |
| `src/core/comparison.py` | RAW processor logic |
| `src/core/working_comparison.py` | WORKING processor logic |
| `src/core/alllang_helpers.py` | ALLLANG processor logic |
| `src/config.py` | Column names, constants, output order |
| `src/processors/*.py` | Processor orchestrators |

---

## 📊 OUTPUT COLUMNS (v12031417)

| Column | Description |
|--------|-------------|
| **CHANGES** | Priority-based label (most important change) |
| **DETAILED_CHANGES** | Full composite (all changes) |
| **PreviousEventName** | Old EventName (when changed) |
| **PreviousText** | Previous translation (all matched rows) |

**Priority Order:** StrOrigin → Desc → CastingKey → TimeFrame → Group → EventName → SequenceName → DialogType → CharacterGroup

---

## ⚠️ CRITICAL PATTERNS

```python
# DataFrame access - ALWAYS use:
value = safe_str(row.get(COL_NAME, ""))

# NEVER use:
value = row[COL_NAME]  # Can cause dict errors
```

---

## 🚀 FRESH START CHECKLIST

1. Read this file (CLAUDE.md) - you're here
2. Check `roadmap.md` for version history
3. Run `git log --oneline -5` for recent changes
4. Run `python3 scripts/check_version_unified.py` to verify environment
5. Run tests to confirm everything works
