"""
Main GUI window for VRS Manager.

This module provides the main application window with buttons for all VRS processes.
"""

import sys
import tkinter as tk
from tkinter import messagebox
import threading

from src.processors.raw_processor import RawProcessor
from src.processors.working_processor import WorkingProcessor
from src.processors.alllang_processor import AllLangProcessor
from src.processors.master_processor import MasterProcessor
from src.ui.history_viewer import show_update_history_viewer
from src.config import VERSION, VERSION_FOOTER, MANDATORY_COLUMNS, AUTO_GENERATED_COLUMNS, OPTIONAL_COLUMNS
from src.settings import (
    get_use_priority_change, set_use_priority_change,
    get_column_settings, set_column_settings, reset_column_settings
)


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
    Show settings dialog with Priority Change toggle.

    Args:
        parent: Parent window for the dialog
    """
    dialog = tk.Toplevel(parent)
    dialog.title("Settings")
    dialog.geometry("400x200")
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
        font=("Arial", 14, "bold"),
        bg=bg_color,
        fg="#333333"
    )
    title_label.pack(pady=(15, 10))

    # Priority Change toggle frame
    toggle_frame = tk.Frame(dialog, bg=bg_color)
    toggle_frame.pack(pady=10, padx=20, fill=tk.X)

    # Variable for checkbox
    use_priority_var = tk.BooleanVar(value=get_use_priority_change())

    # Checkbox
    priority_checkbox = tk.Checkbutton(
        toggle_frame,
        text="Use Priority Change Mode",
        variable=use_priority_var,
        font=("Arial", 11),
        bg=bg_color,
        activebackground=bg_color
    )
    priority_checkbox.pack(anchor=tk.W)

    # Description label
    desc_frame = tk.Frame(dialog, bg=bg_color)
    desc_frame.pack(pady=5, padx=25, fill=tk.X)

    desc_on = tk.Label(
        desc_frame,
        text="ON: CHANGES column shows priority-based label (newest)",
        font=("Arial", 9),
        bg=bg_color,
        fg="#006600"
    )
    desc_on.pack(anchor=tk.W)

    desc_off = tk.Label(
        desc_frame,
        text="OFF: CHANGES column shows full composite label (legacy)",
        font=("Arial", 9),
        bg=bg_color,
        fg="#666666"
    )
    desc_off.pack(anchor=tk.W)

    # Button frame
    button_frame = tk.Frame(dialog, bg=bg_color)
    button_frame.pack(pady=15)

    def save_and_close():
        set_use_priority_change(use_priority_var.get())
        messagebox.showinfo("Settings Saved", "Settings saved successfully!\n\nChanges will apply to future processing runs.")
        dialog.destroy()

    save_btn = tk.Button(
        button_frame,
        text="Save",
        font=("Arial", 10, "bold"),
        bg="#4CAF50",
        fg="white",
        width=10,
        cursor="hand2",
        command=save_and_close
    )
    save_btn.pack(side=tk.LEFT, padx=5)

    cancel_btn = tk.Button(
        button_frame,
        text="Cancel",
        font=("Arial", 10),
        bg="#757575",
        fg="white",
        width=10,
        cursor="hand2",
        command=dialog.destroy
    )
    cancel_btn.pack(side=tk.LEFT, padx=5)


# Auto-generated column help texts
AUTO_GENERATED_HELP = {
    "PreviousData": "Combined previous Text|STATUS|Freememo",
    "PreviousText": "Text value from matched previous row",
    "PreviousEventName": "Previous EventName when it changed",
    "DETAILED_CHANGES": "Full composite change type (all detected)",
    "Previous StrOrigin": "StrOrigin value from matched previous row",
    "Mainline Translation": "Original Text value before import logic"
}


def show_column_settings_dialog(parent):
    """
    Show column settings dialog for customizing output columns.

    Args:
        parent: Parent window for the dialog
    """
    dialog = tk.Toplevel(parent)
    dialog.title("Column Settings")
    dialog.geometry("550x700")
    dialog.resizable(False, True)
    dialog.transient(parent)
    dialog.grab_set()

    # Center dialog on parent
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

    bg_color = "#f0f0f0"
    dialog.configure(bg=bg_color)

    # Load current settings
    col_settings = get_column_settings()

    # Title
    title_label = tk.Label(
        dialog,
        text="Column Settings",
        font=("Arial", 14, "bold"),
        bg=bg_color,
        fg="#333333"
    )
    title_label.pack(pady=(15, 5))

    subtitle_label = tk.Label(
        dialog,
        text="Customize which columns appear in WORKING output (Work Transform sheet)",
        font=("Arial", 9),
        bg=bg_color,
        fg="#666666"
    )
    subtitle_label.pack(pady=(0, 10))

    # Create scrollable frame
    canvas = tk.Canvas(dialog, bg=bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg_color)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # ===== MANDATORY COLUMNS SECTION =====
    mandatory_frame = tk.LabelFrame(
        scrollable_frame,
        text=" MANDATORY COLUMNS (Always Shown) ",
        font=("Arial", 10, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=10,
        pady=5
    )
    mandatory_frame.pack(fill=tk.X, padx=15, pady=5)

    mandatory_inner = tk.Frame(mandatory_frame, bg=bg_color)
    mandatory_inner.pack(fill=tk.X)

    # Display mandatory columns in a grid (locked)
    for i, col in enumerate(MANDATORY_COLUMNS):
        row = i // 3
        col_idx = i % 3
        lbl = tk.Label(
            mandatory_inner,
            text=f"🔒 {col}",
            font=("Arial", 9),
            bg=bg_color,
            fg="#666666"
        )
        lbl.grid(row=row, column=col_idx, sticky="w", padx=5, pady=2)

    # ===== AUTO-GENERATED COLUMNS SECTION =====
    auto_frame = tk.LabelFrame(
        scrollable_frame,
        text=" AUTO-GENERATED COLUMNS ",
        font=("Arial", 10, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=10,
        pady=5
    )
    auto_frame.pack(fill=tk.X, padx=15, pady=5)

    # Store checkbox variables
    auto_vars = {}

    for col in AUTO_GENERATED_COLUMNS:
        row_frame = tk.Frame(auto_frame, bg=bg_color)
        row_frame.pack(fill=tk.X, pady=2)

        # Get current enabled state
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
            width=20,
            anchor="w"
        )
        cb.pack(side=tk.LEFT)

        # Help text
        help_text = AUTO_GENERATED_HELP.get(col, "")
        if help_text:
            help_lbl = tk.Label(
                row_frame,
                text=f"ⓘ {help_text}",
                font=("Arial", 8),
                bg=bg_color,
                fg="#888888"
            )
            help_lbl.pack(side=tk.LEFT, padx=5)

    # ===== OPTIONAL COLUMNS SECTION =====
    optional_frame = tk.LabelFrame(
        scrollable_frame,
        text=" OPTIONAL COLUMNS ",
        font=("Arial", 10, "bold"),
        bg=bg_color,
        fg="#333333",
        padx=10,
        pady=5
    )
    optional_frame.pack(fill=tk.X, padx=15, pady=5)

    # Header row
    header_frame = tk.Frame(optional_frame, bg=bg_color)
    header_frame.pack(fill=tk.X, pady=(0, 5))

    tk.Label(header_frame, text="Column", font=("Arial", 9, "bold"), bg=bg_color, width=18, anchor="w").pack(side=tk.LEFT)
    tk.Label(header_frame, text="Show", font=("Arial", 9, "bold"), bg=bg_color, width=6).pack(side=tk.LEFT)
    tk.Label(header_frame, text="Source", font=("Arial", 9, "bold"), bg=bg_color, width=20).pack(side=tk.LEFT)

    # Separator
    sep = tk.Frame(optional_frame, height=1, bg="#cccccc")
    sep.pack(fill=tk.X, pady=2)

    # Store optional column variables
    optional_vars = {}
    source_vars = {}

    for col in OPTIONAL_COLUMNS:
        row_frame = tk.Frame(optional_frame, bg=bg_color)
        row_frame.pack(fill=tk.X, pady=2)

        # Column name label
        col_lbl = tk.Label(
            row_frame,
            text=col,
            font=("Arial", 9),
            bg=bg_color,
            width=18,
            anchor="w"
        )
        col_lbl.pack(side=tk.LEFT)

        # Get current settings
        col_cfg = col_settings.get("optional", {}).get(col, {"enabled": True, "source": "CURRENT"})
        enabled = col_cfg.get("enabled", True)
        source = col_cfg.get("source", "CURRENT")

        # Checkbox for enabled
        var = tk.BooleanVar(value=enabled)
        optional_vars[col] = var

        cb = tk.Checkbutton(
            row_frame,
            variable=var,
            bg=bg_color,
            activebackground=bg_color,
            width=4
        )
        cb.pack(side=tk.LEFT)

        # Radio buttons for source
        source_var = tk.StringVar(value=source)
        source_vars[col] = source_var

        source_frame = tk.Frame(row_frame, bg=bg_color)
        source_frame.pack(side=tk.LEFT)

        rb_current = tk.Radiobutton(
            source_frame,
            text="CURRENT",
            variable=source_var,
            value="CURRENT",
            font=("Arial", 8),
            bg=bg_color,
            activebackground=bg_color
        )
        rb_current.pack(side=tk.LEFT)

        rb_previous = tk.Radiobutton(
            source_frame,
            text="PREVIOUS",
            variable=source_var,
            value="PREVIOUS",
            font=("Arial", 8),
            bg=bg_color,
            activebackground=bg_color
        )
        rb_previous.pack(side=tk.LEFT)

    # Pack canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15), pady=5)

    # Enable mouse wheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # ===== BUTTON FRAME =====
    button_frame = tk.Frame(dialog, bg=bg_color)
    button_frame.pack(pady=15)

    def reset_to_defaults():
        """Reset all settings to defaults."""
        # Reset auto-generated
        for col, var in auto_vars.items():
            var.set(True)

        # Reset optional
        for col, var in optional_vars.items():
            var.set(True)
        for col, var in source_vars.items():
            var.set("CURRENT")

    def save_and_close():
        """Save settings and close dialog."""
        # Build new settings
        new_settings = {
            "auto_generated": {},
            "optional": {}
        }

        for col, var in auto_vars.items():
            new_settings["auto_generated"][col] = {"enabled": var.get()}

        for col, var in optional_vars.items():
            new_settings["optional"][col] = {
                "enabled": var.get(),
                "source": source_vars[col].get()
            }

        set_column_settings(new_settings)
        canvas.unbind_all("<MouseWheel>")
        messagebox.showinfo(
            "Settings Saved",
            "Column settings saved successfully!\n\nChanges will apply to future Working Process runs."
        )
        dialog.destroy()

    def cancel_dialog():
        """Cancel and close dialog."""
        canvas.unbind_all("<MouseWheel>")
        dialog.destroy()

    reset_btn = tk.Button(
        button_frame,
        text="Reset to Defaults",
        font=("Arial", 10),
        bg="#FF9800",
        fg="white",
        width=15,
        cursor="hand2",
        command=reset_to_defaults
    )
    reset_btn.pack(side=tk.LEFT, padx=5)

    cancel_btn = tk.Button(
        button_frame,
        text="Cancel",
        font=("Arial", 10),
        bg="#757575",
        fg="white",
        width=10,
        cursor="hand2",
        command=cancel_dialog
    )
    cancel_btn.pack(side=tk.LEFT, padx=5)

    save_btn = tk.Button(
        button_frame,
        text="Apply & Save",
        font=("Arial", 10, "bold"),
        bg="#4CAF50",
        fg="white",
        width=12,
        cursor="hand2",
        command=save_and_close
    )
    save_btn.pack(side=tk.LEFT, padx=5)


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

    # Column Settings button
    btn_columns = tk.Button(
        button_frame,
        text="📋 Column Settings",
        font=("Arial", 11, "bold"),
        bg="#009688",
        fg="white",
        width=42,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2",
        command=lambda: show_column_settings_dialog(window)
    )
    btn_columns.pack(pady=8)

    desc_columns = tk.Label(
        button_frame,
        text="Customize output columns for Working Process",
        font=("Arial", 9, "italic"),
        bg=bg_color,
        fg="#666666"
    )
    desc_columns.pack()

    # Settings button
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
