"""common.generate_structured 헬퍼 해설 — 가이드 §6.3 과 1:1 매핑.

이 스크립트는 common/client.py 의 함수를 "처음부터 다시 짓는" 연습입니다.
같은 로직을 inline 으로 펼쳐 놓고 각 단계에 가이드 섹션 라벨을 달아두어,
헬퍼가 내부에서 어떤 보호 장치를 제공하는지 한눈에 볼 수 있게 했습니다.

실제로 이 스크립트가 만들어내는 결과는 common.generate_structured 로 같은 요청을 보낸
결과와 동일합니다. 하단에서 두 호출을 비교해 보여줍니다.

가이드 대응: §6.3 (권장 에러 처리 패턴), §7 (베스트 프랙티스)

실행:
    cd structured_output
    python 07_best_practices/01_robust_helper_walkthrough.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from pprint import pprint
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured
from common.config import BASE_URL, HEADERS, TIMEOUT_SECONDS, require_api_key


SCHEMA = {
    "title": "CityInfo",
    "type": "object",
    "properties": {
        "city": {"type": "string"},
        "population": {"type": "integer"},
        "area_km2": {"type": "number"},
    },
    "required": ["city", "population", "area_km2"],
}


class GenerationError(RuntimeError):
    """학습용 재정의. 실제 코드는 common.GenerationError 를 그대로 쓰세요."""


def inline_generate_structured(
    contents: list[str] | str,
    schema: dict[str, Any],
    **config_opts: Any,
) -> dict[str, Any]:
    """common.generate_structured 를 풀어 쓴 버전 — 학습 목적."""

    # [가이드 §7.3] 입력 검증: 호출 전에 API_KEY 존재 확인
    require_api_key()
    if isinstance(contents, str):
        contents = [contents]

    # [가이드 §2.1] config 두 필드는 자동 주입: response_mime_type + response_schema
    payload = {
        "payload": {
            "model": "gemini-3-flash-preview",
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
        timeout=TIMEOUT_SECONDS,  # [가이드 §7.3] 타임아웃 필수
    )
    response.raise_for_status()
    data = response.json()

    # [가이드 §6.3] 단계 1: status 확인
    if data.get("status") != "success":
        err = data.get("error", {}) or {}
        raise GenerationError(
            f"{err.get('type', 'UnknownError')}: {err.get('message', data)}"
        )

    result = data["result"]

    # [가이드 §6.2] 단계 2: finish_reason 확인 — parsed 보다 먼저!
    finish = (result.get("candidates") or [{}])[0].get("finish_reason")
    if finish == "MAX_TOKENS":
        raise GenerationError(
            "MAX_TOKENS: 스키마를 단순화하거나 max_output_tokens 를 늘려주세요."
        )
    if finish == "SAFETY":
        raise GenerationError(
            "SAFETY: 콘텐츠 정책에 의해 응답이 차단되었습니다."
        )

    # [가이드 §6.1] 단계 3: parsed 우선
    if result.get("parsed") is not None:
        return result["parsed"]

    # [가이드 §6.1] 단계 4: text 수동 파싱 폴백
    text = result.get("text")
    if text is None:
        raise GenerationError("응답에 parsed 도 text 도 없습니다.")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise GenerationError(f"text 필드 JSON 파싱 실패: {exc}") from exc


def main() -> None:
    prompt = "서울의 인구와 면적을 알려줘."

    print("=== (A) inline 버전 ===")
    inline_data = inline_generate_structured(prompt, SCHEMA, temperature=0.2)
    pprint(inline_data)

    print()
    print("=== (B) common.generate_structured ===")
    helper_data = generate_structured(prompt, SCHEMA, temperature=0.2)
    pprint(helper_data)

    print()
    print("두 결과는 스키마 준수 관점에서 동등합니다.")
    print("common 패키지는 이 모든 보호 장치를 기본 제공하므로, 평소엔 그냥 헬퍼를 쓰세요.")


if __name__ == "__main__":
    main()
