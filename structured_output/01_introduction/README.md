# 01_introduction — Structured Output 첫 만남

## 📍 README 맵

| 위치 | 한 줄 요약 |
|---|---|
| [리포 루트 README](../../README.md) | api-gateway 리포 전체 안내 |
| [structured_output/README.md](../README.md) | Structured Output 튜토리얼 로드맵 |
| [common/README.md](../common/README.md) | 공통 헬퍼(config, client) 사용법 |
| [01_introduction/README.md](./README.md) | Structured Output 첫 만남 ← **현재** |
| [02_basic_structure/README.md](../02_basic_structure/README.md) | `response_mime_type` · `response_schema` |
| [03_type_system/README.md](../03_type_system/README.md) | string · integer · array · object · enum |
| [04_design_patterns/README.md](../04_design_patterns/README.md) | 분류 · 추출 · 분석 · 변환 · 비교 |
| [05_pydantic/README.md](../05_pydantic/README.md) | Pydantic으로 스키마 정의 |
| [06_error_handling/README.md](../06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](../07_best_practices/README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](../07_best_practices/templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 1. 이 챕터에서 얻어갈 것

- Structured Output 이 **무엇인지** 한 번의 API 호출로 체감합니다.
- 요청 페이로드에서 `config.response_mime_type`, `config.response_schema` 두 필드가 어떤 역할을 하는지 눈으로 확인합니다.
- 응답 JSON 에서 `result.parsed` 와 `result.text` 가 어떻게 생겼는지 실제 형태를 봅니다.

다음 챕터부터는 이 복잡한 구조를 `common.generate_structured` 헬퍼가 감춥니다. 그래서 "헬퍼 안쪽에 뭐가 있는지" 를 알고 넘어가려고 이 챕터만큼은 `requests.post` 를 그대로 씁니다.

## 2. 언제 이 개념이 필요한가?

LLM 응답을 사람이 읽기만 할 거면 자연어로 받아도 됩니다. 하지만 이런 순간엔 Structured Output 이 필요합니다.

- 응답을 DB 의 컬럼에 그대로 저장해야 한다.
- 다음 파이프라인(Slack 알림, BI 대시보드, 후속 API 호출)이 특정 필드명을 기대한다.
- 분류 결과가 **정해진 몇 개의 라벨** 중 하나여야 한다.

예를 들어 고객 리뷰 100건을 긍/부정 라벨로 집계하고 싶은데, 모델이 "이 리뷰는 긍정적입니다", "매우 좋아요!", "👍" 처럼 매번 다르게 답하면 집계가 불가능합니다. 스키마로 `{"sentiment": "positive"|"negative"|"neutral"}` 을 강제하면 끝입니다.

## 3. 핵심 개념 요약

Structured Output 을 켜는 스위치는 두 필드입니다.

```json
"config": {
  "response_mime_type": "application/json",
  "response_schema": { "type": "object", "properties": { ... } }
}
```

- `response_mime_type` 을 `"application/json"` 으로 지정하면 게이트웨이/모델이 **자연어 모드에서 JSON 모드로 전환**됩니다.
- `response_schema` 는 받고 싶은 JSON 의 모양을 JSON Schema 문법으로 적습니다.

요청이 성공하면 응답의 `result.parsed` 에 **이미 파싱된 딕셔너리**가 들어옵니다. `json.loads` 를 돌릴 필요도 없죠. 다만 드물게 스키마 준수 실패로 `parsed` 가 `null` 일 수 있고, 그 때는 `result.text` 를 직접 파싱해야 합니다 — 폴백 이야기는 [06_error_handling](../06_error_handling/README.md) 에서 자세히 다룹니다.

## 4. 스크립트 한눈에 보기

| 파일 | 설명 |
|---|---|
| [`01_hello_structured.py`](./01_hello_structured.py) | `requests.post` 로 직접 호출해 요청 페이로드와 raw 응답을 전부 출력. "비빔밥" 정보를 4개 필드로 받음. |

이 챕터는 의도적으로 파일이 **하나**입니다. 여러 예제를 한 번에 쏟아붓기 전에, 하나의 호출 흐름을 완전히 이해하는 게 목표입니다. 스크립트 코드에서 주석 번호 (1)~(5) 로 나눠둔 다섯 단계를 따라 읽어보세요.

## 5. 실행 방법

```bash
cd structured_output
python 01_introduction/01_hello_structured.py
```

사전 준비(`.env` 설정, `pip install -r requirements.txt`)는 [`../README.md`](../README.md) 의 "사전 준비" 섹션을 참고하세요.

## 6. 예상 출력

실제 응답은 모델 상태에 따라 조금씩 다르지만, 대략 다음과 같은 모양을 봅니다.

```
============================================================
[raw response]
============================================================
{'status': 'success',
 'result': {'candidates': [{'finish_reason': 'STOP', ...}],
            'parsed': {'calories': 550,
                       'category': '한식',
                       'is_spicy': True,
                       'name': '비빔밥'},
            'text': '{"name": "비빔밥", "category": "한식", ...}'}}

============================================================
[parsed]
============================================================
{'calories': 550, 'category': '한식', 'is_spicy': True, 'name': '비빔밥'}

→ 비빔밥 (한식) 550kcal 🌶️
```

핵심은 `parsed` 에 이미 dict 가 들어 있다는 점입니다. 이 dict 를 바로 함수 인자로, DB 레코드로, JSON 응답으로 흘려보낼 수 있습니다.

## 7. 자주 하는 실수 / 다음으로 넘어가기 전 체크리스트

- [ ] 실행 위치가 `structured_output/` 이다. (`common` import 가 이 가정을 깔고 있음)
- [ ] `.env` 에 API_KEY 를 채워뒀다. (안 채웠으면 실행 즉시 친절한 에러가 뜸)
- [ ] [`01_hello_structured.py`](./01_hello_structured.py) 의 주석 (1) ~ (5) 를 눈으로 따라 읽었다.
- [ ] `parsed` 와 `text` 가 응답 안에 동시에 들어 있음을 확인했다.

이 4개가 체크됐다면 [`../02_basic_structure/README.md`](../02_basic_structure/README.md) 로 넘어가세요.

<!-- 이 디렉토리의 .py 파일: 01_hello_structured.py -->
