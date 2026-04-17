"""분류(Classification) 패턴 — 지원 티켓 자동 분류.

가이드 대응: §4.1 (TicketClassification)

지원 티켓 본문을 받아 카테고리·우선순위·담당 팀으로 분류합니다.
모든 라벨 필드는 enum 으로 제한해 사후 집계/라우팅이 깨지지 않게 합니다.

실행:
    cd structured_output
    python 04_design_patterns/01_classification_ticket.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


SCHEMA = {
    "title": "TicketClassification",
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["bug", "feature_request", "question", "improvement"],
        },
        "priority": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"],
        },
        "assigned_team": {
            "type": "string",
            "enum": ["backend", "frontend", "infra", "data", "design"],
        },
        "summary": {"type": "string"},
    },
    "required": ["category", "priority", "assigned_team", "summary"],
}


TICKETS = [
    "로그인 버튼을 눌러도 아무 반응이 없습니다. 어제 배포 이후부터 안 돼요. 프로덕션입니다.",
    "대시보드 차트에 데이터 필터 기능을 추가해 주시면 좋겠습니다. 지금은 전체만 보여서 불편합니다.",
    "API 호출할 때 403 이 뜨는데 어떤 권한이 필요한가요?",
]


def main() -> None:
    for i, ticket in enumerate(TICKETS, start=1):
        data = generate_structured(
            contents=[
                "아래 지원 티켓을 분류해줘. summary 는 한 문장으로.\n\n"
                f"티켓 #{i}:\n{ticket}"
            ],
            schema=SCHEMA,
            temperature=0.1,
            thinking_level="low",
        )
        print(f"=== Ticket #{i} ===")
        pprint(data)
        print()


if __name__ == "__main__":
    main()
