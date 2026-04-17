"""객체 배열 — type: array + items.type: object.

가이드 대응: §3.2 Array ("products" 예제)

각 아이템이 여러 필드를 가진 레코드인 경우. 이커머스의 상품 목록,
인보이스의 라인 아이템, 검색 결과 카드 등 대부분의 "목록" 에 쓰입니다.

실행:
    cd structured_output
    python 03_type_system/03_array_of_objects.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


def main() -> None:
    schema = {
        "title": "ProductCatalog",
        "type": "object",
        "properties": {
            "products": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                        "stock": {"type": "integer"},
                    },
                    "required": ["name", "price", "stock"],
                },
            },
        },
        "required": ["products"],
    }

    data = generate_structured(
        contents=[
            "가상의 카페 테이크아웃 메뉴 4종을 만들고 각 메뉴의 이름/가격/재고를 채워줘."
        ],
        schema=schema,
        temperature=0.4,
    )

    print("[parsed]")
    pprint(data)
    print()
    for item in data["products"]:
        print(f"  - {item['name']}: {item['price']}원, 재고 {item['stock']}")


if __name__ == "__main__":
    main()
