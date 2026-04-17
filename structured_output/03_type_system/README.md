# 03_type_system — 타입 시스템 완전 정복

## 📍 README 맵

| 위치 | 한 줄 요약 |
|---|---|
| [리포 루트 README](../../README.md) | api-gateway 리포 전체 안내 |
| [structured_output/README.md](../README.md) | Structured Output 튜토리얼 로드맵 |
| [common/README.md](../common/README.md) | 공통 헬퍼(config, client) 사용법 |
| [01_introduction/README.md](../01_introduction/README.md) | Structured Output 첫 만남 |
| [02_basic_structure/README.md](../02_basic_structure/README.md) | `response_mime_type` · `response_schema` |
| [03_type_system/README.md](./README.md) | string · integer · array · object · enum ← **현재** |
| [04_design_patterns/README.md](../04_design_patterns/README.md) | 분류 · 추출 · 분석 · 변환 · 비교 |
| [05_pydantic/README.md](../05_pydantic/README.md) | Pydantic으로 스키마 정의 |
| [06_error_handling/README.md](../06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](../07_best_practices/README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](../07_best_practices/templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 1. 이 챕터에서 얻어갈 것

- JSON Schema 의 **기본 타입 4개** (string, integer, number, boolean) 가 실제 응답에서 어떻게 구분되는지 감이 잡힙니다.
- **복합 타입** (array, object) 과 **제약 타입** (enum) 을 조립해 원하는 구조를 만들 수 있게 됩니다.
- enum 으로 "LLM 이 이상한 값을 내놓는 문제" 를 원천 차단하는 법을 배웁니다.

## 2. 언제 이 개념이 필요한가?

타입 선택을 잘못하면 다음 챕터들이 전부 괴로워집니다. 예를 들어:

- 가격을 `integer` 로 선언하면 `1999.99` 같은 할인가에서 깨집니다 → `number` 로.
- 카테고리를 자유 문자열로 두면 "IT", "it", "Tech", "테크" 가 섞여 집계가 불가 → `enum` 으로.
- 주소를 플랫하게 두면 도시/구/좌표가 섞임 → 중첩 `object` 로 묶어서 계층 유지.

이 챕터의 6개 예제가 각각 **하나의 타입 선택 함정을 피하는 법**을 보여줍니다.

## 3. 핵심 개념 요약

### 기본 타입

| 타입 | 스키마 | 언제 쓰나 |
|---|---|---|
| `string` | `{"type": "string"}` | 이름, 설명, 요약, 토큰 등 문자 전반 |
| `integer` | `{"type": "integer"}` | 수량, 인덱스, 페이지 번호 (소수점 X) |
| `number` | `{"type": "number"}` | 가격, 점수, 비율 (소수점 가능) |
| `boolean` | `{"type": "boolean"}` | 활성화 여부, 플래그 |

실제로 네 가지가 한 스키마에 섞여 있는 모습은 [`01_primitive_types.py`](./01_primitive_types.py) 에서 확인할 수 있습니다.

### 복합 타입

#### Array

`items` 로 배열 요소의 타입을 정의합니다.

- 문자열 배열 → [`02_array_of_strings.py`](./02_array_of_strings.py)
- 객체 배열 → [`03_array_of_objects.py`](./03_array_of_objects.py) (실무에서 가장 자주 쓰는 모양)

#### Object

`properties` 안에 또 다른 object 를 두면 계층이 됩니다. 주소 구조처럼 "상-하" 관계가 있을 때 플랫하게 풀지 말고 중첩으로 표현하세요. 깊이는 3단계 이하 권장 (가이드 §7.1). 예제는 [`04_nested_objects.py`](./04_nested_objects.py).

### Enum — 예측 불가능성을 없애는 치트키

Structured Output 에서 가장 강력한 도구입니다. 자유 문자열을 두면 모델이 "긍정적", "positive", "👍" 를 섞어 쓰는데, `enum` 으로 `["positive", "negative", "neutral"]` 만 허용하면 100% 그 세 가지만 나옵니다.

- 단일 enum → [`05_enum_single.py`](./05_enum_single.py)
- enum 배열 (복수 선택) → [`06_enum_array.py`](./06_enum_array.py)

## 4. 스크립트 한눈에 보기

| 파일 | 주제 | 핵심 |
|---|---|---|
| [`01_primitive_types.py`](./01_primitive_types.py) | 기본 4 타입 | string/integer/number/boolean 을 한 스키마에 |
| [`02_array_of_strings.py`](./02_array_of_strings.py) | 문자열 배열 | 태그, 키워드 등 단순 리스트 |
| [`03_array_of_objects.py`](./03_array_of_objects.py) | 객체 배열 | 상품 목록, 라인 아이템 패턴 |
| [`04_nested_objects.py`](./04_nested_objects.py) | 중첩 객체 | 주소 → 좌표 같은 계층 |
| [`05_enum_single.py`](./05_enum_single.py) | 단일 enum | 리뷰 3건의 sentiment 분류 |
| [`06_enum_array.py`](./06_enum_array.py) | enum 배열 | 뉴스 헤드라인의 복수 카테고리 |

## 5. 실행 방법

```bash
cd structured_output
python 03_type_system/01_primitive_types.py
python 03_type_system/02_array_of_strings.py
python 03_type_system/03_array_of_objects.py
python 03_type_system/04_nested_objects.py
python 03_type_system/05_enum_single.py
python 03_type_system/06_enum_array.py
```

## 6. 예상 출력

### `01_primitive_types.py`

```
[parsed]
{'is_premium': True, 'name': '에티오피아 예가체프 SO', 'price': 18500.0, 'stock': 42}

→ 에티오피아 예가체프 SO: 18500.00원, 재고 42개, 프리미엄=True
```

### `05_enum_single.py`

```
[positive] 배송이 엄청 빠르고 포장도 꼼꼼했어요. 완전 만족!
[negative] 상품 설명과 달라서 반품했어요. 시간 낭비였음.
[ neutral] 가격 대비 무난한 편. 특별히 좋지도 나쁘지도 않네요.
```

세 결과 모두 enum 세 값 안에서 정확히 나오는 걸 확인하세요.

### `06_enum_array.py`

```
→ 대형 제약사, 당뇨 치료 AI 모델을 FDA에 제출
   categories: ['tech', 'health']

→ 프로 야구 가을 시즌 개막, 티켓 판매 역대 최고
   categories: ['sports']
```

## 7. 자주 하는 실수 / 다음으로 넘어가기 전 체크리스트

- [ ] `integer` 와 `number` 의 차이를 안다 (정수 전용 vs 소수점 허용).
- [ ] `array` 는 `items` 로 요소 타입을 반드시 지정한다는 걸 기억한다.
- [ ] 분류 라벨처럼 "정해진 값만 와야 하는" 필드는 반드시 `enum` 을 쓴다.
- [ ] enum 값 목록은 5개 이하로 관리해 정확도를 유지한다. 꼭 많이 필요하면 그룹화 고려.
- [ ] 중첩 깊이는 3단계 이하로 유지한다.

다음은 [`../04_design_patterns/README.md`](../04_design_patterns/README.md) — 여기서 배운 타입들을 조합해 실제 업무 시나리오 5개를 만듭니다.

<!-- 이 디렉토리의 .py 파일: 01_primitive_types.py, 02_array_of_strings.py, 03_array_of_objects.py, 04_nested_objects.py, 05_enum_single.py, 06_enum_array.py -->
