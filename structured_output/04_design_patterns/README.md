# 04_design_patterns — 실무 5대 패턴

## 📍 README 맵

| 위치 | 한 줄 요약 |
|---|---|
| [리포 루트 README](../../README.md) | api-gateway 리포 전체 안내 |
| [structured_output/README.md](../README.md) | Structured Output 튜토리얼 로드맵 |
| [common/README.md](../common/README.md) | 공통 헬퍼(config, client) 사용법 |
| [01_introduction/README.md](../01_introduction/README.md) | Structured Output 첫 만남 |
| [02_basic_structure/README.md](../02_basic_structure/README.md) | `response_mime_type` · `response_schema` |
| [03_type_system/README.md](../03_type_system/README.md) | string · integer · array · object · enum |
| [04_design_patterns/README.md](./README.md) | 분류 · 추출 · 분석 · 변환 · 비교 ← **현재** |
| [05_pydantic/README.md](../05_pydantic/README.md) | Pydantic으로 스키마 정의 |
| [06_error_handling/README.md](../06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](../07_best_practices/README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](../07_best_practices/templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 1. 이 챕터에서 얻어갈 것

- 실제 업무에서 Structured Output 이 가장 빛을 발하는 **다섯 가지 패턴**을 손에 익힙니다.
- 같은 타입 조합이라도 프롬프트와 스키마 구성에 따라 결과 품질이 얼마나 달라지는지 체감합니다.
- 각 패턴을 복제해 자신의 도메인에 맞는 스키마로 빠르게 변형할 수 있게 됩니다.

## 2. 언제 이 개념이 필요한가?

"LLM 으로 뭘 자동화해보자" 는 막연한 아이디어를 프로덕션까지 끌고 가려면 대부분 이 다섯 가지 중 하나로 수렴합니다. 정말로 **90% 이상의 업무가 이 다섯 안에 들어갑니다.**

| 패턴 | 대표 업무 |
|---|---|
| **분류 (Classification)** | 지원 티켓 라우팅, 스팸 필터, 콘텐츠 모더레이션, 의도 분류 |
| **추출 (Extraction)** | 인보이스 OCR 후 필드 정제, 이메일에서 일정 뽑기, 이력서 파싱 |
| **분석 (Analysis)** | 리뷰 다관점 평가, 코드 PR 리스크 스코어, 고객 상담 품질 점수 |
| **변환 (Transformation)** | 긴 기사를 카드 UI 메타데이터로, 문서를 FAQ 로, 번역 + 요약 |
| **비교 (Comparison)** | 제품 추천, 솔루션 평가 리포트, A/B 선택 제안 |

## 3. 핵심 개념 요약

### 패턴별 스키마의 공통점 · 차이점

- **공통점**: 모두 `object` 가 루트이고, 라벨성 필드는 `enum` 으로 제한.
- **차이점**: 목록이냐 점수냐 설명이냐에 따라 중심이 되는 필드가 다름. 아래 표가 각 패턴의 "스키마 스카이라인" 입니다.

| 패턴 | 중심 필드 | 보조 필드 |
|---|---|---|
| Classification | 라벨 enum 들 | 짧은 `summary` |
| Extraction | `items` (객체 배열) | vendor_name, date, total 등 집계 필드 |
| Analysis | `aspects` 배열 + `overall_score` | strengths, weaknesses, recommendation |
| Transformation | `summary`, `key_points`, `topics` | language (enum), word_count |
| Comparison | `products` 배열 | `winner`, `reasoning` |

### 왜 `thinking_level="low"` ?

추출과 분류는 "이해" 보다 **"기계적 작업"** 에 가깝습니다. 추론 토큰을 많이 쓸 필요가 없어 빠르고 싸게 동작하도록 [`01_classification_ticket.py`](./01_classification_ticket.py) 와 [`02_extraction_invoice.py`](./02_extraction_invoice.py) 에 `thinking_level="low"` 를 명시했습니다. 반대로 분석·비교는 판단이 들어가므로 기본값에 맡깁니다.

## 4. 스크립트 한눈에 보기

| 파일 | 가이드 § | 핵심 스키마 구성 |
|---|---|---|
| [`01_classification_ticket.py`](./01_classification_ticket.py) | §4.1 | 3개의 enum (category, priority, assigned_team) + summary |
| [`02_extraction_invoice.py`](./02_extraction_invoice.py) | §4.2 | items (객체 배열) + 총액/소계/세금 |
| [`03_analysis_review.py`](./03_analysis_review.py) | §4.3 | aspects (enum 포함 객체 배열) + overall_score + 강/약점 |
| [`04_transformation_article.py`](./04_transformation_article.py) | §4.4 | summary + key_points + language enum + topics |
| [`05_comparison_products.py`](./05_comparison_products.py) | §4.5 | products (객체 배열) + winner + reasoning |

## 5. 실행 방법

```bash
cd structured_output
python 04_design_patterns/01_classification_ticket.py
python 04_design_patterns/02_extraction_invoice.py
python 04_design_patterns/03_analysis_review.py
python 04_design_patterns/04_transformation_article.py
python 04_design_patterns/05_comparison_products.py
```

## 6. 예상 출력

### `01_classification_ticket.py`

```
=== Ticket #1 ===
{'assigned_team': 'backend',
 'category': 'bug',
 'priority': 'critical',
 'summary': '배포 이후 로그인 버튼 무반응, 프로덕션 영향 발생'}
```

### `02_extraction_invoice.py`

```
→ (주)클라우드웍스 / INV-2026-0417 / 2026-04-17
→ 라인 아이템 3건, 총액 621,500
```

### `03_analysis_review.py`

```
→ 종합 점수: 7.4
  · 배터리         8.5  [positive]
  · 디스플레이     8.0  [positive]
  · 키보드         5.5  [negative]
  · 팬 소음        4.5  [negative]
  · 가격           7.0  [mixed]
```

## 7. 자주 하는 실수 / 다음으로 넘어가기 전 체크리스트

- [ ] 라벨성 필드는 전부 `enum` 으로 제한했다.
- [ ] 추출 시 숫자 필드의 `integer` vs `number` 를 구분했다.
- [ ] 분석 패턴에서 점수 범위(예: 0~10)를 **프롬프트에 명시**해 모델이 임의 스케일로 답하지 않게 했다.
- [ ] 비교 패턴에서 `winner` 가 `products[].name` 중 하나와 일치하는지 체크하는 로직을 호출자 쪽에 둘지 고려했다.
- [ ] 추출·분류에는 `thinking_level="low"` 를 썼다.

다음은 [`../05_pydantic/README.md`](../05_pydantic/README.md) — 이 패턴들을 JSON Schema 수작성이 아니라 Pydantic 모델로 더 깔끔하게 정의합니다.

<!-- 이 디렉토리의 .py 파일: 01_classification_ticket.py, 02_extraction_invoice.py, 03_analysis_review.py, 04_transformation_article.py, 05_comparison_products.py -->
