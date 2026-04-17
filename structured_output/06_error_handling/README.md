# 06_error_handling — 실패 케이스 다루기

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
| [06_error_handling/README.md](./README.md) | `parsed=null` · `MAX_TOKENS` 대응 ← **현재** |
| [07_best_practices/README.md](../07_best_practices/README.md) | 베스트 프랙티스 + 헬퍼 해설 |
| [07_best_practices/templates/README.md](../07_best_practices/templates/README.md) | 복붙용 JSON 스키마 템플릿 |

---

## 1. 이 챕터에서 얻어갈 것

- Structured Output 응답에서 확인해야 하는 **두 지점** (`result.parsed` 유무, `candidates[0].finish_reason`) 을 놓치지 않는 습관을 기릅니다.
- `parsed` 가 `null` 일 때의 폴백 패턴, `MAX_TOKENS` / `SAFETY` 분기 처리를 손끝에 익힙니다.
- 이후 [`07_best_practices`](../07_best_practices/README.md) 에서 소개하는 헬퍼 함수가 이 챕터의 처리를 어떻게 "한 줄"로 감싸는지 이해하기 위한 기반을 다집니다.

## 2. 언제 이 개념이 필요한가?

프로덕션에서 거의 100% 마주치는 상황들입니다.

- 모델이 어쩌다 스키마를 살짝 어기면 `parsed` 가 `null`. 예외 없이 뻗는 서버 = 장애.
- 긴 응답을 요구했는데 `max_output_tokens` 여유가 부족하면 `MAX_TOKENS` 로 중단. JSON 이 중간에 잘려 그대로 파싱하면 **틀린 데이터**가 흘러갑니다.
- 특정 프롬프트가 안전 정책에 걸리면 `SAFETY`. 사용자에게 "재시도해주세요" 로 안내해야지 서버가 크래시나면 안 됩니다.

## 3. 핵심 개념 요약

### 응답에서 반드시 읽을 두 자리

```
data["status"]                                    # success / fail
data["result"]["candidates"][0]["finish_reason"]  # STOP / MAX_TOKENS / SAFETY / ...
data["result"]["parsed"]                          # 정상이면 dict, 아니면 null
data["result"]["text"]                            # 항상 원시 JSON 문자열
```

### 처리 순서 (가이드 §6.3 권장)

```
1. status != "success" → 게이트웨이 에러로 간주, 즉시 실패
2. finish_reason == "MAX_TOKENS"  → 파싱 금지, 즉시 실패
   finish_reason == "SAFETY"      → 파싱 금지, 즉시 실패
3. parsed != null → parsed 그대로 사용
4. parsed == null → json.loads(text) 로 폴백
```

세 갈래가 있지만 규칙은 단순합니다. [`01_parsed_null_fallback.py`](./01_parsed_null_fallback.py) 가 3–4 단계를, [`02_max_tokens.py`](./02_max_tokens.py) 가 2 단계를 각각 실습합니다.

### 왜 `text` 가 폴백으로 쓰이나?

게이트웨이가 `parsed` 를 만들 때 내부적으로 이미 `json.loads(text)` 를 시도합니다. 그게 실패했을 때 `parsed=null` 이 되는 것이고, 이런 경우 `text` 는 "모델이 내놓은 원본" 이라서 약간 다른 파싱 전략(전후 trim, json5 허용 등)을 직접 시도해볼 여지가 있습니다. 이 튜토리얼에선 `json.loads` 만 쓰지만, 현업에서는 `demjson3`, `json_repair` 같은 관용적 파서를 시도하기도 합니다.

## 4. 스크립트 한눈에 보기

| 파일 | 주제 | 핵심 |
|---|---|---|
| [`01_parsed_null_fallback.py`](./01_parsed_null_fallback.py) | parsed/text 폴백 | raw 호출로 if-else 분기를 육안 확인 |
| [`02_max_tokens.py`](./02_max_tokens.py) | MAX_TOKENS 재현 | `max_output_tokens=20` 으로 강제 실패 → `GenerationError` 캐치 |
| [`03_safety_and_finish_reason.py`](./03_safety_and_finish_reason.py) | finish_reason 전반 | match 문으로 STOP/MAX_TOKENS/SAFETY/기타 분기하는 스켈레톤 |

## 5. 실행 방법

```bash
cd structured_output
python 06_error_handling/01_parsed_null_fallback.py
python 06_error_handling/02_max_tokens.py
python 06_error_handling/03_safety_and_finish_reason.py
```

## 6. 예상 출력

### `01_parsed_null_fallback.py`

```
[branch] parsed 필드 사용

[parsed]
{'answer': '서울입니다.', 'question': '한국의 수도는 어디야?'}

→ Q: 한국의 수도는 어디야?
→ A: 서울입니다.
```

> 대부분의 경우 `parsed` 가 살아 있어 `[branch] parsed 필드 사용` 이 찍힙니다. `[branch] parsed 가 null → text 수동 파싱` 을 강제로 재현하기는 어렵지만, 이 분기 구조만큼은 프로덕션 코드에 반드시 넣어야 합니다.

### `02_max_tokens.py`

```
✅ 예상대로 에러가 발생했습니다.
   에러 메시지: MAX_TOKENS: 스키마를 단순화하거나 max_output_tokens 를 늘려주세요.

해결책 (가이드 §6.2):
  1) 스키마를 단순화한다 (필드를 줄이거나 key_points 길이를 제한).
  2) max_output_tokens 를 더 크게 지정한다 (기본값 사용 권장).
```

### `03_safety_and_finish_reason.py`

```
--- Prompt: '한국의 국화(國花) 는 무엇이야? fact 에 이름만 넣어줘.'
   finish_reason = STOP
   ✅ 정상. parsed.fact = '무궁화'
```

## 7. 자주 하는 실수 / 다음으로 넘어가기 전 체크리스트

- [ ] `parsed` 가 항상 있다고 가정하지 않는다. `result.get("parsed")` 로 안전 조회 후 None 체크.
- [ ] `finish_reason` 을 **parsed 보다 먼저** 확인한다. `MAX_TOKENS` 로 잘린 `text` 를 `json.loads` 하면 에러가 나거나, 더 나쁘게는 **부분 JSON 이 valid** 해 보여 틀린 데이터가 흘러간다.
- [ ] 에러 메시지에 `finish_reason` 값 자체를 포함시켜 관측성을 높인다.
- [ ] `use_retry: true` (게이트웨이 기본값) 를 유지해 일시 오류는 게이트웨이에서 자동 재시도되게 한다.

다음은 [`../07_best_practices/README.md`](../07_best_practices/README.md) — 지금까지의 모든 조언을 묶은 체크리스트 + 헬퍼 함수 해설입니다.

<!-- 이 디렉토리의 .py 파일: 01_parsed_null_fallback.py, 02_max_tokens.py, 03_safety_and_finish_reason.py -->
