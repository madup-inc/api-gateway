"""Pydantic 기본 모델 — BaseModel 로 스키마 정의하기.

가이드 대응: §5.1 (기본 모델)

JSON Schema 를 수작성하는 대신 Pydantic BaseModel 을 쓰면:
1) 타입 힌트로 필드가 명확히 드러나고,
2) 응답을 받은 뒤 CityInfo(**data) 로 즉시 검증/인스턴스화할 수 있습니다.

실행:
    cd structured_output
    python 05_pydantic/01_basic_model.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured


class CityInfo(BaseModel):
    city: str
    population: int
    area_km2: float


def main() -> None:
    data = generate_structured(
        contents=["대한민국 서울의 인구와 면적을 알려줘."],
        schema=CityInfo.model_json_schema(),
        temperature=0.2,
    )

    print("[parsed dict]")
    pprint(data)

    # 받은 dict 를 Pydantic 모델에 통과시켜 타입 검증까지 완료.
    city = CityInfo(**data)
    print()
    print(f"→ {city.city}: 인구 {city.population:,}명, 면적 {city.area_km2:,}km²")


if __name__ == "__main__":
    main()
