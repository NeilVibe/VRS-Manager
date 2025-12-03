# Claude Code Reference - VRS Manager

## QUICK STATUS
**Version:** v12031417 | **Status:** Production Ready

## DOCUMENTATION HUB

| Topic | File |
|-------|------|
| **Change Detection** | `docs/CHANGE_TYPES_REFERENCE.md` |
| **User Guide** | `docs/WIKI_CONFLUENCE.md` |
| **Version History** | `roadmap.md` |
| **Build/Release** | `docs/BUILD.md` |

## BUILD (Default: LIGHT)

```bash
# Trigger LIGHT build
echo "Trigger LIGHT build v$(date '+%m%d%H%M')" >> BUILD_TRIGGER.txt
git add BUILD_TRIGGER.txt && git commit -m "Trigger LIGHT build" && git push

# Check: https://github.com/NeilVibe/VRS-Manager/actions
```

## VERSION UPDATE WORKFLOW

```bash
# 1. Update version in all files
NEW_VERSION=$(date '+%m%d%H%M')

# 2. Files to update (12 total):
#    src/config.py, main.py, README.md, README_KR.md,
#    installer/*.iss, .github/workflows/build-installers.yml,
#    scripts/update_excel_guides.py, CLAUDE.md, roadmap.md,
#    docs/WIKI_CONFLUENCE.md, src/processors/master_processor.py

# 3. ALWAYS run check before commit
python3 scripts/check_version_unified.py

# 4. If pass → commit and push
```

## TESTING

```bash
python3 tests/test_unified_change_detection.py  # 518 tests
python3 tests/test_phase4_comprehensive.py      # 48 tests
python3 scripts/check_version_unified.py        # Version check
```

## CORE FILES

| File | Purpose |
|------|---------|
| `src/core/change_detection.py` | Unified detection + `get_priority_change()` |
| `src/core/comparison.py` | RAW processor |
| `src/core/working_comparison.py` | WORKING processor |
| `src/core/alllang_helpers.py` | ALLLANG processor |

## OUTPUT COLUMNS (v12031417)

| Column | Description |
|--------|-------------|
| **CHANGES** | Priority-based label (most important change) |
| **DETAILED_CHANGES** | Full composite (all changes) |
| **PreviousEventName** | Old EventName (when changed) |
| **PreviousText** | Previous translation (all matched rows) |

**Priority:** StrOrigin → Desc → CastingKey → TimeFrame → Group → EventName → SequenceName → DialogType → CharacterGroup

## CRITICAL PATTERNS

```python
# DataFrame access - ALWAYS use:
value = safe_str(row.get(COL_NAME, ""))

# NEVER use:
value = row[COL_NAME]  # Can cause dict errors
```

## FRESH START

1. Read this file (CLAUDE.md)
2. Check `roadmap.md` for current status
3. Run `git log --oneline -5` for recent changes
4. Run tests to verify environment
