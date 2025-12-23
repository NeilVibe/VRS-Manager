"""
Main GUI window for VRS Manager.

This module provides the main application window with buttons for all VRS processes.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import threading

from src.processors.raw_processor import RawProcessor
from src.processors.working_processor import WorkingProcessor
from src.processors.alllang_processor import AllLangProcessor
from src.processors.master_processor import MasterProcessor
from src.ui.history_viewer import show_update_history_viewer
from src.config import VERSION, VERSION_FOOTER, MANDATORY_COLUMNS, AUTO_GENERATED_COLUMNS, OPTIONAL_COLUMNS
from src.settings import (
    get_use_priority_change, set_use_priority_change,
    get_column_settings, set_column_settings, reset_column_settings,
    get_analyzed_columns, set_analyzed_columns,
    get_selected_optional_columns, set_selected_optional_columns
)
from src.io.excel_reader import safe_read_excel


def analyze_excel_columns(file_path):
    """
    Analyze an Excel file and return list of column names.

    Args:
        file_path: Path to Excel file

    Returns:
        tuple: (column_list, filename, error_message)
    """
    try:
        df = safe_read_excel(file_path, header=0, dtype=str)
        columns = list(df.columns)
        filename = os.path.basename(file_path)
        return columns, filename, None
    except Exception as e:
        return [], "", str(e)


def run_raw_process_thread(btn_raw, btn_working, btn_alllang, btn_master, btn_history, status_label):
    """Run Raw VRS Check in a background thread."""
    def run():
        btn_raw.config(state=tk.DISABLED)
        btn_working.config(state=tk.DISABLED)
        btn_alllang.config(state=tk.DISABLED)
        btn_master.config(state=tk.DISABLED)
        btn_history.config(state=tk.DISABLED)
        status_label.config(text="⏳ Processing Raw VRS Check...")

        try:
            processor = RawProcessor()
            processor.process()
        finally:
            btn_raw.config(state=tk.NORMAL)
            btn_working.config(state=tk.NORMAL)
            btn_alllang.config(state=tk.NORMAL)
            btn_master.config(state=tk.NORMAL)
            btn_history.config(state=tk.NORMAL)
            status_label.config(text="✓ Ready")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def run_working_process_thread(btn_raw, btn_working, btn_alllang, btn_master, btn_history, status_label):
    """Run Working VRS Check in a background thread."""
    def run():
        btn_raw.config(state=tk.DISABLED)
        btn_working.config(state=tk.DISABLED)
        btn_alllang.config(state=tk.DISABLED)
        btn_master.config(state=tk.DISABLED)
        btn_history.config(state=tk.DISABLED)
        status_label.config(text="⏳ Processing Working VRS Check...")

        try:
            processor = WorkingProcessor()
            processor.process()
        finally:
            btn_raw.config(state=tk.NORMAL)
            btn_working.config(state=tk.NORMAL)
            btn_alllang.config(state=tk.NORMAL)
            btn_master.config(state=tk.NORMAL)
            btn_history.config(state=tk.NORMAL)
            status_label.config(text="✓ Ready")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def run_alllang_process_thread(btn_raw, btn_working, btn_alllang, btn_master, btn_history, status_label):
    """Run All Language Check in a background thread."""
    def run():
        btn_raw.config(state=tk.DISABLED)
        btn_working.config(state=tk.DISABLED)
        btn_alllang.config(state=tk.DISABLED)
        btn_master.config(state=tk.DISABLED)
        btn_history.config(state=tk.DISABLED)
        status_label.config(text="⏳ Processing All Language Check...")

        try:
            processor = AllLangProcessor()
            processor.process()
        finally:
            btn_raw.config(state=tk.NORMAL)
            btn_working.config(state=tk.NORMAL)
            btn_alllang.config(state=tk.NORMAL)
            btn_master.config(state=tk.NORMAL)
            btn_history.config(state=tk.NORMAL)
            status_label.config(text="✓ Ready")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def run_master_file_update_thread(btn_raw, btn_working, btn_alllang, btn_master, btn_history, status_label):
    """Run Master File Update in a background thread."""
    def run():
        btn_raw.config(state=tk.DISABLED)
        btn_working.config(state=tk.DISABLED)
        btn_alllang.config(state=tk.DISABLED)
        btn_master.config(state=tk.DISABLED)
        btn_history.config(state=tk.DISABLED)
        status_label.config(text="⏳ Processing Master File Update...")

        try:
            processor = MasterProcessor()
            processor.process()
        finally:
            btn_raw.config(state=tk.NORMAL)
            btn_working.config(state=tk.NORMAL)
            btn_alllang.config(state=tk.NORMAL)
            btn_master.config(state=tk.NORMAL)
            btn_history.config(state=tk.NORMAL)
            status_label.config(text="✓ Ready")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def show_settings_dialog(parent):
    """
    Show V2 nested settings dialog.

    Args:
        parent: Parent window for the dialog
    """
    dialog = tk.Toplevel(parent)
    dialog.title("VRS Manager Settings")
    dialog.geometry("450x280")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    # Center dialog on parent
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    bg_color = "#f0f0f0"
    dialog.configure(bg=bg_color)

    # Title
    title_label = tk.Label(
        dialog,
        text="VRS Manager Settings",
        font=("Arial", 16, "bold"),
        bg=bg_color,
        fg="#333333"
    )
    title_label.pack(pady=(20, 15))

    # Settings options frame
    options_frame = tk.Frame(dialog, bg=bg_color)
    options_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)

    # Priority Change Mode button
    priority_status = "ON" if get_use_priority_change() else "OFF"
    priority_frame = tk.Frame(options_frame, bg="white", relief=tk.RAISED, bd=1)
    priority_frame.pack(fill=tk.X, pady=5)

    def open_priority_settings():
        dialog.destroy()
        show_priority_mode_dialog(parent)

    priority_btn = tk.Button(
        priority_frame,
        text="  Priority Change Mode",
        font=("Arial", 11, "bold"),
        bg="white",
        fg="#333333",
        anchor="w",
        relief=tk.FLAT,
        cursor="hand2",
        command=open_priority_settings
    )
    priority_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)

    priority_status_lbl = tk.Label(
        priority_frame,
        text=f"Currently: {priority_status}",
        font=("Arial", 9),
        bg="white",
        fg="#666666"
    )
    priority_status_lbl.pack(side=tk.RIGHT, padx=10)

    # Column Settings button
    analyzed_cols = get_analyzed_columns()
    col_status = f"{len(analyzed_cols)} columns" if analyzed_cols else "Not configured"
    column_frame = tk.Frame(options_frame, bg="white", relief=tk.RAISED, bd=1)
    column_frame.pack(fill=tk.X, pady=5)

    def open_column_settings():
        dialog.destroy()
        show_column_settings_dialog_v2(parent)

    column_btn = tk.Button(
        column_frame,
        text="  Column Settings",
        font=("Arial", 11, "bold"),
        bg="white",
        fg="#333333",
        anchor="w",
        relief=tk.FLAT,
        cursor="hand2",
        command=open_column_settings
    )
    column_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)

    column_status_lbl = tk.Label(
        column_frame,
        text=col_status,
        font=("Arial", 9),
        bg="white",
        fg="#666666"
    )
    column_status_lbl.pack(side=tk.RIGHT, padx=10)

    # Close button
    close_btn = tk.Button(
        dialog,
        text="Close",
        font=("Arial", 10),
        bg="#757575",
        fg="white",
        width=12,
        cursor="hand2",
        command=dialog.destroy
    )
    close_btn.pack(pady=20)


def show_priority_mode_dialog(parent):
    """
    Show Priority Change Mode settings dialog.

    Redesigned UI with clear ON/OFF toggle buttons:
    - Click ON or OFF to select (highlighted in green)
    - Save button saves the selection
    - Current saved state shown on open

    Args:
        parent: Parent window for the dialog
    """
    dialog = tk.Toplevel(parent)
    dialog.title("Priority Change Mode")
    dialog.geometry("600x450")  # Larger, more spacious
    dialog.minsize(550, 400)
    dialog.resizable(True, True)
    dialog.transient(parent)
    dialog.grab_set()

    # Center dialog
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    bg_color = "#f5f5f5"
    dialog.configure(bg=bg_color)

    # Current selection state (not saved until Save clicked)
    current_selection = tk.BooleanVar(value=get_use_priority_change())

    # Store frame references for updating
    on_frame = None
    off_frame = None
    on_widgets = []
    off_widgets = []

    # Colors
    SELECTED_BG = "#e8f5e9"      # Light green background
    SELECTED_BORDER = "#4CAF50"  # Green border
    SELECTED_TEXT = "#2e7d32"    # Dark green text
    UNSELECTED_BG = "#fafafa"    # Light gray background
    UNSELECTED_BORDER = "#e0e0e0"  # Gray border
    UNSELECTED_TEXT = "#757575"  # Gray text

    def update_selection_visuals():
        """Update visual highlighting based on current selection."""
        is_on = current_selection.get()

        # Update ON frame
        if is_on:
            on_frame.config(bg=SELECTED_BG, highlightbackground=SELECTED_BORDER, highlightthickness=3)
            for widget in on_widgets:
                widget.config(bg=SELECTED_BG)
        else:
            on_frame.config(bg=UNSELECTED_BG, highlightbackground=UNSELECTED_BORDER, highlightthickness=1)
            for widget in on_widgets:
                widget.config(bg=UNSELECTED_BG)

        # Update OFF frame
        if not is_on:
            off_frame.config(bg=SELECTED_BG, highlightbackground=SELECTED_BORDER, highlightthickness=3)
            for widget in off_widgets:
                widget.config(bg=SELECTED_BG)
        else:
            off_frame.config(bg=UNSELECTED_BG, highlightbackground=UNSELECTED_BORDER, highlightthickness=1)
            for widget in off_widgets:
                widget.config(bg=UNSELECTED_BG)

    def select_on():
        """Select ON option."""
        current_selection.set(True)
        update_selection_visuals()

    def select_off():
        """Select OFF option."""
        current_selection.set(False)
        update_selection_visuals()

    # Title
    tk.Label(
        dialog,
        text="Priority Change Mode",
        font=("Arial", 16, "bold"),
        bg=bg_color,
        fg="#333333"
    ).pack(pady=(25, 10))

    # Subtitle
    tk.Label(
        dialog,
        text="Choose how the CHANGES column displays change types",
        font=("Arial", 10),
        bg=bg_color,
        fg="#666666"
    ).pack(pady=(0, 20))

    # Options container
    options_frame = tk.Frame(dialog, bg=bg_color)
    options_frame.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)

    # ===== ON Option (clickable card) =====
    on_frame = tk.Frame(
        options_frame,
        bg=UNSELECTED_BG,
        highlightbackground=UNSELECTED_BORDER,
        highlightthickness=1,
        cursor="hand2"
    )
    on_frame.pack(fill=tk.X, pady=10, ipady=10)

    on_header = tk.Label(
        on_frame,
        text="ON - Priority Labels (Recommended)",
        font=("Arial", 12, "bold"),
        bg=UNSELECTED_BG,
        fg=SELECTED_TEXT,
        cursor="hand2"
    )
    on_header.pack(anchor=tk.W, padx=20, pady=(15, 5))
    on_widgets.append(on_header)

    on_desc = tk.Label(
        on_frame,
        text="Shows the most important change type only",
        font=("Arial", 10),
        bg=UNSELECTED_BG,
        fg="#666666",
        cursor="hand2"
    )
    on_desc.pack(anchor=tk.W, padx=20, pady=2)
    on_widgets.append(on_desc)

    on_example = tk.Label(
        on_frame,
        text='Example: "StrOrigin Change" or "Text Change"',
        font=("Arial", 9, "italic"),
        bg=UNSELECTED_BG,
        fg="#888888",
        cursor="hand2"
    )
    on_example.pack(anchor=tk.W, padx=20, pady=(2, 15))
    on_widgets.append(on_example)

    # Bind click to entire ON frame and children
    on_frame.bind("<Button-1>", lambda e: select_on())
    for widget in on_widgets:
        widget.bind("<Button-1>", lambda e: select_on())

    # ===== OFF Option (clickable card) =====
    off_frame = tk.Frame(
        options_frame,
        bg=UNSELECTED_BG,
        highlightbackground=UNSELECTED_BORDER,
        highlightthickness=1,
        cursor="hand2"
    )
    off_frame.pack(fill=tk.X, pady=10, ipady=10)

    off_header = tk.Label(
        off_frame,
        text="OFF - Full Composite Labels",
        font=("Arial", 12, "bold"),
        bg=UNSELECTED_BG,
        fg=UNSELECTED_TEXT,
        cursor="hand2"
    )
    off_header.pack(anchor=tk.W, padx=20, pady=(15, 5))
    off_widgets.append(off_header)

    off_desc = tk.Label(
        off_frame,
        text="Shows all change types combined (legacy mode)",
        font=("Arial", 10),
        bg=UNSELECTED_BG,
        fg="#666666",
        cursor="hand2"
    )
    off_desc.pack(anchor=tk.W, padx=20, pady=2)
    off_widgets.append(off_desc)

    off_example = tk.Label(
        off_frame,
        text='Example: "StrOrigin+EventName+TimeFrame Change"',
        font=("Arial", 9, "italic"),
        bg=UNSELECTED_BG,
        fg="#888888",
        cursor="hand2"
    )
    off_example.pack(anchor=tk.W, padx=20, pady=(2, 15))
    off_widgets.append(off_example)

    # Bind click to entire OFF frame and children
    off_frame.bind("<Button-1>", lambda e: select_off())
    for widget in off_widgets:
        widget.bind("<Button-1>", lambda e: select_off())

    # Set initial visual state
    update_selection_visuals()

    # ===== Button frame =====
    button_frame = tk.Frame(dialog, bg=bg_color)
    button_frame.pack(pady=25)

    def save_and_close():
        set_use_priority_change(current_selection.get())
        status = "ON" if current_selection.get() else "OFF"
        messagebox.showinfo("Saved", f"Priority Change Mode set to {status}")
        dialog.destroy()

    def back_to_settings():
        dialog.destroy()
        show_settings_dialog(parent)

    tk.Button(
        button_frame,
        text="Back",
        font=("Arial", 11),
        bg="#757575",
        fg="white",
        width=12,
        height=1,
        cursor="hand2",
        relief=tk.RAISED,
        bd=2,
        command=back_to_settings
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        button_frame,
        text="Save",
        font=("Arial", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        width=12,
        height=1,
        cursor="hand2",
        relief=tk.RAISED,
        bd=2,
        command=save_and_close
    ).pack(side=tk.LEFT, padx=10)


# Auto-generated column help texts (shortened for UI fit)
AUTO_GENERATED_HELP = {
    "PreviousData": "Prev Text|STATUS|Memo",
    "PreviousText": "Prev row Text",
    "PreviousEventName": "Prev EventName",
    "DETAILED_CHANGES": "Full change type",
    "Previous StrOrigin": "Prev StrOrigin",
    "Mainline Translation": "Original Text"
}


def show_column_settings_dialog_v2(parent):
    """
    Show V2 Column Settings dialog with file analysis.

    Args:
        parent: Parent window for the dialog
    """
    from src.utils.helpers import log

    dialog = tk.Toplevel(parent)
    dialog.title("Column Settings")
    dialog.geometry("880x800")  # Wider and taller
    dialog.minsize(800, 600)    # Minimum size
    dialog.resizable(True, True)  # Fully resizable
    dialog.transient(parent)
    dialog.grab_set()

    # Center dialog
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    bg_color = "#f0f0f0"
    dialog.configure(bg=bg_color)

    # Title
    tk.Label(
        dialog,
        text="Column Settings",
        font=("Arial", 14, "bold"),
        bg=bg_color,
        fg="#333333"
    ).pack(pady=(15, 5))

    tk.Label(
        dialog,
        text="Customize which columns appear in WORKING output (Work Transform sheet)",
        font=("Arial", 9),
        bg=bg_color,
        fg="#666666"
    ).pack(pady=(0, 10))

    # Create scrollable frame with proper expansion
    canvas_frame = tk.Frame(dialog, bg=bg_color)
    canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

    canvas = tk.Canvas(canvas_frame, bg=bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg_color)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Dynamic width based on dialog
    def update_canvas_width(event=None):
        canvas.itemconfig(canvas_window, width=canvas.winfo_width() - 20)

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", update_canvas_width)

    # ===== STEP 1: FILE ANALYSIS =====
    file_frame = tk.LabelFrame(
        scrollable_frame,
        text=" STEP 1: Analyze Source File ",
        font=("Arial", 10, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=15,
        pady=10
    )
    file_frame.pack(fill=tk.X, padx=15, pady=10)

    # Status label
    analyzed_cols = get_analyzed_columns()
    if analyzed_cols:
        status_text = f"Analyzed: {len(analyzed_cols)} columns found"
        status_color = "#2e7d32"
    else:
        status_text = "No file analyzed yet. Upload a PREVIOUS or CURRENT Excel file."
        status_color = "#666666"

    status_var = tk.StringVar(value=status_text)
    status_label = tk.Label(
        file_frame,
        textvariable=status_var,
        font=("Arial", 10),
        bg=bg_color,
        fg=status_color
    )
    status_label.pack(anchor=tk.W, pady=(0, 10))

    # Store checkbox variables
    optional_vars = {}
    optional_frame_container = None

    def refresh_optional_columns():
        """Refresh the optional columns display."""
        nonlocal optional_frame_container, optional_vars

        # Clear existing optional frame if exists
        if optional_frame_container:
            optional_frame_container.destroy()

        analyzed = get_analyzed_columns()
        selected = get_selected_optional_columns()

        # Filter out mandatory and auto-generated columns
        optional_cols = [
            col for col in analyzed
            if col not in MANDATORY_COLUMNS and col not in AUTO_GENERATED_COLUMNS
        ]

        if not optional_cols:
            return

        # Create optional columns section
        optional_frame_container = tk.LabelFrame(
            scrollable_frame,
            text=f" OPTIONAL COLUMNS ({len(optional_cols)} from analyzed file) ",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg="#333333",
            padx=15,
            pady=10
        )
        optional_frame_container.pack(fill=tk.X, padx=15, pady=10)

        # Select All / Deselect All buttons
        btn_row = tk.Frame(optional_frame_container, bg=bg_color)
        btn_row.pack(fill=tk.X, pady=(0, 10))

        def select_all():
            for var in optional_vars.values():
                var.set(True)

        def deselect_all():
            for var in optional_vars.values():
                var.set(False)

        tk.Button(
            btn_row,
            text="Select All",
            font=("Arial", 9),
            bg="#4CAF50",
            fg="white",
            cursor="hand2",
            command=select_all
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_row,
            text="Deselect All",
            font=("Arial", 9),
            bg="#f44336",
            fg="white",
            cursor="hand2",
            command=deselect_all
        ).pack(side=tk.LEFT, padx=2)

        # Separator
        tk.Frame(optional_frame_container, height=1, bg="#cccccc").pack(fill=tk.X, pady=5)

        # Grid of checkboxes (3 columns)
        grid_frame = tk.Frame(optional_frame_container, bg=bg_color)
        grid_frame.pack(fill=tk.X)

        optional_vars.clear()
        for i, col in enumerate(optional_cols):
            row = i // 3
            col_idx = i % 3

            enabled = col in selected or (not selected and True)  # Default ON if no selection yet
            var = tk.BooleanVar(value=enabled)
            optional_vars[col] = var

            cb = tk.Checkbutton(
                grid_frame,
                text=col,
                variable=var,
                font=("Arial", 9),
                bg=bg_color,
                activebackground=bg_color,
                width=20,
                anchor="w"
            )
            cb.grid(row=row, column=col_idx, sticky="w", padx=5, pady=2)

        # Info label
        tk.Label(
            optional_frame_container,
            text="If a selected column is not in processed files, it will be skipped gracefully.",
            font=("Arial", 8, "italic"),
            bg=bg_color,
            fg="#888888"
        ).pack(anchor=tk.W, pady=(10, 0))

    def upload_and_analyze():
        """Upload Excel file and analyze columns with threading."""
        file_path = filedialog.askopenfilename(
            title="Select PREVIOUS or CURRENT Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if not file_path:
            return

        # Disable upload button and show progress
        upload_btn.config(state=tk.DISABLED, text="Analyzing...")
        status_var.set("Analyzing file... Please wait.")
        status_label.config(fg="#2196F3")
        dialog.update()

        filename = os.path.basename(file_path)
        log(f"[Column Settings] Analyzing file: {filename}")

        def analyze_in_thread():
            """Run analysis in background thread."""
            try:
                columns, fname, error = analyze_excel_columns(file_path)

                # Schedule UI update on main thread
                def update_ui():
                    if error:
                        log(f"[Column Settings] ERROR: {error}")
                        status_var.set(f"Error: {error}")
                        status_label.config(fg="#d32f2f")
                        messagebox.showerror("Error", f"Failed to analyze file:\n{error}")
                    else:
                        # Save analyzed columns
                        set_analyzed_columns(columns)

                        # Count optional columns
                        optional_count = len([
                            c for c in columns
                            if c not in MANDATORY_COLUMNS and c not in AUTO_GENERATED_COLUMNS
                        ])

                        log(f"[Column Settings] Found {len(columns)} total columns")
                        log(f"[Column Settings] Optional columns: {optional_count}")

                        # Update status
                        status_var.set(f"Analyzed: {fname} ({len(columns)} columns, {optional_count} optional)")
                        status_label.config(fg="#2e7d32")

                        # Refresh optional columns display
                        refresh_optional_columns()

                        log(f"[Column Settings] Analysis complete")
                        messagebox.showinfo("Success", f"Analyzed {len(columns)} columns from:\n{fname}\n\nOptional columns: {optional_count}")

                    # Re-enable upload button
                    upload_btn.config(state=tk.NORMAL, text="Upload PREVIOUS or CURRENT Excel File")

                dialog.after(0, update_ui)

            except Exception as e:
                log(f"[Column Settings] Exception: {e}")
                def show_error():
                    status_var.set(f"Error: {str(e)}")
                    status_label.config(fg="#d32f2f")
                    upload_btn.config(state=tk.NORMAL, text="Upload PREVIOUS or CURRENT Excel File")
                    messagebox.showerror("Error", f"Analysis failed:\n{e}")
                dialog.after(0, show_error)

        # Run in background thread
        thread = threading.Thread(target=analyze_in_thread, daemon=True)
        thread.start()

    upload_btn = tk.Button(
        file_frame,
        text="Upload PREVIOUS or CURRENT Excel File",
        font=("Arial", 10, "bold"),
        bg="#2196F3",
        fg="white",
        cursor="hand2",
        command=upload_and_analyze
    )
    upload_btn.pack(anchor=tk.W)

    # ===== MANDATORY COLUMNS =====
    mandatory_frame = tk.LabelFrame(
        scrollable_frame,
        text=" MANDATORY COLUMNS (Always Included) ",
        font=("Arial", 10, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=15,
        pady=10
    )
    mandatory_frame.pack(fill=tk.X, padx=15, pady=10)

    mandatory_inner = tk.Frame(mandatory_frame, bg=bg_color)
    mandatory_inner.pack(fill=tk.X)

    for i, col in enumerate(MANDATORY_COLUMNS):
        row = i // 3
        col_idx = i % 3
        tk.Label(
            mandatory_inner,
            text=f" {col}",
            font=("Arial", 9),
            bg=bg_color,
            fg="#666666"
        ).grid(row=row, column=col_idx, sticky="w", padx=5, pady=2)

    # ===== AUTO-GENERATED COLUMNS =====
    auto_frame = tk.LabelFrame(
        scrollable_frame,
        text=" AUTO-GENERATED COLUMNS (Created by VRS Logic) ",
        font=("Arial", 10, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=15,
        pady=10
    )
    auto_frame.pack(fill=tk.X, padx=15, pady=10)

    col_settings = get_column_settings()
    auto_vars = {}

    for col in AUTO_GENERATED_COLUMNS:
        row_frame = tk.Frame(auto_frame, bg=bg_color)
        row_frame.pack(fill=tk.X, pady=2)

        enabled = col_settings.get("auto_generated", {}).get(col, {}).get("enabled", True)
        var = tk.BooleanVar(value=enabled)
        auto_vars[col] = var

        cb = tk.Checkbutton(
            row_frame,
            text=col,
            variable=var,
            font=("Arial", 10),
            bg=bg_color,
            activebackground=bg_color,
            width=22,
            anchor="w"
        )
        cb.pack(side=tk.LEFT)

        help_text = AUTO_GENERATED_HELP.get(col, "")
        if help_text:
            tk.Label(
                row_frame,
                text=f" {help_text}",
                font=("Arial", 8),
                bg=bg_color,
                fg="#888888"
            ).pack(side=tk.LEFT, padx=5)

    # Initialize optional columns if already analyzed
    refresh_optional_columns()

    # Pack canvas and scrollbar inside canvas_frame
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # ===== BUTTON FRAME =====
    button_frame = tk.Frame(dialog, bg=bg_color)
    button_frame.pack(pady=15)

    def reset_to_defaults():
        """Reset all settings to defaults."""
        for var in auto_vars.values():
            var.set(True)
        for var in optional_vars.values():
            var.set(True)

    def save_and_close():
        """Save settings and close dialog."""
        # Save auto-generated settings
        new_auto = {col: {"enabled": var.get()} for col, var in auto_vars.items()}

        # Save optional column selections
        selected_optional = [col for col, var in optional_vars.items() if var.get()]
        set_selected_optional_columns(selected_optional)

        # Update column settings
        settings = get_column_settings()
        settings["auto_generated"] = new_auto
        set_column_settings(settings)

        canvas.unbind_all("<MouseWheel>")
        messagebox.showinfo("Saved", "Column settings saved!\n\nChanges will apply to future Working Process runs.")
        dialog.destroy()

    def back_to_settings():
        canvas.unbind_all("<MouseWheel>")
        dialog.destroy()
        show_settings_dialog(parent)

    tk.Button(
        button_frame,
        text="Back",
        font=("Arial", 10),
        bg="#757575",
        fg="white",
        width=10,
        cursor="hand2",
        command=back_to_settings
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        button_frame,
        text="Reset Defaults",
        font=("Arial", 10),
        bg="#FF9800",
        fg="white",
        width=12,
        cursor="hand2",
        command=reset_to_defaults
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        button_frame,
        text="Apply & Save",
        font=("Arial", 10, "bold"),
        bg="#4CAF50",
        fg="white",
        width=12,
        cursor="hand2",
        command=save_and_close
    ).pack(side=tk.LEFT, padx=5)


def create_gui():
    """Create and display the main GUI window."""
    window = tk.Tk()
    window.title(f"VRS Manager by Neil Schmitt (ver. {VERSION})")
    window.geometry("480x800")
    window.resizable(False, False)

    bg_color = "#f0f0f0"
    window.configure(bg=bg_color)

    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            window.quit()
            window.destroy()
            sys.exit(0)

    window.protocol("WM_DELETE_WINDOW", on_closing)

    # Title frame
    title_frame = tk.Frame(window, bg=bg_color)
    title_frame.pack(pady=20)

    title_label = tk.Label(
        title_frame,
        text="VRS Manager",
        font=("Arial", 18, "bold"),
        bg=bg_color,
        fg="#333333"
    )
    title_label.pack()

    subtitle_label = tk.Label(
        title_frame,
        text="Select a process to begin",
        font=("Arial", 10),
        bg=bg_color,
        fg="#666666"
    )
    subtitle_label.pack()

    # Status label
    status_label = tk.Label(
        window,
        text="✓ Ready",
        font=("Arial", 10, "italic"),
        bg=bg_color,
        fg="#006600"
    )
    status_label.pack(pady=5)

    # Button frame
    button_frame = tk.Frame(window, bg=bg_color)
    button_frame.pack(pady=20)

    # Raw Process button
    btn_raw = tk.Button(
        button_frame,
        text="Raw Process",
        font=("Arial", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        width=42,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2"
    )
    btn_raw.pack(pady=8)

    desc_raw = tk.Label(
        button_frame,
        text="Compare PREVIOUS ↔ CURRENT and detect changes",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#666666"
    )
    desc_raw.pack()

    # Working Process button
    btn_working = tk.Button(
        button_frame,
        text="Working Process",
        font=("Arial", 11, "bold"),
        bg="#2196F3",
        fg="white",
        width=42,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2"
    )
    btn_working.pack(pady=8)

    desc_working = tk.Label(
        button_frame,
        text="Import with intelligent logic (Previous → Current)",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#666666"
    )
    desc_working.pack()

    # All Language Process button
    btn_alllang = tk.Button(
        button_frame,
        text="All Language Process",
        font=("Arial", 11, "bold"),
        bg="#FF9800",
        fg="white",
        width=42,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2"
    )
    btn_alllang.pack(pady=8)

    desc_alllang = tk.Label(
        button_frame,
        text="Tri-lingual import (KR/EN/CN flexible updates)",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#666666"
    )
    desc_alllang.pack()

    # Master File Update button
    btn_master = tk.Button(
        button_frame,
        text="Master File Update",
        font=("Arial", 11, "bold"),
        bg="#9C27B0",
        fg="white",
        width=42,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2"
    )
    btn_master.pack(pady=8)

    desc_master = tk.Label(
        button_frame,
        text="Update Master File with Working Process output (3-Key Copy-Paste)",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#666666"
    )
    desc_master.pack()

    # Separator
    separator = tk.Frame(window, height=2, bd=1, relief=tk.SUNKEN, bg="#cccccc")
    separator.pack(fill=tk.X, padx=20, pady=10)

    # History button
    btn_history = tk.Button(
        button_frame,
        text="📊 View Update History",
        font=("Arial", 11, "bold"),
        bg="#607D8B",
        fg="white",
        width=42,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2",
        command=show_update_history_viewer
    )
    btn_history.pack(pady=8)

    desc_history = tk.Label(
        button_frame,
        text="View complete update history (All processes)",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#666666"
    )
    desc_history.pack()

    # Settings button (V2: nested menu with Priority Mode + Column Settings)
    btn_settings = tk.Button(
        button_frame,
        text="⚙️ Settings",
        font=("Arial", 11, "bold"),
        bg="#757575",
        fg="white",
        width=42,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2",
        command=lambda: show_settings_dialog(window)
    )
    btn_settings.pack(pady=8)

    desc_settings = tk.Label(
        button_frame,
        text="Configure Priority Change mode and other options",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#666666"
    )
    desc_settings.pack()

    # Configure button commands
    btn_raw.config(command=lambda: run_raw_process_thread(btn_raw, btn_working, btn_alllang, btn_master, btn_history, status_label))
    btn_working.config(command=lambda: run_working_process_thread(btn_raw, btn_working, btn_alllang, btn_master, btn_history, status_label))
    btn_alllang.config(command=lambda: run_alllang_process_thread(btn_raw, btn_working, btn_alllang, btn_master, btn_history, status_label))
    btn_master.config(command=lambda: run_master_file_update_thread(btn_raw, btn_working, btn_alllang, btn_master, btn_history, status_label))

    # Footer
    footer_label = tk.Label(
        window,
        text=VERSION_FOOTER,
        font=("Arial", 8),
        bg=bg_color,
        fg="#999999"
    )
    footer_label.pack(side=tk.BOTTOM, pady=10)

    # Center window on screen
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

    window.mainloop()
