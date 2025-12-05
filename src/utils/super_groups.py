"""
Super Group classification and aggregation utilities.

This module provides functionality to classify rows into super groups
and aggregate statistics for easier analysis.
"""

from src.utils.helpers import safe_str
from src.config import COL_GROUP, COL_STRORIGIN


def classify_super_group(row, group_value):
    """
    Classify a row into a super group based on Group and DialogType columns.

    Priority order:
    1. DialogType-based rules (Quest Dialog, AI Dialog, Others)
    2. Group-based rules (Main Chapters, Factions)
    3. Group-based rules (Other - specific groups including faction_etc)
    4. Default to "Everything Else" if no match

    Args:
        row: DataFrame row with DialogType column
        group_value: Value from Group column

    Returns:
        str: Super group name (one of 9 defined super groups)
    """
    # Get DialogType (case-insensitive)
    dialog_type = str(row.get("DialogType", "")).lower()
    group_lower = str(group_value).lower()

    # Priority 1: DialogType-based rules (Quest Dialog, AI Dialog, NarrationDialog)
    # These override Group-based rules
    if "questdialog" in dialog_type:
        return "Quest Dialog"
    if "aidialog" in dialog_type:
        return "AI Dialog"
    if "narrationdialog" in dialog_type:
        return "NarrationDialog"

    # Priority 2: Group-based rules
    # Main Chapters: keyword-based matching (chapter/intro/prolog/epilog)
    if "chapter" in group_lower or "intro" in group_lower or "prolog" in group_lower or "epilog" in group_lower:
        return "Main Chapters"

    # Factions: exact match (case-insensitive)
    if group_lower == "faction_01":
        return "Faction 1"
    if group_lower == "faction_02":
        return "Faction 2"
    if group_lower == "faction_03":
        return "Faction 3"

    # Priority 3: Other group - specific categories (case-insensitive)
    other_groups = [
        "police", "minigame", "challenge_abyss", "trade", "church",
        "shop", "contribution", "royalsupply", "research",
        "questgroup_hernand_request", "questgroup_hernand_daily",
        "questgroup_demeniss_request", "quest_group_demeniss_daily",
        "questgroup_delesyia_daily", "faction_etc", "item"
    ]
    if group_lower in other_groups:
        return "Other"

    # Default: Everything Else (catch-all)
    return "Everything Else"


def aggregate_to_super_groups(df_curr, df_prev, pass1_results):
    """
    Aggregate statistics into super groups by classifying each row.

    This processes the current and previous DataFrames to build super group
    statistics from scratch, including translation tracking.

    Args:
        df_curr: Current DataFrame with all rows
        df_prev: Previous DataFrame with all rows
        pass1_results: Dict from compare_rows with classification per row

    Returns:
        tuple: (super_group_stats, migration_details) where:
            - super_group_stats: Dict with per-super-group statistics
            - migration_details: List of migration tuples (source, destination, word_count)
    """
    from src.config import COL_TEXT

    # Initialize all super groups
    super_groups = [
        "Main Chapters", "Faction 1", "Faction 2", "Faction 3",
        "AI Dialog", "Quest Dialog", "NarrationDialog", "Other", "Everything Else"
    ]

    super_group_stats = {}
    for sg in super_groups:
        super_group_stats[sg] = {
            "total_words_prev": 0,
            "total_words_curr": 0,
            "deleted_words": 0,
            "added_words": 0,
            "changed_words": 0,
            "unchanged_words": 0,
            "migrated_in_words": 0,
            "migrated_out_words": 0,
            "translated_words": 0,           # Current translated words
            "untranslated_words": 0,         # Current untranslated words
            "translated_words_prev": 0,      # Previous translated words
            "untranslated_words_prev": 0     # Previous untranslated words
        }

    # Track detailed migrations
    migration_details = []  # List of (source_group, dest_group, word_count)

    # Process current rows
    for curr_idx, curr_row in df_curr.iterrows():
        group_value = curr_row.get(COL_GROUP, "Unknown")
        super_group = classify_super_group(curr_row, group_value)

        curr_strorigin = safe_str(curr_row.get(COL_STRORIGIN, ""))
        curr_words = len(curr_strorigin.split()) if curr_strorigin else 0

        # Check translation status (case-insensitive)
        curr_text = safe_str(curr_row.get(COL_TEXT, "")).lower()
        is_translated = "no translation" not in curr_text

        # Get classification for this row
        change_label, prev_idx, prev_strorigin, _ = pass1_results.get(curr_idx, (None, None, "", []))

        if change_label == "New Row":
            # New row in this super group
            super_group_stats[super_group]["added_words"] += curr_words
            super_group_stats[super_group]["total_words_curr"] += curr_words

            # Track translation
            if is_translated:
                super_group_stats[super_group]["translated_words"] += curr_words
            else:
                super_group_stats[super_group]["untranslated_words"] += curr_words

        elif prev_idx is not None:
            # Row matched to previous
            prev_row = df_prev.loc[prev_idx]
            prev_group = prev_row.get(COL_GROUP, "Unknown")
            prev_super_group = classify_super_group(prev_row, prev_group)

            prev_strorigin_text = safe_str(prev_row.get(COL_STRORIGIN, ""))
            prev_words = len(prev_strorigin_text.split()) if prev_strorigin_text else 0

            # Check previous translation status (case-insensitive)
            prev_text = safe_str(prev_row.get(COL_TEXT, "")).lower()
            prev_is_translated = "no translation" not in prev_text

            # Add to previous super group total
            super_group_stats[prev_super_group]["total_words_prev"] += prev_words

            # Track previous translation status
            if prev_is_translated:
                super_group_stats[prev_super_group]["translated_words_prev"] += prev_words
            else:
                super_group_stats[prev_super_group]["untranslated_words_prev"] += prev_words

            # Add to current super group total
            super_group_stats[super_group]["total_words_curr"] += curr_words

            # Track current translation status
            if is_translated:
                super_group_stats[super_group]["translated_words"] += curr_words
            else:
                super_group_stats[super_group]["untranslated_words"] += curr_words

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

                # Record detailed migration
                migration_details.append((prev_super_group, super_group, curr_words))

    # Process deleted rows
    marked_indices = set(result[1] for result in pass1_results.values() if result[1] is not None)
    deleted_indices = [idx for idx in df_prev.index if idx not in marked_indices]

    for del_idx in deleted_indices:
        del_row = df_prev.loc[del_idx]
        del_group = del_row.get(COL_GROUP, "Unknown")
        super_group = classify_super_group(del_row, del_group)

        del_strorigin = safe_str(del_row.get(COL_STRORIGIN, ""))
        del_words = len(del_strorigin.split()) if del_strorigin else 0

        # Check deleted row translation status
        del_text = safe_str(del_row.get(COL_TEXT, "")).lower()
        del_is_translated = "no translation" not in del_text

        super_group_stats[super_group]["total_words_prev"] += del_words
        super_group_stats[super_group]["deleted_words"] += del_words

        # Track deleted row previous translation status
        if del_is_translated:
            super_group_stats[super_group]["translated_words_prev"] += del_words
        else:
            super_group_stats[super_group]["untranslated_words_prev"] += del_words

    return super_group_stats, migration_details
