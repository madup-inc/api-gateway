"""Structured Output 첫 호출 — 전체 흐름을 한 화면으로 보여주는 예제.

가이드 대응: §1 (Structured Output이란?), §2 (기본 구조)

이 예제는 유일하게 requests.post 를 직접 사용합니다. 이후 챕터들은 common.generate_structured 헬퍼로
같은 일을 한 줄에 처리하지만, 첫 예제만큼은 요청 페이로드와 응답 구조가 어떻게 생겼는지
한 파일 안에서 전부 볼 수 있게 남겨 두었습니다.

실행:
    cd structured_output
    python 01_introduction/01_hello_structured.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from pprint import pprint

import requests

# structured_output/ 를 sys.path 에 추가 (이 스크립트를 어디서 실행하든 common import 가능)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.config import BASE_URL, HEADERS, TIMEOUT_SECONDS, require_api_key


def main() -> None:
    require_api_key()

    # 1) 스키마 정의 — "비빔밥" 같은 한식 한 그릇 정보를 받고 싶다.
    schema = {
        "title": "FoodInfo",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "category": {"type": "string"},
            "calories": {"type": "integer"},
            "is_spicy": {"type": "boolean"},
        },
        "required": ["name", "category", "calories", "is_spicy"],
    }

    # 2) 요청 페이로드 — 가이드 §2.1 이 말하는 config.response_mime_type + response_schema 가 핵심.
    payload = {
        "payload": {
            "model": "gemini-3-flash-preview",
            "contents": ["한국 음식 '비빔밥' 의 정보를 스키마에 맞춰 알려줘."],
            "config": {
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": 0.2,
            },
        }
    }

    # 3) 호출
    response = requests.post(
        f"{BASE_URL}/v1/tasks/generate-text",
        headers=HEADERS,
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()

    # 4) 응답 전체 구조 감상 — 이 한 번만 raw 응답을 뜯어봅니다.
    print("=" * 60)
    print("[raw response]")
    print("=" * 60)
    pprint(data)

    # 5) 파싱된 결과 꺼내기 — 게이트웨이가 result.parsed 에 이미 dict 로 넣어둠.
    result = data["result"]
    parsed = result.get("parsed") or json.loads(result["text"])

    print()
    print("=" * 60)
    print("[parsed]")
    print("=" * 60)
    pprint(parsed)

    print()
    spicy_mark = "🌶️" if parsed["is_spicy"] else ""
    print(
        f"→ {parsed['name']} ({parsed['category']}) "
        f"{parsed['calories']}kcal {spicy_mark}"
    )


if __name__ == "__main__":
    main()
