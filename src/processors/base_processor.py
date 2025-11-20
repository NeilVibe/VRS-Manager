"""
Abstract base processor class for VRS Manager.

This module provides the base class that all processors inherit from,
implementing the template method pattern for consistent processing workflow.
"""

import os
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd

# Conditional tkinter import for headless testing
if os.environ.get('HEADLESS', '').lower() not in ('1', 'true', 'yes'):
    from tkinter import filedialog, messagebox
    import tkinter as tk
else:
    # Dummy imports for headless mode
    filedialog = None
    messagebox = None
    tk = None

from src.utils.helpers import log, get_script_dir
from src.utils.data_processing import normalize_dataframe_status


class BaseProcessor(ABC):
    """
    Abstract base class for VRS processors.

    Implements the template method pattern, defining the common structure
    for all VRS processing operations.
    """

    def __init__(self):
        """Initialize the processor."""
        self.prev_file = None
        self.curr_file = None
        self.source_file = None
        self.target_file = None
        self.output_path = None
        self.df_result = None
        self.df_deleted = None
        self.df_summary = None
        self.counter = {}

    @abstractmethod
    def get_process_name(self):
        """
        Get the name of this process for logging.

        Returns:
            str: Process name
        """
        pass

    @abstractmethod
    def select_files(self):
        """
        Prompt user to select input files.

        Returns:
            bool: True if files selected successfully, False if cancelled
        """
        pass

    @abstractmethod
    def read_files(self):
        """
        Read and normalize input files.

        Returns:
            bool: True if files read successfully, False on error
        """
        pass

    @abstractmethod
    def process_data(self):
        """
        Perform the main data processing logic.

        Returns:
            bool: True if processing successful, False on error
        """
        pass

    @abstractmethod
    def write_output(self):
        """
        Write results to output file(s).

        Returns:
            bool: True if output written successfully, False on error
        """
        pass

    @abstractmethod
    def show_summary(self):
        """
        Display a summary of the processing results to the user.
        """
        pass

    def process(self):
        """
        Template method defining the processing workflow.

        This method orchestrates the entire processing workflow by calling
        the abstract methods in sequence. Subclasses should not override this
        method; instead, they should implement the abstract methods.

        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        try:
            log("\n" + "=" * 70)
            log(self.get_process_name())
            log("=" * 70)

            # Step 1: Select files
            if not self.select_files():
                log("User cancelled - exiting.")
                return False

            # Step 2: Read files
            if not self.read_files():
                log("Failed to read files - exiting.")
                return False

            # Step 3: Process data
            if not self.process_data():
                log("Failed to process data - exiting.")
                return False

            # Step 4: Write output
            if not self.write_output():
                log("Failed to write output - exiting.")
                return False

            # Step 5: Show summary
            self.show_summary()

            log("=" * 70)
            return True

        except Exception as exc:
            log(f"FATAL ERROR: {exc}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Something went wrong:\n\n{exc}")
            return False

    def _select_single_file(self, title):
        """
        Helper method to select a single Excel file.

        Args:
            title: Dialog title

        Returns:
            str: Selected file path, or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title=title,
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls")]
        )
        root.destroy()
        return filepath if filepath else None

    def _generate_output_path(self, base_filename, suffix):
        """
        Generate output file path in script directory.

        Args:
            base_filename: Base name for the output file
            suffix: Suffix to append before extension

        Returns:
            str: Full output file path
        """
        script_dir = get_script_dir()
        out_filename = os.path.splitext(os.path.basename(base_filename))[0] + suffix
        return os.path.join(script_dir, out_filename)

    def _log_file_read(self, filepath, df):
        """
        Log file reading information.

        Args:
            filepath: Path to the file that was read
            df: DataFrame that was read
        """
        log(f"Reading {os.path.basename(filepath)}")
        log(f"  → {len(df):,} rows, {df.shape[1]} columns")
