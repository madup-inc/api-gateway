"""공통 모듈: 모든 챕터 예제가 공유하는 config와 client.

이 패키지는 얇은 레이어입니다. 실제 요청 로직은 client.py에,
환경 변수 로딩은 config.py에 있습니다.
"""

from .client import GenerationError, generate_structured
from .config import BASE_URL, HEADERS, TIMEOUT_SECONDS

__all__ = [
    "BASE_URL",
    "HEADERS",
    "TIMEOUT_SECONDS",
    "GenerationError",
    "generate_structured",
]
