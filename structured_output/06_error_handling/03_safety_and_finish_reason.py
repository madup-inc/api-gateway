"""finish_reason 전반 점검 — STOP / MAX_TOKENS / SAFETY / OTHER.

가이드 대응: §6.2, §7.3 (finish_reason 을 항상 확인)

candidates[0].finish_reason 은 모델이 응답을 끝낸 이유를 알려줍니다.
이 스크립트는 raw 호출로 finish_reason 을 직접 꺼내 case-by-case 로 분기하는
패턴을 보여줍니다.

    STOP        → 정상 종료. parsed 를 쓰면 된다.
    MAX_TOKENS  → 잘림. 파싱 시도 금지, 사용자에게 재시도 안내.
    SAFETY      → 콘텐츠 정책으로 차단. 입력 프롬프트 재검토.
    그 외       → 일단 에러로 올리고 원문 로그 남기기.

실행:
    cd structured_output
    python 06_error_handling/03_safety_and_finish_reason.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.config import BASE_URL, HEADERS, TIMEOUT_SECONDS, require_api_key


SCHEMA = {
    "title": "SimpleFact",
    "type": "object",
    "properties": {"fact": {"type": "string"}},
    "required": ["fact"],
}


def call(prompt: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/v1/tasks/generate-text",
        headers=HEADERS,
        json={
            "payload": {
                "model": "gemini-3-flash-preview",
                "contents": [prompt],
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


def handle(prompt: str) -> None:
    print(f"--- Prompt: {prompt!r}")
    data = call(prompt)
    if data.get("status") != "success":
        print(f"   게이트웨이 실패: {data.get('error')}")
        return

    result = data["result"]
    finish = (result.get("candidates") or [{}])[0].get("finish_reason")
    print(f"   finish_reason = {finish}")

    match finish:
        case "STOP":
            print(f"   ✅ 정상. parsed.fact = {result['parsed']['fact']!r}")
        case "MAX_TOKENS":
            print("   ⚠️ 응답이 잘림 — 스키마 단순화 또는 max_output_tokens 증가 필요.")
        case "SAFETY":
            print("   🚫 안전 정책으로 차단됨 — 프롬프트 재검토 필요.")
        case _:
            print(f"   ❓ 예상치 못한 finish_reason. raw result:\n{result}")
    print()


def main() -> None:
    require_api_key()
    # 정상 케이스. 나머지(MAX_TOKENS/SAFETY)는 prompt 내용이나 설정에 따라
    # 게이트웨이/모델이 결정하므로, 이 스크립트는 분기 처리 "스켈레톤" 을 보여주는 게 목적입니다.
    handle("한국의 국화(國花) 는 무엇이야? fact 에 이름만 넣어줘.")


if __name__ == "__main__":
    main()
