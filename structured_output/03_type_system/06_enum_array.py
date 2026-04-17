"""Enum 배열 — 정해진 값 중 여러 개를 복수 선택.

가이드 대응: §3.2 Enum (categories 예제)

태그처럼 **여러 개** 골라야 하지만 후보는 미리 정해져 있을 때 쓰는 패턴입니다.
items.enum 에 후보를 넣으면, 배열의 모든 요소가 반드시 그 중 하나가 됩니다.

실행:
    cd structured_output
    python 03_type_system/06_enum_array.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


def main() -> None:
    schema = {
        "title": "NewsTopics",
        "type": "object",
        "properties": {
            "headline": {"type": "string"},
            "categories": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "tech",
                        "health",
                        "finance",
                        "sports",
                        "entertainment",
                        "politics",
                    ],
                },
            },
        },
        "required": ["headline", "categories"],
    }

    headlines = [
        "대형 제약사, 당뇨 치료 AI 모델을 FDA에 제출",
        "프로 야구 가을 시즌 개막, 티켓 판매 역대 최고",
    ]

    for text in headlines:
        data = generate_structured(
            contents=[
                f"다음 헤드라인에 해당하는 카테고리를 모두 골라줘 (최소 1개, 최대 3개):\n\n{text}"
            ],
            schema=schema,
            temperature=0.0,
        )
        print(f"→ {data['headline']}")
        print(f"   categories: {data['categories']}")
        print()


if __name__ == "__main__":
    main()
