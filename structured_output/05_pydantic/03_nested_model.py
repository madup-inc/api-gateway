"""중첩 Pydantic 모델 — 레시피 북을 통째로 받기.

가이드 대응: §5.3 (중첩 모델)

BaseModel 끼리 참조하면 중첩 스키마가 자동으로 만들어집니다.
Pydantic 의 진짜 강점이 여기서 드러나요 — JSON Schema 를 손으로 짜면
깊이 3단계부터 오탈자 지옥인데, 모델 참조로는 자연스럽게 풀립니다.

실행:
    cd structured_output
    python 05_pydantic/03_nested_model.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


class Ingredient(BaseModel):
    name: str
    quantity: str
    category: str


class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[Ingredient]
    cooking_time: str


class RecipeBook(BaseModel):
    recipes: list[Recipe]


def main() -> None:
    data = generate_structured(
        contents=[
            "간단한 한식 2가지 레시피를 만들어줘. 각 레시피에 재료 4~6개, "
            "카테고리(채소/육류/곡물/양념/해산물) 도 같이 분류해줘."
        ],
        schema=RecipeBook.model_json_schema(),
        temperature=0.4,
    )

    print("[parsed dict]")
    pprint(data)

    # 중첩 dict 전체를 한 번에 검증 — Pydantic 이 재귀적으로 내려가며 타입 체크.
    book = RecipeBook(**data)

    print()
    print(f"→ 레시피 {len(book.recipes)}개 수신")
    for r in book.recipes:
        print(f"  · {r.recipe_name} ({r.cooking_time})")
        for ing in r.ingredients:
            print(f"     - {ing.name} {ing.quantity} [{ing.category}]")


if __name__ == "__main__":
    main()
