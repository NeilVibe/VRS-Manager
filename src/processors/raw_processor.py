"""
Raw VRS Check processor.

This processor compares a previous raw VRS file with a current one,
identifying changes and generating a comparison report.
"""

import os
import pandas as pd
from tkinter import messagebox

from src.processors.base_processor import BaseProcessor
from src.io.excel_reader import safe_read_excel
from src.io.formatters import apply_direct_coloring, widen_summary_columns
from src.utils.data_processing import normalize_dataframe_status, filter_output_columns
from src.utils.helpers import log, get_script_dir
from src.core.lookups import build_lookups
from src.core.comparison import compare_rows, find_deleted_rows
from src.core.casting import generate_casting_key
from src.config import (
    OUTPUT_COLUMNS_RAW,
    COL_CASTINGKEY, COL_CHARACTERKEY, COL_DIALOGVOICE, COL_SPEAKER_GROUPKEY,
    COL_PREVIOUS_STRORIGIN
)
from src.io.summary import create_raw_summary


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

            return True

        except Exception as e:
            log(f"Error reading files: {e}")
            return False

    def process_data(self):
        """Process the data using 4-key matching system."""
        try:
            log("Building lookup dictionaries with 4-key system...")
            self.prev_lookup_cw, self.prev_lookup_cg, self.prev_lookup_es, self.prev_lookup_cs = build_lookups(self.df_prev)
            log(f"  → Indexed {len(self.prev_lookup_cw):,} unique previous rows")

            log("Comparing rows...")
            changes, previous_strorigins, self.changed_columns_map, self.counter = compare_rows(
                self.df_curr, self.prev_lookup_cw, self.prev_lookup_cg,
                self.prev_lookup_es, self.prev_lookup_cs
            )

            log("Finding deleted rows...")
            self.df_deleted = find_deleted_rows(self.df_prev, self.df_curr)
            self.counter["Deleted Rows"] = len(self.df_deleted)
            log(f"  → Found {len(self.df_deleted):,} deleted rows")

            # Build result dataframe
            self.df_result = self.df_curr.copy()
            self.df_result["CHANGES"] = changes
            self.df_result[COL_PREVIOUS_STRORIGIN] = previous_strorigins

            log("Generating CastingKey column...")
            casting_keys = []
            for idx, row in self.df_result.iterrows():
                casting_key = generate_casting_key(
                    row.get(COL_CHARACTERKEY, ""),
                    row.get(COL_DIALOGVOICE, ""),
                    row.get(COL_SPEAKER_GROUPKEY, ""),
                    row.get("DialogType", "")
                )
                casting_keys.append(casting_key)
            self.df_result[COL_CASTINGKEY] = casting_keys
            log(f"  → Generated CastingKey for {len(casting_keys):,} rows")

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

                wb = writer.book
                apply_direct_coloring(wb["Comparison"], is_master=False, changed_columns_map=self.changed_columns_map)
                widen_summary_columns(wb["Summary Report"])

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
