# Claude Code Reference - VRS Manager

**Version:** v12051333 | **Status:** Production Ready

---

## 📚 DOCUMENTATION TREE

```
CLAUDE.md (YOU ARE HERE - THE HUB)
│
├── 📖 USER DOCS
│   ├── README.md ................ Project overview, features, installation
│   ├── README_KR.md ............. Korean version
│   ├── docs/WIKI_CONFLUENCE.md .. Complete user guide (EN)
│   └── docs/QUICK_START.md ...... Basic usage
│
├── 🔧 DEVELOPER DOCS
│   ├── docs/CHANGE_TYPES_REFERENCE.md ... All 9 change types, composites, priority
│   ├── docs/DEVELOPER_GUIDE.md .......... Developer onboarding
│   ├── docs/BUILD.md .................... Build system, CI/CD, installers
│   └── docs/BERT_MODEL_SETUP.md ......... Korean BERT (FULL build only)
│
├── 📊 PROJECT STATUS
│   └── roadmap.md ............... Version history, what's current
│
├── 🧪 TESTS
│   ├── tests/test_unified_change_detection.py ... 518 tests (core)
│   └── tests/test_phase4_comprehensive.py ....... 48 tests (Phase 4)
│
├── 📜 SCRIPTS
│   ├── scripts/check_version_unified.py .... Version consistency check
│   └── scripts/update_excel_guides.py ...... Regenerate Excel guides
│
└── 💻 SOURCE CODE
    ├── src/config.py ................. Column names, constants
    ├── src/core/change_detection.py .. Unified detection + priority
    ├── src/core/comparison.py ........ RAW processor logic
    ├── src/core/working_comparison.py  WORKING processor logic
    ├── src/core/alllang_helpers.py ... ALLLANG processor logic
    └── src/processors/*.py ........... Processor orchestrators
```

---

## 🔧 COMMON TASKS

| Task | Command |
|------|---------|
| **Build** | `echo "Trigger LIGHT build" >> BUILD_TRIGGER.txt && git add . && git commit -m "Trigger build" && git push` |
| **Run Tests** | `python3 tests/test_unified_change_detection.py` |
| **Check Versions** | `python3 scripts/check_version_unified.py` |
| **Update Excel** | `python3 scripts/update_excel_guides.py` |

Build status: https://github.com/NeilVibe/VRS-Manager/actions

---

## 📊 OUTPUT COLUMNS (v12051333)

| Column | Description |
|--------|-------------|
| **CHANGES** | Priority-based label (most important change) |
| **DETAILED_CHANGES** | Full composite (all changes) |
| **PreviousEventName** | Old EventName (when changed) |
| **PreviousText** | Previous translation (all matched rows) |

**Priority:** StrOrigin → Desc → CastingKey → TimeFrame → Group → EventName → SequenceName → DialogType → CharacterGroup

---

## ⚠️ CRITICAL PATTERN

```python
# ALWAYS use:
value = safe_str(row.get(COL_NAME, ""))

# NEVER use:
value = row[COL_NAME]  # Can cause dict errors
```

---

## 🚀 FRESH START

1. You're reading the HUB ✓
2. Check `roadmap.md` for current version
3. Run `git log --oneline -5` for recent work
4. Run tests to verify environment
