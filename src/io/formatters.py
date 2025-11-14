"""
Excel formatting module.

This module provides functionality to apply colors, styles, and formatting
to Excel worksheets for VRS Manager output files.
"""

from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

from src.config import CHAR_GROUP_COLS


def generate_color_for_value(value):
    """
    Generate a consistent color for a given value using hashing.

    Args:
        value: Any value to generate a color for

    Returns:
        str: Hex color code (without #)
    """
    fallback_colors = [
        "FFB3BA", "BAFFC9", "BAE1FF", "FFFFBA", "FFD9BA",
        "E0BBE4", "FFDFD3", "D4F1F4", "C9E4DE", "F7D9C4",
    ]
    hash_val = hash(str(value))
    return fallback_colors[hash_val % len(fallback_colors)]


def apply_direct_coloring(ws, is_master=False, changed_columns_map=None):
    """
    Apply direct coloring to worksheet cells based on change types and status values.

    This function colors:
    - Header row
    - CHANGES column based on change type
    - STATUS columns based on status value
    - Character group columns when they've changed

    Args:
        ws: openpyxl worksheet to format
        is_master: If True, looks for STATUS_KR/EN/CN columns (default: False)
        changed_columns_map: Dictionary mapping row indices to lists of changed column names
    """
    changes_col_idx = None
    status_col_indices = {}
    char_group_col_indices = {}

    for idx, cell in enumerate(ws[1], start=1):
        if cell.value == "CHANGES":
            changes_col_idx = idx
        elif is_master:
            if cell.value in ["STATUS_KR", "STATUS_EN", "STATUS_CN"]:
                status_col_indices[cell.value] = idx
        else:
            if cell.value and cell.value.upper() == "STATUS":
                status_col_indices["STATUS"] = idx

        if cell.value in CHAR_GROUP_COLS:
            char_group_col_indices[cell.value] = idx

    changes_fills = {
        "StrOrigin Change": PatternFill(start_color="FFD580", fill_type="solid"),
        "Desc Change": PatternFill(start_color="E1D5FF", fill_type="solid"),
        "TimeFrame Change": PatternFill(start_color="FF9999", fill_type="solid"),
        "EventName Change": PatternFill(start_color="FFFF99", fill_type="solid"),
        "SequenceName Change": PatternFill(start_color="B3E5FC", fill_type="solid"),
        "StrOrigin+Desc Change": PatternFill(start_color="FFA07A", fill_type="solid"),
        "StrOrigin+TimeFrame Change": PatternFill(start_color="FFB6C1", fill_type="solid"),
        "Desc+TimeFrame Change": PatternFill(start_color="DDA0DD", fill_type="solid"),
        "StrOrigin+Desc+TimeFrame Change": PatternFill(start_color="F08080", fill_type="solid"),
        "EventName+Desc Change": PatternFill(start_color="F0E68C", fill_type="solid"),
        "EventName+TimeFrame Change": PatternFill(start_color="FFDAB9", fill_type="solid"),
        "EventName+Desc+TimeFrame Change": PatternFill(start_color="FFD8A8", fill_type="solid"),
        "Character Group Change": PatternFill(start_color="87CEFA", fill_type="solid"),
        "New Row": PatternFill(start_color="90EE90", fill_type="solid"),
        "No Relevant Change": PatternFill(start_color="D3D3D3", fill_type="solid"),
        "No Change": PatternFill(start_color="E8E8E8", fill_type="solid"),
    }

    char_group_change_fill = PatternFill(start_color="FFD700", fill_type="solid")

    status_fills = {
        "RECORDED": PatternFill(start_color="90EE90", fill_type="solid"),
        "POLISHED": PatternFill(start_color="E6D5FF", fill_type="solid"),
        "RE-RECORD": PatternFill(start_color="FFB3B3", fill_type="solid"),
        "RERECORD": PatternFill(start_color="FFB3B3", fill_type="solid"),
        "RE-RECORDED": PatternFill(start_color="C5E8C5", fill_type="solid"),
        "RERECORDED": PatternFill(start_color="C5E8C5", fill_type="solid"),
        "PREVIOUSLY RECORDED": PatternFill(start_color="FFFFE0", fill_type="solid"),
        "FINAL": PatternFill(start_color="87CEEB", fill_type="solid"),
        "SHIPPED": PatternFill(start_color="87CEEB", fill_type="solid"),
        "SPEC-OUT": PatternFill(start_color="FFC0CB", fill_type="solid"),
        "CHECK": PatternFill(start_color="FFE4B5", fill_type="solid"),
        "NEED CHECK": PatternFill(start_color="FFB3B3", fill_type="solid"),
        "전달 완료": PatternFill(start_color="FFFFE0", fill_type="solid"),
        "녹음 완료": PatternFill(start_color="90EE90", fill_type="solid"),
        "재녹음 필요": PatternFill(start_color="FFB3B3", fill_type="solid"),
        "재녹음 완료": PatternFill(start_color="C5E8C5", fill_type="solid"),
        "준비 중": PatternFill(start_color="E6D5FF", fill_type="solid"),
        "확인 필요": PatternFill(start_color="FFE4B5", fill_type="solid"),
        "已传达": PatternFill(start_color="FFFFE0", fill_type="solid"),
        "已录音": PatternFill(start_color="90EE90", fill_type="solid"),
        "需补录": PatternFill(start_color="FFB3B3", fill_type="solid"),
        "已补录": PatternFill(start_color="C5E8C5", fill_type="solid"),
        "准备中": PatternFill(start_color="E6D5FF", fill_type="solid"),
        "需要确认": PatternFill(start_color="FFE4B5", fill_type="solid"),
    }

    header_fill = PatternFill(start_color="ADD8E6", fill_type="solid")

    for cell in ws[1]:
        cell.fill = header_fill

    if changes_col_idx:
        colored_count = 0

        for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row,
                                min_col=changes_col_idx, max_col=changes_col_idx), start=0):
            cell = row[0]
            cell_value = cell.value
            if cell_value in changes_fills:
                cell.fill = changes_fills[cell_value]
                colored_count += 1

                if cell_value == "Character Group Change" and changed_columns_map and row_idx in changed_columns_map:
                    changed_cols = changed_columns_map[row_idx]
                    for col_name in changed_cols:
                        if col_name in char_group_col_indices:
                            col_idx = char_group_col_indices[col_name]
                            char_cell = ws.cell(row=row_idx + 2, column=col_idx)
                            char_cell.fill = char_group_change_fill

        ws.column_dimensions[get_column_letter(changes_col_idx)].width = 40

    for status_col_name, status_col_idx in status_col_indices.items():
        colored_count = 0
        unknown_statuses = {}

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row,
                                min_col=status_col_idx, max_col=status_col_idx):
            cell = row[0]
            cell_value = cell.value

            if cell_value and str(cell_value).strip():
                if cell_value in status_fills:
                    cell.fill = status_fills[cell_value]
                    colored_count += 1
                else:
                    if cell_value not in unknown_statuses:
                        unknown_statuses[cell_value] = PatternFill(
                            start_color=generate_color_for_value(cell_value),
                            fill_type="solid"
                        )
                    cell.fill = unknown_statuses[cell_value]
                    colored_count += 1

        ws.column_dimensions[get_column_letter(status_col_idx)].width = 25

    ws.sheet_view.showGridLines = True
    ws.auto_filter.ref = ws.dimensions


def widen_summary_columns(ws):
    """
    Set appropriate column widths for summary sheets.

    Args:
        ws: openpyxl worksheet to format
    """
    ws.column_dimensions[get_column_letter(1)].width = 50
    ws.column_dimensions[get_column_letter(2)].width = 25
    ws.column_dimensions[get_column_letter(3)].width = 25
    ws.column_dimensions[get_column_letter(4)].width = 25
    ws.column_dimensions[get_column_letter(5)].width = 25
    ws.column_dimensions[get_column_letter(6)].width = 25


def format_update_history_sheet(ws):
    """
    Format the update history sheet with appropriate colors and styling.

    Args:
        ws: openpyxl worksheet to format
    """
    ws.column_dimensions[get_column_letter(1)].width = 80

    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical='top')

            if cell.value:
                content = str(cell.value)

                if "UPDATE HISTORY" in content or "LATEST UPDATE" in content:
                    cell.font = Font(bold=True, size=14, color="000080")
                    cell.fill = PatternFill(start_color="FFFFCC", fill_type="solid")

                elif "✓ UPDATED" in content:
                    cell.font = Font(bold=True, color="006600")
                    cell.fill = PatternFill(start_color="CCFFCC", fill_type="solid")

                elif "○ Preserved" in content:
                    cell.font = Font(italic=True, color="666666")
                    cell.fill = PatternFill(start_color="F0F0F0", fill_type="solid")

    ws.sheet_view.showGridLines = False
