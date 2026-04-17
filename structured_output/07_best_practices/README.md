# 07_best_practices — 베스트 프랙티스 + 헬퍼 해설

## 📍 README 맵

| 위치 | 한 줄 요약 |
|---|---|
| [리포 루트 README](../../README.md) | api-gateway 리포 전체 안내 |
| [structured_output/README.md](../README.md) | Structured Output 튜토리얼 로드맵 |
| [common/README.md](../common/README.md) | 공통 헬퍼(config, client) 사용법 |
| [01_introduction/README.md](../01_introduction/README.md) | Structured Output 첫 만남 |
| [02_basic_structure/README.md](../02_basic_structure/README.md) | `response_mime_type` · `response_schema` |
| [03_type_system/README.md](../03_type_system/README.md) | string · integer · array · object · enum |
| [04_design_patterns/README.md](../04_design_patterns/README.md) | 분류 · 추출 · 분석 · 변환 · 비교 |
| [05_pydantic/README.md](../05_pydantic/README.md) | Pydantic으로 스키마 정의 |
| [06_error_handling/README.md](../06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](./README.md) | 베스트 프랙티스 + 헬퍼 해설 ← **현재** |
| [07_best_practices/templates/README.md](./templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 1. 이 챕터에서 얻어갈 것

- 앞선 여섯 챕터의 모든 권장 사항을 **하나의 체크리스트**로 압축해서 갖게 됩니다.
- `common/client.py` 의 헬퍼 함수가 가이드 §6.3 권장 패턴을 어떻게 그대로 구현했는지, 주석 라벨 (`[가이드 §6.1]`, `[가이드 §6.2]`, `[가이드 §6.3]`) 과 함께 확인합니다.
- 새 프로젝트에서 "어디서부터 시작할지" 망설이지 않도록 [`templates/`](./templates/README.md) 에 복붙 가능한 JSON 스키마를 카탈로그화합니다.

## 2. 언제 이 개념이 필요한가?

- 새로운 Structured Output 엔드포인트를 설계하기 직전 — 이 체크리스트를 먼저 훑으면 반복되는 시행착오를 피할 수 있습니다.
- 코드 리뷰에서 "스키마 잘 짰나?" 를 검증할 때 — 아래 섹션들이 그대로 리뷰어 체크 항목입니다.
- 헬퍼 함수의 동작이 의심될 때 — [`01_robust_helper_walkthrough.py`](./01_robust_helper_walkthrough.py) 를 돌려보면 내부 분기를 한눈에 확인할 수 있습니다.

## 3. 핵심 개념 요약 — 3-레벨 체크리스트

### 3.1 스키마 설계 (가이드 §7.1)

- [ ] 필드 이름은 **명확하고 설명적**. 약어(`desc`, `s`) 금지.
- [ ] `required` 배열에 **모든 핵심 필드**를 명시.
- [ ] 라벨성 필드(분류, 상태, 등급)는 **enum** 으로 제한.
- [ ] 중첩 깊이는 **3단계 이하**.
- [ ] 불필요한 필드는 제거. 스키마가 단순할수록 응답 품질이 올라감.

### 3.2 성능 (가이드 §7.2)

- [ ] 추출/분류 같은 기계적 작업은 `thinking_level="low"`.
- [ ] 스키마 준수가 중요한 요청은 `temperature=0.0 ~ 0.3`.
- [ ] 응답 크기에 맞게 `max_output_tokens` 조정 (너무 작으면 `MAX_TOKENS`, 너무 크면 비용 낭비).

### 3.3 안정성 (가이드 §7.3)

- [ ] `use_retry: true` (게이트웨이 기본값) 유지.
- [ ] 응답 처리 시 `finish_reason` 을 **parsed 보다 먼저** 확인.
- [ ] `parsed` 가 `null` 인 경우를 대비한 `text` 폴백 로직 보유.
- [ ] 요청에 `timeout` 지정 (공통 헬퍼는 30초 기본).

## 4. 스크립트 한눈에 보기

| 파일 | 주제 | 핵심 |
|---|---|---|
| [`01_robust_helper_walkthrough.py`](./01_robust_helper_walkthrough.py) | 헬퍼 해설 | `common.generate_structured` 와 동일한 로직을 inline 으로 풀어 쓰고 가이드 §6 라벨을 붙여 둠. 마지막에 inline 버전과 헬퍼 버전의 결과가 같은 걸 비교. |

## 5. 하위 디렉토리

| 경로 | 내용 |
|---|---|
| [`templates/`](./templates/README.md) | 복붙용 JSON 스키마 템플릿 3종 (single_object, object_array, classification_with_score). 가이드 §8 을 파일화. |

## 6. 실행 방법

```bash
cd structured_output
python 07_best_practices/01_robust_helper_walkthrough.py
```

## 7. 예상 출력

```
=== (A) inline 버전 ===
{'area_km2': 605.2, 'city': '서울', 'population': 9700000}

=== (B) common.generate_structured ===
{'area_km2': 605.2, 'city': '서울', 'population': 9700000}

두 결과는 스키마 준수 관점에서 동등합니다.
common 패키지는 이 모든 보호 장치를 기본 제공하므로, 평소엔 그냥 헬퍼를 쓰세요.
```

두 호출의 결과가 동일한 것을 확인함으로써, 헬퍼가 어떤 마법을 부리는 게 아니라 가이드 §6.3 패턴을 **깔끔하게 캡슐화** 한 것임을 체감할 수 있습니다.

## 8. 졸업 이후

여기까지 왔다면 Structured Output 의 모든 도구를 손에 쥔 상태입니다. 실제 프로젝트에서 할 일은 보통 다음 순서입니다.

1. [`templates/`](./templates/README.md) 에서 가장 가까운 템플릿을 복사.
2. 도메인에 맞게 필드·enum 수정.
3. Pydantic 으로 옮길 가치가 있으면 ([`../05_pydantic/README.md`](../05_pydantic/README.md)) 모델로 변환.
4. `common.generate_structured` 로 호출. 에러 처리는 헬퍼가 담당.
5. 응답을 Pydantic 모델로 즉시 검증하고 다음 단계로 전달.

<!-- 이 디렉토리의 .py 파일: 01_robust_helper_walkthrough.py -->
