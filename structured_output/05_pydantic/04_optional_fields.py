"""Optional 필드 — 값이 없을 수 있음을 허용.

가이드 대응: §5.4 (Optional 필드)

할인률이 없는 제품, 설명이 안 적힌 제품 — 실제 데이터는 결측이 많습니다.
Optional[타입] 으로 선언하면 모델이 "정보가 없다" 고 판단했을 때 null 을
넣을 수 있어, 억지로 거짓 값을 만들지 않게 됩니다.

실행:
    cd structured_output
    python 05_pydantic/04_optional_fields.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint
from typing import Optional

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


class ProductInfo(BaseModel):
    name: str
    price: float
    discount_rate: Optional[float] = None
    description: Optional[str] = None
    in_stock: bool


PROMPTS = [
    # 케이스 A: 모든 정보가 들어있는 경우
    "정가 49,000원, 20% 할인 중인 가을 면 티셔츠 상품을 만들고 설명과 재고 유무를 채워줘.",
    # 케이스 B: 할인 정보가 없는 경우 — Optional 필드가 null 로 와야 함
    "특별 할인 없이 정가 38,000원에 판매 중인 베이식 화이트 스니커즈. 설명을 생략하고 재고만 알려줘.",
]


def main() -> None:
    schema = ProductInfo.model_json_schema()
    for i, prompt in enumerate(PROMPTS, 1):
        data = generate_structured(contents=[prompt], schema=schema, temperature=0.2)
        product = ProductInfo(**data)

        print(f"=== Product #{i} ===")
        pprint(data)
        line = f"→ {product.name}: {product.price:,}원"
        if product.discount_rate is not None:
            line += f" ({int(product.discount_rate * 100)}% 할인)"
        if product.description:
            line += f"\n  설명: {product.description}"
        line += f"\n  재고: {'있음' if product.in_stock else '없음'}"
        print(line)
        print()


if __name__ == "__main__":
    main()
