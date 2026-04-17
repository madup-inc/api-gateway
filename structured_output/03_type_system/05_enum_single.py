"""단일 enum — 정해진 값 중 하나만 허용.

가이드 대응: §3.2 Enum (sentiment 예제)

분류, 등급, 상태 필드처럼 **모델이 자유 문자열로 뱉으면 안 되는** 필드에 필수입니다.
enum 후보가 5개 이하일 때 스키마 준수율이 가장 안정적입니다.

실행:
    cd structured_output
    python 03_type_system/05_enum_single.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


def main() -> None:
    schema = {
        "title": "ReviewSentiment",
        "type": "object",
        "properties": {
            "review_excerpt": {"type": "string"},
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral"],
            },
        },
        "required": ["review_excerpt", "sentiment"],
    }

    reviews = [
        "배송이 엄청 빠르고 포장도 꼼꼼했어요. 완전 만족!",
        "상품 설명과 달라서 반품했어요. 시간 낭비였음.",
        "가격 대비 무난한 편. 특별히 좋지도 나쁘지도 않네요.",
    ]

    for text in reviews:
        data = generate_structured(
            contents=[f"다음 리뷰의 감성을 분류해줘:\n\n{text}"],
            schema=schema,
            temperature=0.0,
        )
        print(f"[{data['sentiment']:>8}] {data['review_excerpt']}")


if __name__ == "__main__":
    main()
