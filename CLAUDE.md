# Claude Code Reference - VRS Manager

## QUICK PROJECT STATUS
**Current Version:** v1118.6
**Status:** Production Ready - All critical bugs fixed
**Last Major Fix:** Dict error in Working VRS Check
**Next Priority:** Phase 2.3 (StrOrigin Change Analysis) - see roadmap.md

## BUILD ("build it", "trigger build")
```bash
# Update BUILD_TRIGGER.txt and push to main
echo "Build v1118.X" >> BUILD_TRIGGER.txt
git add BUILD_TRIGGER.txt
git commit -m "Trigger build v1118.X"
git push origin main
```
Build starts automatically, check: https://github.com/NeilVibe/VRS-Manager/actions

## VERSION UNIFICATION (CRITICAL!)
**Current Version: 1118.6** - Update ALL these files together:
```bash
# 1. src/config.py - VERSION and VERSION_FOOTER
# 2. main.py - Docstring (line 5) and print statements (lines 12-15)
# 3. README.md - Version (line 3)
# 4. README_KR.md - Version (line 3)
# 5. roadmap.md - Current Status header + Version History
# 6. update_excel_guides.py - VERSION, VERSION_TEXT_EN/KR, content
# 7. WIKI_CONFLUENCE.md - Version references
```

**Check version consistency:**
```bash
grep -r "1118\." --include="*.py" --include="*.md" | grep -v test | grep -v ".git"
```

## UPDATE EXCEL GUIDES
**Script:** `update_excel_guides.py`
**Purpose:** Updates EN/KR Excel guides with new version info

**Edit these variables:**
```python
VERSION = "1118.6"
VERSION_TEXT_EN = "Version 1118.6 (Brief description)"
VERSION_TEXT_KR = "버전 1118.6 (간단한 설명)"
EN_CONTENT = [...]  # Add new features
KR_CONTENT = [...]  # Add Korean translation
```

**Run:**
```bash
python3 update_excel_guides.py
git add VRS_Manager_Process_Guide_*.xlsx
git commit -m "Update Excel guides to v1118.X"
```

## ROADMAP.MD (PROJECT BIBLE)
**Location:** `/home/neil1988/vrsmanager/roadmap.md`
**Purpose:** Complete project status, version history, implementation plans

**Key Sections:**
- **Current Status** - What version we're at
- **Version Checklist** - Files to update for new versions
- **Current Priority** - What to work on next (Phase 2.3)
- **Version History** - What each version added
- **Future Considerations** - Planned features

**ALWAYS check roadmap.md first to understand:**
1. Current version and status
2. What's been completed
3. What needs to be done next
4. Implementation requirements for upcoming features

## TESTING
```bash
python3 test_5000_perf.py      # Performance (879 rows/sec expected)
python3 test_accuracy.py       # Accuracy (100% expected)
python3 test_math_verify.py    # Math verification
```

## CRITICAL PATTERN (DataFrame access)
```python
# ALWAYS use this:
value = safe_str(row.get(COL_NAME, ""))

# NEVER use this:
value = row[COL_NAME]  # ✗ Can cause dict errors
```

## CORE FILES
- `src/core/comparison.py` - Raw VRS Check
- `src/core/working_comparison.py` - Working VRS Check
- `src/core/lookups.py` - 10-key lookups (Raw)
- `src/core/working_helpers.py` - 10-key lookups (Working)

## FRESH CLAUDE SETUP
**When starting fresh, read these in order:**
1. `CLAUDE.md` (this file) - Quick reference
2. `roadmap.md` - Full project status
3. `README.md` - Project overview
4. Recent git commits - Latest changes

**Quick context check:**
```bash
# Check version consistency
grep -r "1118\." --include="*.py" --include="*.md" | head -10

# Check recent work
git log --oneline -10

# Check current priority
head -50 roadmap.md | grep "Priority"
```

## COMMIT FORMAT
```
Brief summary

CHANGES:
- What changed
- Why it changed

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
