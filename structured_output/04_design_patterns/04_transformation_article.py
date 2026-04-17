"""변환(Transformation) 패턴 — 기사 원문을 요약 + 메타데이터로 재포장.

가이드 대응: §4.4 (ArticleSummary)

원문을 받아 "제목·요약·핵심 포인트 배열·단어 수·예상 독서 시간·언어·토픽 배열"
로 재구성합니다. 한 번의 호출로 원본을 다양한 표시 용도에 쓸 메타데이터로 바꾸는
패턴이며, 블로그 백엔드·뉴스 큐레이션·콘텐츠 CMS 에서 자주 등장합니다.

실행:
    cd structured_output
    python 04_design_patterns/04_transformation_article.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


SCHEMA = {
    "title": "ArticleSummary",
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "key_points": {"type": "array", "items": {"type": "string"}},
        "word_count": {"type": "integer"},
        "reading_time_minutes": {"type": "integer"},
        "language": {"type": "string", "enum": ["ko", "en", "ja", "zh"]},
        "topics": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "title",
        "summary",
        "key_points",
        "word_count",
        "reading_time_minutes",
        "language",
        "topics",
    ],
}


ARTICLE = """
지난주 서울에서 개최된 국제 AI 컨퍼런스에는 40개국 2천여 명의 연구자가 참여했다.
기조 연설자들은 대규모 언어 모델의 효율성 개선과 도메인 특화 모델의 부상을 주요 트렌드로
꼽았다. 특히 의료·법률·금융 등 규제 산업에서 소형 고정밀 모델 수요가 급증하고 있다는
분석이 이어졌다. 한편 생성 AI 의 환경 영향에 대한 세션에서는 학습 단계의 전력 소비를
10 분의 1 로 줄일 수 있는 새로운 양자화 기법이 소개되어 큰 관심을 모았다. 한국 기업들은
독자 파운데이션 모델 확보와 함께 오픈소스 생태계 기여를 동시에 추진하는 전략을 발표했다.
"""


def main() -> None:
    data = generate_structured(
        contents=[
            "다음 기사를 요약하고 메타데이터를 추출해줘. "
            "summary 는 3문장 이내, key_points 는 3~5개.\n\n"
            + ARTICLE
        ],
        schema=SCHEMA,
        temperature=0.2,
    )

    print("[parsed]")
    pprint(data)
    print()
    print(f"→ 제목: {data['title']}")
    print(f"→ 언어: {data['language']} / 단어 {data['word_count']} / ~{data['reading_time_minutes']}분")
    print("→ 핵심 포인트:")
    for p in data["key_points"]:
        print(f"   · {p}")


if __name__ == "__main__":
    main()
