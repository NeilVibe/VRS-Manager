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
from src.config import VERSION, VERSION_FOOTER, MANDATORY_COLUMNS, AUTO_GENERATED_COLUMNS, OPTIONAL_COLUMNS, VRS_CONDITIONAL_COLUMNS
from src.settings import (
    get_use_priority_change, set_use_priority_change,
    get_column_settings, set_column_settings, reset_column_settings,
    get_analyzed_columns, set_analyzed_columns,
    get_selected_optional_columns, set_selected_optional_columns,
    # V3: Dual-file column analysis
    get_previous_file_columns, get_current_file_columns,
    set_file_info, get_dual_file_status, clear_file_columns,
    # V5: Dual-file column selection
    get_v5_column_settings, set_v5_auto_generated,
    set_v5_current_file, set_v5_previous_file, reset_v5_all
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
    dialog.geometry("600x550")  # Taller to fit Back/Save buttons
    dialog.minsize(550, 500)
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
    button_frame.pack(pady=(30, 40))  # More padding at bottom

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
    Show Column Settings dialog with V5 layout.

    Sections:
    1. FIXED COLUMNS - Compact display of MANDATORY + VRS_CONDITIONAL
    2. AUTO-GENERATED - Horizontal checkboxes, toggleable
    3. OPTIONAL - Dual upload boxes for CURRENT and PREVIOUS files

    Args:
        parent: Parent window for the dialog
    """
    dialog = tk.Toplevel(parent)
    dialog.title("Column Settings")
    dialog.geometry("950x850")
    dialog.minsize(850, 750)
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
    FIXED_COLOR = "#37474F"       # Dark gray
    AUTO_GEN_COLOR = "#7B1FA2"    # Purple
    CURRENT_COLOR = "#2E7D32"     # Green
    PREVIOUS_COLOR = "#1565C0"    # Blue

    # Load V5 settings
    v5_settings = get_v5_column_settings()

    # ===== TITLE =====
    tk.Label(
        dialog,
        text="Column Settings",
        font=("Arial", 16, "bold"),
        bg=bg_color,
        fg="#333333"
    ).pack(pady=(15, 5))

    tk.Label(
        dialog,
        text="Configure which columns appear in WORKING process output",
        font=("Arial", 10),
        bg=bg_color,
        fg="#666666"
    ).pack(pady=(0, 10))

    # ===== SECTION 1: FIXED COLUMNS (Compact) =====
    fixed_frame = tk.LabelFrame(
        dialog,
        text=" FIXED COLUMNS (Always Included) ",
        font=("Arial", 11, "bold"),
        bg=bg_color,
        fg=FIXED_COLOR,
        padx=15,
        pady=8
    )
    fixed_frame.pack(fill=tk.X, padx=20, pady=(5, 10))

    # Full column list display
    mandatory_text = ", ".join(MANDATORY_COLUMNS)
    vrs_cond_text = ", ".join(VRS_CONDITIONAL_COLUMNS)

    tk.Label(
        fixed_frame,
        text=f"✓ MANDATORY ({len(MANDATORY_COLUMNS)}): {mandatory_text}",
        font=("Arial", 9),
        bg=bg_color,
        fg="#1B5E20",
        wraplength=880,
        justify=tk.LEFT
    ).pack(anchor=tk.W, pady=2)

    tk.Label(
        fixed_frame,
        text=f"✓ VRS CONDITIONAL ({len(VRS_CONDITIONAL_COLUMNS)}): {vrs_cond_text}",
        font=("Arial", 9),
        bg=bg_color,
        fg="#1565C0",
        wraplength=880,
        justify=tk.LEFT
    ).pack(anchor=tk.W, pady=2)

    # ===== SECTION 2: AUTO-GENERATED COLUMNS (Horizontal) =====
    auto_gen_vars = {}

    auto_frame = tk.LabelFrame(
        dialog,
        text=" AUTO-GENERATED COLUMNS (Toggle ON/OFF) ",
        font=("Arial", 11, "bold"),
        bg=bg_color,
        fg=AUTO_GEN_COLOR,
        padx=15,
        pady=8
    )
    auto_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    # Horizontal row of checkboxes
    auto_row = tk.Frame(auto_frame, bg=bg_color)
    auto_row.pack(fill=tk.X, pady=5)

    for col in AUTO_GENERATED_COLUMNS:
        is_enabled = v5_settings["auto_generated"].get(col, True)
        var = tk.BooleanVar(value=is_enabled)
        auto_gen_vars[col] = var

        cb = tk.Checkbutton(
            auto_row,
            text=col,
            variable=var,
            font=("Arial", 9),
            bg=bg_color,
            activebackground=bg_color,
            selectcolor="white"
        )
        cb.pack(side=tk.LEFT, padx=8)

    # ===== SECTION 3: OPTIONAL COLUMNS (Dual Upload) =====
    optional_frame = tk.LabelFrame(
        dialog,
        text=" OPTIONAL COLUMNS ",
        font=("Arial", 11, "bold"),
        bg=bg_color,
        fg="#E65100",
        padx=15,
        pady=10
    )
    optional_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

    # RESET ALL button at top right
    reset_row = tk.Frame(optional_frame, bg=bg_color)
    reset_row.pack(fill=tk.X, pady=(0, 10))

    def do_reset_all():
        if messagebox.askyesno("Reset All", "Reset all column settings?\n\nThis will clear uploaded files and reset auto-generated columns to defaults."):
            reset_v5_all()
            dialog.destroy()
            show_column_settings_dialog_v2(parent)

    tk.Button(
        reset_row,
        text="RESET ALL",
        font=("Arial", 9, "bold"),
        bg="#FF5722",
        fg="white",
        cursor="hand2",
        command=do_reset_all
    ).pack(side=tk.RIGHT)

    tk.Label(
        reset_row,
        text="Upload files to see available columns",
        font=("Arial", 9),
        bg=bg_color,
        fg="#666666"
    ).pack(side=tk.LEFT)

    # ===== DUAL UPLOAD BOXES =====
    boxes_frame = tk.Frame(optional_frame, bg=bg_color)
    boxes_frame.pack(fill=tk.BOTH, expand=True)

    # Configure grid weights for equal sizing
    boxes_frame.columnconfigure(0, weight=1)
    boxes_frame.columnconfigure(1, weight=1)
    boxes_frame.rowconfigure(0, weight=1)

    # Track checkbox variables
    current_vars = {}
    previous_vars = {}

    # === CURRENT FILE BOX ===
    current_box = tk.LabelFrame(
        boxes_frame,
        text=" FROM CURRENT FILE ",
        font=("Arial", 10, "bold"),
        bg="#E8F5E9",  # Light green
        fg=CURRENT_COLOR,
        padx=10,
        pady=10
    )
    current_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

    current_content = tk.Frame(current_box, bg="#E8F5E9")
    current_content.pack(fill=tk.BOTH, expand=True)

    # Current file status label
    current_status = tk.Label(
        current_content,
        text="",
        font=("Arial", 9),
        bg="#E8F5E9",
        fg=CURRENT_COLOR
    )
    current_status.pack(anchor=tk.W, pady=(0, 5))

    # Current scrollable area for checkboxes
    current_canvas = tk.Canvas(current_content, bg="#E8F5E9", highlightthickness=0, height=200)
    current_scrollbar = tk.Scrollbar(current_content, orient="vertical", command=current_canvas.yview)
    current_checkbox_frame = tk.Frame(current_canvas, bg="#E8F5E9")

    current_checkbox_frame.bind(
        "<Configure>",
        lambda e: current_canvas.configure(scrollregion=current_canvas.bbox("all"))
    )

    current_canvas.create_window((0, 0), window=current_checkbox_frame, anchor="nw")
    current_canvas.configure(yscrollcommand=current_scrollbar.set)

    # Current buttons frame
    current_buttons = tk.Frame(current_content, bg="#E8F5E9")
    current_buttons.pack(fill=tk.X, pady=(5, 0))

    def populate_current_checkboxes(columns, selected):
        """Populate current file checkboxes."""
        for widget in current_checkbox_frame.winfo_children():
            widget.destroy()
        current_vars.clear()

        if not columns:
            tk.Label(
                current_checkbox_frame,
                text="Upload a file to see columns",
                font=("Arial", 9, "italic"),
                bg="#E8F5E9",
                fg="#666666"
            ).pack(pady=20)
            return

        for col in sorted(columns):
            var = tk.BooleanVar(value=col in selected)
            current_vars[col] = var
            cb = tk.Checkbutton(
                current_checkbox_frame,
                text=col,
                variable=var,
                font=("Arial", 9),
                bg="#E8F5E9",
                activebackground="#E8F5E9",
                selectcolor="white"
            )
            cb.pack(anchor=tk.W, pady=1)

    def upload_current_file():
        """Handle current file upload with threading (no UI freeze)."""
        file_path = filedialog.askopenfilename(
            title="Select CURRENT Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        # Show progress in status label
        filename = os.path.basename(file_path)
        current_status.config(text=f"⏳ Analyzing {filename}...", fg="#FF9800")
        dialog.update()

        def analyze_in_thread():
            """Run analysis in background thread."""
            columns, fname, error = analyze_excel_columns(file_path)

            # Schedule UI update on main thread
            def update_ui():
                if error:
                    current_status.config(text=f"❌ Error: {error[:30]}...", fg="#F44336")
                    messagebox.showerror("Error", f"Failed to analyze file:\n{error}")
                    return

                # Filter to only optional columns
                excluded = set(MANDATORY_COLUMNS) | set(VRS_CONDITIONAL_COLUMNS) | set(AUTO_GENERATED_COLUMNS)
                optional_cols = [c for c in columns if c not in excluded]

                current_status.config(
                    text=f"✓ {fname} ({len(optional_cols)} optional columns)",
                    fg=CURRENT_COLOR
                )
                populate_current_checkboxes(optional_cols, optional_cols)  # All selected by default

                # Show canvas and scrollbar
                current_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                current_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                # Store in temp for saving later
                dialog.current_file_data = {"filename": fname, "columns": optional_cols}

            dialog.after(0, update_ui)

        # Run in background thread
        thread = threading.Thread(target=analyze_in_thread, daemon=True)
        thread.start()

    def select_all_current():
        for var in current_vars.values():
            var.set(True)

    def select_none_current():
        for var in current_vars.values():
            var.set(False)

    # Initial state - show upload button or loaded data
    current_file_info = v5_settings["current_file"]
    if current_file_info.get("filename"):
        current_status.config(text=f"✓ {current_file_info['filename']} ({len(current_file_info['columns'])} optional columns)")
        populate_current_checkboxes(current_file_info["columns"], current_file_info.get("selected", []))
        current_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        current_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        dialog.current_file_data = current_file_info
    else:
        # Empty state - just upload button
        tk.Label(
            current_checkbox_frame,
            text="",
            bg="#E8F5E9"
        ).pack(pady=30)

        upload_btn_current = tk.Button(
            current_checkbox_frame,
            text="📂 Upload File",
            font=("Arial", 10),
            bg=CURRENT_COLOR,
            fg="white",
            cursor="hand2",
            command=upload_current_file
        )
        upload_btn_current.pack(pady=10)

        tk.Label(
            current_checkbox_frame,
            text="Upload to see available columns",
            font=("Arial", 9, "italic"),
            bg="#E8F5E9",
            fg="#666666"
        ).pack()

        current_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dialog.current_file_data = None

    # Current action buttons
    tk.Button(
        current_buttons,
        text="Upload",
        font=("Arial", 9),
        bg=CURRENT_COLOR,
        fg="white",
        cursor="hand2",
        command=upload_current_file
    ).pack(side=tk.LEFT, padx=2)

    tk.Button(
        current_buttons,
        text="All",
        font=("Arial", 9),
        cursor="hand2",
        command=select_all_current
    ).pack(side=tk.LEFT, padx=2)

    tk.Button(
        current_buttons,
        text="None",
        font=("Arial", 9),
        cursor="hand2",
        command=select_none_current
    ).pack(side=tk.LEFT, padx=2)

    # === PREVIOUS FILE BOX ===
    previous_box = tk.LabelFrame(
        boxes_frame,
        text=" FROM PREVIOUS FILE ",
        font=("Arial", 10, "bold"),
        bg="#E3F2FD",  # Light blue
        fg=PREVIOUS_COLOR,
        padx=10,
        pady=10
    )
    previous_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

    previous_content = tk.Frame(previous_box, bg="#E3F2FD")
    previous_content.pack(fill=tk.BOTH, expand=True)

    # Previous file status label
    previous_status = tk.Label(
        previous_content,
        text="",
        font=("Arial", 9),
        bg="#E3F2FD",
        fg=PREVIOUS_COLOR
    )
    previous_status.pack(anchor=tk.W, pady=(0, 5))

    # Previous scrollable area for checkboxes
    previous_canvas = tk.Canvas(previous_content, bg="#E3F2FD", highlightthickness=0, height=200)
    previous_scrollbar = tk.Scrollbar(previous_content, orient="vertical", command=previous_canvas.yview)
    previous_checkbox_frame = tk.Frame(previous_canvas, bg="#E3F2FD")

    previous_checkbox_frame.bind(
        "<Configure>",
        lambda e: previous_canvas.configure(scrollregion=previous_canvas.bbox("all"))
    )

    previous_canvas.create_window((0, 0), window=previous_checkbox_frame, anchor="nw")
    previous_canvas.configure(yscrollcommand=previous_scrollbar.set)

    # Previous buttons frame
    previous_buttons = tk.Frame(previous_content, bg="#E3F2FD")
    previous_buttons.pack(fill=tk.X, pady=(5, 0))

    def populate_previous_checkboxes(columns, selected):
        """Populate previous file checkboxes (no prefix - just column names)."""
        for widget in previous_checkbox_frame.winfo_children():
            widget.destroy()
        previous_vars.clear()

        if not columns:
            tk.Label(
                previous_checkbox_frame,
                text="Upload a file to see columns",
                font=("Arial", 9, "italic"),
                bg="#E3F2FD",
                fg="#666666"
            ).pack(pady=20)
            return

        for col in sorted(columns):
            var = tk.BooleanVar(value=col in selected)
            previous_vars[col] = var
            cb = tk.Checkbutton(
                previous_checkbox_frame,
                text=col,  # No prefix - user sees original column name
                variable=var,
                font=("Arial", 9),
                bg="#E3F2FD",
                activebackground="#E3F2FD",
                selectcolor="white"
            )
            cb.pack(anchor=tk.W, pady=1)

    def upload_previous_file():
        """Handle previous file upload with threading (no UI freeze)."""
        file_path = filedialog.askopenfilename(
            title="Select PREVIOUS Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        # Show progress in status label
        filename = os.path.basename(file_path)
        previous_status.config(text=f"⏳ Analyzing {filename}...", fg="#FF9800")
        dialog.update()

        def analyze_in_thread():
            """Run analysis in background thread."""
            columns, fname, error = analyze_excel_columns(file_path)

            # Schedule UI update on main thread
            def update_ui():
                if error:
                    previous_status.config(text=f"❌ Error: {error[:30]}...", fg="#F44336")
                    messagebox.showerror("Error", f"Failed to analyze file:\n{error}")
                    return

                # Filter to only optional columns
                excluded = set(MANDATORY_COLUMNS) | set(VRS_CONDITIONAL_COLUMNS) | set(AUTO_GENERATED_COLUMNS)
                optional_cols = [c for c in columns if c not in excluded]

                previous_status.config(
                    text=f"✓ {fname} ({len(optional_cols)} optional columns)",
                    fg=PREVIOUS_COLOR
                )
                populate_previous_checkboxes(optional_cols, [])  # None selected by default

                # Show canvas and scrollbar
                previous_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                previous_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                # Store in temp for saving later
                dialog.previous_file_data = {"filename": fname, "columns": optional_cols}

            dialog.after(0, update_ui)

        # Run in background thread
        thread = threading.Thread(target=analyze_in_thread, daemon=True)
        thread.start()

    def select_all_previous():
        for var in previous_vars.values():
            var.set(True)

    def select_none_previous():
        for var in previous_vars.values():
            var.set(False)

    # Initial state - show upload button or loaded data
    previous_file_info = v5_settings["previous_file"]
    if previous_file_info.get("filename"):
        previous_status.config(text=f"✓ {previous_file_info['filename']} ({len(previous_file_info['columns'])} optional columns)")
        populate_previous_checkboxes(previous_file_info["columns"], previous_file_info.get("selected", []))
        previous_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        previous_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        dialog.previous_file_data = previous_file_info
    else:
        # Empty state - just upload button
        tk.Label(
            previous_checkbox_frame,
            text="",
            bg="#E3F2FD"
        ).pack(pady=30)

        upload_btn_previous = tk.Button(
            previous_checkbox_frame,
            text="📂 Upload File",
            font=("Arial", 10),
            bg=PREVIOUS_COLOR,
            fg="white",
            cursor="hand2",
            command=upload_previous_file
        )
        upload_btn_previous.pack(pady=10)

        tk.Label(
            previous_checkbox_frame,
            text="Upload to see available columns",
            font=("Arial", 9, "italic"),
            bg="#E3F2FD",
            fg="#666666"
        ).pack()

        previous_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dialog.previous_file_data = None

    # Previous action buttons
    tk.Button(
        previous_buttons,
        text="Upload",
        font=("Arial", 9),
        bg=PREVIOUS_COLOR,
        fg="white",
        cursor="hand2",
        command=upload_previous_file
    ).pack(side=tk.LEFT, padx=2)

    tk.Button(
        previous_buttons,
        text="All",
        font=("Arial", 9),
        cursor="hand2",
        command=select_all_previous
    ).pack(side=tk.LEFT, padx=2)

    tk.Button(
        previous_buttons,
        text="None",
        font=("Arial", 9),
        cursor="hand2",
        command=select_none_previous
    ).pack(side=tk.LEFT, padx=2)

    # ===== INFO NOTE =====
    tk.Label(
        optional_frame,
        text="ℹ️ PREVIOUS file columns are matched by KEY (Seq+Event+StrOrigin+CastingKey). Output will show as 'Previous_ColumnName'. Rows that only exist in CURRENT (no match in PREVIOUS) will have empty values.",
        font=("Arial", 9),
        bg=bg_color,
        fg="#666666",
        wraplength=850
    ).pack(anchor=tk.W, pady=(10, 0))

    # ===== BUTTONS =====
    button_frame = tk.Frame(dialog, bg=bg_color)
    button_frame.pack(pady=(15, 20))

    def save_and_close():
        # Save auto-generated settings
        new_auto_gen = {col: var.get() for col, var in auto_gen_vars.items()}
        set_v5_auto_generated(new_auto_gen)

        # Save current file settings
        if hasattr(dialog, 'current_file_data') and dialog.current_file_data:
            selected_current = [col for col, var in current_vars.items() if var.get()]
            set_v5_current_file(
                dialog.current_file_data["filename"],
                dialog.current_file_data["columns"],
                selected_current
            )

        # Save previous file settings
        if hasattr(dialog, 'previous_file_data') and dialog.previous_file_data:
            selected_previous = [col for col, var in previous_vars.items() if var.get()]
            set_v5_previous_file(
                dialog.previous_file_data["filename"],
                dialog.previous_file_data["columns"],
                selected_previous
            )

        messagebox.showinfo("Saved", "Column settings saved successfully!")
        dialog.destroy()

    def back_to_settings():
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
    ).pack(side=tk.LEFT, padx=8)

    tk.Button(
        button_frame,
        text="Save",
        font=("Arial", 10, "bold"),
        bg="#4CAF50",
        fg="white",
        width=10,
        cursor="hand2",
        command=save_and_close
    ).pack(side=tk.LEFT, padx=8)




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
