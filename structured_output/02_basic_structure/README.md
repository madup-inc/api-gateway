# 02_basic_structure — 요청 Config와 Schema 뼈대

## 📍 README 맵

| 위치 | 한 줄 요약 |
|---|---|
| [리포 루트 README](../../README.md) | api-gateway 리포 전체 안내 |
| [structured_output/README.md](../README.md) | Structured Output 튜토리얼 로드맵 |
| [common/README.md](../common/README.md) | 공통 헬퍼(config, client) 사용법 |
| [01_introduction/README.md](../01_introduction/README.md) | Structured Output 첫 만남 |
| [02_basic_structure/README.md](./README.md) | `response_mime_type` · `response_schema` ← **현재** |
| [03_type_system/README.md](../03_type_system/README.md) | string · integer · array · object · enum |
| [04_design_patterns/README.md](../04_design_patterns/README.md) | 분류 · 추출 · 분석 · 변환 · 비교 |
| [05_pydantic/README.md](../05_pydantic/README.md) | Pydantic으로 스키마 정의 |
| [06_error_handling/README.md](../06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](../07_best_practices/README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](../07_best_practices/templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 1. 이 챕터에서 얻어갈 것

- `config` 안의 두 필드(`response_mime_type`, `response_schema`) 가 **언제 꺼지고 언제 켜지는지** 감을 잡습니다.
- 스키마의 뼈대 4 요소 — `title`, `type`, `properties`, `required` — 를 외웁니다.
- `required` 에 포함되는 필드와 빠지는 필드의 **실제 응답 차이**를 눈으로 비교합니다.

## 2. 언제 이 개념이 필요한가?

- 새 엔드포인트를 처음 만들 때, "최소한의 스키마" 한 개부터 시작하는 게 안전합니다. 필드 두세 개로 시작해 점점 늘려가는 패턴이 실수가 적습니다.
- 기존 엔드포인트에서 특정 필드가 가끔 누락된다면 `required` 가 빠진 건 아닌지 먼저 의심합니다.

## 3. 핵심 개념 요약

### 스위치 두 개

```json
"config": {
  "response_mime_type": "application/json",
  "response_schema": { ... }
}
```

- `response_mime_type` 을 `"application/json"` 으로 지정 → 자연어 모드가 꺼지고 JSON 모드로 전환.
- `response_schema` 가 없으면 JSON 이긴 한데 구조는 모델 마음대로. 둘은 한 쌍으로 같이 지정합니다.

### 스키마 뼈대 4요소

| 필드 | 역할 | 생략 가능? |
|---|---|---|
| `title` | 스키마의 이름. 모델 프롬프트에 힌트로 전달됨. | 권장 (안 쓰면 좋은 힌트를 못 줌) |
| `type` | 최상위 타입. 보통 `"object"`. | 생략 시 `object` |
| `properties` | 필드 목록. 이 딕셔너리의 **키가 필드명**, 값이 필드 스키마. | **필수** |
| `required` | 반드시 채워져야 할 필드 이름 배열. | 기술적으론 선택이지만 **실전에선 필수** |

`required` 를 빠뜨리면 모델이 일부 필드를 누락할 수 있습니다. 아무 필드나 생략해도 된다는 뜻이 아니라, "이건 없어도 유효한 응답이야" 라는 신호를 줍니다. 이 차이를 직접 확인하려면 [`02_required_fields.py`](./02_required_fields.py) 를 돌려보세요.

## 4. 스크립트 한눈에 보기

| 파일 | 설명 |
|---|---|
| [`01_minimal_schema.py`](./01_minimal_schema.py) | 단 한 개의 문자열 필드만 있는 가장 작은 스키마. 아침 인사 한 문장을 받음. |
| [`02_required_fields.py`](./02_required_fields.py) | 같은 스키마를 `required=[모두]` 와 `required=[name 하나]` 로 두 번 호출해 응답 차이 비교. |

## 5. 실행 방법

```bash
cd structured_output
python 02_basic_structure/01_minimal_schema.py
python 02_basic_structure/02_required_fields.py
```

## 6. 예상 출력

### `01_minimal_schema.py`

```
[parsed]
{'message': '좋은 아침이에요! 오늘도 따뜻한 하루 되세요.'}

→ 모델의 인사: 좋은 아침이에요! 오늘도 따뜻한 하루 되세요.
```

### `02_required_fields.py`

```
[모두 필수] required=['name', 'population', 'famous_food', 'timezone']
{'famous_food': '비빔밥',
 'name': '서울',
 'population': 9700000,
 'timezone': 'Asia/Seoul'}
  → 누락된 필드: 없음

[이름만 필수] required=['name']
{'name': '서울'}
  → 누락된 필드: ['population', 'famous_food', 'timezone']
```

(B) 케이스에서 모델이 세 필드를 누락했다는 점이 핵심입니다. 온도/프롬프트에 따라 일부는 채워질 수도 있지만, **생략될 수 있다**는 사실 자체가 `required` 를 빠뜨리면 안 되는 이유입니다.

## 7. 자주 하는 실수 / 다음으로 넘어가기 전 체크리스트

- [ ] `response_mime_type` 을 빠뜨려 자연어 응답이 오는 상황을 겪어봤거나 이해했다.
- [ ] 스키마 뼈대 4요소(`title`, `type`, `properties`, `required`) 를 암기했다.
- [ ] [`02_required_fields.py`](./02_required_fields.py) 로 누락 현상을 직접 봤다.
- [ ] `required` 배열을 꼼꼼히 채우는 습관이 생겼다.

다음은 [`../03_type_system/README.md`](../03_type_system/README.md) — 각 필드에 어떤 타입을 넣을 수 있는지 배웁니다.

<!-- 이 디렉토리의 .py 파일: 01_minimal_schema.py, 02_required_fields.py -->
