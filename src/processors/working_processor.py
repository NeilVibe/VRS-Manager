"""
Working VRS Check processor.

This processor performs the Working VRS Check, which imports data from previous
to current files using intelligent import logic and the 4-tier key matching system.
"""

import os
import pandas as pd
from tkinter import messagebox

from src.processors.base_processor import BaseProcessor
from src.io.excel_reader import safe_read_excel
from src.io.formatters import apply_direct_coloring, widen_summary_columns, format_update_history_sheet
from src.utils.data_processing import normalize_dataframe_status, filter_output_columns, remove_full_duplicates
from src.utils.helpers import log, get_script_dir, safe_str
from src.core.working_helpers import build_working_lookups, find_working_deleted_rows
from src.core.working_comparison import process_working_comparison
from src.core.casting import generate_casting_key
from src.io.summary import create_working_summary, create_working_update_history_sheet
from src.history.history_manager import add_working_update_record
from src.config import (
    COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY,
    COL_STRORIGIN, COL_PREVIOUSDATA
)
from src.utils.strorigin_analysis import StrOriginAnalyzer


class WorkingProcessor(BaseProcessor):
    """
    Processor for Working VRS Check.

    Imports data from previous to current files using intelligent import logic.
    """

    def __init__(self):
        """Initialize the working processor."""
        super().__init__()
        self.df_prev = None
        self.df_curr = None
        self.prev_lookup_cw = None
        self.prev_lookup_cg = None
        self.prev_lookup_es = None
        self.prev_lookup_cs = None

    def get_process_name(self):
        """Get the process name."""
        return "PROCESS WORKING VRS CHECK"

    def select_files(self):
        """Prompt user to select previous and current files."""
        self.prev_file = self._select_single_file("WORKING CHECK: Select PREVIOUS Excel file")
        if not self.prev_file:
            return False

        self.curr_file = self._select_single_file("WORKING CHECK: Select CURRENT Excel file")
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
            log("  → STATUS columns normalized")

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
            import traceback
            traceback.print_exc()
            return False

    def process_data(self):
        """Process the data using 4-key matching system with import logic."""
        try:
            # Build lookups (10-key system)
            (self.prev_lookup_se, self.prev_lookup_so, self.prev_lookup_sc, self.prev_lookup_eo,
             self.prev_lookup_ec, self.prev_lookup_oc, self.prev_lookup_seo, self.prev_lookup_sec,
             self.prev_lookup_soc, self.prev_lookup_eoc) = build_working_lookups(self.df_prev, "PREVIOUS")

            # Process comparison and import (TWO-PASS algorithm)
            self.df_result, self.counter, marked_prev_indices = process_working_comparison(
                self.df_curr, self.df_prev,
                self.prev_lookup_se, self.prev_lookup_so, self.prev_lookup_sc,
                self.prev_lookup_eo, self.prev_lookup_ec, self.prev_lookup_oc,
                self.prev_lookup_seo, self.prev_lookup_sec, self.prev_lookup_soc, self.prev_lookup_eoc
            )

            # Find deleted rows (TWO-PASS algorithm)
            self.df_deleted = find_working_deleted_rows(self.df_prev, self.df_curr, marked_prev_indices)
            if not self.df_deleted.empty:
                self.counter["Deleted Rows"] = len(self.df_deleted)

            # Filter output columns
            log("Filtering output columns...")
            self.df_result = filter_output_columns(self.df_result)
            log(f"  → Output contains {len(self.df_result.columns)} columns")

            # Create summary
            log("Creating summary report...")
            self.df_summary = create_working_summary(
                self.counter, self.prev_file, self.curr_file, self.df_result
            )
            self.df_history = create_working_update_history_sheet()

            return True

        except Exception as e:
            log(f"Error processing data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_strorigin_analysis_sheet(self):
        """
        Create StrOrigin Change Analysis sheet (Phase 2.3).

        This creates a new sheet with:
        - Filtered rows where CHANGES contains "StrOrigin"
        - All existing columns preserved
        - New "StrOrigin Analysis" column with punctuation/space detection and BERT similarity

        Returns:
            pd.DataFrame or None: Analysis dataframe if StrOrigin changes exist, None otherwise
        """
        try:
            # Filter rows where CHANGES contains "StrOrigin" (case-insensitive)
            changes_col = "CHANGES"
            if changes_col not in self.df_result.columns:
                log("  ℹ️  No CHANGES column found - skipping StrOrigin analysis")
                return None

            # Filter for StrOrigin changes (case-insensitive)
            mask = self.df_result[changes_col].astype(str).str.contains(
                "StrOrigin", case=False, na=False
            )
            df_strorigin_changes = self.df_result[mask].copy()

            if df_strorigin_changes.empty:
                log("  ℹ️  No StrOrigin changes found - skipping analysis sheet")
                return None

            log(f"  → Found {len(df_strorigin_changes)} rows with StrOrigin changes")
            log("  → Running StrOrigin analysis (punctuation/space + BERT similarity)...")

            # Initialize analyzer (may fail if model not available)
            try:
                analyzer = StrOriginAnalyzer()
            except FileNotFoundError as e:
                log(f"  ⚠️  BERT model not found - StrOrigin analysis unavailable")
                log(f"  ⚠️  To enable this feature, download the model:")
                log(f"      python3 download_bert_model.py")
                log(f"  ℹ️  Skipping StrOrigin Analysis sheet creation")
                return None

            # Analyze each row
            analysis_results = []
            for idx, row in df_strorigin_changes.iterrows():
                curr_strorigin = safe_str(row.get(COL_STRORIGIN, ""))

                # Extract previous StrOrigin from PreviousData if it exists
                prev_strorigin = ""
                if COL_PREVIOUSDATA in row and pd.notna(row[COL_PREVIOUSDATA]):
                    previous_data = str(row[COL_PREVIOUSDATA])
                    # PreviousData format: "PrevStrOrigin | PrevSTATUS | PrevFREEMEMO"
                    parts = previous_data.split(" | ")
                    if len(parts) >= 1:
                        prev_strorigin = parts[0]

                # If no previous data, can't analyze
                if not prev_strorigin:
                    analysis_results.append("N/A - No previous data")
                    continue

                # Analyze
                result = analyzer.analyze(prev_strorigin, curr_strorigin)
                analysis_results.append(result)

            # Add "StrOrigin Analysis" column after CHANGES
            changes_col_index = df_strorigin_changes.columns.get_loc(changes_col)
            df_strorigin_changes.insert(
                changes_col_index + 1,
                "StrOrigin Analysis",
                analysis_results
            )

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
            out_filename = os.path.splitext(os.path.basename(self.curr_file))[0] + "_WorkTransform.xlsx"
            self.output_path = os.path.join(script_dir, out_filename)
            log(f"Writing results to: {out_filename}")

            with pd.ExcelWriter(self.output_path, engine="openpyxl") as writer:
                self.df_result.to_excel(writer, sheet_name="Work Transform", index=False)

                self.df_history.to_excel(writer, sheet_name="📅 Update History", index=False, header=False)

                if not self.df_deleted.empty:
                    df_deleted_filtered = filter_output_columns(self.df_deleted)
                    df_deleted_filtered.to_excel(writer, sheet_name="Deleted Rows", index=False)
                    log(f"  → Created 'Deleted Rows' sheet with {len(self.df_deleted)} rows")

                self.df_summary.to_excel(writer, sheet_name="Summary Report", index=False, header=True)

                # Phase 2.3: Create StrOrigin Change Analysis sheet
                log("Creating StrOrigin Change Analysis sheet...")
                df_strorigin_analysis = self.create_strorigin_analysis_sheet()
                if df_strorigin_analysis is not None:
                    df_strorigin_analysis.to_excel(writer, sheet_name="StrOrigin Change Analysis", index=False)
                    log(f"  → Created 'StrOrigin Change Analysis' sheet with {len(df_strorigin_analysis)} rows")

                wb = writer.book
                apply_direct_coloring(wb["Work Transform"], is_master=False)
                format_update_history_sheet(wb["📅 Update History"])
                widen_summary_columns(wb["Summary Report"])

                # Apply coloring to StrOrigin analysis sheet if it exists
                if "StrOrigin Change Analysis" in wb.sheetnames:
                    apply_direct_coloring(wb["StrOrigin Change Analysis"], is_master=False)

            # Add to history
            add_working_update_record(
                out_filename, self.prev_file, self.curr_file, self.counter, len(self.df_result)
            )

            log(f"✓ File saved: {self.output_path}")
            return True

        except Exception as e:
            log(f"Error writing output: {e}")
            import traceback
            traceback.print_exc()
            return False

    def show_summary(self):
        """Display completion message with summary."""
        summary_msg = "Process completed successfully!\n\n"
        summary_msg += f"Output file:\n{self.output_path}\n\n"
        summary_msg += "Change Summary:\n"
        for change_type, count in sorted(self.counter.items()):
            summary_msg += f"  {change_type}: {count:,}\n"

        messagebox.showinfo("WORKING VRS CHECK Complete", summary_msg)
