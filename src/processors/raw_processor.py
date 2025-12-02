"""
Raw VRS Check processor.

This processor compares a previous raw VRS file with a current one,
identifying changes and generating a comparison report.
"""

import os
import pandas as pd

# Conditional tkinter import for headless testing
if os.environ.get('HEADLESS', '').lower() not in ('1', 'true', 'yes'):
    from tkinter import messagebox
else:
    messagebox = None

from src.processors.base_processor import BaseProcessor
from src.io.excel_reader import safe_read_excel
from src.io.formatters import apply_direct_coloring, widen_summary_columns
from src.io.excel_writer import write_super_group_word_analysis
from src.utils.data_processing import normalize_dataframe_status, filter_output_columns, remove_full_duplicates
from src.utils.helpers import log, get_script_dir
from src.utils.super_groups import aggregate_to_super_groups
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.core.casting import generate_casting_key
from src.config import (
    OUTPUT_COLUMNS_RAW,
    COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY,
    COL_STRORIGIN, COL_PREVIOUS_STRORIGIN, COL_EVENTNAME, COL_TEXT,
    COL_CHANGES, COL_DETAILED_CHANGES, COL_PREVIOUS_EVENTNAME, COL_PREVIOUS_TEXT,
    COL_PREVIOUSDATA
)
from src.core.change_detection import get_priority_change
from src.io.summary import create_raw_summary
from src.utils.strorigin_analysis import StrOriginAnalyzer


class RawProcessor(BaseProcessor):
    """
    Processor for Raw VRS Check.

    Compares previous and current raw VRS files to identify changes,
    applying the 4-tier key matching system.
    """

    def __init__(self):
        """Initialize the raw processor."""
        super().__init__()
        self.df_prev = None
        self.df_curr = None
        self.prev_lookup_cw = None
        self.prev_lookup_cg = None
        self.prev_lookup_es = None
        self.prev_lookup_cs = None
        self.changed_columns_map = None

    def get_process_name(self):
        """Get the process name."""
        return "PROCESS RAW VRS CHECK"

    def select_files(self):
        """Prompt user to select previous and current files."""
        self.prev_file = self._select_single_file("RAW CHECK: Select PREVIOUS Excel file")
        if not self.prev_file:
            return False

        self.curr_file = self._select_single_file("RAW CHECK: Select CURRENT Excel file")
        if not self.curr_file:
            return False

        return True

    def read_files(self):
        """Read and normalize the selected files."""
        try:
            log(f"Reading PREVIOUS: {os.path.basename(self.prev_file)}")
            self.df_prev = safe_read_excel(self.prev_file, header=0, dtype=str)
            log(f"  → {len(self.df_prev):,} rows, {self.df_prev.shape[1]} columns")

            log(f"Reading CURRENT: {os.path.basename(self.curr_file)}")
            self.df_curr = safe_read_excel(self.curr_file, header=0, dtype=str)
            log(f"  → {len(self.df_curr):,} rows, {self.df_curr.shape[1]} columns")

            log("Normalizing STATUS columns...")
            self.df_prev = normalize_dataframe_status(self.df_prev)
            self.df_curr = normalize_dataframe_status(self.df_curr)

            log("Removing full duplicate rows...")
            self.df_prev = remove_full_duplicates(self.df_prev, "PREVIOUS")
            self.df_curr = remove_full_duplicates(self.df_curr, "CURRENT")

            log("Generating CastingKey column for PREVIOUS...")
            casting_keys_prev = []
            for idx, row in self.df_prev.iterrows():
                casting_key = generate_casting_key(
                    row.get(COL_CHARACTERKEY, ""),
                    row.get(COL_DIALOGVOICE, ""),
                    row.get(COL_SPEAKER_GROUPKEY, ""),
                    row.get("DialogType", "")
                )
                casting_keys_prev.append(casting_key)
            self.df_prev[COL_CASTINGKEY] = casting_keys_prev
            log(f"  → Generated CastingKey for {len(casting_keys_prev):,} previous rows")

            log("Generating CastingKey column for CURRENT...")
            casting_keys_curr = []
            for idx, row in self.df_curr.iterrows():
                casting_key = generate_casting_key(
                    row.get(COL_CHARACTERKEY, ""),
                    row.get(COL_DIALOGVOICE, ""),
                    row.get(COL_SPEAKER_GROUPKEY, ""),
                    row.get("DialogType", "")
                )
                casting_keys_curr.append(casting_key)
            self.df_curr[COL_CASTINGKEY] = casting_keys_curr
            log(f"  → Generated CastingKey for {len(casting_keys_curr):,} current rows")

            return True

        except Exception as e:
            log(f"Error reading files: {e}")
            return False

    def process_data(self):
        """Process the data using 10-key matching system."""
        try:
            log("Building lookup dictionaries with 10-key system...")
            (self.prev_lookup_se, self.prev_lookup_so, self.prev_lookup_sc, self.prev_lookup_eo,
             self.prev_lookup_ec, self.prev_lookup_oc, self.prev_lookup_seo, self.prev_lookup_sec,
             self.prev_lookup_soc, self.prev_lookup_eoc) = build_lookups(self.df_prev)
            log(f"  → Indexed {len(self.prev_lookup_se):,} unique previous rows")

            log("Comparing rows (TWO-PASS algorithm)...")
            changes, previous_strorigins, self.changed_columns_map, self.counter, marked_prev_indices, group_analysis, pass1_results = compare_rows(
                self.df_curr, self.df_prev, self.prev_lookup_se, self.prev_lookup_so, self.prev_lookup_sc,
                self.prev_lookup_eo, self.prev_lookup_ec, self.prev_lookup_oc,
                self.prev_lookup_seo, self.prev_lookup_sec, self.prev_lookup_soc, self.prev_lookup_eoc
            )
            self.group_analysis = group_analysis  # Store for later use
            self.pass1_results = pass1_results  # Store for super group aggregation

            log("Finding deleted rows (TWO-PASS algorithm)...")
            self.df_deleted = find_deleted_rows(self.df_prev, self.df_curr, marked_prev_indices)
            self.counter["Deleted Rows"] = len(self.df_deleted)
            log(f"  → Found {len(self.df_deleted):,} deleted rows")

            # Build result dataframe (CastingKey already exists from read_files)
            self.df_result = self.df_curr.copy()

            # Phase 4: Add CHANGES (priority), DETAILED_CHANGES (full composite),
            # PreviousEventName, PreviousText columns
            from src.utils.helpers import safe_str

            detailed_changes = []
            priority_changes = []
            previous_eventnames = []
            previous_texts = []
            previous_data_list = []

            for curr_idx in self.df_result.index:
                if curr_idx in pass1_results:
                    change_label, prev_idx, prev_strorigin, _ = pass1_results[curr_idx]

                    # Full composite label
                    detailed_changes.append(change_label)

                    # Priority label (extract highest priority from composite)
                    priority_changes.append(get_priority_change(change_label))

                    # Get previous row data if matched
                    if prev_idx is not None:
                        prev_row = self.df_prev.loc[prev_idx]

                        # PreviousEventName - only when EventName changed
                        if "EventName" in change_label:
                            previous_eventnames.append(safe_str(prev_row.get(COL_EVENTNAME, "")))
                        else:
                            previous_eventnames.append("")

                        # PreviousText - always for matched rows (not New Row)
                        if change_label != "New Row":
                            previous_texts.append(safe_str(prev_row.get(COL_TEXT, "")))
                        else:
                            previous_texts.append("")

                        # PreviousData (existing functionality)
                        from src.utils.helpers import generate_previous_data
                        from src.config import COL_STATUS, COL_FREEMEMO
                        prev_row_dict = prev_row.to_dict()
                        previous_data_list.append(generate_previous_data(prev_row_dict, COL_TEXT, COL_STATUS, COL_FREEMEMO))
                    else:
                        previous_eventnames.append("")
                        previous_texts.append("")
                        previous_data_list.append("")
                else:
                    detailed_changes.append("ERROR: Missing Classification")
                    priority_changes.append("ERROR: Missing Classification")
                    previous_eventnames.append("")
                    previous_texts.append("")
                    previous_data_list.append("")

            self.df_result[COL_CHANGES] = priority_changes
            self.df_result[COL_DETAILED_CHANGES] = detailed_changes
            self.df_result[COL_PREVIOUS_EVENTNAME] = previous_eventnames
            self.df_result[COL_PREVIOUS_TEXT] = previous_texts
            self.df_result[COL_PREVIOUSDATA] = previous_data_list
            self.df_result[COL_PREVIOUS_STRORIGIN] = previous_strorigins

            log("Filtering output columns...")
            self.df_result = filter_output_columns(self.df_result, OUTPUT_COLUMNS_RAW)

            # Create summary
            self.df_summary = create_raw_summary(
                self.counter, self.prev_file, self.curr_file, self.df_result
            )

            return True

        except Exception as e:
            log(f"Error processing data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_strorigin_analysis_sheet(self):
        """
        Create StrOrigin Change Analysis sheet for Raw Process.

        Returns:
            DataFrame with StrOrigin analysis, or None if not applicable
        """
        try:
            # Find rows where StrOrigin changed (CHANGES contains "StrOrigin")
            changes_col = "CHANGES"
            if changes_col not in self.df_result.columns:
                log("  ℹ️  No CHANGES column found - skipping StrOrigin analysis")
                return None

            # Filter to rows with StrOrigin changes
            mask = self.df_result[changes_col].astype(str).str.contains("StrOrigin", case=False, na=False)
            df_strorigin_changes = self.df_result[mask].copy()

            if df_strorigin_changes.empty:
                log("  ℹ️  No StrOrigin changes found - skipping analysis sheet")
                return None

            log(f"  → Found {len(df_strorigin_changes)} rows with StrOrigin changes")

            # Initialize analyzer (checks if BERT is available)
            analyzer = StrOriginAnalyzer()

            # Log which version is being used
            if analyzer.bert_available:
                log("  → Running FULL analysis (Punctuation/Space + BERT similarity)...")
            else:
                log("  → Running LIGHT analysis (Punctuation/Space + Content Change marker)...")
                log("  ℹ️  BERT not available - similarity percentages will show 'Content Change'")

            # Prepare data lists
            prev_strorigins = []
            curr_strorigins = []
            analysis_results = []
            diff_details = []

            # Import progress tracking
            from src.utils.progress import print_progress, finalize_progress
            from src.utils.helpers import safe_str

            total_rows = len(df_strorigin_changes)
            log(f"  → Analyzing {total_rows} rows...")

            # Analyze each row with progress tracking
            for row_num, (idx, row) in enumerate(df_strorigin_changes.iterrows(), start=1):
                curr_strorigin = safe_str(row.get(COL_STRORIGIN, ""))
                prev_strorigin = safe_str(row.get(COL_PREVIOUS_STRORIGIN, ""))

                # Store for columns
                prev_strorigins.append(prev_strorigin)
                curr_strorigins.append(curr_strorigin)

                # If no previous data, can't analyze
                if not prev_strorigin:
                    analysis_results.append("N/A - No previous data")
                    diff_details.append("")
                else:
                    # Analyze - returns tuple (analysis, diff_detail)
                    analysis, diff = analyzer.analyze(prev_strorigin, curr_strorigin)
                    analysis_results.append(analysis)
                    diff_details.append(diff)

                # Progress tracking (update every 5 rows or at end)
                if row_num % 5 == 0 or row_num == total_rows:
                    print_progress(row_num, total_rows, label="Analyzing")

            finalize_progress()

            # Drop existing columns if they already exist (to avoid insert errors)
            cols_to_drop = ["Previous StrOrigin", "Current StrOrigin", "StrOrigin Analysis", "Diff Detail"]
            for col in cols_to_drop:
                if col in df_strorigin_changes.columns:
                    df_strorigin_changes.drop(columns=[col], inplace=True)

            # Add columns in natural reading order:
            # Previous StrOrigin → Current StrOrigin → StrOrigin Analysis → Diff Detail
            changes_col_index = df_strorigin_changes.columns.get_loc(changes_col)

            df_strorigin_changes.insert(changes_col_index + 1, "Previous StrOrigin", prev_strorigins)
            df_strorigin_changes.insert(changes_col_index + 2, "Current StrOrigin", curr_strorigins)
            df_strorigin_changes.insert(changes_col_index + 3, "StrOrigin Analysis", analysis_results)
            df_strorigin_changes.insert(changes_col_index + 4, "Diff Detail", diff_details)

            log(f"  ✓ StrOrigin analysis complete")
            return df_strorigin_changes

        except Exception as e:
            log(f"  ⚠️  Error creating StrOrigin analysis sheet: {e}")
            import traceback
            traceback.print_exc()
            return None

    def write_output(self):
        """Write results to Excel file with formatting."""
        try:
            script_dir = get_script_dir()
            out_filename = os.path.splitext(os.path.basename(self.curr_file))[0] + "_diff.xlsx"
            self.output_path = os.path.join(script_dir, out_filename)
            log(f"Writing results to: {os.path.basename(self.output_path)}")

            with pd.ExcelWriter(self.output_path, engine="openpyxl") as writer:
                self.df_result.to_excel(writer, sheet_name="Comparison", index=False)

                if not self.df_deleted.empty:
                    df_deleted_filtered = filter_output_columns(self.df_deleted, OUTPUT_COLUMNS_RAW)
                    df_deleted_filtered.to_excel(writer, sheet_name="Deleted Rows", index=False)

                self.df_summary.to_excel(writer, sheet_name="Summary Report", index=False, header=True)

                # Write Super Group Word Analysis sheet
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

                # Create StrOrigin Change Analysis sheet
                log("Creating StrOrigin Change Analysis sheet...")
                df_strorigin_analysis = self.create_strorigin_analysis_sheet()
                if df_strorigin_analysis is not None:
                    df_strorigin_analysis.to_excel(writer, sheet_name="StrOrigin Change Analysis", index=False)
                    log(f"  → Created 'StrOrigin Change Analysis' sheet with {len(df_strorigin_analysis)} rows")

                wb = writer.book
                apply_direct_coloring(wb["Comparison"], is_master=False, changed_columns_map=self.changed_columns_map)
                widen_summary_columns(wb["Summary Report"])

                # Apply coloring and formatting to StrOrigin analysis sheet if it exists
                if "StrOrigin Change Analysis" in wb.sheetnames:
                    apply_direct_coloring(wb["StrOrigin Change Analysis"], is_master=False)

                    # Set column widths for better readability
                    ws_strorigin = wb["StrOrigin Change Analysis"]
                    for column_cells in ws_strorigin.columns:
                        col_letter = column_cells[0].column_letter
                        col_name = column_cells[0].value

                        # Set specific widths based on column name
                        if col_name == "Previous StrOrigin":
                            ws_strorigin.column_dimensions[col_letter].width = 25
                        elif col_name == "Current StrOrigin":
                            ws_strorigin.column_dimensions[col_letter].width = 25
                        elif col_name == "StrOrigin Analysis":
                            ws_strorigin.column_dimensions[col_letter].width = 20
                        elif col_name == "Diff Detail":
                            ws_strorigin.column_dimensions[col_letter].width = 35  # Wider for [old→new] display
                        elif col_name == "CHANGES":
                            ws_strorigin.column_dimensions[col_letter].width = 25

            log(f"✓ File saved: {self.output_path}")
            return True

        except Exception as e:
            log(f"Error writing output: {e}")
            import traceback
            traceback.print_exc()
            return False

    def show_summary(self):
        """Display completion message with file path."""
        messagebox.showinfo(
            "RAW VRS CHECK Complete",
            f"Process completed successfully!\n\nOutput file:\n{self.output_path}"
        )
