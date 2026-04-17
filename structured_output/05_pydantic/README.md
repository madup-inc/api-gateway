# 05_pydantic — Pydantic 으로 스키마 정의하기

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
| [05_pydantic/README.md](./README.md) | Pydantic으로 스키마 정의 ← **현재** |
| [06_error_handling/README.md](../06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](../07_best_practices/README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](../07_best_practices/templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 1. 이 챕터에서 얻어갈 것

- JSON Schema 수작성을 버리고 **Pydantic BaseModel** 로 스키마를 선언하는 방법을 익힙니다.
- 응답 dict 를 `Model(**data)` 한 줄로 검증/인스턴스화해 타입 안전하게 다루는 패턴을 몸에 붙입니다.
- Enum, 중첩, Optional 세 가지 고급 기능을 Pydantic 관점에서 전부 다룹니다.

## 2. 언제 이 개념이 필요한가?

JSON Schema 를 직접 쓰다 보면 이런 고통을 겪습니다.

- 괄호/쉼표 오타로 디버깅이 어려움.
- `properties` 와 `required` 를 둘 다 관리하다 싱크가 깨짐.
- 중첩 3단계부터 들여쓰기 지옥.
- 파이썬 쪽 타입과 스키마가 **두 벌의 진실** 이 되어 리팩토링이 위험해짐.

Pydantic 은 이 모든 걸 없애 줍니다. **한 번의 모델 정의**로 타입 힌트, JSON Schema 생성, 응답 검증까지 다 됩니다.

## 3. 핵심 개념 요약

### 한 줄 공식

```python
class MyModel(BaseModel):
    ...

schema = MyModel.model_json_schema()       # 스키마 생성
data = generate_structured(..., schema=schema)
obj = MyModel(**data)                       # 검증 + 인스턴스화
```

이 세 줄이면 JSON Schema 와 런타임 타입 검증이 동시에 걸립니다.

### 타입 ↔ JSON Schema 매핑

| Pydantic 필드 | 생성되는 JSON Schema |
|---|---|
| `name: str` | `"type": "string"` |
| `count: int` | `"type": "integer"` |
| `price: float` | `"type": "number"` |
| `active: bool` | `"type": "boolean"` |
| `tags: list[str]` | `"type": "array", "items": {"type": "string"}` |
| `address: Address` (Address=BaseModel) | 중첩 object |
| `status: MyEnum` (str Enum) | `"enum": [...]` |
| `description: Optional[str] = None` | 해당 필드가 `required` 에서 빠지고 null 허용 |

### Enum 의 필수 조건

`class Sentiment(str, Enum):` 처럼 **`str` 을 같이 상속**해야 `model_json_schema()` 가 `enum` 필드를 제대로 내고, 응답 dict(`"positive"`) 를 모델로 되돌릴 때 `Sentiment.positive` 로 변환됩니다. 순수 `Enum` 만 쓰면 JSON 직렬화/역직렬화 경계에서 꼬입니다.

실제 동작은 [`02_enum_model.py`](./02_enum_model.py) 에서 볼 수 있습니다.

### Optional vs Required

- 필수 필드: 그냥 타입만 적음 → `required` 배열에 자동 포함.
- 선택 필드: `Optional[T] = None` → `required` 에서 빠지고 null 허용.

Optional 을 남발하면 모델이 귀찮은 필드를 전부 null 로 흘려버릴 수 있으니, **진짜로 없을 수 있는** 필드에만 쓰세요. [`04_optional_fields.py`](./04_optional_fields.py) 에서 할인 정보 유/무 두 케이스를 비교합니다.

## 4. 스크립트 한눈에 보기

| 파일 | 주제 | 핵심 |
|---|---|---|
| [`01_basic_model.py`](./01_basic_model.py) | 기본 모델 | `CityInfo` (str/int/float). 응답 dict 를 `CityInfo(**data)` 로 되돌리기 |
| [`02_enum_model.py`](./02_enum_model.py) | Enum | `str Enum` 두 개 + `list[str]` 태그. 티켓 2건 분석 |
| [`03_nested_model.py`](./03_nested_model.py) | 중첩 모델 | `RecipeBook → Recipe → Ingredient` 3단계. 깊은 dict 를 한 번에 검증 |
| [`04_optional_fields.py`](./04_optional_fields.py) | Optional | 할인/설명 필드가 있을 때 vs 없을 때 모델이 null 을 제대로 내는지 |

## 5. 실행 방법

```bash
cd structured_output
python 05_pydantic/01_basic_model.py
python 05_pydantic/02_enum_model.py
python 05_pydantic/03_nested_model.py
python 05_pydantic/04_optional_fields.py
```

## 6. 예상 출력

### `01_basic_model.py`

```
[parsed dict]
{'area_km2': 605.2, 'city': '서울', 'population': 9700000}

→ 서울: 인구 9,700,000명, 면적 605.2km²
```

### `03_nested_model.py`

```
→ 레시피 2개 수신
  · 김치찌개 (25분)
     - 김치 1컵 [채소]
     - 돼지고기 200g [육류]
     - 두부 1모 [곡물]
     ...
  · 비빔밥 (20분)
     ...
```

### `04_optional_fields.py`

```
=== Product #1 ===
{...}
→ 가을 면 티셔츠: 49,000원 (20% 할인)
  설명: ...
  재고: 있음

=== Product #2 ===
{'description': None, 'discount_rate': None, 'in_stock': True, 'name': '...', 'price': 38000.0}
→ 베이식 화이트 스니커즈: 38,000원
  재고: 있음
```

2번 케이스에서 `discount_rate` 와 `description` 이 실제 `None` 으로 들어오는 걸 확인하세요.

## 7. 자주 하는 실수 / 다음으로 넘어가기 전 체크리스트

- [ ] Enum 선언 시 `class X(str, Enum):` 처럼 `str` 을 섞어 상속했는가?
- [ ] 응답 dict 를 받자마자 `Model(**data)` 로 즉시 검증해서, 숨은 타입 불일치를 조기에 잡고 있는가?
- [ ] Optional 을 **꼭 필요한 필드에만** 썼는가? (과용하면 결측값 천국이 됨)
- [ ] 중첩 모델에서 안쪽 모델을 먼저 정의하고, 바깥 모델이 그걸 참조하게 배치했는가? (정의 순서가 중요)
- [ ] `model_json_schema()` 결과를 그대로 `generate_structured(schema=...)` 에 넘기고 있는가?

다음은 [`../06_error_handling/README.md`](../06_error_handling/README.md) — 응답이 예상대로 안 올 때의 대응법입니다.

<!-- 이 디렉토리의 .py 파일: 01_basic_model.py, 02_enum_model.py, 03_nested_model.py, 04_optional_fields.py -->
