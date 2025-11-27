#!/usr/bin/env python3
"""
Generic Excel Process Guides Updater

This script updates both EN and KR Excel guides with new version information.
Edit the version and content sections below to add new updates.
"""

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

# ============================================================================
# CONFIGURATION - EDIT THIS SECTION FOR EACH UPDATE
# ============================================================================

VERSION = "11272023"
VERSION_TEXT_EN = "Version 11272023 (Standalone Change Detection Fix)"
VERSION_TEXT_KR = "버전 11272023 (독립 변경 감지 수정)"

# English content to add
EN_HEADER = "WHAT'S NEW IN v1.121.0?"
EN_CONTENT = [
    {
        "title": "✅ Phase 3.1.1 COMPLETED - Word-Level Diff Enhancement (v1.121.0)",
        "items": [
            "IMPROVED: Word-level diff (cleaner output than character-level)",
            "NEW: Separate 'Diff Detail' column showing exact changes [old→new]",
            "NEW: Progress bar with filling animation during analysis",
            "NEW: StrOrigin Analysis now in BOTH Raw and Working Process",
            "IMPROVED: 4-column layout for better readability",
            "ANALYSIS: Shows which StrOrigin changes are trivial vs substantial",
        ]
    },
    {
        "title": "✅ Critical Bug Fixes (v1118.6)",
        "items": [
            "FIXED: TypeError 'unhashable type: dict' in Working VRS Check",
            "FIXED: All DataFrame column access now uses safe_str() pattern",
            "FIXED: Lookup dictionaries now correctly store indices (not dict objects)",
            "TESTED: 100% accuracy verified with 5000-row comprehensive test suite",
            "TESTED: All processors (Raw, Working, All Language) passing with real data",
        ]
    },
    {
        "title": "✅ Phase 2.2.1 COMPLETED - Super Group Analysis Improvements (v1118.4)",
        "items": [
            "REMOVED: 'Others' super group and stageclosedialog check entirely",
            "REORDERED: Super groups - AI Dialog now appears before Quest Dialog",
            "RENAMED: 'Untranslated Words (Remaining to Translate)' → 'Not Translated'",
            "REMOVED: Migration columns from main table (Words Migrated In/Out)",
            "ADDED: Detailed 'Super Group Migrations' table below main table",
            "Shows source → destination pairs with word counts for all migrations",
            "UPDATED: Explanatory notes below table (removed 'Others' references)",
            "8 super groups total: Main Chapters, F1, F2, F3, AI Dialog, Quest Dialog, Other, Everything Else",
        ]
    },
    {
        "title": "Column Order (Reorganized for Better Readability):",
        "items": [
            "1. Super Group Name, Total Words (Current/Previous), Net Change, % Change",
            "2. Translated/Untranslated words, Translation % (Current/Previous/Change)",
            "3. Detailed breakdown: Words Added/Deleted/Changed/Unchanged/Migrated",
        ]
    },
    {
        "title": "✅ v1118.3 - Master File Update - TimeFrame Preservation Restored",
        "items": [
            "TimeFrame = StartFrame ONLY (EndFrame always updates from SOURCE)",
            "IF StartFrame changed AND StrOrigin changed → Update StartFrame (use SOURCE)",
            "IF StartFrame changed BUT StrOrigin NOT changed → Preserve StartFrame (keep TARGET)",
            "Prevents unwanted timing updates when dialogue content unchanged",
        ]
    },
]

# Korean content to add
KR_HEADER = "v1.121.0의 새로운 기능"
KR_CONTENT = [
    {
        "title": "✅ Phase 3.1.1 완료 - 단어 수준 비교 개선 (v1.121.0)",
        "items": [
            "개선: 단어 수준 비교 (문자 수준보다 깔끔한 출력)",
            "새로운 기능: 정확한 변경사항을 보여주는 별도 'Diff Detail' 컬럼 [이전→현재]",
            "새로운 기능: 분석 중 진행률 표시 막대",
            "새로운 기능: Raw와 Working Process 모두에서 StrOrigin 분석 제공",
            "개선: 가독성을 위한 4컬럼 레이아웃",
        ]
    },
    {
        "title": "✅ 중요 버그 수정 (v1118.6)",
        "items": [
            "수정됨: Working VRS Check에서 TypeError 'unhashable type: dict' 오류",
            "수정됨: 모든 DataFrame 컬럼 접근이 safe_str() 패턴 사용",
            "수정됨: 룩업 사전이 이제 인덱스를 올바르게 저장 (dict 객체 아님)",
            "테스트 완료: 5000행 포괄적 테스트로 100% 정확도 검증",
            "테스트 완료: 모든 프로세서 (Raw, Working, All Language)가 실제 데이터로 통과",
        ]
    },
    {
        "title": "✅ Phase 2.2.1 완료 - 슈퍼 그룹 분석 개선 (v1118.4)",
        "items": [
            "제거됨: 'Others' 슈퍼 그룹 및 stageclosedialog 체크 완전히 제거",
            "재정렬: 슈퍼 그룹 - AI Dialog가 이제 Quest Dialog 앞에 표시됨",
            "이름 변경: 'Untranslated Words (Remaining to Translate)' → 'Not Translated'",
            "제거됨: 메인 테이블에서 마이그레이션 컬럼 제거 (Words Migrated In/Out)",
            "추가됨: 메인 테이블 아래에 상세한 'Super Group Migrations' 테이블",
            "모든 마이그레이션에 대한 소스 → 목적지 쌍과 단어 수 표시",
            "업데이트: 테이블 아래 설명 노트 ('Others' 참조 제거)",
            "총 8개의 슈퍼 그룹: Main Chapters, F1, F2, F3, AI Dialog, Quest Dialog, Other, Everything Else",
        ]
    },
    {
        "title": "컬럼 순서 (가독성 향상을 위해 재구성):",
        "items": [
            "1. 슈퍼 그룹 이름, 총 단어 수 (현재/이전), 순 변화, % 변화",
            "2. 번역/미번역 단어, 번역 % (현재/이전/변화)",
            "3. 상세 분석: 추가/삭제/변경/미변경/마이그레이션된 단어",
        ]
    },
    {
        "title": "✅ v1118.3 - Master File Update - TimeFrame 보존 복원",
        "items": [
            "TimeFrame = StartFrame만 해당 (EndFrame은 항상 SOURCE에서 업데이트)",
            "StartFrame 변경 AND StrOrigin 변경 → StartFrame 업데이트 (SOURCE 사용)",
            "StartFrame 변경 BUT StrOrigin 변경 안 됨 → StartFrame 보존 (TARGET 유지)",
            "대사 내용이 변경되지 않았을 때 원치 않는 타이밍 업데이트 방지",
        ]
    },
]

# ============================================================================
# SCRIPT LOGIC - NO NEED TO EDIT BELOW THIS LINE
# ============================================================================

def widen_columns(wb):
    """Widen columns A, B, C for better text visibility"""
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        ws.column_dimensions['A'].width = 100  # Main content column - wider
        ws.column_dimensions['B'].width = 30   # Secondary column
        ws.column_dimensions['C'].width = 20   # Tertiary column
    return True


def add_content_to_sheet(ws, content_sections):
    """Add content sections to worksheet"""
    # Find last row with content
    last_row = ws.max_row
    while last_row > 0 and not any(ws[f'{col}{last_row}'].value for col in ['A', 'B', 'C']):
        last_row -= 1

    new_row = last_row + 1

    for section in content_sections:
        new_row += 1

        # Add section title
        ws[f'A{new_row}'] = section['title']
        ws[f'A{new_row}'].font = Font(bold=True, size=11)

        # Add section items
        for item in section['items']:
            new_row += 1
            ws[f'A{new_row}'] = f"  • {item}"

    return new_row


def fix_pass1_to_pass2(wb):
    """Fix 'after PASS 1' deleted rows references to 'after PASS 2'"""
    corrections_made = 0

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    original = cell.value

                    # Fix various patterns
                    fixed = original.replace("After PASS 1: Any unmarked", "After PASS 2: Any unmarked")
                    fixed = fixed.replace("after PASS 1", "after PASS 2")
                    fixed = fixed.replace("After all CURRENT processed: Unmarked", "After PASS 2: Unmarked")

                    if fixed != original:
                        cell.value = fixed
                        corrections_made += 1

    return corrections_made


def update_en_guide():
    """Update English Process Guide"""
    print("Updating docs/VRS_Manager_Process_Guide_EN.xlsx...")

    wb = openpyxl.load_workbook('docs/VRS_Manager_Process_Guide_EN.xlsx')

    # Update Overview sheet
    if 'Overview' in wb.sheetnames:
        ws = wb['Overview']

        # Update version (row 2, column A)
        ws['A2'] = VERSION_TEXT_EN
        ws['A2'].font = Font(bold=True, size=12)
        ws['A2'].alignment = Alignment(horizontal='center')

        # Find last row with content
        last_row = ws.max_row
        while last_row > 0 and not any(ws[f'{col}{last_row}'].value for col in ['A', 'B', 'C']):
            last_row -= 1

        # Add new section header
        new_row = last_row + 3

        ws[f'A{new_row}'] = EN_HEADER
        ws[f'A{new_row}'].font = Font(bold=True, size=14)
        ws[f'A{new_row}'].alignment = Alignment(horizontal='left')

        new_row += 1

        # Add content sections
        for section in EN_CONTENT:
            new_row += 1

            # Add section title
            ws[f'A{new_row}'] = section['title']
            ws[f'A{new_row}'].font = Font(bold=True, size=11)

            # Add section items
            for item in section['items']:
                new_row += 1
                ws[f'A{new_row}'] = f"  • {item}"

    # Update Master Update sheet with TimeFrame logic
    if '4. Master Update' in wb.sheetnames:
        ws = wb['4. Master Update']

        # Find last row
        last_row = ws.max_row
        while last_row > 0 and not any(ws[f'{col}{last_row}'].value for col in ['A', 'B', 'C']):
            last_row -= 1

        new_row = last_row + 3

        ws[f'A{new_row}'] = 'TimeFrame Preservation Logic (v1117 - High Importance Only)'
        ws[f'A{new_row}'].font = Font(bold=True, size=13)
        ws[f'A{new_row}'].fill = PatternFill(start_color='FFE699', end_color='FFE699', fill_type='solid')

        new_row += 2
        ws[f'A{new_row}'] = 'Rule:'
        ws[f'A{new_row}'].font = Font(bold=True, size=11)

        new_row += 1
        ws[f'A{new_row}'] = '  • If TimeFrame changed AND StrOrigin changed → Update TimeFrame (use SOURCE)'

        new_row += 1
        ws[f'A{new_row}'] = '  • If TimeFrame changed BUT StrOrigin did NOT change → Preserve TimeFrame (keep TARGET)'

        new_row += 2
        ws[f'A{new_row}'] = 'This ensures TimeFrame updates only apply when accompanied by dialogue content changes.'
        ws[f'A{new_row}'].font = Font(italic=True)

    # Fix PASS 1 → PASS 2 for deleted rows
    corrections = fix_pass1_to_pass2(wb)
    if corrections > 0:
        print(f"  ✅ Fixed {corrections} 'PASS 1' → 'PASS 2' references for deleted rows")

    # Widen columns for better UX
    widen_columns(wb)
    print("  ✅ Widened columns A, B, C for better text visibility")

    wb.save('docs/VRS_Manager_Process_Guide_EN.xlsx')
    print("✅ English guide updated successfully!")


def update_kr_guide():
    """Update Korean Process Guide"""
    print("\nUpdating docs/VRS_Manager_Process_Guide_KR.xlsx...")

    wb = openpyxl.load_workbook('docs/VRS_Manager_Process_Guide_KR.xlsx')

    # Update Overview sheet (개요)
    if '개요' in wb.sheetnames:
        ws = wb['개요']

        # Update version (row 2, column A)
        ws['A2'] = VERSION_TEXT_KR
        ws['A2'].font = Font(bold=True, size=12)
        ws['A2'].alignment = Alignment(horizontal='center')

        # Find last row with content
        last_row = ws.max_row
        while last_row > 0 and not any(ws[f'{col}{last_row}'].value for col in ['A', 'B', 'C']):
            last_row -= 1

        # Add new section header
        new_row = last_row + 3

        ws[f'A{new_row}'] = KR_HEADER
        ws[f'A{new_row}'].font = Font(bold=True, size=14)
        ws[f'A{new_row}'].alignment = Alignment(horizontal='left')

        new_row += 1

        # Add content sections
        for section in KR_CONTENT:
            new_row += 1

            # Add section title
            ws[f'A{new_row}'] = section['title']
            ws[f'A{new_row}'].font = Font(bold=True, size=11)

            # Add section items
            for item in section['items']:
                new_row += 1
                ws[f'A{new_row}'] = f"  • {item}"

    # Update Master Update sheet with TimeFrame logic
    if '4. Master Update' in wb.sheetnames:
        ws = wb['4. Master Update']

        # Find last row
        last_row = ws.max_row
        while last_row > 0 and not any(ws[f'{col}{last_row}'].value for col in ['A', 'B', 'C']):
            last_row -= 1

        new_row = last_row + 3

        ws[f'A{new_row}'] = 'TimeFrame 보존 로직 (v1117 - High Importance만 해당)'
        ws[f'A{new_row}'].font = Font(bold=True, size=13)
        ws[f'A{new_row}'].fill = PatternFill(start_color='FFE699', end_color='FFE699', fill_type='solid')

        new_row += 2
        ws[f'A{new_row}'] = '규칙:'
        ws[f'A{new_row}'].font = Font(bold=True, size=11)

        new_row += 1
        ws[f'A{new_row}'] = '  • TimeFrame 변경 AND StrOrigin 변경 → TimeFrame 업데이트 (SOURCE 사용)'

        new_row += 1
        ws[f'A{new_row}'] = '  • TimeFrame 변경 BUT StrOrigin 변경 안 됨 → TimeFrame 보존 (TARGET 유지)'

        new_row += 2
        ws[f'A{new_row}'] = 'TimeFrame 업데이트는 대사 내용 변경과 함께 발생할 때만 적용됩니다.'
        ws[f'A{new_row}'].font = Font(italic=True)

    # Fix PASS 1 → PASS 2 for deleted rows
    corrections = fix_pass1_to_pass2(wb)
    if corrections > 0:
        print(f"  ✅ Fixed {corrections} 'PASS 1' → 'PASS 2' references for deleted rows")

    # Widen columns for better UX
    widen_columns(wb)
    print("  ✅ Widened columns A, B, C for better text visibility")

    wb.save('docs/VRS_Manager_Process_Guide_KR.xlsx')
    print("✅ Korean guide updated successfully!")


if __name__ == '__main__':
    print(f"Updating Excel guides to version {VERSION}...")
    print("=" * 60)
    update_en_guide()
    update_kr_guide()
    print("\n🎉 All Excel guides updated successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open the Excel files to verify the changes")
    print("2. git add docs/VRS_Manager_Process_Guide_EN.xlsx docs/VRS_Manager_Process_Guide_KR.xlsx")
    print(f'3. git commit -m "Update Excel guides to v{VERSION}"')
    print("4. git push")
