# Excel Guides Update Notes

## Files to Update Manually

1. `VRS_Manager_Process_Guide_EN.xlsx`
2. `VRS_Manager_Process_Guide_KR.xlsx`

---

## Changes to Add (v1117 - TimeFrame+StrOrigin Logic)

### Version Update
- **Old**: v1116 (TWO-PASS Algorithm)
- **New**: v1117 (TWO-PASS Algorithm + TimeFrame+StrOrigin Logic)

### New Feature: Master File Update TimeFrame Preservation
This version adds robust TimeFrame preservation logic for Master File Update (HIGH importance only).
See Section 5 below for detailed explanation and examples.

---

## Previous Changes (v1116 - TWO-PASS Algorithm)

### 1. Update Version Number
- **Old**: v1114v4 (10-Key System)
- **New**: v1116 (TWO-PASS Algorithm)

### 2. Update Feature List

Add the following features to the "What's New" or "Key Features" section:

**English (VRS_Manager_Process_Guide_EN.xlsx):**
```
✅ TWO-PASS Algorithm
  - PASS 1: Detect & mark certainties (No Change, New)
  - PASS 2: Pattern match using UNMARKED rows only
  - After PASS 2: Detect deleted rows (unmarked PREVIOUS rows)
  - Eliminates 1-to-many matching issues

✅ 100% Correct Duplicate Handling
  - Handles duplicate StrOrigin (e.g., "Hello", "Yes", "No")
  - Handles blank StrOrigin (empty cells)
  - Handles duplicate CastingKey (same character speaking multiple times)

✅ Mathematically Correct Row Counting
  - Formula: new_rows - deleted_rows = actual_difference
  - Always accurate, no discrepancies

✅ Identical Detection Logic
  - All 4 processors (Raw, Working, All Language, Master) use same algorithm
  - Consistent results across all processes

✅ Full Duplicate Row Cleanup
  - Automatically removes full duplicate rows before processing
  - Ensures clean data for analysis
```

**Korean (VRS_Manager_Process_Guide_KR.xlsx):**
```
✅ TWO-PASS 알고리즘
  - PASS 1: 확실한 항목 감지 및 마킹 (변경 없음, 신규)
  - PASS 2: 마크되지 않은 행만 사용한 패턴 매칭
  - PASS 2 이후: 삭제된 행 감지 (마크되지 않은 PREVIOUS 행)
  - 1-to-many 매칭 문제 제거

✅ 100% 정확한 중복 처리
  - 중복 StrOrigin 처리 (예: "안녕하세요", "예", "아니오")
  - 빈 StrOrigin 처리 (빈 셀)
  - 중복 CastingKey 처리 (동일한 캐릭터가 여러 번 말하는 경우)

✅ 수학적으로 정확한 행 계산
  - 공식: new_rows - deleted_rows = actual_difference
  - 항상 정확, 불일치 없음

✅ 동일한 감지 로직
  - 모든 4개 프로세서 (Raw, Working, All Language, Master)가 동일한 알고리즘 사용
  - 모든 프로세스에서 일관된 결과

✅ 전체 중복 행 정리
  - 처리 전 전체 중복 행 자동 제거
  - 분석을 위한 깨끗한 데이터 보장
```

### 3. Update Technical Details Section

Add explanation of the TWO-PASS algorithm:

**English:**
```
### TWO-PASS Algorithm

The TWO-PASS algorithm ensures that each row in PREVIOUS matches at most ONE row in CURRENT, preventing 1-to-many matching issues.

**PASS 1 - Detect & Mark Certainties:**
1. Process all CURRENT rows
2. Perfect match (ALL 10 keys match) → "No Change" → Mark PREVIOUS row
3. No match (ALL 10 keys missing) → "New Row"

**PASS 2 - Detect Changes:**
1. Process CURRENT rows not classified in PASS 1
2. Pattern match with 10 keys (3-key first, then 2-key)
3. Only use PREVIOUS rows that are UNMARKED
4. First unmarked match wins → Mark matched PREVIOUS row
5. No unmarked match → "New Row"

**After PASS 2 - Detect Deleted Rows:**
- All unmarked PREVIOUS rows → "Deleted"

**Why This Works:**
- PASS 1 marks certainties, preventing them from being reused
- PASS 2 only uses unmarked rows, ensuring 1-to-1 matching
- Handles all edge cases: duplicate StrOrigin, blank cells, duplicate CastingKey
```

**Korean:**
```
### TWO-PASS 알고리즘

TWO-PASS 알고리즘은 PREVIOUS의 각 행이 CURRENT의 최대 한 행과만 매칭되도록 보장하여 1-to-many 매칭 문제를 방지합니다.

**PASS 1 - 확실한 항목 감지 및 마킹:**
1. 모든 CURRENT 행 처리
2. 완벽한 매치 (모든 10개 키 매치) → "No Change" → PREVIOUS 행 마킹
3. 매치 없음 (모든 10개 키 누락) → "New Row"
4. 모든 CURRENT 처리 후: 마크되지 않은 PREVIOUS 행 → "Deleted"

**PASS 2 - 변경 감지:**
1. PASS 1에서 분류되지 않은 CURRENT 행 처리
2. 10개 키로 패턴 매칭 (3-key 먼저, 그 다음 2-key)
3. 마크되지 않은 PREVIOUS 행만 사용
4. 첫 번째 마크되지 않은 매치 우선 (결정론적)
5. 마크되지 않은 매치 없음 → "New Row"

**왜 이것이 작동하는가:**
- PASS 1이 확실한 항목을 마킹하여 재사용 방지
- PASS 2는 마크되지 않은 행만 사용하여 1-to-1 매칭 보장
- 모든 엣지 케이스 처리: 중복 StrOrigin, 빈 셀, 중복 CastingKey
```

### 4. Update Examples/Use Cases

Add real-world example demonstrating duplicate handling:

**English:**
```
### Example: Duplicate StrOrigin Handling

**Scenario:**
PREVIOUS file has 1 row with common phrase "Hello"
CURRENT file has 3 rows with "Hello" (1 same character, 2 different characters)

**Before (v1114v4 - BROKEN):**
- 1 PREVIOUS row matches all 3 CURRENT rows
- Result: 2 rows incorrectly marked as "EventName Change" instead of "New Row"
- Row count math: BROKEN (new_rows - deleted_rows ≠ actual_difference)

**After (v1116 - FIXED with TWO-PASS):**
- PASS 1: Perfect match found → 1 CURRENT row marked "No Change", PREVIOUS row marked
- PASS 2: 2 remaining CURRENT rows → No unmarked PREVIOUS match → "New Row"
- Result: Correct classification (1 No Change, 2 New Row)
- Row count math: CORRECT (new_rows - deleted_rows = actual_difference) ✅
```

**Korean:**
```
### 예제: 중복 StrOrigin 처리

**시나리오:**
PREVIOUS 파일에 공통 문구 "안녕하세요"가 있는 1개 행
CURRENT 파일에 "안녕하세요"가 있는 3개 행 (1개는 같은 캐릭터, 2개는 다른 캐릭터)

**이전 (v1114v4 - 문제):**
- 1개 PREVIOUS 행이 모든 3개 CURRENT 행과 매칭
- 결과: 2개 행이 "New Row" 대신 "EventName Change"로 잘못 표시됨
- 행 계산 수학: 문제 (new_rows - deleted_rows ≠ actual_difference)

**이후 (v1116 - TWO-PASS로 수정):**
- PASS 1: 완벽한 매치 발견 → 1개 CURRENT 행 "No Change" 표시, PREVIOUS 행 마킹
- PASS 2: 나머지 2개 CURRENT 행 → 마크되지 않은 PREVIOUS 매치 없음 → "New Row"
- 결과: 올바른 분류 (1개 No Change, 2개 New Row)
- 행 계산 수학: 정확 (new_rows - deleted_rows = actual_difference) ✅
```

---

### 5. Master File Update - TimeFrame Preservation Logic

Add this section to explain the TimeFrame preservation rule:

**English:**
```
### Master File Update - TimeFrame Preservation (High Importance Only)

For HIGH importance rows, the system applies a special TimeFrame preservation rule:

**Rule:**
- If TimeFrame changed AND StrOrigin changed → Update TimeFrame (use SOURCE)
- If TimeFrame changed BUT StrOrigin did NOT change → Preserve TimeFrame (keep TARGET)

**Why This Matters:**
TimeFrame updates are only applied when they occur together with StrOrigin changes. This prevents
unwanted TimeFrame updates when only timing changed but the dialogue content remained the same.

**Examples:**
1. TimeFrame + StrOrigin both changed → TimeFrame updated ✅
2. TimeFrame + StrOrigin + EventName all changed → TimeFrame updated ✅
3. TimeFrame changed only (StrOrigin same) → TimeFrame preserved (TARGET kept) ✅
4. TimeFrame + EventName changed (StrOrigin same) → TimeFrame preserved (TARGET kept) ✅

This rule is robust and works for any combination of changes.
```

**Korean:**
```
### Master File Update - TimeFrame 보존 로직 (High Importance만 해당)

HIGH importance 행의 경우, 시스템은 특별한 TimeFrame 보존 규칙을 적용합니다:

**규칙:**
- TimeFrame 변경 AND StrOrigin 변경 → TimeFrame 업데이트 (SOURCE 사용)
- TimeFrame 변경 BUT StrOrigin 변경 안 됨 → TimeFrame 보존 (TARGET 유지)

**중요한 이유:**
TimeFrame 업데이트는 StrOrigin 변경과 함께 발생할 때만 적용됩니다. 이를 통해 대사 내용은
동일하지만 타이밍만 변경된 경우 원치 않는 TimeFrame 업데이트를 방지합니다.

**예시:**
1. TimeFrame + StrOrigin 둘 다 변경 → TimeFrame 업데이트 ✅
2. TimeFrame + StrOrigin + EventName 모두 변경 → TimeFrame 업데이트 ✅
3. TimeFrame만 변경 (StrOrigin 동일) → TimeFrame 보존 (TARGET 유지) ✅
4. TimeFrame + EventName 변경 (StrOrigin 동일) → TimeFrame 보존 (TARGET 유지) ✅

이 규칙은 모든 변경 조합에 대해 강력하게 작동합니다.
```

---

## Files Updated in This Release

### Core Algorithm Files
1. `src/core/comparison.py` - TWO-PASS in compare_rows() and find_deleted_rows()
2. `src/core/working_comparison.py` - TWO-PASS for Working Process
3. `src/core/alllang_helpers.py` - TWO-PASS for All Language Process
4. `src/processors/master_processor.py` - TWO-PASS in all sections

### Test Files
1. `tests/test_comprehensive_twopass.py` - Comprehensive TWO-PASS test (PASSING)
2. `tests/create_comprehensive_test.py` - Test data generator

### Documentation Files
1. `README.md` - Updated to v1116
2. `README_EN.md` - English documentation
3. `README_KR.md` - Korean documentation
4. `claude.md` - AI reference guide
5. `roadmap.md` - Development roadmap

---

## Testing Results

### Comprehensive TWO-PASS Test
- **Status**: PASSING ✅
- **Test Data**: 850 rows → 825 rows (after duplicate cleanup)
- **Results**:
  - New: 100 rows
  - Deleted: 100 rows
  - Net: 0 rows
  - Formula validation: 100 - 100 = 0 ✅
- **Duplicate Handling**:
  - 25 full duplicate rows cleaned
  - 100 duplicate StrOrigin rows handled correctly
  - 100 duplicate CastingKey rows handled correctly

---

## Manual Update Instructions

1. Open each Excel guide file
2. Navigate to the "What's New" or "Version History" sheet
3. Add new section for v1116
4. Copy relevant text from sections above (English for EN file, Korean for KR file)
5. Update version number in header/title
6. Add screenshots if needed (optional)
7. Save file

**Note:** Excel files cannot be easily updated programmatically without risking formatting loss. Please update manually using this guide.
