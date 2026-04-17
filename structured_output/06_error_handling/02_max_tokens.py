"""MAX_TOKENS 재현 — 일부러 max_output_tokens 를 낮춰 실패 유도.

가이드 대응: §6.2 (MAX_TOKENS 처리)

candidates[0].finish_reason 이 "MAX_TOKENS" 이면 JSON 출력이 중간에 잘려
그대로 파싱 시 거짓 데이터가 들어올 수 있습니다. 이럴 땐 파싱을 시도하지 말고
즉시 에러로 떨어뜨려야 합니다.

common.generate_structured 는 이 조건을 감지하면 GenerationError 를 던집니다.
이 스크립트는 max_output_tokens=20 처럼 극단적으로 작은 값을 줘서 의도적으로 상황을 재현합니다.

실행:
    cd structured_output
    python 06_error_handling/02_max_tokens.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import GenerationError, generate_structured


SCHEMA = {
    "title": "LongAnswer",
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "body": {"type": "string"},
        "key_points": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "body", "key_points"],
}


def main() -> None:
    try:
        data = generate_structured(
            contents=[
                "인공지능의 역사를 1900년대부터 현재까지 5문단으로 설명하고 "
                "주요 포인트 10개를 뽑아줘. 상세히."
            ],
            schema=SCHEMA,
            temperature=0.3,
            max_output_tokens=20,  # 의도적으로 극단적으로 작게
        )
    except GenerationError as exc:
        print("✅ 예상대로 에러가 발생했습니다.")
        print(f"   에러 메시지: {exc}")
        print()
        print("해결책 (가이드 §6.2):")
        print("  1) 스키마를 단순화한다 (필드를 줄이거나 key_points 길이를 제한).")
        print("  2) max_output_tokens 를 더 크게 지정한다 (기본값 사용 권장).")
        return

    # 여기 도달했다면 max_output_tokens 가 충분했거나 모델이 초압축했을 수 있습니다.
    print("⚠️ MAX_TOKENS 가 발생하지 않았습니다. 응답:")
    print(data)


if __name__ == "__main__":
    main()
