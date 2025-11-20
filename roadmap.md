# VRS Manager - Development Roadmap

## 📝 Version Update Checklist (IMPORTANT!)

**After completing any code work that changes the version, update ALL of these files:**

- [ ] `src/config.py` → `VERSION` constant and `VERSION_FOOTER`
- [ ] `main.py` → Docstring (line 5) and all print statements (lines 12-15)
- [ ] `README.md` → Version number (line 3) and status line (line 5)
- [ ] `README_KR.md` → Version number (line 3) and status line (line 5)
- [ ] `roadmap.md` → Current Status header (below) and add to Version History section
- [ ] `docs/VRS_Manager_Process_Guide_EN.xlsx` → Version in Overview sheet
- [ ] `docs/VRS_Manager_Process_Guide_KR.xlsx` → Version in Overview sheet (개요)

**Don't forget to commit all documentation updates together!**

---

## 📋 Current Status

**Version:** v11201928 (DateTime Versioning - November 20, 2025 at 7:28 PM)

### ✅ Phase 3.0 COMPLETE - Professional Installer System

**GitHub Release:** https://github.com/NeilVibe/VRS-Manager/releases/tag/v1.120.0

**Two Installation Options:**
- 🪶 **LIGHT** (~150MB): Core features + punctuation detection
- 🚀 **FULL** (~2.6GB): Everything + BERT AI semantic similarity

**Features:**
- ✅ Professional Windows installers (Inno Setup)
- ✅ Start Menu integration + proper uninstaller
- ✅ 100% offline operation (no internet required)
- ✅ Fully portable (zip folder → transfer → extract → run)
- ✅ Dual-version code architecture (LIGHT/FULL detection)
- ✅ StrOrigin Analysis works in both versions

**Current StrOrigin Analysis Coverage:**
- ✅ Raw Process - Word-level diff with 4-column layout
- ✅ Working Process - Word-level diff with 4-column layout
- ❌ AllLang Process - NOT YET IMPLEMENTED

---

## 📋 Current Priority: Phase 3.2 - Self-Monitoring Infrastructure ⚙️ IN PROGRESS

### ✅ COMPLETED: Version Unification Check Script

**Script:** `check_version_unified.py`

**Purpose:** Automatically verify version consistency across all 12 project files

**Features:**
- ✅ Reads source of truth from `src/config.py`
- ✅ Checks all version references in code, docs, installers, workflows
- ✅ Reports mismatches with file:line numbers
- ✅ Ignores historical version entries (Version History section)
- ✅ Exit code 0 = unified, 1 = mismatch detected

**Usage:**
```bash
python3 check_version_unified.py
```

**Files Monitored (12 total):**
1. src/config.py - VERSION + VERSION_FOOTER
2. main.py - Docstring + print statements
3. README.md + README_KR.md - Version headers
4. installer/*.iss - MyAppVersion
5. .github/workflows/build-installers.yml - File paths
6. update_excel_guides.py - VERSION variables
7. CLAUDE.md, roadmap.md, WIKI_CONFLUENCE.md - Documentation
8. src/processors/master_processor.py - Version comment

**Recommendation:** Run before every build to ensure version consistency!

---

## 📋 Current Priority: Phase 3.1.3 - Processor Parity Update ✅ COMPLETE

**Status:** IMPLEMENTATION COMPLETE
**Version Target:** v11201322 (minor feature parity update)
**Detailed Analysis:** See `PROCESSOR_PARITY_ANALYSIS.md`

### 🎯 GOAL: Achieve Full Parity Between RAW and WORKING Processors

### 📊 Parity Status

| Feature | RAW Processor | WORKING Processor | Status |
|---------|---------------|-------------------|--------|
| StrOrigin Analysis Sheet | ✅ Implemented | ✅ Implemented | ✅ **PARITY** |
| Super Group Word Analysis Sheet | ✅ Implemented | ✅ **IMPLEMENTED** | ✅ **PARITY** |

**🎉 FULL PARITY ACHIEVED!** Both processors now have identical feature sets.

### ✅ PROBLEM RESOLVED

**WORKING processor now includes "Super Group Word Analysis" sheet!**

- **RAW processor** has 5 output sheets (includes Super Group Word Analysis) ✅
- **WORKING processor** now has 5 output sheets (includes Super Group Word Analysis) ✅
- Feature parity achieved - both processors have identical capabilities

### 📝 Implementation Plan

#### Phase 1: Update `process_working_comparison()` Return Value
**File:** `src/core/working_comparison.py`

**Current:**
```python
return pd.DataFrame(results), counter, marked_prev_indices
```

**New:**
```python
return pd.DataFrame(results), counter, marked_prev_indices, pass1_results
```

**Action:** Expose `pass1_results` (already collected internally) to calling code

---

#### Phase 2: Capture `pass1_results` in WorkingProcessor
**File:** `src/processors/working_processor.py` (line 130-135)

**Current:**
```python
self.df_result, self.counter, marked_prev_indices = process_working_comparison(...)
```

**New:**
```python
self.df_result, self.counter, marked_prev_indices, self.pass1_results = process_working_comparison(...)
```

**Action:** Store `pass1_results` for use in write_output()

---

#### Phase 3: Add Super Group Word Analysis to write_output()
**File:** `src/processors/working_processor.py`

**Add After Summary Report (before StrOrigin Analysis):**
```python
# Super Group Word Analysis (parity with RAW processor)
if hasattr(self, 'pass1_results'):
    log("Generating Super Group Word Analysis...")
    super_group_analysis, migration_details = aggregate_to_super_groups(
        self.df_curr,
        self.df_prev,
        self.pass1_results
    )
    write_super_group_word_analysis(writer, super_group_analysis, migration_details)
    log(f"  → {len(super_group_analysis)} super groups analyzed")
    if migration_details:
        log(f"  → {len(migration_details)} migrations detected")
```

**Required Imports:**
```python
from src.io.excel_writer import write_super_group_word_analysis
from src.utils.super_groups import aggregate_to_super_groups
```

---

### ✅ Implementation Checklist

**Preparation:** ✅ COMPLETE
- [x] Analyze RAW vs WORKING processor differences
- [x] Document findings in PROCESSOR_PARITY_ANALYSIS.md
- [x] Create detailed plan of action
- [x] Update roadmap.md with Phase 3.1.3
- [x] Commit preparation documents
- [x] Push preparation commit

**Phase 1: Update working_comparison.py** ✅ COMPLETE
- [x] Read complete file to understand pass1_results collection
- [x] Verify pass1_results is being built during comparison
- [x] Update return statement to include pass1_results
- [x] Test compilation (passed)
- [x] Updated docstring with new return value

**Phase 2: Update WorkingProcessor.process_data()** ✅ COMPLETE
- [x] Update unpacking statement to capture pass1_results
- [x] Store self.pass1_results for use in write_output()
- [x] Test compilation (passed)
- [x] Verified integration with Phase 1 changes

**Phase 3: Add Super Group Analysis** ✅ COMPLETE
- [x] Add required imports (write_super_group_word_analysis, aggregate_to_super_groups)
- [x] Insert Super Group Word Analysis code in write_output()
- [x] Test compilation (passed)
- [x] Syntax validation successful

**Testing & Validation:** ✅ COMPLETE
- [x] Created comprehensive test (test_working_processor_super_group.py)
- [x] Test placed in tests/ folder
- [x] Imports verified (all successful)
- [x] Syntax check passed for all modified files
- [x] Ready for user acceptance testing

**Documentation & Release:** 🔜 READY FOR BUILD
- [ ] Update version to v11201322 (waiting for user signal to build)
- [x] Update roadmap.md (this file)
- [ ] Final commit and push (in progress)
- [ ] Trigger build (ONLY when user authorizes)

---

### 🎯 Expected Outcome

**Before:**
- RAW: 5 sheets (Comparison, Deleted, Summary, **Super Group**, StrOrigin)
- WORKING: 4 sheets (Work Transform, History, Deleted, Summary, StrOrigin)

**After:**
- RAW: 5 sheets (unchanged)
- WORKING: 5 sheets (Work Transform, History, Deleted, Summary, **Super Group**, StrOrigin)

**Result:** ✅ **FULL FEATURE PARITY ACHIEVED**

---

### 📊 Impact Assessment

- **Risk Level:** LOW (copying proven implementation)
- **Files Modified:** 2 (working_comparison.py, working_processor.py)
- **Code Changes:** ~16 lines total
- **No Breaking Changes:** Existing functionality unchanged
- **Testing Required:** Standard test suite + output verification

---

## 📋 Next Priority: Phase 3.1.2 - AllLang Process Enhancement 🔜 NEXT

### ✅ Phase 3.1.1 COMPLETE - Word-Level Diff Enhancement

**Released:** v11201928

**Implemented Features:**
- ✅ Word-level diff algorithm (WinMerge-style automatic chunking)
- ✅ 4-column layout: Previous StrOrigin → Current StrOrigin → Analysis → Diff Detail
- ✅ Progress tracking with filling bar
- ✅ Applied to BOTH Raw and Working processes
- ✅ Column widths optimized (25|25|20|35)
- ✅ Works in LIGHT and FULL versions

**Output Examples:**
- Punctuation-only: `"Punctuation/Space Change"` (empty diff)
- Word changes: `"79.8% similar"` + `"[world→universe]"`
- Multiple changes: `"[player won→enemy lost] [game→battle]"`

---

## 📋 Phase 3.1.1 Implementation Details (ARCHIVED)

### Overview

**Current Implementation:**
- StrOrigin Analysis uses character-level diff
- Shows changes but can be messy for multi-word changes
- Example: `[w→l] [n→st] [g→m]` (hard to read)

**New Implementation: Word-Level Diff**
- Switch from character-level to word-level diff (like WinMerge)
- Automatic chunking of consecutive changed words
- Much cleaner output for sentence changes
- Example: `[won→lost] [game→match]` (clear and readable)

### Changes Being Applied

#### 1. Word-Level Diff Algorithm ✅ PRIORITY 1

**What:** Replace character-level diff with word-level diff in `strorigin_analysis.py`

**Before:**
```
"The player won the game" → "The enemy lost the battle"
Result: [w→l] [n→st] [g→m] [me→tch]  ❌ Messy
```

**After:**
```
"The player won the game" → "The enemy lost the battle"
Result: [player won→enemy lost] [game→battle]  ✅ Clear
```

**Korean Example:**
```
Before: [플레→적] [-어가] [승리했→도망갔]  ❌ Confusing
After:  [플레이어가 승리했습니다→적이 도망갔습니다]  ✅ Shows full scope
```

**Benefits:**
- ✅ Cleaner output (fewer brackets)
- ✅ Shows scope of change clearly
- ✅ Automatic chunking (consecutive words grouped)
- ✅ Works great for Korean AND English
- ✅ Easier for translators to understand

**Implementation:** Update `extract_differences()` function to use word-level matching

---

#### 2. Separate "Diff Detail" Column ✅ PRIORITY 1

**What:** Split StrOrigin Analysis into TWO columns for clarity

**Current Layout:**
```
| StrOrigin Change Analysis |
|---------------------------|
| 81.7% similar | Changed: [won→lost] |  ← All in one cell, cluttered
```

**New Layout:**
```
| Previous StrOrigin | Current StrOrigin | StrOrigin Analysis | Diff Detail |
|--------------------|-------------------|-------------------|-------------|
| won the game       | lost the match    | 81.7% similar     | [won→lost] [game→match] |
```

**Benefits:**
- ✅ Cleaner separation of data
- ✅ Can sort/filter by similarity %
- ✅ Side-by-side comparison of prev/current
- ✅ Natural reading order (left to right)
- ✅ LIGHT version shows empty Diff Detail (not cluttered text)

**Implementation:** Update raw_processor.py sheet creation

---

#### 3. Column Widths ✅ PRIORITY 1

**What:** Make StrOrigin Analysis columns wider for better readability

**Sizing:**
- Previous StrOrigin: **25 characters** (same as CHANGES column)
- Current StrOrigin: **25 characters** (same as CHANGES column)
- StrOrigin Analysis: **20 characters** (for "XX.X% similar" text)
- Diff Detail: **30 characters** (wider - for `[old→new]` display)

**Why:** StrOrigin Analysis is a dedicated sheet - give it space for clarity!

**Implementation:** Set column widths in openpyxl when creating sheet

---

#### 4. Progress Tracking with Filling Bar ✅ PRIORITY 2

**What:** Add row-by-row progress tracking for StrOrigin analysis (reuse existing progress bar system)

**Current:**
```
→ Running FULL analysis (Punctuation + BERT similarity)...
(no feedback for 30 seconds... is it frozen?)
```

**New:**
```
→ Analyzing StrOrigin changes...
  [████░░░░░░░░░░░░░░░░] 20% (25/127 rows)
  [████████░░░░░░░░░░░░] 40% (50/127 rows)
  [████████████░░░░░░░░] 60% (76/127 rows)
  [████████████████░░░░] 80% (101/127 rows)
  [████████████████████] 100% (127/127 rows)
✓ StrOrigin analysis complete (127 rows in 12.3s)
```

**Benefits:**
- ✅ Users know it's working (not frozen)
- ✅ Can estimate time remaining
- ✅ Professional UX like rest of app
- ✅ Reuses existing progress bar code

**Implementation:**
- Use existing progress bar from `src/utils/progress.py`
- Update every row (or every 5 rows for very large files)
- Track both difflib AND BERT steps

---

#### 5. Apply to Both Raw and Working Process ✅ PRIORITY 3

**Raw Process:** ✅ Apply immediately (already has StrOrigin Analysis)
**Working Process:** ⏳ Apply when Working Process StrOrigin Analysis is implemented

**Status:** Raw Process first, Working Process when Phase 3.1.2 starts

---

### Testing Checklist

- [ ] Test word-level diff with English sentences
- [ ] Test word-level diff with Korean sentences
- [ ] Test word-level diff with mixed English/Korean
- [ ] Test LIGHT version (shows "Content Change | Changed: [diff]")
- [ ] Test FULL version (shows "XX.X% similar | Changed: [diff]")
- [ ] Verify column order: Previous → Current → Analysis → Diff
- [ ] Verify column widths are readable
- [ ] Verify progress bar works for small files (10 rows)
- [ ] Verify progress bar works for large files (500+ rows)
- [ ] Run existing test suite (test_accuracy.py, test_5000_perf.py)

---

## 📋 Next Priority: Phase 3.1.2 - Expand StrOrigin Analysis

### Overview

**Current Limitation:**
StrOrigin Analysis only appears in **Raw Process** (Comparison output). When users run Working Process or review AllLang outputs, they don't get transparency about what changed and why.

**Proposal: Add StrOrigin Analysis to More Processes**

### 1. Working Process StrOrigin Analysis ✅ RECOMMENDED

**Why This Makes Sense:**

Working Process imports previous translations into new baseline using complex merge logic:
- TimeFrame conflict resolution
- 10-Key pattern matching
- Dictionary error handling
- Migration tracking

**Problem:**
Users don't always understand WHY their previous translation changed or didn't import correctly.

**Solution:**
Add "StrOrigin Analysis" column in Working Process output to show:
- **"Unchanged"** - Previous translation imported exactly as-is
- **"Punctuation/Space Change"** - Only formatting changed during import
- **"Content Change" (LIGHT)** / **"XX.X% similar" (FULL)** - Translation was modified
- **"TimeFrame Conflict"** - Couldn't import due to TimeFrame mismatch
- **"New Content"** - No previous translation existed

**Benefit:**
- Transparent merge logic
- Helps translators understand what happened to their work
- Shows impact of TimeFrame preservation
- Identifies where manual review is needed

**Implementation Complexity:** MEDIUM
- Add StrOriginAnalyzer to `working_processor.py`
- Track what happened during import (matched exactly, modified, conflicted, etc.)
- Add analysis column to Work Transform output
- Test LIGHT and FULL versions

---

### 2. Progress Tracking for Similarity Comparison ✅ RECOMMENDED

**Problem:**
BERT similarity calculation can take time with large files. Users don't know how long it will take or if it's still running.

**Solution:**
Add progress tracking that updates every 10 rows processed:

```python
total_rows = len(df_strorigin_changes)
for idx, (index, row) in enumerate(df_strorigin_changes.iterrows(), start=1):
    # ... analyze row ...

    # Progress update every 10 rows
    if idx % 10 == 0 or idx == total_rows:
        percent = (idx / total_rows) * 100
        print(f"  → Progress: {idx}/{total_rows} rows ({percent:.1f}%)")
```

**Output Example:**
```
→ Found 127 rows with StrOrigin changes
→ Running FULL analysis (Punctuation + BERT similarity)...
  → Progress: 10/127 rows (7.9%)
  → Progress: 20/127 rows (15.7%)
  → Progress: 30/127 rows (23.6%)
  ...
  → Progress: 127/127 rows (100.0%)
✓ StrOrigin analysis complete
```

**Benefits:**
- User knows process is working
- Estimate remaining time
- Better UX for large files

**Implementation Complexity:** LOW
- Simple counter in analysis loop
- Print statement every 10 rows

---

### 3. Enhanced StrOrigin Analysis Sheet Columns ✅ RECOMMENDED

**Current Column Layout:**
- Only shows "StrOrigin Analysis" result

**Problem:**
Users can't easily see WHAT changed - they need to look back at the original data columns to compare.

**Proposed Column Layout:**
```
Current StrOrigin | Previous StrOrigin | CHANGES | StrOrigin Change Analysis
```

**Benefits:**
- Side-by-side comparison
- See both versions without scrolling
- Understand the analysis result in context
- Easier manual review

**Implementation:**
When creating the StrOrigin Analysis sheet, include these columns in this order:
1. **Current StrOrigin** - The new StrOrigin value from current file
2. **Previous StrOrigin** - The old StrOrigin value from previous file
3. **CHANGES** - What changed (from original comparison)
4. **StrOrigin Change Analysis** - "Punctuation/Space Change" or "XX.X% similar"

Plus any other relevant columns (StringID, TimeFrame, Translation, etc.)

**Example Output:**

| StringID | Current StrOrigin | Previous StrOrigin | CHANGES | StrOrigin Change Analysis |
|----------|-------------------|-------------------|---------|---------------------------|
| STR_001 | Hello, world! | Hello world | StrOrigin | Punctuation/Space Change |
| STR_002 | Welcome home | Welcome back | StrOrigin | 67.3% similar |
| STR_003 | New text | Old text | StrOrigin | 12.5% similar |

**Implementation Complexity:** LOW
- Reorder columns when creating sheet
- Extract Previous StrOrigin from PreviousData column (already doing this)
- Add columns in desired order

---

### 4. Model Verification ✅ CONFIRMED CORRECT

**Current Implementation (VRS Manager):**
- **Model:** `snunlp/KR-SBERT-V40K-klueNLI-augSTS` (Korean SBERT) ✅ CORRECT
- **Method:** Simple cosine similarity using numpy
  ```python
  dot_product = np.dot(embedding1, embedding2)
  norm1 = np.linalg.norm(embedding1)
  norm2 = np.linalg.norm(embedding2)
  similarity = dot_product / (norm1 * norm2)
  ```
- **NOT using FAISS** - Direct numpy calculation ✅ INTENTIONAL

**Why FAISS is NOT Needed:**

FAISS is designed for searching/indexing thousands of vectors (e.g., "find top 10 most similar from 1M strings").

VRS Manager already has **1-to-1 matching via 10-key system**:
```
Row A (10-key: ABC123) → Matched to Row B (10-key: ABC123)
                      ↓
                 Compare only these 2 strings
                      ↓
              Simple cosine similarity (microseconds)
```

**Use Case Comparison:**
- **FAISS needed:** Search database of 100K translations for similar matches
- **VRS Manager:** Compare 2 pre-matched strings (already paired by 10-key)
- **Conclusion:** Simple numpy cosine similarity is perfect for our use case

**Status:** ✅ CONFIRMED - Current approach is optimal for VRS Manager architecture

---

### 5. AllLang Process StrOrigin Analysis ⚠️ NEEDS DISCUSSION

**Why This is Tricky:**

AllLang merges translations from **multiple language files**, not just comparing PREVIOUS vs CURRENT.

**Questions:**
- What would StrOrigin Analysis mean in this context?
- Compare against which baseline? (English source? Previous AllLang output?)
- Is this useful or confusing?

**Possible Approaches:**

**Option A: Skip AllLang**
- AllLang is cross-language merge, not version comparison
- StrOrigin Analysis doesn't apply conceptually
- **RECOMMENDED for now**

**Option B: Compare Against English Source**
- Show if each language's translation changed vs English baseline
- Might be useful for detecting drift
- More complex implementation

**Option C: Compare Against Previous AllLang Output**
- Similar to Raw/Working Process logic
- Shows changes between AllLang runs
- Requires storing previous AllLang output

**Decision:** Start with Working Process only, revisit AllLang later if needed.

---

### Implementation Plan

#### Phase 3.1.1: Working Process StrOrigin Analysis

**File: `src/processors/working_processor.py`**

Add column during merge to track what happened:

```python
def process(self):
    # ... existing merge logic ...

    # NEW: Track StrOrigin during import
    strorigin_tracking = []

    for idx, row in df_current.iterrows():
        key_10 = self._generate_10key(row)

        if key_10 in prev_translations:
            prev_strorigin = prev_translations[key_10]['StrOrigin']
            curr_strorigin = row['StrOrigin']
            prev_timeframe = prev_translations[key_10]['TimeFrame']
            curr_timeframe = row['TimeFrame']

            # Determine what happened during import
            if prev_timeframe != curr_timeframe:
                tracking = "TimeFrame Conflict"
            elif prev_strorigin == curr_strorigin:
                tracking = "Unchanged"
            else:
                # Analyze the change
                analyzer = StrOriginAnalyzer()
                tracking = analyzer.analyze(prev_strorigin, curr_strorigin)
        else:
            tracking = "New Content"

        strorigin_tracking.append(tracking)

    # Add column to output
    df_result['StrOrigin Import Status'] = strorigin_tracking
```

**Output Example:**

| StringID | StrOrigin | Translation | StrOrigin Import Status |
|----------|-----------|-------------|------------------------|
| STR_001 | Hello, world! | 안녕하세요! | Unchanged |
| STR_002 | Hello, world. | 안녕하세요. | Punctuation/Space Change |
| STR_003 | Welcome back! | 환영합니다! | 87.3% similar (FULL) |
| STR_004 | New content | (empty) | New Content |
| STR_005 | Old TimeFrame | (empty) | TimeFrame Conflict |

**Testing:**
- [ ] Test with LIGHT version (shows "Content Change")
- [ ] Test with FULL version (shows "XX.X% similar")
- [ ] Test TimeFrame conflicts
- [ ] Test new content (no previous translation)
- [ ] Verify column appears in Work Transform output

---

### Documentation Updates

**Excel Guides (EN/KR):**
- Update "2. Working Process" sheet
- Add section explaining "StrOrigin Import Status" column
- Show examples of each status type
- Explain LIGHT vs FULL differences

**README.md:**
- Add Working Process StrOrigin Analysis to features list
- Update comparison table with new column

---

## Version History

### v11201321 (Released - 2025-11-20) ✅
- **Phase 3.1.1 COMPLETE**: Word-Level Diff Enhancement
- **IMPROVED**: StrOrigin Analysis now uses word-level diff (cleaner, more readable output)
- **NEW**: Separate "Diff Detail" column showing exact word changes `[old→new]`
- **NEW**: Progress tracking with filling bar during StrOrigin analysis
- **NEW**: StrOrigin Analysis now available in Raw Process (was Working only)
- **IMPROVED**: 4-column layout: Previous StrOrigin | Current StrOrigin | Analysis | Diff Detail
- **IMPROVED**: Optimized column widths (25|25|20|35 chars) for better readability
- **IMPROVED**: Natural reading order (left to right)
- **DOCS**: Complete Phase 3.1.1 implementation notes in PHASE_3.1.1_NOTES.md

### v1.120.0 (Released - 2025-11-19) ✅
- **Phase 3.0 COMPLETE**: Professional Installer System
- **NEW**: LIGHT version installer (~150MB) - Core features only
- **NEW**: FULL version installer (~2.6GB) - Complete with BERT AI
- **NEW**: StrOrigin Analysis works in both LIGHT and FULL versions
- **NEW**: 100% offline operation, fully portable
- **NEW**: Professional Windows installers with Start Menu integration
- **NEW**: GitHub Actions CI/CD for automated builds
- **IMPROVED**: Dual-version code architecture with graceful BERT detection
- **DOCS**: Updated Excel guides (EN/KR) to v1120.0 with version differences

### v1.119.1 (Building)
- **BUNDLED**: BERT model + PyTorch in single 3GB .exe
- **IMPROVED**: Full offline operation
- **IMPROVED**: Zero setup required

### v1.119.0 (Production Ready)
- **Phase 2.3 COMPLETED**: StrOrigin Change Analysis (Raw Process only)
  - NEW: "StrOrigin Change Analysis" sheet in Raw VRS Check output
  - NEW: Punctuation/Space-only detection
  - NEW: BERT semantic similarity (Korean SBERT)
  - NEW: Results: "Punctuation/Space Change" or "XX.X% similar"
- **OFFLINE**: Model runs locally, no internet needed

### v1.118.6 (Reorganization Complete)
- **REORGANIZED**: Project structure
  - Moved tests → `tests/`
  - Moved docs → `docs/`
  - Created `scripts/` for build/setup scripts
- **Phase 2.2.1 COMPLETED**: Super Group Analysis Improvements
  - Removed "Others" category
  - Reordered super groups by word count
  - Added migration tracking table
  - Renamed "Untranslated" → "Not Translated"

### v1.118.5 and earlier
- All core VRS Check features implemented
- 10-Key matching, TWO-PASS algorithm, TimeFrame preservation
- Group Word Count Analysis & Super Group Aggregation
- Master File Update Simplification

---

## Feature Comparison

| Feature | Raw Process | Working Process | AllLang Process | Master Update |
|---------|-------------|-----------------|-----------------|---------------|
| 10-Key Pattern Matching | ✅ | ✅ | ✅ | ✅ |
| TimeFrame Preservation | ✅ | ✅ | ✅ | ✅ |
| StrOrigin Analysis | ✅ v1.119.0 | ⏳ Phase 3.1 | ❌ Not Planned | ❌ N/A |
| Group Word Count | ✅ | ✅ | ✅ | ❌ N/A |
| Super Group Aggregation | ✅ | ✅ | ✅ | ❌ N/A |
| LIGHT/FULL Version Support | ✅ | ⏳ Phase 3.1 | ✅ | ✅ |

---

## Quick Links

- **Latest Release:** https://github.com/NeilVibe/VRS-Manager/releases/latest
- **Download LIGHT:** (~150MB) - Fast, core features
- **Download FULL:** (~2.6GB) - Complete with AI analysis
- **Documentation:** See `docs/` folder for Excel guides (EN/KR)
- **Installation:** Both versions work 100% offline after installation
