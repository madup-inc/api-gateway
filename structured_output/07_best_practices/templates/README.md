# templates — 복붙용 JSON 스키마 템플릿

## 📍 README 맵

| 위치 | 한 줄 요약 |
|---|---|
| [리포 루트 README](../../../README.md) | api-gateway 리포 전체 안내 |
| [structured_output/README.md](../../README.md) | Structured Output 튜토리얼 로드맵 |
| [common/README.md](../../common/README.md) | 공통 헬퍼(config, client) 사용법 |
| [01_introduction/README.md](../../01_introduction/README.md) | Structured Output 첫 만남 |
| [02_basic_structure/README.md](../../02_basic_structure/README.md) | `response_mime_type` · `response_schema` |
| [03_type_system/README.md](../../03_type_system/README.md) | string · integer · array · object · enum |
| [04_design_patterns/README.md](../../04_design_patterns/README.md) | 분류 · 추출 · 분석 · 변환 · 비교 |
| [05_pydantic/README.md](../../05_pydantic/README.md) | Pydantic으로 스키마 정의 |
| [06_error_handling/README.md](../../06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](../README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](./README.md) | 복붙용 JSON 스키마 템플릿 ← **현재** |

---

## 이 디렉토리는 어떤 곳인가?

가이드 §8 "빠른 참조" 의 JSON 스키마 템플릿을 **그대로 파일화**한 곳입니다. 새 프로젝트를 시작할 때 가장 가까운 템플릿을 하나 복사해 고치면, 처음부터 뼈대를 그리는 수고를 덜 수 있습니다.

전부 JSON 파일이라 그대로 `response_schema` 에 넣어도 되고, Python 쪽에서는 `json.load` 로 읽어서 `schema=` 인자로 넘기면 됩니다.

```python
import json
from common import generate_structured

with open("07_best_practices/templates/single_object.json") as f:
    schema = json.load(f)

data = generate_structured(
    contents=["..."],
    schema=schema,
    temperature=0.3,
)
```

## 템플릿 카탈로그

### 1) [`single_object.json`](./single_object.json)

가장 기본. 필드 3개(`name: string`, `value: number`, `active: boolean`)짜리 단일 객체.

- **쓸 만한 상황**: 한 건의 정보를 받는 간단한 요청. 예: "이 문서의 제목과 중요도 점수와 활성 여부를 알려줘."
- **커스터마이즈 포인트**: `properties` 의 필드 이름/타입을 프로젝트 도메인에 맞게 교체. 필드가 늘어나면 `required` 배열에도 같이 추가.
- 실전 예시는 [`../../02_basic_structure/01_minimal_schema.py`](../../02_basic_structure/01_minimal_schema.py) 와 [`../../05_pydantic/01_basic_model.py`](../../05_pydantic/01_basic_model.py).

### 2) [`object_array.json`](./object_array.json)

객체 배열. `items` 가 `type: object` 인 가장 흔한 패턴.

- **쓸 만한 상황**: 목록/카탈로그/검색결과/라인아이템. 예: 상품 목록, 티켓 목록, 기사 요약 여러 건.
- **커스터마이즈 포인트**: `items.properties` 에서 각 레코드 필드를 정의. 바깥 `properties` 에 `total_count`, `page` 같은 메타 필드를 추가해도 좋음.
- 실전 예시는 [`../../03_type_system/03_array_of_objects.py`](../../03_type_system/03_array_of_objects.py), [`../../04_design_patterns/02_extraction_invoice.py`](../../04_design_patterns/02_extraction_invoice.py).

### 3) [`classification_with_score.json`](./classification_with_score.json)

분류 + 신뢰도 점수 + 근거. 제일 많이 쓰이는 실전 패턴.

- **쓸 만한 상황**: 모든 이진/다진 분류 문제. 스팸 분류, 위험도 판정, 의도 분류, 라우팅.
- **커스터마이즈 포인트**:
  - `category.enum` 을 도메인 라벨로 교체. 라벨 수 **5개 이하 권장**.
  - `confidence` 를 0~1 이 아니라 0~10 처럼 쓰려면 프롬프트에 범위를 명시.
  - `reasoning` 필드로 모델이 답의 근거를 스스로 적게 만들면 디버깅에 큰 도움이 됩니다.
- 실전 예시는 [`../../04_design_patterns/01_classification_ticket.py`](../../04_design_patterns/01_classification_ticket.py).

## Pydantic 으로 바꾸고 싶다면

JSON 을 손으로 관리하는 게 불편해지면 [`../../05_pydantic/README.md`](../../05_pydantic/README.md) 를 참고해 같은 구조를 BaseModel 로 옮기세요. 이 디렉토리의 세 템플릿은 각각 아래 예제와 같은 모양입니다.

| 템플릿 | 대응 Pydantic 예제 |
|---|---|
| [`single_object.json`](./single_object.json) | [`../../05_pydantic/01_basic_model.py`](../../05_pydantic/01_basic_model.py) |
| [`object_array.json`](./object_array.json) | [`../../05_pydantic/03_nested_model.py`](../../05_pydantic/03_nested_model.py) |
| [`classification_with_score.json`](./classification_with_score.json) | [`../../05_pydantic/02_enum_model.py`](../../05_pydantic/02_enum_model.py) (패턴이 가장 가까움) |

## 복붙 시 체크리스트

- [ ] `title` 을 내 도메인에 맞게 바꿨다 (기본값 `MySchema` 는 힌트가 약함).
- [ ] `required` 가 새 `properties` 와 싱크가 맞는다.
- [ ] enum 후보를 도메인 라벨로 교체했고, 개수는 5개 이하다.
- [ ] 파일을 그대로 `schema=` 로 넘기지 않고 꼭 한 번은 실제 호출로 검증했다.

<!-- 이 디렉토리의 파일(.py 없음, .json 템플릿): single_object.json, object_array.json, classification_with_score.json -->
