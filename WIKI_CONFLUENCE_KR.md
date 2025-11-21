# VRS Manager - 사용자 가이드

**버전:** 11202116 | **상태:** 프로덕션 배포 완료 | **날짜:** 2025년 11월

---

## 📋 목차

1. [VRS Manager란?](#vrs-manager란)
2. [핵심 개념](#핵심-개념)
3. [네 가지 프로세서](#네-가지-프로세서)
4. [행 식별 시스템](#행-식별-시스템)
5. [임포트 로직 규칙](#임포트-로직-규칙)
6. [빠른 참조](#빠른-참조)

---

## VRS Manager란?

VRS Manager는 **게임 개발 및 멀티미디어 프로젝트에서 음성 녹음 스크립트(VRS) 데이터를 관리하는 전문 도구**입니다. 서로 다른 버전의 VRS 엑셀 파일을 비교하여 변경사항을 감지하고, 여러 언어(한국어, 영어, 중국어)의 번역을 관리하며, 마스터 파일을 지능적으로 업데이트합니다.

### 주요 목적

개발팀에서 새로운 VRS 파일을 받으면 다음 작업이 필요합니다:
- **변경사항 파악** - 새로운 대사, 수정된 텍스트, 삭제된 라인, 타이밍 업데이트
- **완료된 작업 보존** - 이전 버전의 번역과 녹음 상태 유지
- **마스터 파일 업데이트** - 새로운 콘텐츠를 기존 데이터와 지능적으로 병합

VRS Manager는 이 전체 프로세스를 100% 정확도로 자동화합니다.

---

## 핵심 개념

### 1️⃣ 키 컬럼

모든 VRS 행은 **네 개의 키 컬럼**으로 식별됩니다:

| 컬럼 | 용도 | 예시 |
|------|------|------|
| **SequenceName** | 씬/시퀀스 식별자 | `"Scene_01_Battle"` |
| **EventName** | 시퀀스 내 이벤트 ID | `"E12345"` |
| **StrOrigin** | 원본 한글 대사 텍스트 | `"안녕하세요"` |
| **CastingKey** | 캐릭터 식별자 | `"Hero_Male_Main_A"` |

### 2️⃣ 중요도 레벨

행은 두 가지 중요도 레벨을 가집니다:

- **High Importance**: 업데이트와 추적이 필요한 중요 콘텐츠
- **Low Importance**: 중요도가 낮은 콘텐츠 (배경 오디오, 앰비언스 사운드)

### 3️⃣ 상태 유형

녹음 상태는 두 가지 카테고리로 나뉩니다:

- **녹음 전**: `"POLISHED"`, `"SPEC-OUT"`, `"CHECK"` 등
- **녹음 후**: `"RECORDED"`, `"FINAL"`, `"SHIPPED"` 등

**왜 중요한가**: 녹음 완료된 데이터는 임포트 시 항상 보존됩니다.

---

## 네 가지 프로세서

VRS Manager는 **4개의 메인 프로세스**를 제공합니다. 각각 목적은 다르지만 동일한 핵심 감지 로직을 공유합니다.

### 비교표

| 항목 | Raw Process | Working Process | All Language Process | Master File Update |
|------|-------------|-----------------|---------------------|-------------------|
| **입력 파일** | PREVIOUS + CURRENT (동일 파일 타입) | PREVIOUS + CURRENT (동일 파일 타입) | PREVIOUS (KR/EN/CN) + CURRENT (KR/EN/CN) | SOURCE (working 출력물) + TARGET (마스터 파일) |
| **목적** | 모든 변경사항 감지 | 완료된 작업을 새 베이스라인에 임포트 | 3개 언어를 임포트 로직과 함께 병합 | 새 데이터로 마스터 파일 업데이트 |
| **데이터 임포트?** | ❌ 아니오 - 감지만 수행 | ✅ 예 - 스마트 임포트 | ✅ 예 - 언어별 | ✅ 예 - 중요도 기반 |
| **출력 시트** | 메인 시트 + 삭제된 행 + 요약 | 메인 시트 + 삭제된 행 + 요약 | 메인 시트 + 삭제된 행 + 요약 | High + Low + Deleted + History |
| **사용 사례** | "v1과 v2 사이에 뭐가 바뀌었지?" | "내 번역을 새 버전에 옮기자" | "3개 언어를 한번에 업데이트" | "작업 파일을 마스터로 병합" |

---

### 🔍 프로세스 1: Raw VRS Check

**목적**: 두 VRS 파일을 비교하여 **무엇이 변경되었는지** 감지합니다.

**사용 시점**:
- 개발팀에서 새 VRS 버전을 받았을 때
- 이전 버전과 무엇이 다른지 알고 싶을 때
- 작업을 시작하기 전에 변경사항 요약이 필요할 때

**수행 작업**:
1. PREVIOUS ↔ CURRENT 비교
2. 모든 행을 다음으로 분류: 새 행, 변경 없음, StrOrigin 변경, EventName 변경 등
3. 이전 StrOrigin 값 추적
4. 통계 및 단어 수 생성

**수행하지 않는 작업**:
- 데이터 임포트 하지 않음
- 번역이나 상태를 복사하지 않음
- 변경사항만 표시

**출력물**:
- 메인 시트: CHANGES 컬럼이 있는 모든 현재 행
- 삭제된 행: PREVIOUS에서 제거된 행
- StrOrigin Analysis: 텍스트 변경사항 상세 비교 (v11202116의 새 기능)
- 요약: 통계 및 단어 수

---

### 📥 프로세스 2: Working VRS Check

**목적**: PREVIOUS의 완료된 작업을 CURRENT로 **스마트 로직**을 사용해 임포트합니다.

**사용 시점**:
- 완료된 번역/녹음 상태가 있는 PREVIOUS 파일이 있을 때
- 개발팀에서 새로운 CURRENT 베이스라인을 받았을 때
- 완료된 작업을 보존하고 새로운/변경된 콘텐츠만 작업하고 싶을 때

**수행 작업**:
1. PREVIOUS ↔ CURRENT 비교 (Raw Process와 동일)
2. 변경 유형에 따라 **임포트 로직** 적용 (임포트 로직 섹션 참조)
3. 녹음 완료 상태 자동 보존
4. 과거 변경사항 추적을 위한 PreviousData 컬럼 생성

**임포트 동작**:
- **변경 없음** → 전체 임포트 (STATUS, Text, FREEMEMO)
- **StrOrigin 변경** → STATUS/FREEMEMO 보존, 이전 StrOrigin을 PreviousData에 저장
- **EventName 변경** → 전체 임포트 (타이밍은 바뀔 수 있지만 내용은 동일)
- **새 행** → 임포트 안 함 (완전히 새로운 콘텐츠)

**출력물**:
- 메인 시트: PREVIOUS 데이터로 강화된 현재 행
- 삭제된 행: PREVIOUS에서 제거된 행
- StrOrigin Analysis: 텍스트 변경사항 상세 비교 (v11202116의 새 기능)
- 요약: 통계

---

### 🌍 프로세스 3: All Language Check

**목적**: **3개 언어(KR/EN/CN)**를 동시에 병합하고 업데이트합니다.

**사용 시점**:
- 한국어, 영어, 중국어 번역을 관리하고 있을 때
- 모든 언어에 대한 새로운 CURRENT 파일을 받았을 때
- 각 언어에 대해 완료된 작업이 있는 PREVIOUS 파일이 있을 때

**수행 작업**:
1. CURRENT KR + EN + CN을 단일 파일로 병합 (StrOrigin 키 기준)
2. 언어별로 독립적으로 **Working Process 임포트 로직** 적용
3. 누락된 언어를 우아하게 처리 (1개, 2개 또는 3개 언어 모두 처리 가능)
4. 언어별 컬럼 생성 (STATUS_KR, STATUS_EN, STATUS_CN)

**임포트 동작**: Working Process와 동일하지만 각 언어에 개별 적용됩니다.

**출력물**:
- 메인 시트: 임포트된 데이터로 병합된 모든 언어
- 삭제된 행: PREVIOUS에서 제거된 행
- 요약: 언어별 통계

---

### 🎯 프로세스 4: Master File Update

**목적**: Working Process 출력물의 데이터로 **마스터 파일**을 업데이트합니다.

**사용 시점**:
- Working Process를 완료하고 작업 출력 파일이 있을 때
- 이를 마스터 파일로 병합해야 할 때
- 간단한 데이터 이동 작업 (비교/차이 분석이 아님)

**수행 작업**:
1. SOURCE를 High/Low 중요도로 분리
2. **EventName만**으로 행 매칭 (간단함!)
3. **High Importance**: TARGET 컬럼을 SOURCE 데이터로 업데이트
4. **Low Importance**: 완전히 건너뜀 (처리 안 함)
5. **삭제된 행**: CHANGES = "Deleted"로 인라인 표시
6. SOURCE의 CHANGES 컬럼 보존 (재계산 안 함)

**단순화된 로직** (v1118.2):
- **High + EventName 매칭** → SOURCE 값으로 TARGET 컬럼 업데이트
- **High + EventName이 TARGET에 없음** → 새 행 추가
- **Low importance** → 완전히 건너뜀 (처리 안 함)
- **삭제됨** → EventName이 TARGET에 있지만 SOURCE에 없음 → CHANGES = "Deleted" 표시
- **CHANGES 컬럼** → 항상 SOURCE에서 보존

**출력물**:
- 메인 시트: 모든 행 (HIGH + DELETED)
- 업데이트 히스토리: 타임스탬프와 통계가 있는 추적 시트
- 요약: 통계

---

## 행 식별 시스템

VRS Manager는 **10-Key 패턴 매칭 + TWO-PASS 알고리즘**을 사용하여 초정밀 변경 감지를 수행합니다.

### 10개의 키

모든 행은 **10개의 서로 다른 키 조합**을 생성합니다:

**2-Key 조합 (6개):**
- `(Sequence, Event)` - SE
- `(Sequence, StrOrigin)` - SO
- `(Sequence, CastingKey)` - SC
- `(Event, StrOrigin)` - EO
- `(Event, CastingKey)` - EC
- `(StrOrigin, CastingKey)` - OC

**3-Key 조합 (4개):**
- `(Sequence, Event, StrOrigin)` - SEO
- `(Sequence, Event, CastingKey)` - SEC
- `(Sequence, StrOrigin, CastingKey)` - SOC
- `(Event, StrOrigin, CastingKey)` - EOC

### 왜 10개의 키인가?

**문제**: "안녕하세요", "네", "아니오" 같은 흔한 대사 문구는 여러 캐릭터에 걸쳐 여러 번 나타납니다.

**10개 키 없이**:
```
PREVIOUS: 행 A - "안녕하세요" (주인공이 말함)
CURRENT:  행 B - "안녕하세요" (NPC가 말함, 다른 캐릭터)
```
→ 시스템 판단: "EventName이 바뀜" ❌ 틀림 - 이건 새 행입니다!

**10개 키 사용 시**:
- 행이 새 행인 경우는 **모든 10개 키가** PREVIOUS에 없을 때만
- 행이 삭제된 경우는 **모든 10개 키가** CURRENT에 없을 때만
- 중복이 존재할 때 잘못된 매칭 방지

### TWO-PASS 알고리즘

시스템은 1-대-다 매칭 문제를 방지하기 위해 **두 번의 패스**로 행을 처리합니다.

#### PASS 1: 확실한 것 감지
- 완벽한 4-키 매칭 (S+E+O+C 모두 매칭) → **"변경 없음"** → PREVIOUS 행을 "사용됨"으로 표시
- 모든 10개 키가 없음 → **"새 행"**

#### PASS 2: 변경사항 감지 (미표시 행만 사용)
- 가장 구체적인 것(3-키)부터 가장 덜 구체적인 것(2-키)까지 패턴 매칭
- **미표시 PREVIOUS 행만 사용** (PASS 1에서 매칭되지 않은 것)
- 첫 번째 미표시 매칭이 승리 → "사용됨"으로 표시
- 미표시 매칭 없음 → **"새 행"**

#### PASS 2 이후: 삭제 감지
- 여전히 미표시인 PREVIOUS 행 → **"삭제된 행"**

**왜 TWO-PASS인가?**

TWO-PASS 없이:
```
PREVIOUS: 행 A - (Scene1, E1000, "안녕하세요", Hero)

CURRENT:
  행 1: (Scene1, E1000, "안녕하세요", Hero) → 행 A와 매칭 → "변경 없음"
  행 2: (Scene1, E2000, "안녕하세요", NPC)  → 행 A와도 매칭 → "EventName 변경" ❌
  행 3: (Scene1, E3000, "안녕하세요", Boss) → 행 A와도 매칭 → "EventName 변경" ❌

결과: 1개의 PREVIOUS 행이 3개의 CURRENT 행과 매칭 (1-대-다) ❌
```

TWO-PASS 사용:
```
PASS 1:
  행 1 → 완벽 매칭 → "변경 없음" → 행 A를 사용됨으로 표시

PASS 2:
  행 2 → (Scene1, "안녕하세요") 키 확인 → 행 A는 이미 표시됨 → 건너뜀 → 다른 키 확인 → 미표시 매칭 없음 → "새 행" ✅
  행 3 → 동일한 로직 → "새 행" ✅

결과: 1개의 PREVIOUS 행이 1개의 CURRENT 행과 매칭 (1-대-1) ✅
```

### 변경 분류

어떤 키가 매칭되는지에 따라 시스템은 변경사항을 분류합니다:

| 매칭 패턴 | 분류 | 예시 |
|----------|------|------|
| SEO 매칭, C 다름 | CastingKey 변경 | 같은 대사, 다른 화자 |
| SEC 매칭, O 다름 | StrOrigin 변경 | 같은 타이밍/캐릭터, 대사 수정됨 |
| SOC 매칭, E 다름 | EventName 변경 | 같은 대사/캐릭터, 이벤트 ID 변경됨 |
| EOC 매칭, S 다름 | SequenceName 변경 | 같은 대사, 다른 씬으로 이동됨 |
| SE 매칭, O+C 다름 | StrOrigin+CastingKey 변경 | 대대적인 수정 |
| 모든 10개 키 없음 | 새 행 | 완전히 새로운 콘텐츠 |
| (PASS 2 미표시) | 삭제된 행 | 콘텐츠 제거됨 |

---

## StrOrigin 분석 시트

**v11202116의 새로운 기능** - Phase 3.1.1: 단어 수준 비교 개선

### StrOrigin 분석이란?

**Raw Process** 또는 **Working Process**를 실행할 때, VRS Manager는 자동으로 **별도의 "StrOrigin Analysis" 시트**를 생성하여 한글 텍스트 변경사항에 대한 상세한 비교를 제공합니다. 이를 통해 대사에서 정확히 무엇이 바뀌었는지, 그리고 변경사항이 사소한 것(구두점)인지 중요한 것(내용)인지 파악할 수 있습니다.

### 두 가지 버전

VRS Manager는 서로 다른 분석 기능을 가진 두 가지 설치 버전으로 제공됩니다:

| 버전 | 용량 | StrOrigin 분석 출력 |
|------|------|-------------------|
| **LIGHT** | ~150MB | "구두점/공백 변경" 또는 "내용 변경" 표시 |
| **FULL** | ~2.6GB | 한국어 BERT AI 모델을 사용한 의미 유사도 백분율 표시 (예: "79.8% similar", "94.5% similar") |

두 버전 모두 오프라인으로 작동하며 정확한 변경 감지를 제공합니다—FULL 버전은 단지 더 상세한 유사도 점수를 제공할 뿐입니다.

### 4컬럼 레이아웃

StrOrigin 분석 시트는 쉬운 비교를 위해 **4컬럼 레이아웃**을 사용합니다:

| 컬럼 | 내용 | 예시 |
|------|------|------|
| **Previous StrOrigin** | PREVIOUS 파일의 텍스트 | `"플레이어가 게임에서 이겼다"` |
| **Current StrOrigin** | CURRENT 파일의 텍스트 | `"적이 전투에서 졌다"` |
| **Analysis** | 유사도 또는 변경 유형 | `"79.8% similar"` 또는 `"Content Change"` |
| **Diff Detail** | 단어 수준 변경사항 | `"[플레이어가→적이] [게임→전투] [이겼다→졌다]"` |

**최적화된 컬럼 너비**: 25% | 25% | 20% | 35%로 가독성을 극대화했습니다.

### 단어 수준 비교

**Diff Detail** 컬럼은 문자 수준 비교 대신 **단어 수준 비교**를 사용합니다 (WinMerge 방식과 유사):

**이전 (문자 수준)**: `[플→적] [이→이] [어→] [가→] [게→전] [임→투]`
**이후 (단어 수준)**: `[플레이어가→적이] [게임→전투] [이겼다→졌다]`

훨씬 깔끔하고 이해하기 쉽습니다!

### 출력 예시

**구두점만 변경** (두 버전 모두):
```
Analysis: "Punctuation/Space Change"
Diff Detail: (비어 있음 - 내용 변경 없음)
```

**내용 변경** (LIGHT 버전):
```
Analysis: "Content Change"
Diff Detail: "[플레이어→적] [이겼다→졌다]"
```

**내용 변경** (FULL 버전):
```
Analysis: "79.8% similar"
Diff Detail: "[플레이어→적] [이겼다→졌다]"
```

### 진행률 표시

StrOrigin 분석 중에는 **채워지는 애니메이션이 있는 진행률 표시 막대**가 실시간 진행 상황을 보여줍니다:

```
Performing StrOrigin Analysis... [████████░░] 82% (164/200 rows)
```

특히 큰 파일의 경우 분석 진행 상황을 추적하는 데 도움이 됩니다.

### 언제 나타나나요?

StrOrigin 분석 시트는 다음의 경우에 나타납니다:
- **Raw Process** 실행 시 (StrOrigin 변경 감지)
- **Working Process** 실행 시 (StrOrigin 변경 임포트 및 분석)
- ❌ All Language Process에서는 **아직 미구현** (Phase 3.1.2에서 계획됨)
- ❌ Master File Update에서는 **해당 없음** (적용 불가)

### 무엇이 분석되나요?

PREVIOUS와 CURRENT 사이에 **StrOrigin이 변경된** 행만 분석됩니다:
- StrOrigin 변경
- StrOrigin+EventName 변경
- StrOrigin+CastingKey 변경
- StrOrigin이 포함된 모든 복합 변경

"변경 없음" 또는 StrOrigin에 영향을 주지 않는 변경(TimeFrame 변경, EventName 변경 등)이 있는 행은 분석 시트에서 제외됩니다.

---

## 임포트 로직 규칙

임포트 로직은 다음에 적용됩니다: **Working Process**, **All Language Process**, **Master File Update**

### Working Process 임포트 로직

| 변경 유형 | 임포트되는 것 | 이유 |
|----------|-------------|------|
| **변경 없음** | ✅ STATUS, Text, FREEMEMO | PREVIOUS의 모든 것 (완료된 작업) |
| **StrOrigin 변경** | ✅ STATUS, FREEMEMO<br>📝 PreviousData<br>❌ Text | 상태는 보존하지만 텍스트는 재번역 필요 |
| **Desc 변경** | ✅ STATUS, Text, FREEMEMO | 설명이 바뀌었지만 내용은 동일 |
| **TimeFrame 변경** | ✅ STATUS, Text, FREEMEMO | 타이밍이 바뀌었지만 내용은 동일 |
| **EventName 변경** | ✅ STATUS, Text, FREEMEMO | 이벤트 ID가 바뀌었지만 내용은 대체로 동일 |
| **SequenceName 변경** | ✅ STATUS, Text, FREEMEMO | 씬이 이동했지만 내용은 동일 |
| **복합 변경** | StrOrigin 변경 여부에 따라 다름 | StrOrigin이 변경에 포함되면 → PreviousData 생성 |
| **새 행** | ❌ 없음 | 완전히 새로운 콘텐츠는 새 번역 필요 |

**PreviousData 형식**: `"{이전StrOrigin} | {이전STATUS} | {이전FREEMEMO}"`

**녹음 완료 규칙**: PREVIOUS STATUS가 녹음 완료 상태(RECORDED, FINAL 등)라면 변경 유형과 관계없이 항상 보존합니다.

### Master File Update 임포트 로직 (v1118.2 - 단순화됨)

**High Importance 행**:

| 상황 | 동작 |
|------|------|
| EventName이 TARGET에 매칭 | SOURCE 값으로 TARGET 컬럼 업데이트<br>SOURCE의 CHANGES 보존 |
| EventName이 TARGET에 없음 | TARGET 스키마를 사용하여 새 행 추가<br>SOURCE의 CHANGES 보존 |

**Low Importance 행**:

| 상황 | 동작 |
|------|------|
| 모든 LOW importance 행 | 완전히 건너뜀 (처리 안 함) |

**삭제된 행**:

| 상황 | 동작 |
|------|------|
| EventName이 TARGET에 있지만 SOURCE에 없음 | 행 유지, CHANGES = "Deleted" 설정 |

**CHANGES 컬럼 처리**:
- 항상 SOURCE에서 보존 (Working Process가 이미 계산함)
- Master File Update에서 재계산 안 함
- TARGET에 CHANGES 컬럼이 없으면 → 자동으로 추가
- TARGET에 CHANGES 컬럼이 있으면 → SOURCE 값으로 교체

**핵심 포인트**: Master File Update는 이제 비교 프로세스가 아닌 간단한 데이터 이동 작업입니다.

---

## 빠른 참조

### 각 프로세스를 사용해야 할 때

| 목표 | 이 프로세스 사용 |
|------|---------------|
| "버전 간에 뭐가 바뀌었지?" | **Raw Process** |
| "내 번역을 새 버전에 옮기자" | **Working Process** |
| "3개 언어를 한번에 업데이트" | **All Language Process** |
| "작업 파일을 마스터로 병합" | **Master File Update** |

### 주요 컬럼

**자동 생성**:
- `CHANGES` - 변경 분류 (새 행, StrOrigin 변경 등)
- `CastingKey` - 캐릭터 식별자 (CharacterKey + DialogVoice + GroupKey + DialogType에서 자동 생성)
- `PreviousData` - StrOrigin이 변경될 때 과거 추적

**사용자 컬럼**:
- `SequenceName`, `EventName`, `StrOrigin` - 핵심 식별자
- `STATUS` - 녹음 상태 (POLISHED, RECORDED, FINAL 등)
- `Text` - 번역된 텍스트
- `FREEMEMO` - 자유 형식 노트
- `StartFrame`, `EndFrame` - 타이밍 정보

### 색상 코딩 (엑셀 출력)

| 색상 | 의미 |
|------|------|
| 🟢 초록색 | 새 행 |
| 🟡 노란색 | StrOrigin 변경 / SequenceName 변경 |
| 🟠 주황색 | TimeFrame 변경 |
| 🌸 분홍색 | EventName 변경 |
| 🟣 보라색 | Desc 변경 |
| 🔵 청록색 | 복합 변경 |
| 🔴 빨간색 | 삭제된 행 |

### 통계 정확도

VRS Manager는 **100% 정확한 행 카운팅**을 보장합니다:

```
새_행 - 삭제된_행 = 실제_행_차이
```

이 공식은 다음 덕분에 항상 성립합니다:
- ✅ 10-Key 시스템 (잘못된 NEW/DELETED 감지 방지)
- ✅ TWO-PASS 알고리즘 (1-대-다 매칭 방지)
- ✅ 중복 처리 (StrOrigin, CastingKey, 빈 셀)

---

## 버전 정보

**현재 버전**: 11202116 (프로덕션 배포 완료 - 모든 핵심 기능 구현됨)

**주요 기능**:
- ✅ **Phase 3.1.1 - 단어 수준 비교 개선** (v11202116) - 상세한 비교 기능을 갖춘 StrOrigin 분석
  - 단어 수준 비교 (문자 수준보다 깔끔한 출력)
  - 4컬럼 레이아웃의 별도 "StrOrigin Analysis" 시트
  - 정확한 변경사항을 보여주는 "Diff Detail" 컬럼 [이전→현재]
  - 분석 중 채워지는 애니메이션이 있는 진행률 표시 막대
  - Raw와 Working Process 모두에서 작동
  - LIGHT 버전: 구두점 감지 / FULL 버전: BERT 의미 유사도 백분율
- ✅ **슈퍼 그룹 분석 개선** (v1118.4 - Phase 2.2.1) - 향상된 명확성과 추적
  - "Others" 슈퍼 그룹 및 stageclosedialog 체크 제거
  - 슈퍼 그룹 재정렬: AI Dialog가 Quest Dialog 앞에 위치
  - 컬럼명 "Not Translated"로 변경 (단순화된 헤더)
  - 메인 테이블 아래 상세한 "Super Group Migrations" 테이블 추가
  - 소스 → 목적지 쌍과 단어 수 표시
- ✅ **단순화된 Master File Update** (v1118.2) - EventName만 매칭, CHANGES 보존
  - 간단한 데이터 이동 작업 (비교가 아님)
  - CHANGES 값을 항상 SOURCE에서 보존
  - 강건한 처리 (TARGET에 CHANGES 유무와 관계없이 작동)
  - 단일 출력 시트 (HIGH + DELETED 행)
- ✅ **컬럼 강건성** (v1117.1) - 다른 컬럼 구조를 가진 파일 처리
- ✅ 10-Key 패턴 매칭 시스템 (Raw/Working/All Language 프로세스)
- ✅ TWO-PASS 알고리즘 (1-대-1 행 매칭)
- ✅ 100% 정확한 중복 처리
- ✅ 다국어 지원 (KR/EN/CN)
- ✅ 모듈식 아키텍처 (31개 Python 파일)
- ✅ 업데이트 히스토리 추적

**GitHub**: [VRS-Manager](https://github.com/NeilVibe/VRS-Manager)

---

## 지원

질문이나 이슈가 있으시면 개발팀에 문의하거나 프로젝트 문서를 확인하세요:
- `README.md` / `README_KR.md` - 사용자 문서
- `DEVELOPER_GUIDE.md` - 기술 구현 세부사항
- `CLAUDE.md` - AI 참조 및 아키텍처 개요
- `roadmap.md` - 개발 이력 및 완료된 기능

---

*최종 업데이트: 2025년 11월 21일 | 버전 11202116*
