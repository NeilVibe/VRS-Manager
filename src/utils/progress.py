"""
Progress bar utilities for VRS Manager
"""


def print_progress(current, total, label="Progress"):
    """Print a progress bar to console"""
    pct = int((current / total) * 100)
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r   {label}: {bar} {pct}%", end="", flush=True)


def finalize_progress():
    """Finalize progress bar (print newline)"""
    print()
