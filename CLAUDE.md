# Claude Code Reference - VRS Manager

## QUICK PROJECT STATUS
**Current Version:** v11241313
**Status:** Production Ready - DateTime Versioning Build
**Last Major Feature:** Standalone Change Detection Fix (All 9 Types)
**Next Priority:** Phase 3.1.2 (Expand to AllLang Process) - see roadmap.md

## CRITICAL DOCUMENTATION REFERENCE
**⭐ NEW: Comprehensive Change Types Reference** → `docs/CHANGE_TYPES_REFERENCE.md`
- **Single source of truth** for all 9 core change types + composites
- Detection logic by processor (RAW, WORKING, ALLLANG, MASTER)
- Import logic rules for each change type
- Known bugs and implementation details
- **READ THIS FIRST** when working on change detection!

## VERSIONING SCHEME (NEW!)

**Format:** `MMDDHHMM` (DateTime-based versioning)
- MM = Month (11 = November)
- DD = Day (20)
- HH = Hour (13 = 1 PM)
- MM = Minute (14)

**Example:** `11241313` = November 24, 2025 at 1:13 PM

**Why?** Clear, sortable, and shows when each version was created.

## VERSION UPDATE WORKFLOW (FOLLOW THIS!)

**CRITICAL: Always run check BEFORE commit/push!**

```bash
# 1. Get new datetime version
NEW_VERSION=$(date '+%m%d%H%M')
echo "New version: $NEW_VERSION"

# 2. Update all 12 files manually (see VERSION UNIFICATION section below)
#    - src/config.py
#    - main.py
#    - README.md, README_KR.md
#    - installer/*.iss
#    - .github/workflows/build-installers.yml
#    - update_excel_guides.py
#    - CLAUDE.md, roadmap.md, WIKI_CONFLUENCE.md
#    - src/processors/master_processor.py

# 3. RUN CHECK BEFORE COMMIT! (This catches mistakes!)
python3 check_version_unified.py

# 4. Only if check passes (exit code 0), then commit
git add -A
git commit -m "Version unification: v$NEW_VERSION"
git push origin main

# 5. NOW trigger build
echo "Build v$NEW_VERSION" >> BUILD_TRIGGER.txt
git add BUILD_TRIGGER.txt
git commit -m "Trigger build v$NEW_VERSION"
git push origin main
```

**Golden Rule:** Never commit version changes without running `check_version_unified.py` first!

## BUILD ("build it", "trigger build") - MODULAR SYSTEM

**NEW:** Choose what to build - LIGHT only, FULL only, or BOTH!

```bash
# Option 1: Build LIGHT only (~150MB, no BERT)
echo "Build LIGHT v$(date '+%m%d%H%M')" >> BUILD_TRIGGER.txt
git add BUILD_TRIGGER.txt
git commit -m "Trigger LIGHT build v$(date '+%m%d%H%M')"
git push origin main

# Option 2: Build FULL only (~2.6GB, with BERT)
echo "Build FULL v$(date '+%m%d%H%M')" >> BUILD_TRIGGER.txt
git add BUILD_TRIGGER.txt
git commit -m "Trigger FULL build v$(date '+%m%d%H%M')"
git push origin main

# Option 3: Build BOTH (default)
echo "Build BOTH v$(date '+%m%d%H%M')" >> BUILD_TRIGGER.txt
git add BUILD_TRIGGER.txt
git commit -m "Trigger BOTH builds v$(date '+%m%d%H%M')"
git push origin main
```

**Why MODULAR?**
- Build only what you need (saves time & storage)
- LIGHT builds ~5-10 min, FULL builds ~15-20 min
- GitHub artifact storage: LIGHT ~150MB, FULL ~2.6GB
- Faster iteration when only one version changed

Build starts automatically, check: https://github.com/NeilVibe/VRS-Manager/actions

## BUILD TROUBLESHOOTING

### ⚠️ LFS Bandwidth Quota Exceeded (CRITICAL LESSON LEARNED!)

**If you see:** `This repository exceeded its LFS budget`

**What happened:**
- GitHub LFS has monthly bandwidth quota (1GB free)
- BERT model is 447MB stored in LFS
- Each build download counts against quota

**The Fix (Already Applied):**
```yaml
# LIGHT build (no BERT needed)
build-light:
  - uses: actions/checkout@v3
    with:
      lfs: false  # ✅ Skip LFS download

# FULL build (BERT required)
build-full:
  - uses: actions/checkout@v3
    with:
      lfs: true  # ✅ Download BERT model

# Release job (only needs artifacts)
create-release:
  - uses: actions/checkout@v3
    with:
      lfs: false  # ✅ No source files needed
```

**Key Lesson:** Only enable `lfs: true` where BERT model is actually needed!

**Check build logs:**
```bash
gh run list --workflow=build-installers.yml --limit 5
gh run view [run-id] --log-failed | grep "LFS\|error"
```

## VERSION UNIFICATION (CRITICAL!)

**WHY CRITICAL:** Version inconsistencies cause confusion for users, documentation mismatches, and make debugging difficult. When building releases, ALL documentation must match the actual code version. User trust depends on accurate version reporting across all files.

**AUTOMATED CHECK - COMPREHENSIVE MONITORING:**
```bash
python3 check_version_unified.py
```

**What it checks (THOROUGH COVERAGE):**
- ✅ **12 Static Files:** Code, docs, installers, workflows
- ✅ **Runtime Imports:** src.config VERSION/VERSION_FOOTER
- ✅ **GUI Display:** Window title + footer (centralized import)
- ✅ **Terminal Prints:** main.py startup messages (4 statements)
- ✅ **Processor Comments:** Version headers in code
- ✅ **Build System:** Installer file paths + workflow references
- ✅ **Documentation:** README, roadmap, WIKI, guides

**Runs automatically!** Reports exact file:line for any mismatch.

**⚠️ MANDATORY WORKFLOW:**
1. Update version in all 12 files
2. **RUN THIS CHECK** → `python3 check_version_unified.py`
3. Only if exit code 0 (success) → commit and push
4. Then trigger build

**NEVER commit version changes without running this check first!**

**Current Version: 11241313** - Update ALL these files together:
```bash
# 1. src/config.py - VERSION and VERSION_FOOTER
# 2. main.py - Docstring (line 5) and print statements (lines 12-15)
# 3. README.md - Version (line 3)
# 4. README_KR.md - Version (line 3)
# 5. roadmap.md - Current Status header + Version History
# 6. update_excel_guides.py - VERSION, VERSION_TEXT_EN/KR, content
# 7. WIKI_CONFLUENCE.md - Version references
# 8. CLAUDE.md - Current Version (line 4 and line 23)
# 9. src/processors/master_processor.py - Version comment (line 5)
```

**Check version consistency:**
```bash
grep -r "1118\." --include="*.py" --include="*.md" | grep -v test | grep -v ".git"
```

**VERIFY:** All 10 files listed above MUST show the same version. Any mismatch means incomplete update!

## UPDATE EXCEL GUIDES
**Script:** `update_excel_guides.py`
**Purpose:** Updates EN/KR Excel guides with new version info

**Edit these variables:**
```python
VERSION = "1121.0"
VERSION_TEXT_EN = "Version 1121.0 (Phase 3.1.1 - Word-Level Diff Enhancement)"
VERSION_TEXT_KR = "버전 1121.0 (Phase 3.1.1 - 단어 수준 비교 개선)"
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
python3 tests/test_5000_perf.py      # Performance (879 rows/sec expected)
python3 tests/test_accuracy.py       # Accuracy (100% expected)
python3 tests/test_math_verify.py    # Math verification
```

## BERT MODEL SETUP (Phase 2.3)
**Model:** Korean SBERT for semantic similarity analysis
**Size:** 447MB (stored locally in `models/kr-sbert/`)
**Status:** ✅ Downloaded and ready

**One-time setup (if models/ directory missing):**
```bash
python3 download_bert_model.py
```

**Why not in git?** Model is 447MB - exceeds GitHub's 100MB file size limit. Must download locally on each machine.

**Test model:**
```bash
python3 -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('./models/kr-sbert'); print('✅ Model ready!')"
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
