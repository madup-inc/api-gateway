"""parsed 가 null 로 돌아오는 경우의 폴백 패턴.

가이드 대응: §6.1 (parsed 가 null 인 경우)

게이트웨이는 대부분 result.parsed 에 파싱된 dict 를 넣어주지만,
모델이 스키마를 완전히 준수하지 못한 드문 경우 parsed 가 null 일 수 있습니다.
그 때는 result.text (원시 문자열)를 json.loads 로 직접 파싱해야 합니다.

이 스크립트는 common 헬퍼를 쓰지 않고 raw 응답을 직접 다루며,
parsed / text 양쪽을 우선순위대로 처리하는 if-else 패턴을 보여줍니다.
common.generate_structured 도 내부에서 정확히 이 처리를 합니다.

실행:
    cd structured_output
    python 06_error_handling/01_parsed_null_fallback.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from pprint import pprint
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.config import BASE_URL, HEADERS, TIMEOUT_SECONDS, require_api_key


SCHEMA = {
    "title": "ShortAnswer",
    "type": "object",
    "properties": {
        "question": {"type": "string"},
        "answer": {"type": "string"},
    },
    "required": ["question", "answer"],
}


def call_raw() -> dict[str, Any]:
    """게이트웨이에 직접 POST 하고 raw data 를 돌려줍니다."""

    response = requests.post(
        f"{BASE_URL}/v1/tasks/generate-text",
        headers=HEADERS,
        json={
            "payload": {
                "model": "gemini-3-flash-preview",
                "contents": ["한국의 수도는 어디야? 한 문장으로 답해줘."],
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": SCHEMA,
                    "temperature": 0.0,
                },
            }
        },
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def safe_extract(result: dict[str, Any]) -> dict[str, Any]:
    """parsed 우선, 없으면 text 를 수동 파싱."""

    if result.get("parsed") is not None:
        print("[branch] parsed 필드 사용")
        return result["parsed"]

    text = result.get("text")
    if text is None:
        raise RuntimeError("응답에 parsed 도 text 도 없습니다.")

    print("[branch] parsed 가 null → text 수동 파싱")
    return json.loads(text)


def main() -> None:
    require_api_key()
    data = call_raw()

    if data.get("status") != "success":
        raise RuntimeError(f"게이트웨이 실패: {data}")

    result = data["result"]
    parsed = safe_extract(result)

    print()
    print("[parsed]")
    pprint(parsed)
    print()
    print(f"→ Q: {parsed['question']}")
    print(f"→ A: {parsed['answer']}")


if __name__ == "__main__":
    main()
