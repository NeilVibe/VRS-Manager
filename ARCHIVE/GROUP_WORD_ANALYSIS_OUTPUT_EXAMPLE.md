# Group Word Analysis - Output Example

## What the New Sheet Will Look Like

When the feature is implemented, every comparison output Excel file will have a new sheet called **"Group Word Analysis"**.

### Sheet Structure

```
┌────────────────┬──────────┬──────────┬────────┬─────────┬─────────┬───────────┬────────────┬─────────────┬───────────┬─────────┐
│ Group Name     │ Prev     │ Curr     │ Added  │ Deleted │ Changed │ Unchanged │ Migr In    │ Migr Out    │ Net Chg   │ % Chg   │
├────────────────┼──────────┼──────────┼────────┼─────────┼─────────┼───────────┼────────────┼─────────────┼───────────┼─────────┤
│ Intro          │ 1,200    │ 1,200    │ 0      │ 0       │ 0       │ 1,200     │ 0          │ 0           │ 0         │ 0.00%   │
│ Prolog         │ 1,500    │ 1,400    │ 0      │ 100     │ 0       │ 1,400     │ 0          │ 0           │ -100      │ -6.67%  │
│ Chapter1       │ 5,000    │ 5,250    │ 250    │ 0       │ 0       │ 5,000     │ 0          │ 0           │ +250      │ +5.00%  │
│ Chapter2       │ 8,000    │ 8,200    │ 0      │ 0       │ 200     │ 8,000     │ 0          │ 0           │ +200      │ +2.50%  │
│ Chapter3       │ 15,000   │ 11,300   │ 500    │ 1,200   │ 0       │ 13,300    │ 0          │ 3,000       │ -3,700    │ -24.67% │
│ Chapter4       │ 7,500    │ 7,500    │ 0      │ 0       │ 0       │ 7,500     │ 0          │ 0           │ 0         │ 0.00%   │
│ Chapter5       │ 6,200    │ 6,400    │ 350    │ 150     │ 0       │ 6,050     │ 0          │ 0           │ +200      │ +3.23%  │
│ Chapter6       │ 4,000    │ 7,500    │ 500    │ 0       │ 0       │ 4,000     │ 3,000      │ 0           │ +3,500    │ +87.50% │
│ Final Chapter  │ 2,800    │ 2,800    │ 0      │ 0       │ 0       │ 2,800     │ 0          │ 0           │ 0         │ 0.00%   │
├────────────────┼──────────┼──────────┼────────┼─────────┼─────────┼───────────┼────────────┼─────────────┼───────────┼─────────┤
│ TOTAL          │ 51,200   │ 51,550   │ 1,600  │ 1,450   │ 200     │ 50,250    │ 3,000      │ 3,000       │ +350      │ +0.68%  │
└────────────────┴──────────┴──────────┴────────┴─────────┴─────────┴───────────┴────────────┴─────────────┴───────────┴─────────┘
```

### Column Explanations

| Column | Meaning | Calculation |
|--------|---------|-------------|
| **Group Name** | Name of the chapter/category | From "Group" column in Excel |
| **Prev** | Total words in this group (previous file) | Sum of all StrOrigin word counts in group (previous) |
| **Curr** | Total words in this group (current file) | Sum of all StrOrigin word counts in group (current) |
| **Added** | Words from NEW rows added to this group | Word count of rows that didn't exist in previous, now in this group |
| **Deleted** | Words from rows deleted from this group | Word count of rows that existed in previous, no longer in current |
| **Changed** | Words in rows where StrOrigin text changed | Word count (current) of rows that matched but StrOrigin modified |
| **Unchanged** | Words in rows that didn't change | Word count of rows that matched with no StrOrigin change |
| **Migr In** | Words that moved INTO this group from other groups | Word count of rows that matched but came from different group |
| **Migr Out** | Words that moved OUT of this group to other groups | Word count of rows that matched but went to different group |
| **Net Chg** | Net change in word count | Curr - Prev |
| **% Chg** | Percentage change | ((Curr - Prev) / Prev) × 100% |

### Example Interpretation

Looking at the table above:

**Chapter3 Analysis:**
- Started with 15,000 words
- Ended with 11,300 words
- Lost 3,700 words total (-24.67%)
- **Why?**
  - 3,000 words migrated OUT to other groups (likely Chapter6)
  - 1,200 words deleted entirely
  - 500 NEW words added
  - Net: 15,000 + 500 - 1,200 - 3,000 = 11,300 ✓

**Chapter6 Analysis:**
- Started with 4,000 words
- Ended with 7,500 words
- Gained 3,500 words (+87.50%)
- **Why?**
  - 3,000 words migrated IN from other groups (likely Chapter3)
  - 500 NEW words added
  - 0 words deleted
  - Net: 4,000 + 3,000 + 500 = 7,500 ✓

### Visual Formatting

The Excel sheet will have:
- **Bold blue header** row with white text
- **Number formatting** with thousand separators (15,000)
- **Color coding** for Net Change column:
  - 🟢 Green for positive (+250)
  - 🔴 Red for negative (-100)
  - ⚫ Black for zero (0)
- **Bold TOTAL row** at the bottom
- **Auto-sized columns** for readability

### How This Helps Your Team

**For Voice Actors:**
- Filter by their assigned group (e.g., "Chapter3")
- See exactly how many words changed in their section
- Understand if content moved to other chapters
- Know if they need to re-record lines

**For Managers:**
- Quickly identify which chapters changed the most
- Track content migrations between chapters
- Validate that total word counts match expectations
- Monitor scope changes across the project

**For QA:**
- Verify word count changes are intentional
- Catch unexpected deletions or additions
- Ensure migrations are tracked correctly
- Validate consistency across groups

### Validation

The sheet includes validation logic:
- **Sum of all "Prev" must equal total file word count (previous)**
- **Sum of all "Curr" must equal total file word count (current)**
- **Sum of "Migr In" must equal sum of "Migr Out"** (words don't disappear when migrating)
- **For each group: Curr = Prev + Added - Deleted + Migr In - Migr Out ± Changed**

These validations ensure 100% accuracy of group-level tracking.

---

## Real-World Use Case

**Scenario**: Game script update with voice acting

1. **Initial state (Previous file)**:
   - Chapter3 has 1000 lines (15,000 words)
   - Chapter6 has 300 lines (4,000 words)

2. **Script revision (Current file)**:
   - Writers moved 200 lines from Chapter3 to Chapter6 (3,000 words)
   - Writers deleted 80 lines from Chapter3 (1,200 words)
   - Writers added 30 NEW lines to Chapter3 (500 words)

3. **Without Group Analysis**:
   - Voice actors see "3,700 words changed in the file"
   - No idea which chapter changed
   - No idea what happened to their recorded lines

4. **With Group Analysis** ✅:
   - **Chapter3 actor sees**:
     - Lost 3,000 words to Chapter6 (not their responsibility anymore)
     - Lost 1,200 words to deletions (don't need to record)
     - Got 500 NEW words (need to record these)
     - Net: -3,700 words in their chapter

   - **Chapter6 actor sees**:
     - Gained 3,000 words from Chapter3 (need to record these)
     - Gained 500 NEW words (need to record these)
     - Net: +3,500 words in their chapter

5. **Result**:
   - Clear action items for each voice actor
   - No confusion about scope changes
   - Managers can track content migrations
   - QA can validate changes are intentional

---

## Technical Notes

### Word Count Calculation
```python
word_count = len(str(row['StrOrigin']).split())
```

Examples:
- "안녕하세요 반갑습니다" → 2 words
- "Hello world" → 2 words
- "This is a test string" → 5 words

### Group Migration Detection
```python
if row_matched and (curr_group != prev_group):
    # This is a MIGRATION
    prev_groups[prev_group]['migrated_out'] += word_count
    curr_groups[curr_group]['migrated_in'] += word_count
```

### Edge Cases Handled
- **Missing Group value**: Assigned to "Unknown" group
- **New groups in current file**: Shown with Prev = 0
- **Deleted groups**: Shown with Curr = 0
- **Empty StrOrigin**: Word count = 0

---

**Document Version**: 1.0
**Date**: 2025-11-17
**Purpose**: Visual reference for implementation and user understanding
