"""네 가지 기본 타입 — string, integer, number, boolean.

가이드 대응: §3.1 (기본 타입)

한 스키마 안에 네 타입을 모두 넣어 하나의 상품 레코드로 받아봅니다.
- string  : 상품명
- integer : 재고 수량 (소수점 없는 정수)
- number  : 가격 (소수점 있을 수 있음)
- boolean : 프리미엄 여부

실행:
    cd structured_output
    python 03_type_system/01_primitive_types.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


def main() -> None:
    schema = {
        "title": "Product",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "stock": {"type": "integer"},
            "price": {"type": "number"},
            "is_premium": {"type": "boolean"},
        },
        "required": ["name", "stock", "price", "is_premium"],
    }

    data = generate_structured(
        contents=[
            "가상의 프리미엄 원두커피 제품을 하나 만들고 스키마에 맞춰 정보를 채워줘. "
            "가격은 소수점 포함 가능, 재고는 정수."
        ],
        schema=schema,
        temperature=0.3,
    )

    print("[parsed]")
    pprint(data)
    print()
    print(
        f"→ {data['name']}: {data['price']:.2f}원, 재고 {data['stock']}개, "
        f"프리미엄={data['is_premium']}"
    )


if __name__ == "__main__":
    main()
