"""분석(Analysis) 패턴 — 제품 리뷰를 다관점으로 분해.

가이드 대응: §4.3 (ContentAnalysis)

점수 + 분류 + 증거 인용을 함께 받는 복합 분석. aspects 배열 각 원소가
"관점·점수·sentiment·근거 문장" 4필드를 가져서, 하나의 리뷰를
여러 측면에서 동시에 평가합니다.

실행:
    cd structured_output
    python 04_design_patterns/03_analysis_review.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


SCHEMA = {
    "title": "ContentAnalysis",
    "type": "object",
    "properties": {
        "overall_score": {"type": "number"},
        "aspects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "aspect": {"type": "string"},
                    "score": {"type": "number"},
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "negative", "neutral", "mixed"],
                    },
                    "evidence": {"type": "string"},
                },
                "required": ["aspect", "score", "sentiment", "evidence"],
            },
        },
        "strengths": {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {"type": "string"}},
        "recommendation": {"type": "string"},
    },
    "required": [
        "overall_score",
        "aspects",
        "strengths",
        "weaknesses",
        "recommendation",
    ],
}


REVIEW = """
노트북을 3개월 정도 써봤습니다. 배터리는 업무용으로 하루종일 쓸 수 있어 만족스럽습니다.
디스플레이 색감도 사진 편집에 충분히 좋고 밝기도 훌륭합니다. 다만 키보드는 키감이 얕아서
장시간 타이핑하면 손이 피로하고, 팬 소음이 게임이나 렌더링 시 꽤 거슬립니다. 가격은
성능 대비 합리적이라고 보지만, 더 저렴한 대안이 있다면 고려해볼만 합니다.
"""


def main() -> None:
    data = generate_structured(
        contents=[
            "다음 제품 리뷰를 분석해서 관점별 점수와 근거를 뽑아줘. "
            "점수는 0~10 범위, overall_score 는 관점 점수들의 가중 평균.\n\n"
            + REVIEW
        ],
        schema=SCHEMA,
        temperature=0.2,
    )

    print("[parsed]")
    pprint(data)
    print()
    print(f"→ 종합 점수: {data['overall_score']}")
    for a in data["aspects"]:
        print(f"  · {a['aspect']:<12} {a['score']:>4.1f}  [{a['sentiment']}]")


if __name__ == "__main__":
    main()
