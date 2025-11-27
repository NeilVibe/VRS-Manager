"""
Add Group column to comprehensive test files.

This script adds a "Group" column to the existing test_comprehensive_PREVIOUS.xlsx
and test_comprehensive_CURRENT.xlsx files to enable testing of group-level
word count analysis.

Groups created:
- Intro, Prolog, Chapter1, Chapter2, Chapter3, Chapter4, Chapter5, Chapter6, Final Chapter

Test scenarios:
- Stable groups (no changes)
- Group migrations (Chapter3 → Chapter6)
- Deletions within groups
- Additions within groups
- StrOrigin changes within groups
"""

import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def add_group_column():
    """Add Group column to test files with realistic scenarios."""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prev_path = os.path.join(script_dir, "test_comprehensive_PREVIOUS.xlsx")
    curr_path = os.path.join(script_dir, "test_comprehensive_CURRENT.xlsx")

    print("="*70)
    print("ADDING GROUP COLUMN TO COMPREHENSIVE TEST FILES")
    print("="*70)

    # Read existing test files
    print(f"\nReading test files...")
    df_prev = pd.read_excel(prev_path)
    df_curr = pd.read_excel(curr_path)

    print(f"  PREVIOUS: {len(df_prev):,} rows")
    print(f"  CURRENT:  {len(df_curr):,} rows")

    # Define groups (9 groups to distribute ~850 rows)
    groups = [
        "Intro",
        "Prolog",
        "Chapter1",
        "Chapter2",
        "Chapter3",
        "Chapter4",
        "Chapter5",
        "Chapter6",
        "Final Chapter"
    ]

    rows_per_group = len(df_prev) // len(groups)
    print(f"\nDistributing ~{rows_per_group} rows per group")

    # Assign groups to PREVIOUS (simple distribution)
    print("\nAssigning groups to PREVIOUS file...")
    group_assignments_prev = []
    group_counts_prev = {g: 0 for g in groups}

    for i in range(len(df_prev)):
        group_idx = (i // rows_per_group) % len(groups)
        group_name = groups[group_idx]
        group_assignments_prev.append(group_name)
        group_counts_prev[group_name] += 1

    # Insert Group column as second column (after first column)
    df_prev.insert(1, 'Group', group_assignments_prev)

    print("  Group distribution in PREVIOUS:")
    for group, count in group_counts_prev.items():
        print(f"    {group:15s}: {count:3d} rows")

    # Assign groups to CURRENT with migrations
    print("\nAssigning groups to CURRENT file (with migrations)...")
    group_assignments_curr = []
    group_counts_curr = {g: 0 for g in groups}
    migration_count = 0

    for i in range(len(df_curr)):
        # Get the previous group assignment for this row index
        if i < len(group_assignments_prev):
            prev_group = group_assignments_prev[i]

            # Create migrations: Move some Chapter3 rows to Chapter6
            # This simulates realistic scenario where content moves between chapters
            if prev_group == "Chapter3" and i % 10 == 0:
                # Every 10th Chapter3 row migrates to Chapter6
                group_assignments_curr.append("Chapter6")
                group_counts_curr["Chapter6"] += 1
                migration_count += 1
            else:
                # Keep same group
                group_assignments_curr.append(prev_group)
                group_counts_curr[prev_group] += 1
        else:
            # Fallback for any extra rows
            group_assignments_curr.append("Intro")
            group_counts_curr["Intro"] += 1

    # Insert Group column as second column
    df_curr.insert(1, 'Group', group_assignments_curr)

    print("  Group distribution in CURRENT:")
    for group, count in group_counts_curr.items():
        print(f"    {group:15s}: {count:3d} rows")

    print(f"\n  Migrations created: {migration_count} rows (Chapter3 → Chapter6)")

    # Save updated files
    print("\nSaving updated files...")
    df_prev.to_excel(prev_path, index=False)
    df_curr.to_excel(curr_path, index=False)

    print(f"  ✓ Saved: {prev_path}")
    print(f"  ✓ Saved: {curr_path}")

    # Validation
    print("\n" + "="*70)
    print("VALIDATION")
    print("="*70)

    # Re-read to verify
    df_prev_check = pd.read_excel(prev_path)
    df_curr_check = pd.read_excel(curr_path)

    prev_has_group = 'Group' in df_prev_check.columns
    curr_has_group = 'Group' in df_curr_check.columns

    print(f"\nGroup column in PREVIOUS: {'✓ YES' if prev_has_group else '✗ NO'}")
    print(f"Group column in CURRENT:  {'✓ YES' if curr_has_group else '✗ NO'}")

    if prev_has_group:
        print(f"\nPREVIOUS - Unique groups: {df_prev_check['Group'].unique()}")
        print(f"PREVIOUS - Total rows: {len(df_prev_check):,}")

    if curr_has_group:
        print(f"\nCURRENT - Unique groups: {df_curr_check['Group'].unique()}")
        print(f"CURRENT - Total rows: {len(df_curr_check):,}")

    # Check migrations
    if prev_has_group and curr_has_group:
        print("\nMigration check:")
        chapter3_prev = group_counts_prev.get("Chapter3", 0)
        chapter3_curr = group_counts_curr.get("Chapter3", 0)
        chapter6_prev = group_counts_prev.get("Chapter6", 0)
        chapter6_curr = group_counts_curr.get("Chapter6", 0)

        chapter3_lost = chapter3_prev - chapter3_curr
        chapter6_gained = chapter6_curr - chapter6_prev

        print(f"  Chapter3: {chapter3_prev} → {chapter3_curr} ({chapter3_lost:+d} rows)")
        print(f"  Chapter6: {chapter6_prev} → {chapter6_curr} ({chapter6_gained:+d} rows)")
        print(f"  Expected migrations: {migration_count}")

    print("\n" + "="*70)
    print("✓✓✓ GROUP COLUMN SUCCESSFULLY ADDED ✓✓✓")
    print("="*70)
    print("\nTest files are ready for Group Word Count Analysis testing!")

    return True


if __name__ == "__main__":
    try:
        success = add_group_column()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
