# VRS Manager - User Guide

**Version:** 12051348 | **Status:** Production Ready | **Date:** November 2025

---

## 📋 Table of Contents

1. [What is VRS Manager?](#what-is-vrs-manager)
2. [Core Concepts](#core-concepts)
3. [The Four Processors](#the-four-processors)
4. [Row Identification System](#row-identification-system)
5. [Import Logic Rules](#import-logic-rules)
6. [Quick Reference](#quick-reference)

---

## What is VRS Manager?

VRS Manager is a **specialized tool for managing Voice Recording Script (VRS) data** in game development and multimedia projects. It compares different versions of VRS Excel files to detect changes, manage translations across multiple languages (Korean, English, Chinese), and intelligently update master files.

### Main Purpose

When you receive a new VRS file from developers, you need to:
- **Identify what changed** - new dialogue, edited text, deleted lines, timing updates
- **Preserve completed work** - keep translations and recording status from previous versions
- **Update master files** - merge new content with existing data intelligently

VRS Manager automates this entire process with 100% accuracy.

---

## Core Concepts

### 1️⃣ Key Columns

Every VRS row is identified by **four key columns**:

| Column | Purpose | Example |
|--------|---------|---------|
| **SequenceName** | Scene/sequence identifier | `"Scene_01_Battle"` |
| **EventName** | Event ID within sequence | `"E12345"` |
| **StrOrigin** | Original Korean dialogue text | `"안녕하세요"` |
| **CastingKey** | Character identifier | `"Hero_Male_Main_A"` |

### 2️⃣ Importance Levels

Rows have two importance levels:

- **High Importance**: Critical content requiring updates and tracking
- **Low Importance**: Non-critical content (background audio, ambient sounds)

### 3️⃣ Status Types

Recording status falls into two categories:

- **Pre-recording**: `"POLISHED"`, `"SPEC-OUT"`, `"CHECK"`, etc.
- **After-recording**: `"RECORDED"`, `"FINAL"`, `"SHIPPED"`, etc.

**Why it matters**: After-recording data is always preserved during imports.

---

## The Four Processors

VRS Manager has **4 main processes**. Each serves a different purpose but shares the same core detection logic.

### Comparison Table

| Aspect | Raw Process | Working Process | All Language Process | Master File Update |
|--------|-------------|-----------------|---------------------|-------------------|
| **Input** | PREVIOUS + CURRENT (same file type) | PREVIOUS + CURRENT (same file type) | PREVIOUS (KR/EN/CN) + CURRENT (KR/EN/CN) | SOURCE (working output) + TARGET (master file) |
| **Purpose** | Detect all changes | Import completed work into new baseline | Merge 3 languages with import logic | Update master file with new data |
| **Import Data?** | ❌ No - only detects | ✅ Yes - smart import | ✅ Yes - per language | ✅ Yes - importance-based |
| **Output Sheets** | Main Sheet + Deleted Rows + Summary | Main Sheet + Deleted Rows + Summary | Main Sheet + Deleted Rows + Summary | High + Low + Deleted + History |
| **Use Case** | "What changed between v1 and v2?" | "Import my translations into new version" | "Update all 3 languages at once" | "Merge working file into master" |

---

### 🔍 Process 1: Raw VRS Check

**Purpose**: Compare two VRS files and detect **what changed**.

**When to use**:
- You received a new VRS version from developers
- You want to know what's different from the previous version
- You need a summary of changes before starting work

**What it does**:
1. Compares PREVIOUS ↔ CURRENT
2. Classifies every row as: New Row, No Change, StrOrigin Change, EventName Change, etc.
3. Tracks previous StrOrigin values
4. Generates statistics and word counts

**What it does NOT do**:
- Does NOT import any data
- Does NOT copy translations or status
- Only shows you what changed

**Output**:
- Main Sheet: All current rows with CHANGES column
- Deleted Rows: Rows removed from PREVIOUS
- StrOrigin Analysis: Detailed comparison of text changes (NEW in v11202116)
- Summary: Statistics and word counts

---

### 📥 Process 2: Working VRS Check

**Purpose**: Import completed work from PREVIOUS into CURRENT with **smart logic**.

**When to use**:
- You have a PREVIOUS file with completed translations/recording status
- You received a new CURRENT baseline from developers
- You want to preserve your completed work and only work on new/changed content

**What it does**:
1. Compares PREVIOUS ↔ CURRENT (same as Raw Process)
2. Applies **import logic** based on change type (see Import Logic section)
3. Preserves after-recording status automatically
4. Creates PreviousData column for tracking historical changes

**Import Behavior**:
- **No Change** → Full import (STATUS, Text, FREEMEMO)
- **StrOrigin Change** → Preserve STATUS/FREEMEMO, store old StrOrigin in PreviousData
- **EventName Change** → Full import (timing might have changed, but content same)
- **New Row** → No import (brand new content)

**Output**:
- Main Sheet: Current rows enriched with PREVIOUS data
- Deleted Rows: Rows removed from PREVIOUS
- StrOrigin Analysis: Detailed comparison of text changes (NEW in v11202116)
- Summary: Statistics

---

### 🌍 Process 3: All Language Check

**Purpose**: Merge and update **3 languages (KR/EN/CN)** simultaneously.

**When to use**:
- You're managing Korean, English, and Chinese translations
- You received new CURRENT files for all languages
- You have PREVIOUS files with completed work for each language

**What it does**:
1. Merges CURRENT KR + EN + CN into single file (by StrOrigin key)
2. Applies **Working Process import logic** independently per language
3. Handles missing languages gracefully (can process just 1, 2, or all 3 languages)
4. Creates language-specific columns (STATUS_KR, STATUS_EN, STATUS_CN)

**Import Behavior**: Same as Working Process, but applied separately for each language.

**Output**:
- Main Sheet: All languages merged with imported data
- Deleted Rows: Rows removed from PREVIOUS
- Summary: Statistics per language

---

### 🎯 Process 4: Master File Update

**Purpose**: Update the **Master File** with data from Working Process output.

**When to use**:
- You completed Working Process and have a working output file
- You need to merge this into your Master File
- Simple data movement operation (not comparison/diff)

**What it does**:
1. Separates SOURCE into High/Low importance
2. Matches rows by **EventName only** (simple!)
3. **High Importance**: Updates TARGET columns with SOURCE data
4. **Low Importance**: Skipped entirely (no processing)
5. **Deleted Rows**: Marked inline with CHANGES = "Deleted"
6. Preserves CHANGES column from SOURCE (no recalculation)

**Simplified Logic** (v1118.2):
- **High + EventName matches** → Update TARGET columns with SOURCE values
- **High + EventName not in TARGET** → Add new row
- **Low importance** → Skip entirely (not processed)
- **Deleted** → EventName in TARGET but not in SOURCE → Mark CHANGES = "Deleted"
- **CHANGES column** → Always preserved from SOURCE

**Output**:
- Main Sheet: All rows (HIGH + DELETED)
- Update History: Tracking sheet with timestamp and stats
- Summary: Statistics

---

## Row Identification System

VRS Manager uses a **10-Key Pattern Matching + TWO-PASS Algorithm** for ultra-precise change detection.

### The 10 Keys

Every row generates **10 different key combinations**:

**2-Key Combinations (6):**
- `(Sequence, Event)` - SE
- `(Sequence, StrOrigin)` - SO
- `(Sequence, CastingKey)` - SC
- `(Event, StrOrigin)` - EO
- `(Event, CastingKey)` - EC
- `(StrOrigin, CastingKey)` - OC

**3-Key Combinations (4):**
- `(Sequence, Event, StrOrigin)` - SEO
- `(Sequence, Event, CastingKey)` - SEC
- `(Sequence, StrOrigin, CastingKey)` - SOC
- `(Event, StrOrigin, CastingKey)` - EOC

### Why 10 Keys?

**Problem**: Common dialogue phrases like "Hello", "Yes", "No" appear multiple times across different characters.

**Without 10 keys**:
```
PREVIOUS: Row A - "Hello" spoken by Hero
CURRENT:  Row B - "Hello" spoken by NPC (different character)
```
→ System thinks: "EventName changed" ❌ WRONG - this is a NEW row!

**With 10 keys**:
- Row is NEW only when **ALL 10 keys are missing** from PREVIOUS
- Row is DELETED only when **ALL 10 keys are missing** from CURRENT
- Prevents false matches when duplicates exist

### TWO-PASS Algorithm

The system processes rows in **two passes** to prevent 1-to-many matching issues.

#### PASS 1: Detect Certainties
- Perfect 4-key match (S+E+O+C all match) → **"No Change"** → Mark PREVIOUS row as "used"
- All 10 keys missing → **"New Row"**

#### PASS 2: Detect Changes (using UNMARKED rows only)
- Match patterns from most specific (3-key) to least specific (2-key)
- **Only use UNMARKED PREVIOUS rows** (not matched in PASS 1)
- First unmarked match wins → Mark as "used"
- No unmarked match → **"New Row"**

#### After PASS 2: Detect Deletions
- Any PREVIOUS row still UNMARKED → **"Deleted Row"**

**Why TWO-PASS?**

Without TWO-PASS:
```
PREVIOUS: Row A - (Scene1, E1000, "Hello", Hero)

CURRENT:
  Row 1: (Scene1, E1000, "Hello", Hero) → Matches Row A → "No Change"
  Row 2: (Scene1, E2000, "Hello", NPC)  → Also matches Row A → "EventName Change" ❌
  Row 3: (Scene1, E3000, "Hello", Boss) → Also matches Row A → "EventName Change" ❌

Result: 1 PREVIOUS row matches 3 CURRENT rows (1-to-many) ❌
```

With TWO-PASS:
```
PASS 1:
  Row 1 → Perfect match → "No Change" → Mark Row A as USED

PASS 2:
  Row 2 → Check (Scene1, "Hello") key → Row A is MARKED → Skip → Check other keys → No unmarked match → "New Row" ✅
  Row 3 → Same logic → "New Row" ✅

Result: 1 PREVIOUS row matches 1 CURRENT row (1-to-1) ✅
```

### Change Classification

Based on which keys match, the system classifies changes:

| Match Pattern | Classification | Example |
|--------------|----------------|---------|
| SEO matches, C differs | CastingKey Change | Same dialogue, different speaker |
| SEC matches, O differs | StrOrigin Change | Same timing/character, dialogue edited |
| SOC matches, E differs | EventName Change | Same dialogue/character, event ID changed |
| EOC matches, S differs | SequenceName Change | Same dialogue, moved to different scene |
| SE matches, O+C differ | StrOrigin+CastingKey Change | Major edit |
| All 10 keys missing | New Row | Brand new content |
| (PASS 2 unmarked) | Deleted Row | Content removed |

---

## StrOrigin Analysis Sheet

**NEW in v11202116** - Phase 3.1.1: Word-Level Diff Enhancement

### What is StrOrigin Analysis?

When running **Raw Process** or **Working Process**, VRS Manager automatically generates a **separate "StrOrigin Analysis" sheet** that provides detailed comparison of Korean text changes. This helps you understand exactly what changed in the dialogue and whether changes are trivial (punctuation) or substantial (content).

### Available in Two Versions

VRS Manager comes in two installation versions with different analysis capabilities:

| Version | Size | StrOrigin Analysis Output |
|---------|------|---------------------------|
| **LIGHT** | ~150MB | Shows "Punctuation/Space Change" or "Content Change" |
| **FULL** | ~2.6GB | Shows semantic similarity percentages (e.g., "79.8% similar", "94.5% similar") using Korean BERT AI model |

Both versions work offline and provide accurate change detection—FULL version just gives more detailed similarity scoring.

### 4-Column Layout

The StrOrigin Analysis sheet uses a **4-column layout** for easy comparison:

| Column | Content | Example |
|--------|---------|---------|
| **Previous StrOrigin** | Text from PREVIOUS file | `"플레이어가 게임에서 이겼다"` |
| **Current StrOrigin** | Text from CURRENT file | `"적이 전투에서 졌다"` |
| **Analysis** | Similarity or change type | `"79.8% similar"` or `"Content Change"` |
| **Diff Detail** | Word-level changes | `"[플레이어가→적이] [게임→전투] [이겼다→졌다]"` |

**Column widths optimized**: 25% | 25% | 20% | 35% for best readability.

### Word-Level Diff

The **Diff Detail** column uses **word-level diff** (similar to WinMerge) instead of character-level diff:

**Before (character-level)**: `[플→적] [이→이] [어→] [가→] [게→전] [임→투]`
**After (word-level)**: `[플레이어가→적이] [게임→전투] [이겼다→졌다]`

Much cleaner and easier to understand!

### Example Outputs

**Punctuation-only changes** (both versions):
```
Analysis: "Punctuation/Space Change"
Diff Detail: (empty - no content change)
```

**Content changes** (LIGHT version):
```
Analysis: "Content Change"
Diff Detail: "[player→enemy] [won→lost]"
```

**Content changes** (FULL version):
```
Analysis: "79.8% similar"
Diff Detail: "[player→enemy] [won→lost]"
```

### Progress Bar

During StrOrigin Analysis, a **progress bar with filling animation** shows real-time progress:

```
Performing StrOrigin Analysis... [████████░░] 82% (164/200 rows)
```

This helps you track analysis progress, especially for large files.

### When Does It Appear?

The StrOrigin Analysis sheet appears when:
- Running **Raw Process** (detects StrOrigin changes)
- Running **Working Process** (imports and analyzes StrOrigin changes)
- ❌ **NOT** in All Language Process yet (planned for Phase 3.1.2)
- ❌ **NOT** in Master File Update (not applicable)

### What Gets Analyzed?

Only rows where **StrOrigin changed** between PREVIOUS and CURRENT:
- StrOrigin Change
- StrOrigin+EventName Change
- StrOrigin+CastingKey Change
- Any composite change involving StrOrigin

Rows with "No Change" or changes that don't affect StrOrigin (like TimeFrame Change, EventName Change) are excluded from the analysis sheet.

---

## Import Logic Rules

Import logic applies to: **Working Process**, **All Language Process**, **Master File Update**

### Working Process Import Logic

| Change Type | What Gets Imported | Why |
|-------------|-------------------|-----|
| **No Change** | ✅ STATUS, Text, Desc, FREEMEMO | Everything from PREVIOUS (completed work) |
| **StrOrigin Change** | ✅ STATUS, FREEMEMO, Desc<br>📝 PreviousData<br>❌ Text | Preserve status, but text needs re-translation |
| **Desc Change** | ✅ STATUS, Text, FREEMEMO | Description changed, but content same |
| **TimeFrame Change** | ✅ STATUS, Text, Desc, FREEMEMO | Timing changed, but content same |
| **EventName Change** | ✅ STATUS, Text, Desc, FREEMEMO | Event ID changed, but content likely same |
| **SequenceName Change** | ✅ STATUS, Text, Desc, FREEMEMO | Scene moved, but content same |
| **CastingKey Change** | ✅ STATUS, Text, Desc, FREEMEMO | Voice actor changed, preserve work |
| **DialogType Change** | ✅ STATUS, Text, Desc, FREEMEMO | Classification changed, preserve work |
| **Group Change** | ✅ STATUS, Text, Desc, FREEMEMO | Group assignment changed, preserve work |
| **Character Group Change** | ✅ STATUS, Text, Desc, FREEMEMO | Character attributes changed, preserve work |
| **Composite Changes** | Depends on whether StrOrigin changed | If StrOrigin in change → PreviousData created |
| **New Row** | ❌ Nothing | Brand new content needs fresh translation |

**Complete Change Type List**: See `docs/CHANGE_TYPES_REFERENCE.md` for all 9 core change types, composites, and detection details.

**PreviousData Format**: `"{PreviousStrOrigin} | {PreviousSTATUS} | {PreviousFREEMEMO}"`

**After-Recording Rule**: If PREVIOUS STATUS is after-recording (RECORDED, FINAL, etc.), always preserve it regardless of change type.

### Master File Update Import Logic (v1118.2 - Simplified)

**High Importance Rows**:

| Situation | Action |
|-----------|--------|
| EventName matches in TARGET | Update TARGET columns with SOURCE values<br>Preserves CHANGES from SOURCE |
| EventName not in TARGET | Add new row using TARGET schema<br>Preserves CHANGES from SOURCE |

**Low Importance Rows**:

| Situation | Action |
|-----------|--------|
| All LOW importance rows | Skipped entirely (not processed) |

**Deleted Rows**:

| Situation | Action |
|-----------|--------|
| EventName in TARGET but not in SOURCE | Keep row, set CHANGES = "Deleted" |

**CHANGES Column Handling**:
- Always preserved from SOURCE (Working Process already calculated it)
- No recalculation in Master File Update
- If TARGET doesn't have CHANGES column → Added automatically
- If TARGET has CHANGES column → Replaced with SOURCE values

**Key Point**: Master File Update is now a simple data movement operation, not a comparison process.

---

## Quick Reference

### When to Use Each Process

| Goal | Use This Process |
|------|-----------------|
| "What changed between versions?" | **Raw Process** |
| "Import my translations into new version" | **Working Process** |
| "Update all 3 languages at once" | **All Language Process** |
| "Merge working file into master" | **Master File Update** |

### Common Columns

**Auto-Generated**:
- `CHANGES` - Change classification (New Row, StrOrigin Change, etc.)
- `CastingKey` - Character identifier (auto-generated from CharacterKey + DialogVoice + GroupKey + DialogType)
- `PreviousData` - Historical tracking when StrOrigin changes

**User Columns**:
- `SequenceName`, `EventName`, `StrOrigin` - Core identification
- `STATUS` - Recording status (POLISHED, RECORDED, FINAL, etc.)
- `Text` - Translated text
- `FREEMEMO` - Free-form notes
- `StartFrame`, `EndFrame` - Timing information

### Color Coding (Excel Output)

| Color | Meaning |
|-------|---------|
| 🟢 Green | New Row |
| 🟡 Yellow | StrOrigin Change / SequenceName Change |
| 🟠 Orange | TimeFrame Change |
| 🌸 Pink | EventName Change |
| 🟣 Purple | Desc Change |
| 🔵 Cyan | Combined changes |
| 🔴 Red | Deleted Rows |

### Statistics Accuracy

VRS Manager guarantees **100% accurate row counting**:

```
new_rows - deleted_rows = actual_row_difference
```

This formula always holds true thanks to:
- ✅ 10-Key system (prevents false NEW/DELETED detection)
- ✅ TWO-PASS algorithm (prevents 1-to-many matching)
- ✅ Duplicate handling (StrOrigin, CastingKey, blank cells)

---

## Output Columns (v12051348)

VRS Manager outputs several columns to help you understand and track changes:

### CHANGES Column (Priority-Based)

The **CHANGES** column shows the **most important change** when multiple fields are different. This helps you quickly identify what needs attention first.

**Priority Order** (highest to lowest):
1. StrOrigin Change (dialogue text changed - usually needs re-translation)
2. Desc Change (description/context changed)
3. CastingKey Change (voice actor assignment changed)
4. TimeFrame Change (timing changed)
5. Group Change (organizational change)
6. EventName Change (event identifier changed)
7. SequenceName Change (scene reorganized)
8. DialogType Change (classification changed)
9. CharacterGroup Change (character attributes changed)

**Example**: If both EventName AND StrOrigin changed, the CHANGES column shows "StrOrigin Change" because StrOrigin has higher priority.

### DETAILED_CHANGES Column

The **DETAILED_CHANGES** column shows the **complete list** of all fields that changed. This appears at the far right of the output.

**Example**: `"EventName+StrOrigin+Desc Change"` means all three fields changed.

**When to use**:
- CHANGES = Quick triage (what's most important?)
- DETAILED_CHANGES = Full picture (what exactly changed?)

### PreviousEventName Column

Shows the **old EventName** when an event has been renamed or reorganized.

- **When populated**: Only when EventName changed
- **When empty**: No Change, New Row, or changes that don't involve EventName

### PreviousText Column

Shows the **previous Text/Translation** for all matched rows.

- **When populated**: All rows that were matched (No Change, any Change type)
- **When empty**: New Row (no previous data exists)

**Useful for**: Quickly reviewing what the old translation was without searching the PREVIOUS file.

---

## Version Information

**Current Version**: 12051348 (Production Ready - Smart Change Classification)

**Key Features**:
- ✅ **Smart Change Classification** (v12051348) - Priority-based CHANGES column
  - Shows most important change when multiple fields differ
  - New DETAILED_CHANGES column for complete composite labels
  - New PreviousEventName column for tracking event renames
  - New PreviousText column for easy translation comparison
  - Improved CastingKey handling across different file structures
- ✅ **Word-Level Diff Enhancement** - StrOrigin Analysis with detailed comparison
  - Word-level diff (cleaner output than character-level)
  - Separate "StrOrigin Analysis" sheet with 4-column layout
  - "Diff Detail" column showing exact changes [old→new]
  - Progress bar with filling animation during analysis
  - Works in BOTH Raw and Working Process
  - LIGHT version: Punctuation detection / FULL version: BERT semantic similarity percentages
- ✅ **Super Group Analysis Improvements** - Enhanced clarity and tracking
  - Removed "Others" super group and stageclosedialog check
  - Reordered super groups: AI Dialog before Quest Dialog
  - Added detailed "Super Group Migrations" table below main table
  - Added Narration Dialog tracking (from DialogType column)
  - Added "Item" to Other super group cluster
  - Main Chapters: keyword-based matching (chapter/intro/prolog/epilog)
  - NET CHANGE explanation added below table
- ✅ **Settings Button** - Toggle Priority Change mode ON/OFF
  - ON: CHANGES column shows priority-based label (default)
  - OFF: CHANGES column shows full composite label (legacy mode)
- ✅ **Simplified Master File Update** - EventName-only matching, CHANGES preservation
  - Simple data movement operation (not comparison)
  - CHANGES values always preserved from SOURCE
- ✅ **Column Robustness** - Handles files with different column structures
- ✅ 10-Key Pattern Matching System (Raw/Working/All Language processes)
- ✅ TWO-PASS Algorithm (1-to-1 row matching)
- ✅ 100% Correct Duplicate Handling
- ✅ Multi-language Support (KR/EN/CN)
- ✅ Modular Architecture (31 Python files)
- ✅ Update History Tracking

**GitHub**: [VRS-Manager](https://github.com/NeilVibe/VRS-Manager)

---

## Support

For questions or issues, contact the development team or check the project documentation:
- `README_EN.md` / `README_KR.md` - User documentation
- `DEVELOPER_GUIDE.md` - Technical implementation details
- `claude.md` - AI reference and architecture overview
- `roadmap.md` - Development history and completed features

---

*Last Updated: December 5, 2025 | Version 12051348*
