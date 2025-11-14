"""
All Language VRS Check processor.

This processor performs the All Language Check, which merges and imports data
from tri-lingual files (KR/EN/CN) using the 4-tier key matching system.
"""

import os
import pandas as pd
from datetime import datetime
from tkinter import messagebox

from src.processors.base_processor import BaseProcessor
from src.io.excel_reader import safe_read_excel
from src.io.formatters import apply_direct_coloring, widen_summary_columns, format_update_history_sheet
from src.utils.data_processing import normalize_dataframe_status, filter_output_columns
from src.utils.helpers import log, get_script_dir
from src.config import OUTPUT_COLUMNS_MASTER
from src.core.alllang_helpers import (
    find_alllang_files,
    merge_current_files,
    process_alllang_comparison
)
from src.core.working_helpers import build_working_lookups, find_working_deleted_rows
from src.io.summary import create_alllang_summary, create_alllang_update_history_sheet
from src.history.history_manager import add_alllang_update_record


class AllLangProcessor(BaseProcessor):
    """
    Processor for All Language VRS Check.

    Merges current KR/EN/CN files and imports data from previous files
    using flexible language updates.
    """

    def __init__(self):
        """Initialize the all language processor."""
        super().__init__()
        self.curr_kr = None
        self.curr_en = None
        self.curr_cn = None
        self.prev_kr = None
        self.prev_en = None
        self.prev_cn = None
        self.has_kr = False
        self.has_en = False
        self.has_cn = False
        self.df_curr = None
        self.lookup_kr = {}
        self.lookup_en = {}
        self.lookup_cn = {}
        self.lookup_cg_kr = {}
        self.lookup_es_kr = {}
        self.lookup_cs_kr = {}

    def get_process_name(self):
        """Get the process name."""
        return "PROCESS ALL LANGUAGE CHECK"

    def select_files(self):
        """Auto-detect files from Previous/ and Current/ folders."""
        try:
            log("Auto-detecting files from Previous/ and Current/ folders...")
            self.curr_kr, self.curr_en, self.curr_cn, self.prev_kr, self.prev_en, self.prev_cn = find_alllang_files()

            log("\nCURRENT FILES (complete base - required):")
            log(f"  ✓ KR: {os.path.basename(self.curr_kr)}")
            log(f"  ✓ EN: {os.path.basename(self.curr_en)}")
            log(f"  ✓ CN: {os.path.basename(self.curr_cn)}")

            log("\nPREVIOUS FILES (selective updates - flexible):")
            log(f"  {'✓' if self.prev_kr else '○'} KR: {os.path.basename(self.prev_kr) if self.prev_kr else 'Not present - will preserve'}")
            log(f"  {'✓' if self.prev_en else '○'} EN: {os.path.basename(self.prev_en) if self.prev_en else 'Not present - will preserve'}")
            log(f"  {'✓' if self.prev_cn else '○'} CN: {os.path.basename(self.prev_cn) if self.prev_cn else 'Not present - will preserve'}")

            self.has_kr = self.prev_kr is not None
            self.has_en = self.prev_en is not None
            self.has_cn = self.prev_cn is not None

            return True

        except Exception as e:
            log(f"Error detecting files: {e}")
            messagebox.showerror("Error", f"Failed to detect files:\n\n{e}")
            return False

    def read_files(self):
        """Read and merge current files, then read previous files."""
        try:
            # Merge current files
            self.df_curr = merge_current_files(self.curr_kr, self.curr_en, self.curr_cn)

            # Read previous files and build lookups
            if self.has_kr:
                log(f"\nReading KR Previous: {os.path.basename(self.prev_kr)}")
                df_kr = safe_read_excel(self.prev_kr, header=0, dtype=str)
                df_kr = normalize_dataframe_status(df_kr)
                log(f"  → {len(df_kr):,} rows")
                self.lookup_kr, self.lookup_cg_kr, self.lookup_es_kr, self.lookup_cs_kr = \
                    build_working_lookups(df_kr, "KR PREVIOUS")

            if self.has_en:
                log(f"\nReading EN Previous: {os.path.basename(self.prev_en)}")
                df_en = safe_read_excel(self.prev_en, header=0, dtype=str)
                df_en = normalize_dataframe_status(df_en)
                log(f"  → {len(df_en):,} rows")
                self.lookup_en, _, _, _ = build_working_lookups(df_en, "EN PREVIOUS")

            if self.has_cn:
                log(f"\nReading CN Previous: {os.path.basename(self.prev_cn)}")
                df_cn = safe_read_excel(self.prev_cn, header=0, dtype=str)
                df_cn = normalize_dataframe_status(df_cn)
                log(f"  → {len(df_cn):,} rows")
                self.lookup_cn, _, _, _ = build_working_lookups(df_cn, "CN PREVIOUS")

            return True

        except Exception as e:
            log(f"Error reading files: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_data(self):
        """Process the data using 4-key matching system for all languages."""
        try:
            # Process comparison
            self.df_result, self.counter = process_alllang_comparison(
                self.df_curr,
                self.lookup_kr,
                self.lookup_en,
                self.lookup_cn,
                self.lookup_cg_kr,
                self.lookup_es_kr,
                self.lookup_cs_kr,
                self.has_kr,
                self.has_en,
                self.has_cn
            )

            # Find deleted rows (only if KR was updated)
            if self.has_kr:
                df_kr_full = safe_read_excel(self.prev_kr, header=0, dtype=str)
                self.df_deleted = find_working_deleted_rows(df_kr_full, self.df_curr)
                if not self.df_deleted.empty:
                    self.counter["Deleted Rows"] = len(self.df_deleted)
            else:
                self.df_deleted = pd.DataFrame()

            # Filter output columns
            log("\nFiltering output columns...")
            self.df_result = filter_output_columns(self.df_result, OUTPUT_COLUMNS_MASTER)
            log(f"  → Output contains {len(self.df_result.columns)} columns")

            # Create summary
            log("Creating summary report...")
            self.df_summary = create_alllang_summary(
                self.counter, self.prev_kr, self.prev_en, self.prev_cn, self.curr_kr,
                self.df_result, self.has_kr, self.has_en, self.has_cn
            )
            self.df_history = create_alllang_update_history_sheet()

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
            out_filename = "AllLanguage_VRS_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx"
            self.output_path = os.path.join(script_dir, out_filename)
            log(f"\nWriting results to: {out_filename}")

            with pd.ExcelWriter(self.output_path, engine="openpyxl") as writer:
                self.df_result.to_excel(writer, sheet_name="All Language Transform", index=False)

                self.df_history.to_excel(writer, sheet_name="📅 Update History", index=False, header=False)

                if not self.df_deleted.empty:
                    df_deleted_filtered = filter_output_columns(self.df_deleted, OUTPUT_COLUMNS_MASTER)
                    df_deleted_filtered.to_excel(writer, sheet_name="Deleted Rows", index=False)
                    log(f"  → Created 'Deleted Rows' sheet with {len(self.df_deleted)} rows")

                self.df_summary.to_excel(writer, sheet_name="Summary Report", index=False, header=True)

                wb = writer.book
                apply_direct_coloring(wb["All Language Transform"], is_master=True)
                format_update_history_sheet(wb["📅 Update History"])
                widen_summary_columns(wb["Summary Report"])

            # Add to history
            add_alllang_update_record(
                out_filename, self.prev_kr, self.prev_en, self.prev_cn,
                self.curr_kr, self.curr_en, self.curr_cn,
                self.counter, len(self.df_result)
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
        summary_msg += "Languages Updated:\n"
        summary_msg += f"  KR: {'✓ UPDATED' if self.has_kr else '○ Preserved'}\n"
        summary_msg += f"  EN: {'✓ UPDATED' if self.has_en else '○ Preserved'}\n"
        summary_msg += f"  CN: {'✓ UPDATED' if self.has_cn else '○ Preserved'}\n\n"
        summary_msg += "Change Summary:\n"
        for change_type, count in sorted(self.counter.items()):
            summary_msg += f"  {change_type}: {count:,}\n"

        messagebox.showinfo("ALL LANGUAGE CHECK Complete", summary_msg)
