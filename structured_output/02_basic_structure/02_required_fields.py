"""required 배열의 효과를 눈으로 비교.

가이드 대응: §2.2 (Schema 기본 구조), §7.1 (required 를 빠짐없이 명시)

required 에 들어간 필드는 반드시 응답에 포함되고, 빠지면 모델이 생략할 수 있습니다.
이 예제는 같은 스키마를 두 번 호출해 (1) required 가 모두 채워진 경우와
(2) required 를 최소화했을 때 모델이 어떤 필드를 내놓는지를 비교합니다.

실행:
    cd structured_output
    python 02_basic_structure/02_required_fields.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import generate_structured

PROPERTIES = {
    "name": {"type": "string"},
    "population": {"type": "integer"},
    "famous_food": {"type": "string"},
    "timezone": {"type": "string"},
}

PROMPT = "대한민국 서울에 대한 기본 정보를 알려줘."


def call(label: str, required: list[str]) -> None:
    schema = {
        "title": "CityInfo",
        "type": "object",
        "properties": PROPERTIES,
        "required": required,
    }
    data = generate_structured(contents=[PROMPT], schema=schema, temperature=0.2)
    print(f"[{label}] required={required}")
    pprint(data)
    missing = [k for k in PROPERTIES if k not in data]
    print(f"  → 누락된 필드: {missing or '없음'}\n")


def main() -> None:
    # (A) 모든 필드를 required 로 — 네 개가 모두 채워져야 응답이 유효.
    call("모두 필수", list(PROPERTIES))

    # (B) name 하나만 required — 나머지는 모델이 생략할 수 있음.
    call("이름만 필수", ["name"])


if __name__ == "__main__":
    main()
