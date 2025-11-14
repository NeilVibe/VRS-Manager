"""
Update history viewer for VRS Manager.

This module provides a GUI window to view, manage, and delete update history
for all VRS processes (Working, AllLang, Master).
"""

import tkinter as tk
from tkinter import messagebox, simpledialog

from src.history.history_manager import (
    load_update_history,
    clear_update_history,
    delete_specific_update
)


def show_update_history_viewer():
    """Display the update history viewer window."""
    viewer = tk.Toplevel()
    viewer.title("Update History Viewer")
    viewer.geometry("900x700")

    control_frame = tk.Frame(viewer, bg="#f0f0f0", pady=10)
    control_frame.pack(fill=tk.X)

    tk.Label(control_frame, text="Select Process:", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)

    process_var = tk.StringVar(value="master")

    def refresh_history():
        """Refresh the history display based on selected process."""
        process_type = process_var.get()
        history = load_update_history(process_type)

        text_widget.delete(1.0, tk.END)

        if not history["updates"]:
            text_widget.insert(tk.END, f"No {process_type.upper()} process updates recorded yet.\n\n")
            text_widget.insert(tk.END, f"Updates will appear here after you run the {process_type.upper()} process.")
            return

        process_name = "MASTER FILE UPDATE" if process_type == "master" else ("ALL LANGUAGE PROCESS" if process_type == "alllang" else "WORKING PROCESS")
        text_widget.insert(tk.END, "═" * 100 + "\n", "header")
        text_widget.insert(tk.END, f"   {process_name} - UPDATE HISTORY\n", "header")
        text_widget.insert(tk.END, "═" * 100 + "\n", "header")
        text_widget.insert(tk.END, f"\n   Total Updates: {len(history['updates'])}\n\n", "subheader")

        for idx, update in enumerate(reversed(history["updates"]), 1):
            actual_idx = len(history["updates"]) - idx

            text_widget.insert(tk.END, "─" * 100 + "\n", "divider")
            text_widget.insert(tk.END, f"UPDATE #{idx}", "update_num")
            text_widget.insert(tk.END, f" (Index: {actual_idx})\n", "small")
            text_widget.insert(tk.END, "─" * 100 + "\n", "divider")

            text_widget.insert(tk.END, f"📅 Timestamp: ", "label")
            text_widget.insert(tk.END, f"{update['timestamp']}\n", "value")

            text_widget.insert(tk.END, f"📄 Output File: ", "label")
            text_widget.insert(tk.END, f"{update['output_file']}\n\n", "value")

            if process_type == "alllang":
                text_widget.insert(tk.END, "🌐 LANGUAGES UPDATED:\n", "section")
                for lang in ["KR", "EN", "CN"]:
                    status = "✓ UPDATED" if update["languages_updated"][lang] else "○ Preserved"
                    color_tag = "updated" if update["languages_updated"][lang] else "preserved"
                    previous = update["previous_files"][lang] if update["previous_files"][lang] else "N/A"
                    text_widget.insert(tk.END, f"   {lang}: ", "label")
                    text_widget.insert(tk.END, f"{status}", color_tag)
                    text_widget.insert(tk.END, f" | Previous: {previous}\n", "small")

                text_widget.insert(tk.END, "\n📁 CURRENT FILES (Complete Base):\n", "section")
                for lang in ["KR", "EN", "CN"]:
                    text_widget.insert(tk.END, f"   {lang}: ", "label")
                    text_widget.insert(tk.END, f"{update['current_files'][lang]}\n", "value")

            elif process_type == "master":
                text_widget.insert(tk.END, "📁 FILES:\n", "section")
                text_widget.insert(tk.END, f"   Source: ", "label")
                text_widget.insert(tk.END, f"{update['source_file']}\n", "value")
                text_widget.insert(tk.END, f"   Target: ", "label")
                text_widget.insert(tk.END, f"{update['target_file']}\n", "value")

            else:
                text_widget.insert(tk.END, "📁 FILES:\n", "section")
                text_widget.insert(tk.END, f"   Previous: ", "label")
                text_widget.insert(tk.END, f"{update['previous_file']}\n", "value")
                text_widget.insert(tk.END, f"   Current: ", "label")
                text_widget.insert(tk.END, f"{update['current_file']}\n", "value")

            text_widget.insert(tk.END, "\n📊 STATISTICS:\n", "section")
            stats = update["statistics"]
            text_widget.insert(tk.END, f"   Total Rows: ", "label")
            text_widget.insert(tk.END, f"{stats['total_rows']:,}\n", "value")

            text_widget.insert(tk.END, "\n   Change Breakdown:\n", "subsection")
            for key, value in stats.items():
                if key != "total_rows":
                    text_widget.insert(tk.END, f"      • {key}: ", "change_label")
                    text_widget.insert(tk.END, f"{value:,}\n", "change_value")

            text_widget.insert(tk.END, "\n")

        text_widget.insert(tk.END, "═" * 100 + "\n", "header")
        text_widget.insert(tk.END, f"   End of History ({len(history['updates'])} total updates)\n", "footer")
        text_widget.insert(tk.END, "═" * 100 + "\n", "header")

    def on_process_change():
        """Handle process selection change."""
        refresh_history()

    # Radio buttons for process selection
    tk.Radiobutton(control_frame, text="Master File Update", variable=process_var, value="master",
                   command=on_process_change, font=("Arial", 10), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(control_frame, text="All Language Process", variable=process_var, value="alllang",
                   command=on_process_change, font=("Arial", 10), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(control_frame, text="Working Process", variable=process_var, value="working",
                   command=on_process_change, font=("Arial", 10), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)

    # Refresh button
    tk.Button(control_frame, text="🔄 Refresh", command=refresh_history,
              font=("Arial", 9), bg="#4CAF50", fg="white", padx=10).pack(side=tk.LEFT, padx=20)

    def clear_current_history():
        """Clear history for current process type."""
        process_type = process_var.get()
        if clear_update_history(process_type):
            refresh_history()

    # Clear history button
    tk.Button(control_frame, text="🗑️ Clear History", command=clear_current_history,
              font=("Arial", 9), bg="#f44336", fg="white", padx=10).pack(side=tk.LEFT, padx=5)

    def delete_update():
        """Delete a specific update by index."""
        process_type = process_var.get()
        index_str = simpledialog.askstring("Delete Update",
                                            "Enter the index number of the update to delete:")
        if index_str:
            try:
                index = int(index_str)
                success, deleted = delete_specific_update(index, process_type)
                if success:
                    messagebox.showinfo("Success", f"Update #{index} deleted successfully!")
                    refresh_history()
                else:
                    messagebox.showerror("Error", f"Invalid index: {index}")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")

    # Delete update button
    tk.Button(control_frame, text="🗑️ Delete Update", command=delete_update,
              font=("Arial", 9), bg="#FF9800", fg="white", padx=10).pack(side=tk.LEFT, padx=5)

    # Text frame with scrollbar
    text_frame = tk.Frame(viewer)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                         font=("Courier New", 9), bg="#ffffff", fg="#000000")
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)

    # Configure text tags for styling
    text_widget.tag_config("header", foreground="#000080", font=("Courier New", 10, "bold"))
    text_widget.tag_config("subheader", foreground="#0066cc", font=("Courier New", 9, "bold"))
    text_widget.tag_config("update_num", foreground="#006600", font=("Courier New", 10, "bold"))
    text_widget.tag_config("divider", foreground="#999999")
    text_widget.tag_config("label", foreground="#000000", font=("Courier New", 9, "bold"))
    text_widget.tag_config("value", foreground="#0066cc")
    text_widget.tag_config("section", foreground="#cc6600", font=("Courier New", 9, "bold"))
    text_widget.tag_config("subsection", foreground="#666666", font=("Courier New", 9, "bold"))
    text_widget.tag_config("small", foreground="#666666", font=("Courier New", 8))
    text_widget.tag_config("updated", foreground="#006600", font=("Courier New", 9, "bold"))
    text_widget.tag_config("preserved", foreground="#999999", font=("Courier New", 9))
    text_widget.tag_config("change_label", foreground="#333333")
    text_widget.tag_config("change_value", foreground="#0066cc", font=("Courier New", 9, "bold"))
    text_widget.tag_config("footer", foreground="#666666", font=("Courier New", 9, "italic"))

    # Initial load
    refresh_history()
