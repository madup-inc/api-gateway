# common — 공통 헬퍼

## 📍 README 맵

| 위치 | 한 줄 요약 |
|---|---|
| [리포 루트 README](../../README.md) | api-gateway 리포 전체 안내 |
| [structured_output/README.md](../README.md) | Structured Output 튜토리얼 로드맵 |
| [common/README.md](./README.md) | 공통 헬퍼(config, client) 사용법 ← **현재** |
| [01_introduction/README.md](../01_introduction/README.md) | Structured Output 첫 만남 |
| [02_basic_structure/README.md](../02_basic_structure/README.md) | `response_mime_type` · `response_schema` |
| [03_type_system/README.md](../03_type_system/README.md) | string · integer · array · object · enum |
| [04_design_patterns/README.md](../04_design_patterns/README.md) | 분류 · 추출 · 분석 · 변환 · 비교 |
| [05_pydantic/README.md](../05_pydantic/README.md) | Pydantic으로 스키마 정의 |
| [06_error_handling/README.md](../06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](../07_best_practices/README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](../07_best_practices/templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 이 디렉토리가 존재하는 이유

튜토리얼의 모든 챕터가 공통으로 쓰는 두 가지가 있습니다.

1. **접속 정보**: `BASE_URL`, `API_KEY`, 인증 헤더. 환경 변수로 관리해야 깃에 커밋되지 않습니다.
2. **요청 함수**: 게이트웨이에 POST를 보내고 `parsed` 를 꺼내는 로직. 매 예제마다 같은 코드를 복붙하면 예제가 지저분해지고, 정작 보여주려는 **스키마**가 묻혀 버립니다.

그래서 이 두 가지를 `common/` 에 한 번만 정의하고, 챕터 2부터는 한 줄 import 로 씁니다.

```python
from common import generate_structured

data = generate_structured(
    contents=["서울의 인구와 면적을 알려줘."],
    schema={...},
    temperature=0.3,
)
```

> 📎 챕터 1 ([`01_introduction/01_hello_structured.py`](../01_introduction/01_hello_structured.py))만 예외입니다. 거기서는 헬퍼 없이 `requests.post` 를 직접 써서 **응답 구조 전체**를 보여줍니다. "헬퍼가 안쪽에서 뭘 하는지" 를 챕터 1에서 눈으로 본 뒤, 챕터 2부터는 안심하고 헬퍼를 쓰는 흐름입니다.

---

## 파일 구성

| 파일 | 역할 |
|---|---|
| [`__init__.py`](./__init__.py) | 패키지 진입점. `generate_structured`, `BASE_URL`, `HEADERS` 를 재노출합니다. |
| [`config.py`](./config.py) | `.env` 로딩과 게이트웨이 접속 정보(`BASE_URL`, `HEADERS`, `TIMEOUT_SECONDS`). |
| [`client.py`](./client.py) | `generate_structured()` 함수와 `GenerationError` 예외. 가이드 §6.3 구현체. |

---

## `config.py` 파헤치기

핵심은 세 개의 상수와 한 개의 헬퍼입니다.

| 이름 | 타입 | 설명 |
|---|---|---|
| `BASE_URL` | `str` | 게이트웨이 루트 URL. 끝 슬래시 자동 제거. |
| `HEADERS` | `dict[str, str]` | 요청 헤더. 기본은 `Authorization: Bearer <API_KEY>`. |
| `TIMEOUT_SECONDS` | `int` | 요청 타임아웃. 기본 30초. |
| `require_api_key()` | 함수 | API_KEY가 비어 있으면 즉시 친절한 에러. |

### `.env` 로딩

[`config.py`](./config.py) 가 임포트되는 순간 `structured_output/.env` 파일을 읽어 `os.environ` 에 로드합니다. `.env` 가 없으면 조용히 스킵하고 OS 환경 변수를 그대로 씁니다.

`.env` 설정 시 자주 하는 실수:

- 값 전체를 따옴표로 감싼다: `API_KEY="abcd"` → 따옴표까지 값에 포함됩니다. **따옴표 없이** 적으세요.
- 등호 앞뒤에 공백: `API_KEY = abcd` → 공백이 키 이름과 값에 들어갑니다. 공백 없이.
- 마지막 줄 개행 누락: 대부분 편집기가 자동 처리하지만, 문제 시 한 줄 개행을 추가.

### 인증 헤더를 바꾸고 싶을 때

게이트웨이가 `X-API-Key` 같은 다른 헤더를 요구한다면 [`config.py`](./config.py) 의 `HEADERS` 딕셔너리만 바꾸면 모든 챕터가 자동으로 적용됩니다.

```python
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}
```

---

## `client.py` 파헤치기

함수는 단 하나: `generate_structured(contents, schema, *, model, **config_opts)`.

### 시그니처

| 파라미터 | 타입 | 설명 |
|---|---|---|
| `contents` | `str \| list[str]` | LLM 입력. 문자열 하나만 줘도 내부에서 리스트로 감쌉니다. |
| `schema` | `dict` | `response_schema` 로 쓸 JSON Schema. Pydantic이라면 `Model.model_json_schema()`. |
| `model` | `str` | 기본 `gemini-3-flash-preview`. |
| `**config_opts` | — | `temperature`, `max_output_tokens`, `thinking_level` 등 config 에 얹을 추가 옵션. |

### 반환 & 예외

- **정상**: 파싱된 `dict` 또는 `list` (스키마 최상위가 array 인 경우).
- **실패**: `GenerationError` 를 던집니다. 메시지에 어떤 단계에서 실패했는지 (status, MAX_TOKENS, SAFETY, JSON 파싱) 구체적으로 들어갑니다.

### 가이드 §6.3 과의 1:1 대응

[`client.py`](./client.py) 주석에는 `# [가이드 §6.1]`, `# [가이드 §6.2]`, `# [가이드 §6.3]` 라벨을 남겨 두었습니다. 가이드 문서를 옆에 펴놓고 헬퍼 코드를 읽으면 어느 줄이 어느 문단의 구현인지 바로 찾을 수 있습니다.

| 헬퍼 내 처리 | 가이드 섹션 |
|---|---|
| `status != "success"` 분기 | §6.3 상단 "status 확인" |
| `finish_reason == "MAX_TOKENS"` 분기 | §6.2 |
| `result.get("parsed") is not None` 분기 | §6.1 |
| `json.loads(result["text"])` 폴백 | §6.1 후반 |

---

## 체크리스트

처음 실행이 안 된다면 이 순서로 확인하세요.

- [ ] `structured_output/` 디렉토리에서 실행하고 있는가? (import 경로상 중요)
- [ ] `.env` 파일이 `structured_output/.env` 경로에 있는가? (`common/.env` 가 아니라 **상위**)
- [ ] `API_KEY` 값이 실제 키로 치환되었는가?
- [ ] 값에 따옴표/공백이 섞여 있지 않은가?
- [ ] 방화벽/프록시로 `BASE_URL` 에 접근 가능한가?

<!-- 이 디렉토리의 .py 파일: __init__.py, config.py, client.py -->
