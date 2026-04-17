"""비교/평가(Comparison) 패턴 — 두 제품의 장단점을 표 형태로 정리.

가이드 대응: §4.5 (ProductComparison)

여러 제품 각각에 대해 장점/단점/점수를 받고, 최종 승자(winner) 와 이유(reasoning)를
함께 돌려받습니다. 상품 비교 페이지, 솔루션 평가 리포트, A/B 선택 제안 등에 유용합니다.

실행:
    cd structured_output
    python 04_design_patterns/05_comparison_products.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


SCHEMA = {
    "title": "ProductComparison",
    "type": "object",
    "properties": {
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "pros": {"type": "array", "items": {"type": "string"}},
                    "cons": {"type": "array", "items": {"type": "string"}},
                    "score": {"type": "number"},
                },
                "required": ["name", "pros", "cons", "score"],
            },
        },
        "winner": {"type": "string"},
        "reasoning": {"type": "string"},
    },
    "required": ["products", "winner", "reasoning"],
}


PROMPT = """
다음 두 가지 협업 도구 제품을 비교해줘. 각 제품의 장점 3개, 단점 2개, 0~10 점수를 매기고
최종 추천 제품(winner) 과 이유를 한 문단으로 적어줘.

A. ClearBoard — 실시간 화이트보드 협업. 무한 캔버스, 100명 동시 편집, 스티커/도형 라이브러리,
   댓글 스레드, 화상통화 내장. 무료 플랜은 보드 3개까지, 유료 월 12,000원.

B. NoteSync — 올인원 문서·위키·칸반 도구. 실시간 공동 편집, 데이터베이스 블록, API 연동,
   템플릿 갤러리. 개인 무료, 팀 사용 시 인당 월 9,000원.
"""


def main() -> None:
    data = generate_structured(
        contents=[PROMPT],
        schema=SCHEMA,
        temperature=0.3,
    )

    print("[parsed]")
    pprint(data)
    print()
    for p in data["products"]:
        print(f"== {p['name']} (score {p['score']}) ==")
        print(f"   + {'; '.join(p['pros'])}")
        print(f"   - {'; '.join(p['cons'])}")
    print()
    print(f"→ Winner: {data['winner']}")
    print(f"→ Reasoning: {data['reasoning']}")


if __name__ == "__main__":
    main()
