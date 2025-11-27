# VRS Manager (한국어)

**버전:** 11272145
**작성자:** Neil Schmitt
**상태:** 프로덕션 준비 완료 (TWO-PASS 알고리즘 + 깔끔한 슈퍼 그룹 테이블 + 마이그레이션 추적)

[![Build Executables](https://github.com/NeilVibe/VRS-Manager/actions/workflows/build-executables.yml/badge.svg)](https://github.com/NeilVibe/VRS-Manager/actions/workflows/build-executables.yml)
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/NeilVibe/VRS-Manager/releases)

---

## 개요

VRS Manager는 음성 녹음 스크립트(VRS) 데이터를 여러 언어와 버전에 걸쳐 관리하는 전문 도구입니다. 게임 개발 또는 멀티미디어 프로젝트의 음성 녹음 콘텐츠에 대한 변경 사항, 업데이트 및 번역을 추적하는 데 도움을 줍니다.

이 도구는 VRS Excel 파일의 이전 버전과 현재 버전을 비교하여 변경 사항을 감지 및 분류하고, 다국어 번역(한국어, 영어, 중국어)을 관리하며, 중요도 수준에 따라 마스터 파일을 지능적으로 업데이트합니다.

---

## 주요 기능

### 🔑 10-Key 패턴 매칭 + TWO-PASS 알고리즘 (v1116 - 최신)
- **초정밀 변경 감지** - 포괄적인 10-key 조합 사용:
  - **2-Key 조합 (6개)**: SE, SO, SC, EO, EC, OC
  - **3-Key 조합 (4개)**: SEO, SEC, SOC, EOC
- **TWO-PASS 알고리즘**: 1-to-many 매칭 문제 제거
  - **PASS 1**: 확실한 항목 감지 및 마킹 (변경 없음, 신규, 삭제)
  - **PASS 2**: 마크되지 않은 행만 사용한 패턴 매칭
- **100% 정확한 NEW/DELETED 감지**: 모든 10개 키가 없을 때만 NEW/DELETED로 판정
- **모든 중복 처리**: 중복 StrOrigin, 빈 셀, 중복 CastingKey
- **단계별 패턴 매칭**: 가장 구체적인 것(3-key)부터 가장 덜 구체적인 것(2-key)까지
- **오탐 방지**: 여러 캐릭터에서 공통 문구가 나타날 때도 정확히 감지
- **수학적으로 정확**: `new_rows - deleted_rows = actual_difference` ✅

### 🌍 다국어 지원
- **3개 언어 처리** (한국어, 영어, 중국어)
- **유연한 업데이트** - 1개, 2개 또는 모든 3개 언어 업데이트 가능
- **자동 감지** - 폴더 구조에서 언어 파일 자동 감지

### 🎯 지능형 Import 로직
- **상태 인식** - 녹음 완료 후 데이터 자동 보존
- **변경 유형별 처리** - StrOrigin, Desc, TimeFrame 변경에 따른 다른 로직
- **중요도 기반** - High와 Low 중요도 행을 다르게 처리

### 📊 4가지 주요 프로세스

1. **Raw VRS Check** - PREVIOUS ↔ CURRENT 비교 및 모든 변경 감지
2. **Working VRS Check** - 스마트 로직으로 PREVIOUS 데이터를 CURRENT로 Import
3. **All Language Check** - 3개 언어 병합 및 업데이트 (KR/EN/CN)
4. **Master File Update** - 3-key 복사-붙여넣기 검증으로 Master File 업데이트

### 📈 업데이트 히스토리 추적
- **모든 프로세스의 완전한 감사 추적**
- **타임스탬프와 통계가 포함된 JSON 기반 저장**
- **GUI를 통한 풍부한 형식의 히스토리 보기**

---

## 설치

### 옵션 1: 사전 빌드된 실행 파일 사용 (권장)

**Python 설치 불필요!**

#### GitHub Actions에서 다운로드 (최신 빌드)
1. [Actions 탭](https://github.com/NeilVibe/VRS-Manager/actions)으로 이동
2. 최신 "Build Executables" 워크플로우 클릭
3. 플랫폼별 아티팩트 다운로드:
   - **Windows**: `VRSManager-Windows.zip` → 압축 해제 → `VRSManager.exe` 실행
   - **Linux**: `VRSManager-Linux.zip` → 압축 해제 → `chmod +x VRSManager` → `./VRSManager`
   - **macOS**: `VRSManager-macOS.zip` → 압축 해제 → `chmod +x VRSManager` → `./VRSManager`

#### Releases에서 다운로드 (안정 버전)
1. [Releases 페이지](https://github.com/NeilVibe/VRS-Manager/releases)로 이동
2. 플랫폼별 최신 릴리스 다운로드
3. 압축 해제 후 실행!

모든 파일(히스토리 JSON, Excel 출력)은 실행 파일과 같은 폴더에 생성됩니다.

### 옵션 2: 소스에서 실행

**전제 조건:**
- **Python 3.7+**
- **필수 패키지:**
  ```bash
  pip install -r requirements.txt
  ```

**단계:**

1. **리포지토리 복제:**
   ```bash
   git clone git@github.com:NeilVibe/VRS-Manager.git
   cd VRS-Manager
   ```

2. **종속성 설치:**
   ```bash
   pip install -r requirements.txt
   ```

3. **애플리케이션 실행:**
   ```bash
   python main.py
   ```

---

## 사용법

### 1. Raw VRS Check

**목적:** PREVIOUS ↔ CURRENT 비교 및 모든 변경 감지

**단계:**
1. **"PROCESS RAW VRS CHECK"** 클릭
2. PREVIOUS 파일 선택
3. CURRENT 파일 선택
4. 색상으로 코딩된 변경 사항이 포함된 출력 Excel 검토

**출력:**
- 각 행의 변경 분류
- Previous StrOrigin 추적
- 번역 작업량에 대한 단어 수
- 별도 시트의 삭제된 행

---

### 2. Working VRS Check

**목적:** 지능형 로직으로 PREVIOUS 데이터를 CURRENT로 Import

**단계:**
1. **"PROCESS WORKING VRS CHECK"** 클릭
2. PREVIOUS 파일 선택 (완료된 작업 포함)
3. CURRENT 파일 선택 (업데이트할 새 베이스라인)
4. 보강된 출력 검토

**출력:**
- Import된 STATUS, Text, FREEMEMO가 포함된 CURRENT 파일
- 변경 유형 및 녹음 상태 기반 스마트 Import
- 감사 추적을 위한 PreviousData 컬럼

---

### 3. All Language Check

**목적:** 3개 언어 병합 및 업데이트 (KR/EN/CN)

**단계:**
1. **"PROCESS ALL LANGUAGE CHECK"** 클릭
2. `Previous/` 및 `Current/` 하위 폴더가 포함된 폴더 선택
3. 파일 자동 감지: `*_KR.xlsx`, `*_EN.xlsx`, `*_CN.xlsx`
4. 병합된 출력 검토

**출력:**
- 모든 3개 언어가 포함된 단일 파일
- 언어별 독립적인 변경 추적
- 유연함: 1개, 2개 또는 3개 언어 업데이트 가능

---

### 4. Master File Update

**목적:** Working Process 출력으로 Master File 업데이트

**단계:**
1. **"PROCESS MASTER FILE UPDATE"** 클릭
2. SOURCE 파일 선택 (Working Process 출력)
3. TARGET 파일 선택 (업데이트할 Master File)
4. 업데이트된 Master 검토

**출력:**
- Main Sheet (High): 모든 high-importance 행
- Low Importance: 모든 low-importance 행 (TARGET 데이터 보존)
- Deleted Rows: 3-key 검증된 삭제
- Update History: 자동 생성된 추적

---

## 변경 유형

도구가 감지하고 분류하는 변경 유형:

### 핵심 필드 변경

| 변경 유형 | 설명 | 색상 |
|-------------|-------------|-------|
| **StrOrigin Change** | 대사 텍스트 변경 | 노란색 |
| **EventName Change** | EventName 식별자 변경 | 연한 노란색 |
| **SequenceName Change** | 시퀀스/장면 재구성 | 연한 파란색 |
| **CastingKey Change** | 성우 할당 변경 | 주황색 |

### 메타데이터 필드 변경

| 변경 유형 | 설명 | 색상 |
|-------------|-------------|-------|
| **TimeFrame Change** | StartFrame/EndFrame 타이밍 변경 | 빨강-주황색 |
| **Desc Change** | 설명/컨텍스트 변경 | 보라색 |
| **DialogType Change** | 대화 유형 분류 변경 | (복합) |
| **Group Change** | 그룹 할당 변경 | (복합) |
| **Character Group Change** | 캐릭터 속성 변경 (Tribe/Age/Gender/Job/Region) | 연한 하늘색 |

### 시스템 상태

| 분류 | 설명 | 색상 |
|---------------|-------------|-------|
| **New Row** | CURRENT에 있지만 PREVIOUS에 없는 행 | 녹색 |
| **Deleted Row** | PREVIOUS에 있지만 CURRENT에 없는 행 | 빨간색 |
| **No Change** | 완벽한 일치 (4개 핵심 키 모두 동일) | 연한 회색 |
| **No Relevant Change** | 한국어가 아닌 텍스트만 변경 (무시됨) | 진한 회색 |

### 복합 변경

시스템은 여러 필드가 함께 변경될 때 100개 이상의 조합을 감지할 수 있습니다:
- **예시:** "StrOrigin+Desc Change" (텍스트와 설명 모두 변경됨)
- **예시:** "EventName+CastingKey Change" (이벤트 이름 변경 AND 성우 변경)
- **예시:** "StrOrigin+Desc+TimeFrame Change" (주요 수정)

**참고:** 모든 변경 유형, 감지 로직 및 프로세서 호환성에 대한 자세한 내용은 `docs/CHANGE_TYPES_REFERENCE.md`를 참조하세요.

---

## Import 로직 규칙

### Working Process 및 All Language

| 변경 유형 | 데이터 소스 | 비고 |
|-------------|----------------|-------|
| **No Change** | PREVIOUS | 전체 Import (STATUS, Text, Desc, FREEMEMO) |
| **StrOrigin Change** | PREVIOUS → PreviousData<br>CURRENT → Text | PREVIOUS의 STATUS, FREEMEMO, Desc 보존 |
| **Desc Change** | PREVIOUS → PreviousData<br>PREVIOUS → Text | Text 포함 전체 Import |
| **TimeFrame Change** | PREVIOUS → PreviousData<br>PREVIOUS → 전체 Import | STATUS, Text, Desc, FREEMEMO 전체 Import |
| **EventName Change** | PREVIOUS → 전체 Import | PREVIOUS의 모든 것 |
| **SequenceName Change** | PREVIOUS → 전체 Import | PREVIOUS의 모든 것 |
| **CastingKey Change** | PREVIOUS → 전체 Import | PREVIOUS의 모든 것 |
| **DialogType Change** | PREVIOUS → 전체 Import | PREVIOUS의 모든 것 |
| **Group Change** | PREVIOUS → 전체 Import | PREVIOUS의 모든 것 |
| **Character Group Change** | PREVIOUS → 전체 Import | PREVIOUS의 모든 것 |
| **복합 변경** | StrOrigin에 따라 다름 | StrOrigin이 변경에 포함되면 → PreviousData 생성 |
| **New Row** | CURRENT만 | Import 없음 (새 콘텐츠) |

**특별 규칙:** PREVIOUS STATUS가 녹음 후 상태 (RECORDED, FINAL 등)인 경우 변경 유형에 관계없이 항상 STATUS를 보존합니다.

### Master File Update

| 변경 유형 | High Importance | Low Importance |
|-------------|----------------|----------------|
| **기존 행** | SOURCE 데이터 복사<br>**예외:** TimeFrame 변경되었지만 StrOrigin은 변경되지 않은 경우 TARGET TimeFrame 보존 | **TARGET 데이터 유지** |
| **신규 행** | 출력에 포함 | **출력에서 제외** |
| **삭제된 행** | "Deleted Rows" 시트에 추적 | "Deleted Rows" 시트에 추적 |

**TimeFrame 보존 규칙 (High Importance만 해당):**
- **TimeFrame 변경 AND StrOrigin 변경:** TimeFrame 업데이트 (SOURCE 사용)
- **TimeFrame 변경 BUT StrOrigin 변경 안 됨:** TimeFrame 보존 (TARGET 유지)
- 이를 통해 TimeFrame 업데이트는 StrOrigin 변경과 함께 발생할 때만 적용됩니다

---

## 버전 히스토리

### v1117.1 (현재 - TimeFrame+StrOrigin 로직 + 컬럼 견고성)
- ✅ **컬럼 견고성 수정** - 다른 컬럼 구조를 가진 파일 처리
  - 두 파일(PREVIOUS와 CURRENT)에 모두 존재하는 컬럼만 비교
  - 선택적 컬럼이 없어도 충돌 없음 (Desc, StartFrame, EndFrame, Text 등)
  - 필수 핵심 컬럼: SequenceName, EventName, StrOrigin, CastingKey 구성요소
  - 없는 선택적 컬럼에 대한 변경 감지를 우아하게 건너뜀
- ✅ v1117의 모든 기능 포함

### v1117 (이전 - TimeFrame+StrOrigin 로직)
- ✅ **Master File Update TimeFrame 보존 로직** - 강력하고 범용적인 구현
  - TimeFrame 변경 AND StrOrigin 변경 → TimeFrame 업데이트
  - TimeFrame 변경 BUT StrOrigin 변경 안 됨 → TimeFrame 보존
  - 모든 복합 변경 조합에 대해 작동 (TimeFrame+EventName, TimeFrame+CastingKey 등)
- ✅ **문서 업데이트** - 모든 가이드에 TimeFrame 로직 추가
- ✅ **버그 수정** - 삭제된 행 감지 문서 "PASS 1" → "PASS 1 또는 PASS 2"

### v1116 (TWO-PASS 알고리즘)
- ✅ **TWO-PASS 알고리즘** - 1-to-many 매칭 문제 제거
  - PASS 1: 확실한 항목 감지 및 마킹 (변경 없음, 신규, 삭제)
  - PASS 2: 마크되지 않은 행만 사용한 패턴 매칭
- ✅ **100% 정확한 중복 처리** - StrOrigin, CastingKey, 빈 셀
- ✅ **수학적으로 정확한 행 계산** - `new - deleted = actual_diff` ✅
- ✅ **포괄적인 테스트 스위트** - 완전한 중복 처리 검증
- ✅ **동일한 감지 로직** - 모든 4개 프로세서가 동일한 알고리즘 사용
- ✅ 4개 핵심 파일 업데이트 (comparison, working_comparison, alllang_helpers, master_processor)
- ✅ 처리 전 전체 중복 행 정리
- ✅ 10-Key 패턴 매칭 시스템
- ✅ 모듈형 아키텍처 유지
- ✅ 다국어 지원 (KR/EN/CN)
- ✅ 업데이트 히스토리 추적
- ✅ 지능형 Import 로직

### v1114v4 (이전 - 10-Key 시스템)
- ✅ **10-Key 패턴 매칭 시스템** - 초정밀 변경 감지
  - 2-key 조합: SE, SO, SC, EO, EC, OC
  - 3-key 조합: SEO, SEC, SOC, EOC
- ✅ **버그 수정**: NEW/DELETED 감지 이제 100% 정확
- ✅ **사전 NEW 확인**: 모든 10개 키가 없어야 함
- ✅ **단계별 패턴 매칭**: 가장 구체적에서 가장 덜 구체적으로
- ✅ **올바른 행 계산 수학**: `new_rows - deleted_rows = actual_difference`
- ✅ 9개 핵심 파일 업데이트 (lookups, comparison, processors)
- ✅ 모듈형 아키텍처 유지
- ✅ 다국어 지원 (KR/EN/CN)
- ✅ 업데이트 히스토리 추적
- ✅ 지능형 Import 로직

### v1114v3 (이전 - 4-Tier Key 시스템)
- ✅ **4-Tier Key 시스템** (CW, CG, ES, CS)
- ✅ **Stage 2 검증** with Key 4 (CastingKey 기반)
- ✅ **중복 StrOrigin 처리** 공통 문구용
- ✅ **캐릭터 신원 검증** 모든 프로세스에서
- ✅ **모듈형 아키텍처** - 31개 Python 파일, 4,400+ 줄
- ✅ **2,700줄 모놀리스에서 완전히 리팩토링**
- ✅ Master File LOW importance 로직 수정
- ✅ 색상 코딩된 변경 시각화

---

## 개발

### 테스트 실행

```bash
# 구문 검증
python3 -m py_compile main.py
python3 -m py_compile src/processors/*.py

# 미래: 단위 테스트
pytest tests/
```

### 기여

1. 기능 브랜치 생성
2. 명확한 커밋 메시지로 변경
3. 실제 데이터로 철저히 테스트
4. Pull request 제출

---

## 라이선스

독점 - © Neil Schmitt

---

## 지원

문제, 질문 또는 기능 요청:
- **GitHub Issues:** https://github.com/NeilVibe/VRS-Manager/issues
- **Email:** (연락처 정보)

---

## 감사의 말

- **Built with:** Python, pandas, openpyxl, tkinter
- **AI Assistant:** Claude Code (Anthropic)
- **Architecture:** Template Method Pattern, Modular Design

---

**Happy VRS Managing! 🎙️🎬**
