"""문자열 배열 — type: array + items.type: string.

가이드 대응: §3.2 Array ("tags" 예제)

태그, 키워드, 카테고리 라벨처럼 문자열 여러 개를 리스트로 받고 싶을 때 쓰는 가장 기본 패턴입니다.

실행:
    cd structured_output
    python 03_type_system/02_array_of_strings.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


def main() -> None:
    schema = {
        "title": "BlogTags",
        "type": "object",
        "properties": {
            "post_title": {"type": "string"},
            "tags": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["post_title", "tags"],
    }

    data = generate_structured(
        contents=[
            "한국에서 최근 유행하는 AI 마케팅 트렌드에 대한 블로그 글 제목 하나와 "
            "관련 태그 5개를 만들어줘."
        ],
        schema=schema,
        temperature=0.5,
    )

    print("[parsed]")
    pprint(data)
    print()
    print(f"→ 제목: {data['post_title']}")
    print(f"→ 태그: {', '.join(data['tags'])}")


if __name__ == "__main__":
    main()
