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
    get_selected_optional_columns, set_selected_optional_columns,
    # V3: Dual-file column analysis
    get_previous_file_columns, get_current_file_columns,
    set_file_info, get_dual_file_status, clear_file_columns
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
    Show V3 Column Settings dialog with dual-file analysis.

    Features:
    - Upload PREVIOUS and CURRENT files separately
    - Columns from both files shown with prefixes for duplicates
    - Select which columns to include in output

    Args:
        parent: Parent window for the dialog
    """
    from src.utils.helpers import log

    dialog = tk.Toplevel(parent)
    dialog.title("Column Settings")
    dialog.geometry("950x800")  # Wider for dual-file layout
    dialog.minsize(900, 700)
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

    # Colors
    PREV_COLOR = "#1565C0"   # Blue for PREVIOUS
    CURR_COLOR = "#2E7D32"   # Green for CURRENT
    CARD_BG = "#ffffff"

    # ===== TITLE =====
    tk.Label(
        dialog,
        text="Column Settings",
        font=("Arial", 16, "bold"),
        bg=bg_color,
        fg="#333333"
    ).pack(pady=(20, 5))

    tk.Label(
        dialog,
        text="Upload PREVIOUS and CURRENT files to select columns for WORKING output",
        font=("Arial", 10),
        bg=bg_color,
        fg="#666666"
    ).pack(pady=(0, 15))

    # ===== SCROLLABLE CONTENT =====
    canvas_frame = tk.Frame(dialog, bg=bg_color)
    canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    canvas = tk.Canvas(canvas_frame, bg=bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg_color)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    def update_canvas_width(event=None):
        canvas.itemconfig(canvas_window, width=canvas.winfo_width() - 20)

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", update_canvas_width)

    # Store state
    prev_vars = {}
    curr_vars = {}
    prev_columns_frame = None
    curr_columns_frame = None

    # Get current status
    status = get_dual_file_status()

    # ===== STEP 1: DUAL FILE UPLOAD =====
    upload_section = tk.LabelFrame(
        scrollable_frame,
        text=" STEP 1: Upload Source Files ",
        font=("Arial", 11, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=15,
        pady=15
    )
    upload_section.pack(fill=tk.X, padx=10, pady=10)

    # Two-column layout for PREVIOUS and CURRENT
    files_row = tk.Frame(upload_section, bg=bg_color)
    files_row.pack(fill=tk.X, pady=10)

    # Configure grid columns to expand equally
    files_row.columnconfigure(0, weight=1)
    files_row.columnconfigure(1, weight=1)

    # ----- PREVIOUS FILE CARD -----
    prev_card = tk.Frame(files_row, bg=CARD_BG, relief=tk.RAISED, bd=1)
    prev_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

    tk.Label(
        prev_card,
        text="PREVIOUS File",
        font=("Arial", 12, "bold"),
        bg=CARD_BG,
        fg=PREV_COLOR
    ).pack(pady=(15, 5))

    prev_status_var = tk.StringVar()
    if status["previous"]["uploaded"]:
        prev_status_var.set(f"✓ {status['previous']['filename']}\n({status['previous']['count']} columns)")
    else:
        prev_status_var.set("No file uploaded")

    prev_status_label = tk.Label(
        prev_card,
        textvariable=prev_status_var,
        font=("Arial", 9),
        bg=CARD_BG,
        fg="#666666",
        justify=tk.CENTER
    )
    prev_status_label.pack(pady=5)

    def upload_previous():
        file_path = filedialog.askopenfilename(
            title="Select PREVIOUS Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if not file_path:
            return

        prev_upload_btn.config(state=tk.DISABLED, text="Analyzing...")
        dialog.update()

        def analyze():
            try:
                columns, fname, error = analyze_excel_columns(file_path)
                def update_ui():
                    if error:
                        messagebox.showerror("Error", f"Failed to analyze:\n{error}")
                        prev_status_var.set("Error analyzing file")
                    else:
                        set_file_info("previous", fname, columns)
                        prev_status_var.set(f"✓ {fname}\n({len(columns)} columns)")
                        log(f"[Column Settings] PREVIOUS: {len(columns)} columns from {fname}")
                        refresh_column_lists()
                    prev_upload_btn.config(state=tk.NORMAL, text="Upload PREVIOUS")
                dialog.after(0, update_ui)
            except Exception as e:
                def show_err():
                    messagebox.showerror("Error", str(e))
                    prev_upload_btn.config(state=tk.NORMAL, text="Upload PREVIOUS")
                dialog.after(0, show_err)

        threading.Thread(target=analyze, daemon=True).start()

    prev_upload_btn = tk.Button(
        prev_card,
        text="Upload PREVIOUS",
        font=("Arial", 10, "bold"),
        bg=PREV_COLOR,
        fg="white",
        cursor="hand2",
        width=18,
        command=upload_previous
    )
    prev_upload_btn.pack(pady=(10, 5))

    def clear_previous():
        clear_file_columns("previous")
        prev_status_var.set("No file uploaded")
        refresh_column_lists()

    tk.Button(
        prev_card,
        text="Clear",
        font=("Arial", 9),
        bg="#9E9E9E",
        fg="white",
        cursor="hand2",
        width=10,
        command=clear_previous
    ).pack(pady=(0, 15))

    # ----- CURRENT FILE CARD -----
    curr_card = tk.Frame(files_row, bg=CARD_BG, relief=tk.RAISED, bd=1)
    curr_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

    tk.Label(
        curr_card,
        text="CURRENT File",
        font=("Arial", 12, "bold"),
        bg=CARD_BG,
        fg=CURR_COLOR
    ).pack(pady=(15, 5))

    curr_status_var = tk.StringVar()
    if status["current"]["uploaded"]:
        curr_status_var.set(f"✓ {status['current']['filename']}\n({status['current']['count']} columns)")
    else:
        curr_status_var.set("No file uploaded")

    curr_status_label = tk.Label(
        curr_card,
        textvariable=curr_status_var,
        font=("Arial", 9),
        bg=CARD_BG,
        fg="#666666",
        justify=tk.CENTER
    )
    curr_status_label.pack(pady=5)

    def upload_current():
        file_path = filedialog.askopenfilename(
            title="Select CURRENT Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if not file_path:
            return

        curr_upload_btn.config(state=tk.DISABLED, text="Analyzing...")
        dialog.update()

        def analyze():
            try:
                columns, fname, error = analyze_excel_columns(file_path)
                def update_ui():
                    if error:
                        messagebox.showerror("Error", f"Failed to analyze:\n{error}")
                        curr_status_var.set("Error analyzing file")
                    else:
                        set_file_info("current", fname, columns)
                        curr_status_var.set(f"✓ {fname}\n({len(columns)} columns)")
                        log(f"[Column Settings] CURRENT: {len(columns)} columns from {fname}")
                        refresh_column_lists()
                    curr_upload_btn.config(state=tk.NORMAL, text="Upload CURRENT")
                dialog.after(0, update_ui)
            except Exception as e:
                def show_err():
                    messagebox.showerror("Error", str(e))
                    curr_upload_btn.config(state=tk.NORMAL, text="Upload CURRENT")
                dialog.after(0, show_err)

        threading.Thread(target=analyze, daemon=True).start()

    curr_upload_btn = tk.Button(
        curr_card,
        text="Upload CURRENT",
        font=("Arial", 10, "bold"),
        bg=CURR_COLOR,
        fg="white",
        cursor="hand2",
        width=18,
        command=upload_current
    )
    curr_upload_btn.pack(pady=(10, 5))

    def clear_current():
        clear_file_columns("current")
        curr_status_var.set("No file uploaded")
        refresh_column_lists()

    tk.Button(
        curr_card,
        text="Clear",
        font=("Arial", 9),
        bg="#9E9E9E",
        fg="white",
        cursor="hand2",
        width=10,
        command=clear_current
    ).pack(pady=(0, 15))

    # ===== STEP 2: SELECT COLUMNS =====
    columns_section = tk.LabelFrame(
        scrollable_frame,
        text=" STEP 2: Select Columns to Include ",
        font=("Arial", 11, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=15,
        pady=15
    )
    columns_section.pack(fill=tk.X, padx=10, pady=10)

    # Info about prefixes
    tk.Label(
        columns_section,
        text="Duplicate column names will be prefixed with 'Previous_' or 'Current_' automatically",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#888888"
    ).pack(anchor=tk.W, pady=(0, 10))

    # Two-column layout for column lists
    columns_row = tk.Frame(columns_section, bg=bg_color)
    columns_row.pack(fill=tk.BOTH, expand=True)
    columns_row.columnconfigure(0, weight=1)
    columns_row.columnconfigure(1, weight=1)

    # Container frames for column lists (will be populated by refresh)
    prev_list_container = tk.Frame(columns_row, bg=bg_color)
    prev_list_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    curr_list_container = tk.Frame(columns_row, bg=bg_color)
    curr_list_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    def refresh_column_lists():
        """Refresh the column selection lists."""
        nonlocal prev_columns_frame, curr_columns_frame, prev_vars, curr_vars

        # Clear existing
        for widget in prev_list_container.winfo_children():
            widget.destroy()
        for widget in curr_list_container.winfo_children():
            widget.destroy()

        prev_vars.clear()
        curr_vars.clear()

        prev_cols = get_previous_file_columns()
        curr_cols = get_current_file_columns()
        duplicates = set(prev_cols) & set(curr_cols)
        selected = get_selected_optional_columns()

        # Filter out mandatory/auto-generated
        prev_optional = [c for c in prev_cols if c not in MANDATORY_COLUMNS and c not in AUTO_GENERATED_COLUMNS]
        curr_optional = [c for c in curr_cols if c not in MANDATORY_COLUMNS and c not in AUTO_GENERATED_COLUMNS]

        # ----- PREVIOUS COLUMNS LIST -----
        tk.Label(
            prev_list_container,
            text=f"From PREVIOUS ({len(prev_optional)} optional)",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg=PREV_COLOR
        ).pack(anchor=tk.W, pady=(0, 5))

        if prev_optional:
            prev_btn_row = tk.Frame(prev_list_container, bg=bg_color)
            prev_btn_row.pack(fill=tk.X, pady=(0, 5))

            def select_all_prev():
                for v in prev_vars.values():
                    v.set(True)

            def deselect_all_prev():
                for v in prev_vars.values():
                    v.set(False)

            tk.Button(prev_btn_row, text="All", font=("Arial", 8), bg="#4CAF50", fg="white",
                      command=select_all_prev, width=6).pack(side=tk.LEFT, padx=2)
            tk.Button(prev_btn_row, text="None", font=("Arial", 8), bg="#f44336", fg="white",
                      command=deselect_all_prev, width=6).pack(side=tk.LEFT, padx=2)

            prev_columns_frame = tk.Frame(prev_list_container, bg=CARD_BG, relief=tk.SUNKEN, bd=1)
            prev_columns_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            for col in prev_optional:
                display_name = f"Previous_{col}" if col in duplicates else col
                var = tk.BooleanVar(value=display_name in selected or col in selected or not selected)
                prev_vars[display_name] = var

                cb = tk.Checkbutton(
                    prev_columns_frame,
                    text=display_name,
                    variable=var,
                    font=("Arial", 9),
                    bg=CARD_BG,
                    activebackground=CARD_BG,
                    anchor="w"
                )
                cb.pack(fill=tk.X, padx=10, pady=1)
        else:
            tk.Label(
                prev_list_container,
                text="No columns (upload PREVIOUS file)",
                font=("Arial", 9, "italic"),
                bg=bg_color,
                fg="#999999"
            ).pack(anchor=tk.W)

        # ----- CURRENT COLUMNS LIST -----
        tk.Label(
            curr_list_container,
            text=f"From CURRENT ({len(curr_optional)} optional)",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg=CURR_COLOR
        ).pack(anchor=tk.W, pady=(0, 5))

        if curr_optional:
            curr_btn_row = tk.Frame(curr_list_container, bg=bg_color)
            curr_btn_row.pack(fill=tk.X, pady=(0, 5))

            def select_all_curr():
                for v in curr_vars.values():
                    v.set(True)

            def deselect_all_curr():
                for v in curr_vars.values():
                    v.set(False)

            tk.Button(curr_btn_row, text="All", font=("Arial", 8), bg="#4CAF50", fg="white",
                      command=select_all_curr, width=6).pack(side=tk.LEFT, padx=2)
            tk.Button(curr_btn_row, text="None", font=("Arial", 8), bg="#f44336", fg="white",
                      command=deselect_all_curr, width=6).pack(side=tk.LEFT, padx=2)

            curr_columns_frame = tk.Frame(curr_list_container, bg=CARD_BG, relief=tk.SUNKEN, bd=1)
            curr_columns_frame.pack(fill=tk.BOTH, expand=True, pady=5)

            for col in curr_optional:
                display_name = f"Current_{col}" if col in duplicates else col
                # Skip if already added from PREVIOUS (non-duplicate)
                if col not in duplicates and col in [c.replace("Previous_", "") for c in prev_vars.keys()]:
                    continue
                var = tk.BooleanVar(value=display_name in selected or col in selected or not selected)
                curr_vars[display_name] = var

                cb = tk.Checkbutton(
                    curr_columns_frame,
                    text=display_name,
                    variable=var,
                    font=("Arial", 9),
                    bg=CARD_BG,
                    activebackground=CARD_BG,
                    anchor="w"
                )
                cb.pack(fill=tk.X, padx=10, pady=1)
        else:
            tk.Label(
                curr_list_container,
                text="No columns (upload CURRENT file)",
                font=("Arial", 9, "italic"),
                bg=bg_color,
                fg="#999999"
            ).pack(anchor=tk.W)

    # Initialize column lists
    refresh_column_lists()

    # ===== MANDATORY COLUMNS (Info Only) =====
    mandatory_frame = tk.LabelFrame(
        scrollable_frame,
        text=" MANDATORY COLUMNS (Always Included - Cannot Disable) ",
        font=("Arial", 11, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=15,
        pady=10
    )
    mandatory_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(
        mandatory_frame,
        text="These columns are required for VRS processing and are always included:",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#666666"
    ).pack(anchor=tk.W, pady=(0, 8))

    # Display mandatory columns in a grid (3 columns)
    mandatory_grid = tk.Frame(mandatory_frame, bg=bg_color)
    mandatory_grid.pack(fill=tk.X)

    for i, col in enumerate(MANDATORY_COLUMNS):
        row = i // 3
        col_idx = i % 3
        tk.Label(
            mandatory_grid,
            text=f"✓ {col}",
            font=("Arial", 9),
            bg=bg_color,
            fg="#2E7D32"
        ).grid(row=row, column=col_idx, sticky="w", padx=10, pady=2)

    # ===== AUTO-GENERATED COLUMNS =====
    auto_frame = tk.LabelFrame(
        scrollable_frame,
        text=" AUTO-GENERATED COLUMNS (Created by VRS Logic) ",
        font=("Arial", 11, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=15,
        pady=15
    )
    auto_frame.pack(fill=tk.X, padx=10, pady=10)

    col_settings = get_column_settings()
    auto_vars = {}

    for col in AUTO_GENERATED_COLUMNS:
        row_frame = tk.Frame(auto_frame, bg=bg_color)
        row_frame.pack(fill=tk.X, pady=3)

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
            width=24,
            anchor="w"
        )
        cb.pack(side=tk.LEFT)

        help_text = AUTO_GENERATED_HELP.get(col, "")
        if help_text:
            tk.Label(
                row_frame,
                text=f"  {help_text}",
                font=("Arial", 9),
                bg=bg_color,
                fg="#888888"
            ).pack(side=tk.LEFT)

    # Pack canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # ===== BUTTON FRAME =====
    button_frame = tk.Frame(dialog, bg=bg_color)
    button_frame.pack(pady=20)

    def save_and_close():
        """Save settings and close dialog."""
        # Combine all selected columns
        all_selected = []
        for col, var in prev_vars.items():
            if var.get():
                all_selected.append(col)
        for col, var in curr_vars.items():
            if var.get():
                all_selected.append(col)

        set_selected_optional_columns(all_selected)

        # Save auto-generated settings
        new_auto = {col: {"enabled": var.get()} for col, var in auto_vars.items()}
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
        font=("Arial", 11),
        bg="#757575",
        fg="white",
        width=12,
        cursor="hand2",
        command=back_to_settings
    ).pack(side=tk.LEFT, padx=10)

    tk.Button(
        button_frame,
        text="Apply & Save",
        font=("Arial", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        width=14,
        cursor="hand2",
        command=save_and_close
    ).pack(side=tk.LEFT, padx=10)


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
