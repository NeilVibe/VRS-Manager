# VRS Manager - Development Roadmap

## 📝 Version Update Checklist (IMPORTANT!)

**After completing any code work that changes the version, update ALL of these files:**

- [ ] `src/config.py` → `VERSION` constant and `VERSION_FOOTER`
- [ ] `main.py` → Docstring (line 5) and all print statements (lines 12-15)
- [ ] `README.md` → Version number (line 3) and status line (line 5)
- [ ] `README_EN.md` → Version number (line 3) and status line (line 5)
- [ ] `README_KR.md` → Version number (line 3) and status line (line 5)
- [ ] `roadmap.md` → Current Status header (below) and add to Version History section

**Don't forget to commit all documentation updates together!**

---

## 🎯 Current Status: v1118.6 Production Ready

### ✅ Completed Phases
- **Phase 1.0-2.2**: All core functionality implemented and tested ✅
  - 10-Key Pattern Matching System
  - TWO-PASS Algorithm (1-to-1 Row Matching)
  - TimeFrame Preservation Logic
  - Group Word Count Analysis
  - Master File Update Simplification
  - Super Group Aggregation & Translation Tracking
  - DialogType & Group Change Detection

---

## 📋 Current Priority: StrOrigin Change Analysis (Phase 2.3)

### **Phase 2.2.1: Super Group Analysis Improvements** ✅ **COMPLETED**

#### Overview
Fix confusion and improve clarity in Super Group Word Analysis sheet by resolving "Others" vs "Other" confusion, reordering groups logically, and creating a detailed migration tracking table.

#### Issues Identified

**Issue 1: Remove "Others" Category and stageclosedialog**
- **Current**:
  - `"Others"` super group exists (line 88-90 super_groups.py)
  - DialogType "stageclosedialog" returns "Others" (line 39-40 super_groups.py)
  - `"Other"` is separate category for small groups (police, shop, minigame, etc.)
- **Problem**: "Others" and stageclosedialog are no longer needed
- **Solution**:
  - ❌ Remove "Others" super group entirely from list
  - ❌ Remove stageclosedialog DialogType check (lines 39-40)
  - Result: stageclosedialog (if encountered) falls through to "Everything Else"

**Issue 2: Super Group Order**
- **Current Order**: Main Chapters, Faction 1, Faction 2, Faction 3, Quest Dialog, AI Dialog, Others, Other, Everything Else
- **Desired Order**: Main Chapters, Faction 1, Faction 2, Faction 3, **AI Dialog**, **Quest Dialog**, Other, **Everything Else** (last)
- **Changes**:
  - Swap AI Dialog and Quest Dialog positions
  - Remove "Others"
  - Ensure "Everything Else" is always last in table

**Issue 3: Column Header Too Long**
- **Current**: Column header "Untranslated Words (Remaining to Translate)"
- **Problem**: Header text is too long and takes up excessive space
- **Solution**: Rename to "Not Translated" (simple and clear)

**Issue 4: Migration Tracking**
- **Current**:
  - Main table shows "Words Migrated In" and "Words Migrated Out" columns
  - Only aggregate totals (can't see source → destination details)
- **Problem**: No visibility into WHICH groups moved to WHICH groups
- **Solution**:
  - ❌ Remove "Words Migrated In" and "Words Migrated Out" from main table
  - ✅ Create NEW separate "Super Group Migration Details" table
  - ✅ Show detailed migration pairs with word counts
  - Format: `Source Group → Destination Group : Word Count`
  - Example rows:
    - `Chapter 3 → Faction 3: 4,000 words`
    - `Faction 2 → Main Chapters: 1,250 words`

#### Implementation Requirements

##### **1. Remove "Others" Category and stageclosedialog Check**

**File**: `src/utils/super_groups.py`

**Changes**:
```python
# Lines 39-40: REMOVE these lines entirely
# DELETE:
# if "stageclosedialog" in dialog_type:
#     return "Others"

# Line 88-90: Remove "Others" from list
super_groups = [
    "Main Chapters", "Faction 1", "Faction 2", "Faction 3",
    "AI Dialog", "Quest Dialog", "Other", "Everything Else"  # Removed "Others"
]
```

**Result**: Any DialogType "stageclosedialog" will fall through to default "Everything Else" category

##### **2. Reorder Super Groups**

**File**: `src/utils/super_groups.py`

**Changes**:
```python
# Line 88-90: New order
super_groups = [
    "Main Chapters",      # Story content first
    "Faction 1",          # Faction groups
    "Faction 2",
    "Faction 3",
    "AI Dialog",          # Dialog types (AI before Quest)
    "Quest Dialog",
    "Other",              # Small miscellaneous groups
    "Everything Else"     # Catch-all LAST
]
```

**File**: `src/io/excel_writer.py`

**Impact**: Table rows will now appear in this order automatically (sorted() on line 175 uses dict order)

##### **3. Rename "Untranslated Words" Column Header**

**File**: `src/io/excel_writer.py`

**Changes**:
```python
# Line 219: Rename column header
rows.append({
    # ... other columns ...
    "Translated Words": translated_words,
    "Not Translated": untranslated_words,  # ❌ CHANGED FROM: "Untranslated Words (Remaining to Translate)"
    # ... other columns ...
})

# Line 246-247: Update column width key
column_widths = {
    # ... other columns ...
    'F': 16,  # Translated Words
    'G': 16,  # Not Translated  # ❌ CHANGED FROM: 28 (was too wide for long header)
    # ... other columns ...
}
```

##### **4. Update Explanatory Notes Below Table**

**File**: `src/io/excel_writer.py`

**Changes**:
```python
# Line 354: Remove "Others" from Everything Else note
note_text_3 = (
    'Everything Else: All groups that do not match any other Super Group classification. '
    'This includes groups not specifically categorized under Main Chapters, Factions, Quest Dialog, '
    'AI Dialog, or Other.'  # ❌ REMOVED: "Others, or Other" → NOW: "or Other"
)
```

##### **5. Remove Migration Columns from Main Table**

**File**: `src/io/excel_writer.py`

**Changes**:
```python
# Lines 212-229: Remove migration columns from row dict
rows.append({
    "Super Group Name": super_group_name,
    "Total Words (Current)": curr_total,
    "Total Words (Previous)": prev_total,
    "Net Change": net_change,
    "% Change": pct_change_str,
    "Translated Words": translated_words,
    "Untranslated Words (Remaining to Translate)": untranslated_words,
    "Translation % (Current)": translation_pct_curr_str,
    "Translation % (Previous)": translation_pct_prev_str,
    "Translation % Change": translation_pct_change_str,
    "Words Added": stats["added_words"],
    "Words Deleted": stats["deleted_words"],
    "Words Changed": stats["changed_words"],
    "Words Unchanged": stats["unchanged_words"]
    # ❌ REMOVED: "Words Migrated In": stats["migrated_in_words"],
    # ❌ REMOVED: "Words Migrated Out": stats["migrated_out_words"]
})

# Lines 240-257: Update column widths (remove O and P)
column_widths = {
    'A': 22,  # Super Group Name
    'B': 18,  # Total Words (Current)
    'C': 18,  # Total Words (Previous)
    'D': 14,  # Net Change
    'E': 12,  # % Change
    'F': 16,  # Translated Words
    'G': 28,  # Untranslated Words (Remaining to Translate)
    'H': 18,  # Translation % (Current)
    'I': 18,  # Translation % (Previous)
    'J': 18,  # Translation % Change
    'K': 14,  # Words Added
    'L': 14,  # Words Deleted
    'M': 14,  # Words Changed
    'N': 14   # Words Unchanged
    # ❌ REMOVED: 'O': 16,  # Words Migrated In
    # ❌ REMOVED: 'P': 16   # Words Migrated Out
}
```

##### **6. Track Detailed Migration Pairs**

**File**: `src/utils/super_groups.py`

**New Return Value**: Add migration details tracking

**Changes**:
```python
def aggregate_to_super_groups(df_curr, df_prev, pass1_results):
    """
    Returns:
        tuple: (super_group_stats, migration_details) where:
            - super_group_stats: Dict with per-super-group statistics
            - migration_details: List of migration tuples (source, destination, word_count)
    """
    # ... existing code ...

    # NEW: Track detailed migrations
    migration_details = []  # List of (source_group, dest_group, word_count)

    # In the migration detection section (line 167-176):
    if super_group == prev_super_group:
        # Same super group - check for StrOrigin changes
        if "StrOrigin" in change_label:
            super_group_stats[super_group]["changed_words"] += curr_words
        else:
            super_group_stats[super_group]["unchanged_words"] += curr_words
    else:
        # SUPER GROUP MIGRATION DETECTED
        super_group_stats[prev_super_group]["migrated_out_words"] += prev_words
        super_group_stats[super_group]["migrated_in_words"] += curr_words

        # NEW: Record detailed migration
        migration_details.append((prev_super_group, super_group, curr_words))

    return super_group_stats, migration_details  # Return both
```

##### **7. Create Migration Details Table**

**File**: `src/io/excel_writer.py`

**New Function**: `write_super_group_migration_details()`

**Implementation**:
```python
def write_super_group_migration_details(worksheet, migration_details, start_row):
    """
    Write detailed super group migration table below main analysis.

    Args:
        worksheet: Excel worksheet object
        migration_details: List of tuples (source_group, dest_group, word_count)
        start_row: Row number to start writing (below main table)
    """
    if not migration_details:
        # No migrations detected
        return

    # Aggregate migrations by source → destination pairs
    migration_summary = {}
    for source, dest, words in migration_details:
        key = (source, dest)
        migration_summary[key] = migration_summary.get(key, 0) + words

    # Create migration table
    # Header row
    worksheet[f"A{start_row}"] = "Super Group Migrations"
    worksheet[f"A{start_row}"].font = Font(bold=True, size=12)

    # Column headers
    header_row = start_row + 2
    worksheet[f"A{header_row}"] = "Source Group"
    worksheet[f"B{header_row}"] = "Destination Group"
    worksheet[f"C{header_row}"] = "Words Migrated"

    # Apply header formatting
    for col in ['A', 'B', 'C']:
        cell = worksheet[f"{col}{header_row}"]
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal="center")

    # Data rows
    data_row = header_row + 1
    for (source, dest), word_count in sorted(migration_summary.items(),
                                               key=lambda x: x[1], reverse=True):
        worksheet[f"A{data_row}"] = source
        worksheet[f"B{data_row}"] = dest
        worksheet[f"C{data_row}"] = word_count
        worksheet[f"C{data_row}"].number_format = '#,##0'
        worksheet[f"C{data_row}"].alignment = Alignment(horizontal="right")
        data_row += 1

    # Set column widths
    worksheet.column_dimensions['A'].width = 22
    worksheet.column_dimensions['B'].width = 22
    worksheet.column_dimensions['C'].width = 16

    # Add total row
    total_row = data_row + 1
    worksheet[f"A{total_row}"] = "TOTAL MIGRATIONS"
    worksheet[f"A{total_row}"].font = Font(bold=True)
    worksheet[f"C{total_row}"] = f"=SUM(C{header_row+1}:C{data_row-1})"
    worksheet[f"C{total_row}"].font = Font(bold=True)
    worksheet[f"C{total_row}"].number_format = '#,##0'
    worksheet[f"C{total_row}"].alignment = Alignment(horizontal="right")
```

**Integration**: Call from `write_super_group_word_analysis()` after main table

#### Implementation Steps ✅ ALL COMPLETED

- [x] Remove stageclosedialog check entirely in `super_groups.py` (delete lines 39-40)
- [x] Remove "Others" from super_groups list (line 88-90)
- [x] Reorder super_groups list to new desired order
- [x] Rename column header from "Untranslated Words (Remaining to Translate)" to "Not Translated" (line 219)
- [x] Update column width for "Not Translated" from 28 to 16 (line 247)
- [x] Update "Everything Else" note in `excel_writer.py` (line 354) - remove "Others" reference
- [x] Add migration_details tracking in `aggregate_to_super_groups()`
- [x] Update return value to include migration_details
- [x] Remove migration columns from main table in `excel_writer.py`
- [x] Update column widths dictionary (remove O, P)
- [x] Update formatting loop to exclude O, P columns
- [x] Create `write_super_group_migration_details()` function
- [x] Integrate migration table into `write_super_group_word_analysis()`
- [x] Update all callers to handle new tuple return value
- [x] Test with sample data containing migrations
- [x] Verify table order and migration details

#### Success Criteria

- ✅ "Others" super group completely removed (no longer exists)
- ✅ stageclosedialog DialogType check completely removed (falls through to "Everything Else")
- ✅ Only 8 super groups exist: Main Chapters, F1, F2, F3, AI Dialog, Quest Dialog, Other, Everything Else
- ✅ Super groups appear in correct order: Main Chapters, F1, F2, F3, AI Dialog, Quest Dialog, Other, Everything Else
- ✅ "Everything Else" is always last in table
- ✅ Column header renamed from "Untranslated Words (Remaining to Translate)" to "Not Translated"
- ✅ Column width for "Not Translated" reduced from 28 to 16 (fits new shorter header)
- ✅ Explanatory notes below table updated - "Others" removed from "Everything Else" note
- ✅ Main table has NO migration columns (O, P removed)
- ✅ New "Super Group Migrations" table appears below main table
- ✅ Migration table shows: Source Group | Destination Group | Words Migrated
- ✅ Migration counts are accurate
- ✅ All existing functionality still works

---

## 📋 Next Development Phase

### **Phase 2.2: DialogType & Group Change Detection** ✅ **COMPLETED**

#### Overview
Add "DialogType Change" and "Group Change" markers to the CHANGES column to track when these metadata fields change between Previous and Current TimeFrames. This builds on existing DialogType and Group column identification logic.

#### Feature Components

##### **Change Detection Logic**
- **Target**: Rows where DialogType or Group values differ between Previous and Current
- **Markers**:
  - `"DialogType Change"` - When DialogType value changes
  - `"Group Change"` - When Group value changes
- **Composite Support**: Combine with existing CHANGES markers (e.g., "StrOrigin+DialogType Change")

##### **Implementation Requirements**
1. Use existing DialogType and Group column identification logic
2. Compare Previous vs Current values for each row
3. Add appropriate marker(s) to CHANGES column
4. Follow existing change marker pattern and formatting

#### Implementation Steps
- [x] Identify where DialogType and Group columns are currently tracked
- [x] Add DialogType change detection to CHANGES column logic
- [x] Add Group change detection to CHANGES column logic
- [x] Test with sample data containing DialogType/Group changes
- [x] Verify composite change markers work correctly
- [x] Update version and documentation

#### Success Criteria
- ✅ CHANGES column correctly shows "DialogType Change" when DialogType differs
- ✅ CHANGES column correctly shows "Group Change" when Group differs
- ✅ Composite markers work (e.g., "StrOrigin+DialogType Change")
- ✅ No false positives (empty values, matching values)
- ✅ Existing change detection still works correctly

---

### **Phase 2.3: StrOrigin Change Detail Analysis** 🎯 **IN PLANNING**

#### Overview
Create a dedicated analysis sheet to help analysts understand the nature of StrOrigin changes. This feature creates a new Excel sheet called **"StrOrigin Change Analysis"** that filters and analyzes all rows where CHANGES contains "StrOrigin".

#### Output Structure

**New Sheet**: "StrOrigin Change Analysis"
- **Filter**: Only rows where CHANGES column contains "StrOrigin" (standalone or composite like "StrOrigin+TimeFrame")
- **Column Structure**: All normal columns + new **"StrOrigin Analysis"** column (placed next to CHANGES)
- **Analysis Column Values**:
  - `"Punctuation/Space Change"` - Only whitespace or punctuation differs
  - `"XX.XX% similar"` - Semantic similarity percentage (e.g., "94.5% similar")

#### Feature Components

##### **1. Sheet Creation & Row Filtering**

**Purpose**: Create dedicated analysis sheet with StrOrigin-changed rows only

**Implementation**:
- Create new sheet named **"StrOrigin Change Analysis"**
- Filter all rows where CHANGES contains "StrOrigin" (case-insensitive)
- Include composite changes: "StrOrigin+TimeFrame", "StrOrigin+Group", etc.
- Preserve all existing columns
- Add new column **"StrOrigin Analysis"** immediately after CHANGES column

##### **2. Punctuation/Space Difference Detection (First Pass)**

**Purpose**: Quickly identify if changes are ONLY punctuation or whitespace differences

**Implementation**:
- **Target**: All filtered rows in the new sheet
- **Detection Method**:
  1. Extract Previous StrOrigin and Current StrOrigin values
  2. Normalize both texts:
     - Remove all spaces (`\s+`)
     - Remove all punctuation: `. , ! ? : ; ( ) [ ] { } " ' - — … ` ~` etc.
     - Include Korean/Japanese/Chinese punctuation (Unicode category P*)
  3. Compare normalized strings (case-insensitive)
  4. If identical → Mark as punctuation/space only

- **Output**:
  - Column: **"StrOrigin Analysis"**
  - Value: `"Punctuation/Space Change"` when texts are identical after normalization
  - If NOT identical → Skip to BERT analysis (next step)

**Technical Details**:
```python
# Normalization function
import re
import unicodedata

def normalize_text_for_comparison(text):
    """Remove all spaces and punctuation for comparison"""
    if not isinstance(text, str):
        return ""

    # Remove all whitespace
    text = re.sub(r'\s+', '', text)

    # Remove all punctuation (including Korean, Japanese, Chinese punctuation)
    # Unicode categories: P* = punctuation
    text = ''.join(char for char in text if not unicodedata.category(char).startswith('P'))

    return text.lower()  # Case-insensitive comparison
```

##### **3. Semantic Similarity Analysis (BERT + FAISS) (Second Pass)**

**Purpose**: Calculate semantic similarity percentage for rows that are NOT punctuation/space-only changes

**Trigger**: Only process rows where punctuation check returned FALSE (i.e., substantial content differences exist)

**Model & Dependencies**:
- **Model**: `snunlp/KR-SBERT-V40K-klueNLI-augSTS` (stored locally for offline use)
- **Library**: `sentence-transformers`, `faiss-cpu` or `faiss-gpu`
- **Reference Script**: `/home/neil1988/LocalizationTools/RessourcesForCodingTheProject/MAIN PYTHON SCRIPTS/XLSTransfer0225.py`
- **Storage Location**: `models/kr-sbert/` (inside project directory)

**Local Model Setup (OFFLINE OPERATION)**:

The model will be stored locally in the project for full offline operation. This ensures the program works without internet connectivity.

1. **Initial Model Download** (one-time setup):
```python
from sentence_transformers import SentenceTransformer
import os

# Download model and save locally
model_name = 'snunlp/KR-SBERT-V40K-klueNLI-augSTS'
local_model_path = './models/kr-sbert'

# Create directory if it doesn't exist
os.makedirs(local_model_path, exist_ok=True)

# Download and save model
model = SentenceTransformer(model_name)
model.save(local_model_path)
print(f"Model saved to {local_model_path}")
```

2. **Runtime Usage** (loads from local path - no internet required):
```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'kr-sbert')

# Load model from local path (fully offline)
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Please run model download setup first.")

model = SentenceTransformer(MODEL_PATH)

# Note: Let model.encode() use automatic optimization settings
# No forced batch encoding - auto-detection is preferred
```

**Model Distribution**:
- Model folder (`models/kr-sbert/`) will be included in project distribution
- Uses relative path for portability
- Works on any machine without internet connection
- Model size: ~500MB (will be documented for storage planning)

**Processing Flow**:
   - **Input**: Rows that failed punctuation/space check (substantial changes exist)
   - For each row:
     1. Extract Previous StrOrigin text from row
     2. Extract Current StrOrigin text from row
     3. Generate BERT embeddings for both texts
     4. Calculate cosine similarity using FAISS IndexFlatIP
     5. Convert to percentage (0-100%)
     6. Write to "StrOrigin Analysis" column

**Similarity Calculation**:
```python
def calculate_similarity(text1, text2, model):
    """Calculate cosine similarity between two Korean texts"""
    # Generate embeddings
    embeddings = model.encode([text1, text2], convert_to_tensor=False)
    embeddings = np.array(embeddings)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    # Create FAISS index and search
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings[0:1])  # Add first embedding

    # Search for second embedding
    distances, indices = index.search(embeddings[1:2], 1)
    similarity_score = distances[0][0]

    # Convert to percentage
    similarity_percentage = round(similarity_score * 100, 2)

    return similarity_percentage
```

**Output**:
   - Column: **"StrOrigin Analysis"**
   - Value: `"{similarity_percentage}% similar"` (e.g., "94.5% similar", "87.32% similar")
   - Format: Always 2 decimal places
   - Only runs for rows NOT marked as "Punctuation/Space Change"

#### Processing Summary

**Two-Step Analysis Process**:

1. **Step 1 (Fast)**: Punctuation/Space Check
   - All StrOrigin-changed rows processed
   - If ONLY punctuation/space differs → Write `"Punctuation/Space Change"` → DONE
   - If substantial content differs → Proceed to Step 2

2. **Step 2 (BERT+FAISS)**: Semantic Similarity
   - Only rows with substantial content changes
   - Calculate similarity percentage using Korean BERT embeddings
   - Write `"XX.XX% similar"` to StrOrigin Analysis column

**Performance Optimization**:
- Step 1 is fast (simple string normalization)
- Step 2 only runs when necessary (skips punctuation-only changes)
- Reduces BERT processing load significantly

---

#### Implementation Plan

**Step 1: Sheet Creation & Filtering**
- [ ] Create new Excel sheet "StrOrigin Change Analysis" in Working processor output
- [ ] Filter rows where CHANGES contains "StrOrigin" (case-insensitive substring match)
- [ ] Include composite changes (e.g., "StrOrigin+TimeFrame", "StrOrigin+Group")
- [ ] Copy all existing columns to new sheet
- [ ] Add new column "StrOrigin Analysis" immediately after CHANGES column

**Step 2: Punctuation/Space Detection Module**
- [ ] Create utility function `normalize_text_for_comparison(text)` for text normalization
- [ ] Test normalization with Korean/Japanese/Chinese punctuation examples
- [ ] Implement two-step comparison logic:
  - Step 1: Normalize and compare texts
  - Step 2: If identical → Write "Punctuation/Space Change"
  - Step 3: If NOT identical → Skip to BERT analysis
- [ ] Write unit tests with sample punctuation-only changes

**Step 3: Local Model Setup (Offline Operation)**
- [ ] Create `models/kr-sbert/` directory in project root
- [ ] Write model download script (`download_model.py`) for initial setup
- [ ] Download and save EXACT model: `snunlp/KR-SBERT-V40K-klueNLI-augSTS` (~500MB)
- [ ] Verify model files are saved correctly (config.json, pytorch_model.bin, etc.)
- [ ] Test loading model from local path (verify offline operation)
- [ ] **Disconnect from internet and test again** (confirm fully offline)
- [ ] Add `models/` folder to project structure and version control (or distribution package)
- [ ] Update .gitignore if model is too large (use Git LFS or document download process)
- [ ] Document model setup in README with clear instructions

**Step 4: BERT/FAISS Similarity Module**
- [ ] Install dependencies: `sentence-transformers`, `faiss-cpu`
- [ ] Implement model loader with local path (PROJECT_ROOT/models/kr-sbert)
- [ ] Add error handling for missing model files
- [ ] Implement `calculate_similarity(text1, text2, model)` function
- [ ] Return similarity as percentage (0-100%) with 2 decimal places
- [ ] Add progress logging for batch processing (every N rows)
- [ ] Test with sample Korean text pairs (verify offline mode)

**Step 5: Integration & Processing Logic**
- [ ] Implement two-step processing in "StrOrigin Change Analysis" sheet:
  - **First Pass**: Run punctuation/space check on ALL filtered rows
  - **Second Pass**: Run BERT similarity ONLY on rows that failed first pass
- [ ] Write results to "StrOrigin Analysis" column:
  - `"Punctuation/Space Change"` for punctuation-only
  - `"XX.XX% similar"` for BERT-analyzed rows
- [ ] Add row counter/progress indicator for BERT processing
- [ ] Handle edge cases (empty strings, very short texts, etc.)

**Step 6: Performance Optimization**
- [ ] Profile execution time with real data
- [ ] Consider batching embeddings if processing many rows
- [ ] Add optional feature flag to enable/disable similarity analysis
- [ ] Document memory requirements (BERT model size: ~500MB)

**Step 7: Testing & Validation**
- [ ] Create test dataset with known punctuation-only changes
- [ ] Create test dataset with high/low similarity pairs
- [ ] Validate output column is correctly populated
- [ ] Test with production-scale data
- [ ] Update user documentation

---

#### Success Criteria
- ✅ **Sheet Creation**: "StrOrigin Change Analysis" sheet created in Working processor output
- ✅ **Row Filtering**: Only rows with "StrOrigin" in CHANGES are included (including composites)
- ✅ **Column Structure**: "StrOrigin Analysis" column added immediately after CHANGES
- ✅ **Punctuation Detection**: Correctly identifies punctuation/space-only changes
- ✅ **Similarity Scores**: Accurate percentages matching manual inspection
- ✅ **Two-Step Process**: Punctuation check runs first, BERT only on remaining rows
- ✅ **Performance**: Processing time reasonable (< 5 seconds per 100 rows for BERT)
- ✅ **Edge Cases**: No crashes with empty strings, special characters, or very short texts
- ✅ **Offline Operation**: Works without internet connection
- ✅ **Model Verification**: Uses EXACT model `snunlp/KR-SBERT-V40K-klueNLI-augSTS`
- ✅ **Documentation**: User guide updated with new sheet explanation and model setup

---

#### Technical Notes

**⚠️ CRITICAL: Model Specification**:
- **MUST USE**: `snunlp/KR-SBERT-V40K-klueNLI-augSTS` (EXACT model from XLSTransfer0225.py line 41)
- **NO SUBSTITUTIONS** - This is the only approved model
- **Local Storage**: `./models/kr-sbert/` (relative to project root)
- **Model Size**: Approximately 500MB
- **Offline Operation**: Model downloaded once, then runs fully offline

**Reference Locations**:
- BERT Model Usage: `XLSTransfer0225.py` line 41
- FAISS Index Creation: `XLSTransfer0225.py` lines 310-353
- FAISS Similarity Search: `XLSTransfer0225.py` lines 506-525
- Encoding Reference: `XLSTransfer0225.py` line 266, 508 (model.encode usage)

**Key Implementation Details**:
- **Offline First**: Load model from local path, no internet required at runtime
- **Relative Paths**: Use `os.path.join(PROJECT_ROOT, 'models', 'kr-sbert')` for portability
- **Automatic Optimization**: Let model.encode() use automatic settings (no forced batching)
- **FAISS Normalization**: Use `faiss.normalize_L2()` before similarity calculation
- **Index Type**: `IndexFlatIP` for inner product (cosine similarity after normalization)
- **Filtering**: Process only rows with StrOrigin changes (filter by CHANGES column)
- **Performance**: Punctuation check runs first (faster), similarity only if not punctuation-only

**Project Structure**:
```
vrsmanager/
├── models/
│   └── kr-sbert/           # Local BERT model (included in distribution)
│       ├── config.json
│       ├── pytorch_model.bin
│       ├── tokenizer_config.json
│       └── ... (other model files)
├── src/
│   └── processors/
│       └── working_processor.py   # Will contain StrOrigin analysis
├── download_model.py      # One-time model download script
└── requirements.txt
```

**Dependencies to Add**:
```python
# requirements.txt additions
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4  # or faiss-gpu for GPU support
torch>=1.9.0
```

**Initial Setup Script** (`download_model.py`):
```python
"""
One-time model download script
Run this once to set up the local model for offline use
"""
from sentence_transformers import SentenceTransformer
import os

# CRITICAL: Use exact model from XLSTransfer0225.py
MODEL_NAME = 'snunlp/KR-SBERT-V40K-klueNLI-augSTS'
LOCAL_PATH = './models/kr-sbert'

os.makedirs(LOCAL_PATH, exist_ok=True)
print(f"Downloading model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)
model.save(LOCAL_PATH)
print(f"✓ Model saved to {LOCAL_PATH}")
print("✓ Offline operation ready!")
```

---

## Version History

### v1118.6 (Current - Production Ready)
- **CRITICAL BUG FIXES**:
  - Fixed TypeError 'unhashable type: dict' in Working VRS Check
  - Fixed lookup dictionaries storing dict objects instead of indices (src/core/working_helpers.py)
  - Applied safe_str() pattern to all DataFrame column access across all processors
  - Fixed src/core/lookups.py, comparison.py, working_comparison.py, alllang_helpers.py
- **COMPREHENSIVE TESTING**:
  - Created 5000-row test suite with 10 edge case scenarios
  - Verified 100% accuracy: change detection, new rows, deleted rows
  - Mathematical verification: all rows accounted for, zero loss
  - Performance tested: 879 rows/sec (Raw), 856 rows/sec (Working)
- **DOCUMENTATION**:
  - Created CLAUDE.md reference guide for future Claude instances
  - Updated all Excel guides (EN/KR) with v1118.6 changelog
  - Unified version numbers across all files
  - Manual-trigger build system (BUILD_TRIGGER.txt)

### v1118.5
- DialogType & Group Change Detection
- Added "DialogType Change" and "Group Change" markers to CHANGES column
- Support for composite markers (e.g., "StrOrigin+DialogType Change")
- Works in both Raw and Working processors

### v1118.4
- **Phase 2.2.1 COMPLETED**: Super Group Analysis Improvements
  - Removed "Others" super group and stageclosedialog check
  - Reordered super groups: AI Dialog now before Quest Dialog
  - Renamed "Untranslated Words (Remaining to Translate)" → "Not Translated"
  - Removed migration columns from main table
  - Added detailed "Super Group Migrations" table (source → destination pairs)
  - Updated explanatory notes below table
- Super Group Aggregation & Translation Tracking
- Enhanced Word Analysis with reorganized columns

### v1118.3
- Master File Update with TimeFrame Preservation

### v1118.2
- Master File Update Simplification
- EventName-only matching

---

## Future Considerations

**After Phase 2.2**:
- Additional change detail analysis for other change types
- Visual diff tool for StrOrigin changes
- Export detailed change reports
- Performance optimization for large datasets
