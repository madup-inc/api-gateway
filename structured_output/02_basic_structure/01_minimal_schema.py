"""가장 단순한 Structured Output — 단일 문자열 필드.

가이드 대응: §2.2 (Schema 기본 구조)

스키마의 최소 모양은 "type: object, properties: {한 필드}" 입니다.
이 예제는 한 필드만 있는 스키마로도 Structured Output 이 동작하는 걸 보여줍니다.

실행:
    cd structured_output
    python 02_basic_structure/01_minimal_schema.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


def main() -> None:
    # title, type, properties — 이 세 필드가 스키마의 골격.
    schema = {
        "title": "Greeting",
        "type": "object",
        "properties": {
            "message": {"type": "string"},
        },
        "required": ["message"],
    }

    data = generate_structured(
        contents=["한국어로 따뜻한 아침 인사를 한 문장 만들어줘."],
        schema=schema,
        temperature=0.7,
    )

    print("[parsed]")
    pprint(data)
    print()
    print(f"→ 모델의 인사: {data['message']}")


if __name__ == "__main__":
    main()
