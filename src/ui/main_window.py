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
from src.config import VERSION, VERSION_FOOTER


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
