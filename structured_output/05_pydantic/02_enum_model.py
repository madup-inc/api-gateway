"""Pydantic + Enum — str Enum 으로 허용값 제한.

가이드 대응: §5.2 (Enum 활용)

Pydantic 에서 enum 을 쓸 때는 str Enum 을 섞어 선언합니다. 그래야
model_json_schema() 가 자동으로 "enum": [...] 필드를 JSON Schema 에 심어주고,
응답 dict 를 모델로 되돌릴 때도 문자열→Enum 으로 잘 변환됩니다.

실행:
    cd structured_output
    python 05_pydantic/02_enum_model.py
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from pprint import pprint

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class TicketAnalysis(BaseModel):
    title: str
    sentiment: Sentiment
    priority: Priority
    tags: list[str]


TICKETS = [
    "결제 API 가 500 을 뱉습니다. 어제까지는 잘 됐는데 오늘부터 안 돼요. 고객 결제가 막혔습니다.",
    "다크 모드가 있으면 눈이 편할 것 같아요. 추가 부탁드립니다.",
]


def main() -> None:
    schema = TicketAnalysis.model_json_schema()
    for i, text in enumerate(TICKETS, 1):
        data = generate_structured(
            contents=[f"아래 티켓을 분석해 title/sentiment/priority/tags 로 정리해줘.\n\n{text}"],
            schema=schema,
            temperature=0.1,
            thinking_level="low",
        )
        ticket = TicketAnalysis(**data)
        print(f"=== Ticket #{i} ===")
        pprint(data)
        print(
            f"→ {ticket.title} | sentiment={ticket.sentiment.value} "
            f"priority={ticket.priority.value} tags={ticket.tags}"
        )
        print()


if __name__ == "__main__":
    main()
