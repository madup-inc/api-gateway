"""추출(Extraction) 패턴 — 인보이스 텍스트에서 구조화 데이터 꺼내기.

가이드 대응: §4.2 (InvoiceExtraction)

비정형 인보이스 텍스트를 받아 벤더/번호/날짜/라인아이템/소계/세금/총액으로 분해합니다.
items 가 객체 배열이라는 점, 숫자 필드는 integer/number 를 구분한다는 점이 핵심.

실행:
    cd structured_output
    python 04_design_patterns/02_extraction_invoice.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


SCHEMA = {
    "title": "InvoiceExtraction",
    "type": "object",
    "properties": {
        "vendor_name": {"type": "string"},
        "invoice_number": {"type": "string"},
        "date": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "unit_price": {"type": "number"},
                    "amount": {"type": "number"},
                },
                "required": ["description", "quantity", "unit_price", "amount"],
            },
        },
        "subtotal": {"type": "number"},
        "tax": {"type": "number"},
        "total": {"type": "number"},
    },
    "required": [
        "vendor_name",
        "invoice_number",
        "date",
        "items",
        "subtotal",
        "tax",
        "total",
    ],
}


INVOICE_TEXT = """
인보이스

공급자: (주)클라우드웍스
인보이스 번호: INV-2026-0417
발행일: 2026-04-17

항목:
1. Premium 서버 호스팅 (월) — 수량 3, 단가 120,000, 금액 360,000
2. 백업 스토리지 100GB — 수량 1, 단가 45,000, 금액 45,000
3. 긴급 지원 (시간) — 수량 2, 단가 80,000, 금액 160,000

소계: 565,000
부가세(10%): 56,500
총액: 621,500
"""


def main() -> None:
    data = generate_structured(
        contents=[
            "아래 인보이스 텍스트를 구조화해서 스키마에 맞게 추출해줘.\n\n"
            + INVOICE_TEXT
        ],
        schema=SCHEMA,
        temperature=0.0,
        thinking_level="low",
    )

    print("[parsed]")
    pprint(data)
    print()
    print(f"→ {data['vendor_name']} / {data['invoice_number']} / {data['date']}")
    print(f"→ 라인 아이템 {len(data['items'])}건, 총액 {data['total']:,}")


if __name__ == "__main__":
    main()
