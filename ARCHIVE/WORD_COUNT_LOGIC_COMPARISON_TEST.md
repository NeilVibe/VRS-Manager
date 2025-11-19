# Word Count Logic Comparison Test

## Objective

Compare two approaches for calculating super group word counts:
1. **Current 10-Key System**: Uses complex matching with 10 different key combinations
2. **Simple EventName Pairing**: Uses only EventName as unique identifier

## Research Question

**Can we achieve accurate word count tracking using just EventName pairing, without the complexity of the 10-key matching system?**

## Hypothesis

**Simple EventName Matching Approach:**
- Use EventName as the ONLY matching key (assume it's unique)
- Match rows between PREVIOUS and CURRENT files by EventName
- For matched rows: Check if StrOrigin changed, check if super group changed
- For unmatched rows: Classify as added (CURRENT only) or deleted (PREVIOUS only)
- Calculate all the same metrics: added, deleted, changed, unchanged, migrations

**Question:** Does EventName-only matching produce identical results to the 10-key system?

**What we want to find out:**
- Are the word counts exactly the same?
- Do we get the same additions/deletions/changes?
- Do we detect the same migrations?
- Is the 10-key system necessary, or is it over-engineering?

## Test Methodology

### Approach 1: Current 10-Key System
```
1. Match rows using 10-key TWO-PASS algorithm (SE, SO, SC, EO, EC, OC, SEO, SEC, SOC, EOC)
2. For each matched pair:
   - Track which super group in PREVIOUS
   - Track which super group in CURRENT
   - Detect migrations (different super groups)
   - Detect changes (different StrOrigin)
3. Track deleted rows (in PREVIOUS but no match in CURRENT)
4. Track new rows (in CURRENT but no match in PREVIOUS)
5. Calculate per super group:
   - total_words_prev
   - total_words_curr
   - added_words, deleted_words, changed_words, unchanged_words
   - migrated_in_words, migrated_out_words
```

### Approach 2: Simple EventName Pairing
```
1. Create EventName → row mapping for PREVIOUS file
2. Create EventName → row mapping for CURRENT file
3. For each EventName in CURRENT:
   - If exists in PREVIOUS: Pair them
   - If not in PREVIOUS: Mark as "New"
4. For each EventName in PREVIOUS:
   - If not in CURRENT: Mark as "Deleted"
5. For each paired row:
   - Calculate word count in both files
   - Assign to super group in both files
   - Check if StrOrigin changed
   - Check if super group changed (migration)
6. Calculate per super group:
   - total_words_prev (sum of all PREVIOUS rows in this super group)
   - total_words_curr (sum of all CURRENT rows in this super group)
   - Derive changes from the difference
```

### Comparison Metrics

For each super group, compare:
1. **Total Words (Previous)**: Do both approaches get same count?
2. **Total Words (Current)**: Do both approaches get same count?
3. **Added Words**: Same?
4. **Deleted Words**: Same?
5. **Changed Words**: Same?
6. **Unchanged Words**: Same?
7. **Migrated In/Out**: Same?
8. **Translation Counts**: Same?

### Success Criteria

**Simple approach is viable IF:**
- ✅ Total word counts match exactly (PREVIOUS and CURRENT)
- ✅ All super group totals match exactly
- ✅ Addition/deletion/modification counts match
- ✅ Migration detection works correctly
- ✅ No false positives or false negatives

**Simple approach fails IF:**
- ❌ Any word count mismatches
- ❌ Missing migrations
- ❌ Incorrect change classification
- ❌ Duplicate EventName handling issues

## Test Data

Using existing test files:
- `tests/test_supergroup_PREVIOUS.xlsx` (650 rows)
- `tests/test_supergroup_CURRENT.xlsx` (650 rows)

These files contain:
- Various super groups (Main Chapters, Factions, Quest Dialog, AI Dialog, Others)
- New rows (50 added)
- Deleted rows (50 removed)
- Migrations (group changes)
- DialogType-based classification
- Translation status (Text column)

## Expected Outcomes

### Scenario A: EventName Is Always Unique AND Never Changes
**Expected result:** Both approaches produce IDENTICAL results
**Conclusion:** Simple EventName matching is sufficient, 10-key system is unnecessary complexity

### Scenario B: EventName Has Duplicates
**Expected result:**
- Simple approach: 1-to-many matching problems, wrong word counts
- 10-key approach: Correct matching using additional context
**Conclusion:** 10-key system is necessary

### Scenario C: EventName Changes Between Files (Renamed Events)
**Expected result:**
- Simple approach: Misses matches, counts as deleted + added (inflated changes)
- 10-key approach: Finds match via StrOrigin fallback, correct classification
**Conclusion:** 10-key fallback is necessary

### Scenario D: EventName Unique BUT Data Has Edge Cases
**Expected result:** Differences reveal specific edge cases where 10-key helps
**Conclusion:** Identify which fallback keys are actually used in practice

## What We'll Learn

1. **Data Quality**: Are EventNames truly unique in our test data?
2. **Match Accuracy**: Does simple pairing find all correct matches?
3. **Migration Detection**: Can we detect super group changes with simple pairing?
4. **Edge Cases**: What breaks with the simple approach?
5. **Simplification Viability**: Can we safely remove the 10-key complexity?

## Implementation Plan

1. Create `test_simple_eventname_pairing.py`:
   - Implement simple EventName-based word counting
   - Calculate super group totals using simple pairing
   - Compare results with 10-key system output

2. Generate comparison report showing:
   - Side-by-side results (10-key vs simple)
   - Differences highlighted
   - Match quality metrics
   - Recommendations

3. Analyze results and decide:
   - Keep 10-key system (if necessary)
   - Simplify to EventName pairing (if sufficient)
   - Hybrid approach (EventName primary, 10-key fallback)

## Questions to Answer

1. Do both approaches produce identical word counts per super group?
2. Are there any EventName duplicates in the test data?
3. Does the simple approach miss any matches that 10-key finds?
4. Does the simple approach produce false matches that 10-key avoids?
5. Which approach is more accurate for word count tracking?

---

**Test Status:** Ready to implement
**Date:** 2025-11-17
**Goal:** Determine if we can simplify word count logic without losing accuracy
