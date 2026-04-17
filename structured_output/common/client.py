"""Structured Output 요청 헬퍼.

가이드 문서 §6.3 "권장 에러 처리 패턴" 의 generate_structured 함수를
그대로 구현하고, finish_reason=SAFETY 케이스와 예외 타입을 조금 다듬었습니다.

모든 예제 스크립트는 이 함수 하나만 import 하면 됩니다.

  from common import generate_structured

  data = generate_structured(
      contents=["서울의 인구와 면적을 알려줘."],
      schema={"type": "object", "properties": {...}, "required": [...]},
      temperature=0.3,
  )
"""

from __future__ import annotations

import json
from typing import Any

import requests

from .config import BASE_URL, HEADERS, TIMEOUT_SECONDS, require_api_key

DEFAULT_MODEL = "gemini-3-flash-preview"


class GenerationError(RuntimeError):
    """게이트웨이 응답이 실패 상태이거나 스키마 준수 실패로 파싱 불가일 때."""


def generate_structured(
    contents: list[str] | str,
    schema: dict[str, Any],
    *,
    model: str = DEFAULT_MODEL,
    **config_opts: Any,
) -> dict[str, Any] | list[Any]:
    """Structured Output을 요청하고 파싱된 결과(딕셔너리 또는 리스트)를 돌려줍니다.

    Parameters
    ----------
    contents:
        LLM에게 줄 사용자 입력. 문자열 하나여도 되고, 여러 턴이면 리스트.
    schema:
        response_schema 로 쓸 JSON Schema. Pydantic 모델을 쓸 경우
        Model.model_json_schema() 의 반환값을 그대로 넘기면 됩니다.
    model:
        사용할 LLM 모델 ID. 기본은 가이드 §7.2 권장값.
    **config_opts:
        temperature, max_output_tokens, thinking_level 등 config 에 얹을
        추가 옵션. response_mime_type / response_schema 는 자동 주입되니
        여기에 넣지 마세요.

    Returns
    -------
    parsed 딕셔너리 (혹은 스키마 최상위가 array면 리스트).

    Raises
    ------
    GenerationError
        게이트웨이가 실패를 반환했거나, finish_reason 이 MAX_TOKENS/SAFETY,
        또는 parsed 와 text 모두로 파싱 불가한 경우.
    """

    require_api_key()
    if isinstance(contents, str):
        contents = [contents]

    payload = {
        "payload": {
            "model": model,
            "contents": contents,
            "config": {
                "response_mime_type": "application/json",
                "response_schema": schema,
                **config_opts,
            },
        }
    }

    response = requests.post(
        f"{BASE_URL}/v1/tasks/generate-text",
        headers=HEADERS,
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()

    # [가이드 §6.3] status 확인
    if data.get("status") != "success":
        err = data.get("error", {}) or {}
        raise GenerationError(
            f"{err.get('type', 'UnknownError')}: {err.get('message', data)}"
        )

    result = data["result"]

    # [가이드 §6.2] finish_reason 확인 — MAX_TOKENS 면 JSON 이 잘렸을 수 있음
    candidates = result.get("candidates") or [{}]
    finish = candidates[0].get("finish_reason")
    if finish == "MAX_TOKENS":
        raise GenerationError(
            "MAX_TOKENS: 스키마를 단순화하거나 max_output_tokens 를 늘려주세요."
        )
    if finish == "SAFETY":
        raise GenerationError(
            "SAFETY: 콘텐츠 정책에 의해 응답이 차단되었습니다."
        )

    # [가이드 §6.1] parsed 우선, 없으면 text 수동 파싱
    if result.get("parsed") is not None:
        return result["parsed"]

    text = result.get("text")
    if text is None:
        raise GenerationError("응답에 parsed 도 text 도 없습니다.")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise GenerationError(f"text 필드 JSON 파싱 실패: {exc}") from exc
