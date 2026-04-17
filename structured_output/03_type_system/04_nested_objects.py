"""중첩 객체 — object 안에 object.

가이드 대응: §3.2 Object (address/coordinates 예제)

주소처럼 자연스레 계층이 있는 데이터를 받을 때 씁니다. 깊이는 3단계 이하로
유지하라는 가이드 §7.1 권장을 지키면 토큰도 아끼고 스키마 준수율도 올라갑니다.

실행:
    cd structured_output
    python 03_type_system/04_nested_objects.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


def main() -> None:
    schema = {
        "title": "Place",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "district": {"type": "string"},
                    "coordinates": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lng": {"type": "number"},
                        },
                        "required": ["lat", "lng"],
                    },
                },
                "required": ["city", "district", "coordinates"],
            },
        },
        "required": ["name", "address"],
    }

    data = generate_structured(
        contents=["대한민국 서울에 있는 유명한 고궁 한 곳을 스키마에 맞춰 알려줘."],
        schema=schema,
        temperature=0.2,
    )

    print("[parsed]")
    pprint(data)
    print()
    addr = data["address"]
    print(
        f"→ {data['name']} — {addr['city']} {addr['district']} "
        f"({addr['coordinates']['lat']:.4f}, {addr['coordinates']['lng']:.4f})"
    )


if __name__ == "__main__":
    main()
