"""
Master File Update processor.

This processor updates a Master File by importing data from a Working Process output,
using the 4-tier key system with high/low importance logic.
"""

import os
import pandas as pd
from datetime import datetime
from tkinter import messagebox
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from copy import copy

from src.processors.base_processor import BaseProcessor
from src.io.excel_reader import safe_read_excel
from src.io.formatters import apply_direct_coloring, widen_summary_columns, format_update_history_sheet
from src.utils.data_processing import normalize_dataframe_status
from src.utils.helpers import log, get_script_dir, safe_str
from src.config import (
    COL_SEQUENCE, COL_EVENTNAME, COL_STRORIGIN, COL_CASTINGKEY,
    COL_IMPORTANCE, COL_STARTFRAME, COL_ENDFRAME
)
from src.io.summary import create_master_file_update_history_sheet
from src.history.history_manager import add_master_file_update_record


class MasterProcessor(BaseProcessor):
    """
    Processor for Master File Update.

    Updates a master file with data from a working process output,
    using 4-tier key matching with high/low importance logic.
    """

    def __init__(self):
        """Initialize the master processor."""
        super().__init__()
        self.df_source = None
        self.df_target = None
        self.df_high = None
        self.df_low = None
        self.df_high_output = None
        self.df_low_output = None
        self.target_wb = None
        self.output_structure = []
        self.high_counter = {}
        self.low_counter = {}
        self.total_counter = {}

    def get_process_name(self):
        """Get the process name."""
        return "PROCESS MASTER FILE UPDATE"

    def select_files(self):
        """Prompt user to select source and target files."""
        self.source_file = self._select_single_file(
            "MASTER FILE UPDATE: Select SOURCE (Working Process output)"
        )
        if not self.source_file:
            return False

        self.target_file = self._select_single_file(
            "MASTER FILE UPDATE: Select TARGET (Master File to update)"
        )
        if not self.target_file:
            return False

        return True

    def read_files(self):
        """Read and normalize the source and target files."""
        try:
            log(f"Reading SOURCE: {os.path.basename(self.source_file)}")
            self.df_source = safe_read_excel(self.source_file, header=0, dtype=str)
            log(f"  → {len(self.df_source):,} rows, {self.df_source.shape[1]} columns")

            log(f"Reading TARGET: {os.path.basename(self.target_file)}")
            self.df_target = safe_read_excel(self.target_file, header=0, dtype=str)
            log(f"  → {len(self.df_target):,} rows, {self.df_target.shape[1]} columns")

            # Identify target structure
            target_columns = list(self.df_target.columns)
            log(f"\nTARGET structure: {len(target_columns)} columns")

            # Define output structure (TARGET + CHANGES + Importance)
            self.output_structure = target_columns.copy()
            if "CHANGES" not in self.output_structure:
                self.output_structure.append("CHANGES")
            if COL_IMPORTANCE not in self.output_structure:
                self.output_structure.append(COL_IMPORTANCE)

            log(f"Output structure: {len(self.output_structure)} columns (all sheets will use this)")

            log("\nNormalizing STATUS columns...")
            self.df_source = normalize_dataframe_status(self.df_source)
            self.df_target = normalize_dataframe_status(self.df_target)

            if COL_IMPORTANCE not in self.df_source.columns:
                log("Warning: SOURCE has no 'Importance' column - treating all rows as High")
                self.df_source[COL_IMPORTANCE] = "High"

            return True

        except Exception as e:
            log(f"Error reading files: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_data(self):
        """Process the data using 4-key matching with high/low importance logic."""
        try:
            # Separate high and low importance
            log("\nSeparating SOURCE by Importance...")
            self.df_high = self.df_source[self.df_source[COL_IMPORTANCE].str.lower() == "high"].copy()
            self.df_low = self.df_source[self.df_source[COL_IMPORTANCE].str.lower() != "high"].copy()
            log(f"  → High importance: {len(self.df_high):,} rows")
            log(f"  → Low importance: {len(self.df_low):,} rows")

            # Build lookups
            log("\nBuilding lookups with 4-tier key system...")
            source_high_lookup, source_high_lookup_cg, source_high_lookup_es, source_high_lookup_cs = \
                self._build_lookups(self.df_high, "SOURCE High")
            source_low_lookup, source_low_lookup_cg, source_low_lookup_es, source_low_lookup_cs = \
                self._build_lookups(self.df_low, "SOURCE Low")
            target_lookup, target_lookup_cg, target_lookup_es, target_lookup_cs = \
                self._build_lookups(self.df_target, "TARGET")

            # Process high importance rows
            log("\nProcessing HIGH importance rows...")
            self.df_high_output, self.high_counter = self._process_high_importance(
                self.df_high, target_lookup, target_lookup_cg, target_lookup_es, target_lookup_cs
            )
            log(f"  → Processed {len(self.df_high_output):,} HIGH rows")

            # Process low importance rows
            log("\nProcessing LOW importance rows...")
            self.df_low_output, self.low_counter = self._process_low_importance(
                self.df_low, target_lookup, target_lookup_cg, target_lookup_es, target_lookup_cs
            )
            log(f"  → Processed {len(self.df_low_output):,} LOW rows")

            # Filter out LOW + NEW rows
            log("\nFiltering LOW importance NEW rows...")
            original_low_count = len(self.df_low_output)
            self.df_low_output = self.df_low_output[self.df_low_output["CHANGES"] != "New Row"]
            filtered_count = original_low_count - len(self.df_low_output)
            if filtered_count > 0:
                log(f"  → Removed {filtered_count:,} LOW importance NEW rows")
                self.low_counter["Deleted (LOW+New)"] = filtered_count
            log(f"  → Final LOW rows: {len(self.df_low_output):,}")

            # Find deleted rows
            log("\nFinding deleted rows with 4-key system...")
            self.df_deleted = self._find_deleted_rows(
                self.df_target,
                source_high_lookup, source_high_lookup_cg, source_high_lookup_es, source_high_lookup_cs,
                source_low_lookup, source_low_lookup_cg, source_low_lookup_es, source_low_lookup_cs
            )
            log(f"  → Found {len(self.df_deleted):,} deleted rows")

            # Create summary
            log("\nCreating summary report...")
            self.total_counter = {}
            for k, v in self.high_counter.items():
                self.total_counter[k] = self.total_counter.get(k, 0) + v
            for k, v in self.low_counter.items():
                self.total_counter[k] = self.total_counter.get(k, 0) + v
            if len(self.df_deleted) > 0:
                self.total_counter["Deleted Rows"] = len(self.df_deleted)

            self.df_summary = self._create_summary()
            self.df_history = create_master_file_update_history_sheet()

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
            out_filename = "MasterFile_Updated_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx"
            self.output_path = os.path.join(script_dir, out_filename)
            log(f"\nWriting results to: {out_filename}")

            # Load target workbook for formatting
            log("Loading TARGET workbook for formatting...")
            wb_target = load_workbook(self.target_file)
            ws_target = wb_target.active

            with pd.ExcelWriter(self.output_path, engine="openpyxl") as writer:
                self.df_high_output.to_excel(writer, sheet_name="Main Sheet (High)", index=False)
                self.df_low_output.to_excel(writer, sheet_name="Low Importance", index=False)
                self.df_deleted.to_excel(writer, sheet_name="Deleted Rows", index=False)
                self.df_history.to_excel(writer, sheet_name="📅 Update History", index=False, header=False)
                self.df_summary.to_excel(writer, sheet_name="Summary Report", index=False, header=True)

                wb = writer.book

                # Apply formatting
                for sheet_name in ["Main Sheet (High)", "Low Importance", "Deleted Rows"]:
                    ws = wb[sheet_name]

                    log(f"Applying formatting to {sheet_name}...")

                    # Copy column widths
                    for col_idx in range(1, min(ws_target.max_column + 1, ws.max_column + 1)):
                        col_letter = get_column_letter(col_idx)
                        if col_letter in ws_target.column_dimensions:
                            ws.column_dimensions[col_letter].width = ws_target.column_dimensions[col_letter].width

                    # Copy header row formatting
                    for col_idx in range(1, min(ws_target.max_column + 1, ws.max_column + 1)):
                        source_cell = ws_target.cell(row=1, column=col_idx)
                        target_cell = ws.cell(row=1, column=col_idx)

                        if source_cell.has_style:
                            target_cell.font = copy(source_cell.font)
                            target_cell.border = copy(source_cell.border)
                            target_cell.fill = copy(source_cell.fill)
                            target_cell.alignment = copy(source_cell.alignment)

                    # Apply CHANGES column coloring
                    apply_direct_coloring(ws, is_master=False)

                format_update_history_sheet(wb["📅 Update History"])
                widen_summary_columns(wb["Summary Report"])

            wb_target.close()

            # Add to history
            add_master_file_update_record(
                out_filename, self.source_file, self.target_file,
                self.total_counter, len(self.df_high_output)
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
        summary_msg = "Master File Update completed successfully!\n\n"
        summary_msg += f"Output file:\n{self.output_path}\n\n"
        summary_msg += "Results:\n"
        summary_msg += f"  Main Sheet (High): {len(self.df_high_output):,} rows\n"
        summary_msg += f"  Low Importance: {len(self.df_low_output):,} rows\n"
        summary_msg += f"  Deleted Rows: {len(self.df_deleted):,} rows\n\n"
        summary_msg += "Change Summary:\n"
        for change_type, count in sorted(self.total_counter.items()):
            summary_msg += f"  {change_type}: {count:,}\n"

        messagebox.showinfo("MASTER FILE UPDATE Complete", summary_msg)

    # Helper methods
    def _build_lookups(self, df, label):
        """Build 4-tier lookup dictionaries."""
        lookup_cw = {}
        lookup_cg = {}
        lookup_es = {}
        lookup_cs = {}

        for _, row in df.iterrows():
            key_cw = (row[COL_SEQUENCE], row[COL_EVENTNAME])
            key_cg = (row[COL_SEQUENCE], row[COL_STRORIGIN])
            key_es = (row[COL_EVENTNAME], row[COL_STRORIGIN])
            key_cs = (row[COL_CASTINGKEY], row[COL_SEQUENCE])

            if key_cw not in lookup_cw:
                lookup_cw[key_cw] = row.to_dict()
            if key_cg not in lookup_cg:
                lookup_cg[key_cg] = row[COL_EVENTNAME]
            if key_es not in lookup_es:
                lookup_es[key_es] = row.to_dict()
            if key_cs not in lookup_cs:
                lookup_cs[key_cs] = row.to_dict()

        log(f"  → {label} indexed: {len(lookup_cw):,} rows")
        return lookup_cw, lookup_cg, lookup_es, lookup_cs

    def _process_high_importance(self, df_high, target_lookup, target_lookup_cg, target_lookup_es, target_lookup_cs):
        """Process high importance rows."""
        high_rows = []
        counter = {}

        for idx, source_row in df_high.iterrows():
            key_cw = (source_row[COL_SEQUENCE], source_row[COL_EVENTNAME])
            key_cg = (source_row[COL_SEQUENCE], source_row[COL_STRORIGIN])
            key_es = (source_row[COL_EVENTNAME], source_row[COL_STRORIGIN])
            key_cs = (source_row[COL_CASTINGKEY], source_row[COL_SEQUENCE])

            # Copy SOURCE values to output structure
            output_row = {}
            for col in self.output_structure:
                if col in source_row.index:
                    output_row[col] = safe_str(source_row[col])
                else:
                    output_row[col] = ""

            # Determine change type using 4-tier key system
            target_row = None

            # Stage 1: Direct match
            if key_cw in target_lookup:
                change_type = safe_str(source_row.get("CHANGES", "Edited"))
                target_row = target_lookup[key_cw]

            # Stage 2: StrOrigin+Sequence match - VERIFY with Key 4
            elif key_cg in target_lookup_cg:
                if key_cs in target_lookup_cs:
                    # Same character → EventName Change
                    change_type = safe_str(source_row.get("CHANGES", "Edited"))
                    old_eventname = target_lookup_cg[key_cg]
                    target_row = target_lookup.get((source_row[COL_SEQUENCE], old_eventname))
                else:
                    # Different character → New Row
                    change_type = "New Row"
                    target_row = None

            # Stage 3: SequenceName changed
            elif key_es in target_lookup_es:
                change_type = "SequenceName Change"
                target_row = target_lookup_es[key_es]

            # Stage 4: New row
            else:
                change_type = "New Row"
                target_row = None

            # EXCEPTION: Preserve TARGET TimeFrame for specific cases
            if target_row and change_type in ["TimeFrame Change", "EventName+TimeFrame Change", "TimeFrame+EventName Change"]:
                if COL_STARTFRAME in target_row:
                    output_row[COL_STARTFRAME] = safe_str(target_row[COL_STARTFRAME])
                if COL_ENDFRAME in target_row:
                    output_row[COL_ENDFRAME] = safe_str(target_row[COL_ENDFRAME])

            output_row["CHANGES"] = change_type
            output_row[COL_IMPORTANCE] = "High"

            high_rows.append(output_row)
            counter[change_type] = counter.get(change_type, 0) + 1

        df_output = pd.DataFrame(high_rows, columns=self.output_structure)
        return df_output, counter

    def _process_low_importance(self, df_low, target_lookup, target_lookup_cg, target_lookup_es, target_lookup_cs):
        """Process low importance rows."""
        low_rows = []
        counter = {}

        for idx, source_row in df_low.iterrows():
            key_cw = (source_row[COL_SEQUENCE], source_row[COL_EVENTNAME])
            key_cg = (source_row[COL_SEQUENCE], source_row[COL_STRORIGIN])
            key_es = (source_row[COL_EVENTNAME], source_row[COL_STRORIGIN])
            key_cs = (source_row[COL_CASTINGKEY], source_row[COL_SEQUENCE])

            # Determine change type
            target_row = None

            # Stage 1: Direct match
            if key_cw in target_lookup:
                change_type = safe_str(source_row.get("CHANGES", "Edited"))
                target_row = target_lookup[key_cw]

            # Stage 2: StrOrigin+Sequence match - VERIFY with Key 4
            elif key_cg in target_lookup_cg:
                if key_cs in target_lookup_cs:
                    # Same character → EventName Change
                    change_type = safe_str(source_row.get("CHANGES", "Edited"))
                    old_eventname = target_lookup_cg[key_cg]
                    target_row = target_lookup.get((source_row[COL_SEQUENCE], old_eventname))
                else:
                    # Different character → New Row
                    change_type = "New Row"
                    target_row = None

            # Stage 3: SequenceName changed
            elif key_es in target_lookup_es:
                change_type = "SequenceName Change"
                target_row = target_lookup_es[key_es]

            # Stage 4: New row
            else:
                change_type = "New Row"
                target_row = None

            # LOW IMPORTANCE LOGIC: For existing rows, preserve TARGET data
            output_row = {}
            if change_type != "New Row" and target_row is not None:
                # Existing row: Use TARGET data (preserve original)
                for col in self.output_structure:
                    if col in target_row:
                        output_row[col] = safe_str(target_row[col])
                    elif col in source_row.index:
                        output_row[col] = safe_str(source_row[col])
                    else:
                        output_row[col] = ""
            else:
                # New row: Use SOURCE data (will be deleted in post-process)
                for col in self.output_structure:
                    if col in source_row.index:
                        output_row[col] = safe_str(source_row[col])
                    else:
                        output_row[col] = ""

            # Always set CHANGES and Importance
            output_row["CHANGES"] = change_type
            output_row[COL_IMPORTANCE] = "Low"

            low_rows.append(output_row)
            counter[change_type] = counter.get(change_type, 0) + 1

        df_output = pd.DataFrame(low_rows, columns=self.output_structure) if low_rows else pd.DataFrame(columns=self.output_structure)
        return df_output, counter

    def _find_deleted_rows(self, df_target, sh_lookup_cw, sh_lookup_cg, sh_lookup_es, sh_lookup_cs,
                           sl_lookup_cw, sl_lookup_cg, sl_lookup_es, sl_lookup_cs):
        """Find deleted rows using 4-key system."""
        deleted_rows = []

        # Build all current keys (4 types)
        source_all_keys_cw = set(sh_lookup_cw.keys()) | set(sl_lookup_cw.keys())
        source_all_keys_cg = set(sh_lookup_cg.keys()) | set(sl_lookup_cg.keys())
        source_all_keys_es = set(sh_lookup_es.keys()) | set(sl_lookup_es.keys())
        source_all_keys_cs = set(sh_lookup_cs.keys()) | set(sl_lookup_cs.keys())

        for _, target_row in df_target.iterrows():
            key_cw = (target_row[COL_SEQUENCE], target_row[COL_EVENTNAME])
            key_cg = (target_row[COL_SEQUENCE], target_row[COL_STRORIGIN])
            key_es = (target_row[COL_EVENTNAME], target_row[COL_STRORIGIN])
            key_cs = (target_row[COL_CASTINGKEY], target_row[COL_SEQUENCE])

            # Only mark as deleted if ALL 4 keys are missing
            if (key_cw not in source_all_keys_cw) and \
               (key_cg not in source_all_keys_cg) and \
               (key_es not in source_all_keys_es) and \
               (key_cs not in source_all_keys_cs):
                output_row = {}
                for col in self.output_structure:
                    if col in target_row.index:
                        output_row[col] = safe_str(target_row[col])
                    else:
                        output_row[col] = ""

                output_row["CHANGES"] = ""
                output_row[COL_IMPORTANCE] = ""

                deleted_rows.append(output_row)

        df_deleted = pd.DataFrame(deleted_rows, columns=self.output_structure) if deleted_rows else pd.DataFrame(columns=self.output_structure)
        return df_deleted

    def _create_summary(self):
        """Create summary DataFrame."""
        summary_rows = [
            ["MASTER FILE UPDATE SUMMARY", "", "", ""],
            ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", ""],
            ["Source file", os.path.basename(self.source_file), "", ""],
            ["Target file", os.path.basename(self.target_file), "", ""],
            ["", "", "", ""],
            ["RESULT COUNTS", "Count", "", ""],
            ["Main Sheet (High)", len(self.df_high_output), "", ""],
            ["Low Importance Sheet", len(self.df_low_output), "", ""],
            ["Deleted Rows Sheet", len(self.df_deleted), "", ""],
            ["", "", "", ""],
            ["CHANGE BREAKDOWN", "Count", "", ""],
        ]

        for change_type in sorted(self.total_counter.keys()):
            summary_rows.append([f"  {change_type}", self.total_counter[change_type], "", ""])

        return pd.DataFrame(summary_rows, columns=["Metric", "Value", "Col3", "Col4"])
