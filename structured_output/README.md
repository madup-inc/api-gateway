# structured_output — Structured Output 튜토리얼

## 📍 README 맵

| 위치 | 한 줄 요약 |
|---|---|
| [리포 루트 README](../README.md) | api-gateway 리포 전체 안내 |
| [structured_output/README.md](./README.md) | Structured Output 튜토리얼 로드맵 ← **현재** |
| [common/README.md](./common/README.md) | 공통 헬퍼(config, client) 사용법 |
| [01_introduction/README.md](./01_introduction/README.md) | Structured Output 첫 만남 |
| [02_basic_structure/README.md](./02_basic_structure/README.md) | `response_mime_type` · `response_schema` |
| [03_type_system/README.md](./03_type_system/README.md) | string · integer · array · object · enum |
| [04_design_patterns/README.md](./04_design_patterns/README.md) | 분류 · 추출 · 분석 · 변환 · 비교 |
| [05_pydantic/README.md](./05_pydantic/README.md) | Pydantic으로 스키마 정의 |
| [06_error_handling/README.md](./06_error_handling/README.md) | `parsed=null` · `MAX_TOKENS` 대응 |
| [07_best_practices/README.md](./07_best_practices/README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](./07_best_practices/templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 이 튜토리얼이 풀어주는 문제

LLM 을 실서비스에 쓸 때 가장 귀찮은 순간은 **응답을 코드로 처리해야 할 때**입니다. 자연어로 돌아오는 답변은 사람이 읽기엔 좋지만, `json.loads` 를 돌리면 깨지기 일쑤고 포맷이 응답마다 달라 파싱 코드가 누더기가 됩니다.

**Structured Output** 은 이 문제를 JSON Schema 로 해결합니다. 요청에 스키마를 같이 넣어 주면, 게이트웨이 뒤의 모델은 **정해진 구조**로만 응답합니다. 파싱은 무조건 성공하고, 필드 이름/타입이 약속대로라서 Pydantic 모델에 바로 통과시킬 수 있습니다.

이 튜토리얼은 원본 문서 [`../Structured_Output_Usage_Guide.md`](../Structured_Output_Usage_Guide.md) 의 모든 섹션을 **실행 가능한 예제 스크립트**로 풀어낸 학습용 리포입니다. 처음부터 끝까지 순서대로 따라가면 스키마 설계의 기본 → 복잡한 패턴 → 에러 처리 → 베스트 프랙티스까지 자연스럽게 익히게 됩니다.

---

## 대상 독자

- 게이트웨이를 처음 써보는 개발자
- LLM 으로 JSON 을 받아 DB 에 저장하거나 파이프라인에 태우고 싶은 개발자
- 문서로만 읽었을 때 감이 안 와서 **돌려보면서 배우고 싶은** 분

Python 기초 (dict/list, 함수 정의, import) 만 알면 충분합니다. 타입 힌트는 예제에서 쓰지만, 몰라도 읽는 데 지장 없게 주석을 달았습니다.

---

## 디렉토리 구성

```
structured_output/
├── README.md                  ← 지금 읽는 파일
├── requirements.txt           의존성 (requests, pydantic, python-dotenv)
├── .env.example               BASE_URL / API_KEY 템플릿
├── common/                    모든 챕터가 공유하는 config + client 헬퍼
├── 01_introduction/           Structured Output이 뭔지 맛보기
├── 02_basic_structure/        response_mime_type / response_schema 뼈대
├── 03_type_system/            string · number · array · object · enum
├── 04_design_patterns/        분류 · 추출 · 분석 · 변환 · 비교 5대 패턴
├── 05_pydantic/               JSON Schema 대신 Pydantic으로 정의
├── 06_error_handling/         parsed null, MAX_TOKENS, 폴백 전략
└── 07_best_practices/         헬퍼 해설 + 복붙용 JSON 스키마 템플릿
```

각 챕터 안에는 **README + 번호 매긴 스크립트들**이 있습니다. README 가 개념을 설명하고 각 스크립트로 링크를 걸어 두었으니, 디렉토리를 왔다갔다 하지 않고 README 하나만 봐도 해당 챕터 전부를 파악할 수 있습니다.

---

## 학습 로드맵

```
01_introduction
      ↓  "뭔지 봤다"
02_basic_structure
      ↓  "최소한의 스키마를 쓸 줄 안다"
03_type_system
      ↓  "타입 다섯 개를 조립할 수 있다"
04_design_patterns
      ↓  "실제 업무 시나리오 5개를 할 수 있다"
05_pydantic
      ↓  "JSON Schema 수작성에서 벗어났다"
06_error_handling
      ↓  "실패 케이스를 다룰 줄 안다"
07_best_practices
           "프로덕션 수준으로 다듬었다"
```

1–2 번은 30분이면 끝나고, 3–4 번에서 실제 쓸 수 있는 패턴이 몸에 붙습니다. 5 번부터는 선택이지만 권장입니다.

---

## 사전 준비

### 1) 의존성 설치

```bash
cd structured_output
python -m venv .venv && source .venv/bin/activate   # 선택: 가상환경
pip install -r requirements.txt
```

### 2) `.env` 설정

```bash
cp .env.example .env
# .env 를 열어 API_KEY 를 실제 값으로 바꾸세요.
```

`.env` 의 값에 **따옴표나 공백을 넣지 않는** 것만 주의하면 됩니다.

### 3) 스모크 테스트

```bash
python -m 01_introduction.01_hello_structured
```

화면에 JSON 이 찍히면 성공입니다.

---

## 실행 규약 (중요)

모든 스크립트는 **`structured_output/` 디렉토리에서** `python -m <chapter>.<script>` 형태로 실행합니다.

```bash
# ✅ 올바른 실행
cd structured_output
python -m 04_design_patterns.02_extraction_invoice

# ❌ 동작하지 않음 (상대 import 실패)
python structured_output/04_design_patterns/02_extraction_invoice.py
```

`python -m` 형태로 실행해야 `from common import generate_structured` import 가 정상 동작합니다.

---

## 문제 해결 FAQ

| 증상 | 원인 / 해결 |
|---|---|
| `ModuleNotFoundError: No module named 'common'` | `structured_output/` 바깥에서 실행했거나 `python -m` 대신 파일 경로로 실행 중. 위 [실행 규약](#실행-규약-중요) 참고. |
| `RuntimeError: API_KEY 가 비어 있습니다` | `.env` 파일이 없거나 키가 비어 있음. `cp .env.example .env` 후 값 채우기. |
| `requests.exceptions.ConnectionError` | 사내망/VPN 연결 또는 `BASE_URL` 오타. 브라우저로 `BASE_URL` 에 접속 확인. |
| `GenerationError: MAX_TOKENS` | 응답이 중간에 잘림. 스키마를 단순화하거나 `max_output_tokens` 증가. 자세한 해설은 [06_error_handling](./06_error_handling/README.md). |
| `parsed` 가 `None` 으로 돌아옴 | 스키마 준수 실패. 헬퍼가 `text` 필드를 폴백으로 파싱함. 스키마 단순화 권장. |
| 결과가 매번 다르게 나옴 | `temperature` 가 높음. 스키마 준수가 중요한 작업은 `0.0 ~ 0.3` 권장 (가이드 §7.2). |
| enum 값이 스펙에 없는 문자로 나옴 | 프롬프트에 "다음 중 하나" 명시 안 했거나 enum 후보가 너무 많음. 후보 수 줄이기. |

---

## 원본 가이드와의 관계

이 튜토리얼의 모든 예제는 원본 가이드 [`../Structured_Output_Usage_Guide.md`](../Structured_Output_Usage_Guide.md) 의 어느 섹션에 대응하는지 스크립트 독스트링과 챕터 README 에 명시되어 있습니다. **공식 레퍼런스는 원본 가이드**이고, 이 리포는 그걸 **돌려보며 익히기 좋게** 풀어 쓴 학습용입니다.
