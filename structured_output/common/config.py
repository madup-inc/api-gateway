"""환경 변수를 로드하고 게이트웨이 접속 정보를 노출합니다.

.env 파일이 있으면 자동으로 읽고, 없으면 OS 환경 변수를 그대로 사용합니다.
예제 스크립트들은 이 모듈에서 BASE_URL과 HEADERS만 꺼내 쓰면 됩니다.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# structured_output/.env 를 탐색해 로드 (이미 설정된 OS 환경변수는 덮어쓰지 않음)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH, override=False)

BASE_URL: str = os.environ.get("BASE_URL", "http://ai-api-gateway.tech.madup").rstrip("/")
API_KEY: str = os.environ.get("API_KEY", "")

# 요청 타임아웃 (초). 모든 요청에 공통 적용.
TIMEOUT_SECONDS: int = int(os.environ.get("TIMEOUT_SECONDS", "30"))

# 인증 헤더 이름이 게이트웨이 규격에 따라 다를 수 있습니다.
# 실제 게이트웨이가 다른 헤더(예: "X-API-Key")를 요구하면 아래 딕셔너리만 바꾸세요.
HEADERS: dict[str, str] = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def require_api_key() -> None:
    """API_KEY가 비어 있으면 친절한 에러를 냅니다.

    예제 스크립트는 실행 시작점에서 이 함수를 호출해,
    키가 비어 있을 때 요청을 보내기 전에 바로 실패하도록 합니다.
    """

    if not API_KEY:
        raise RuntimeError(
            "API_KEY 가 비어 있습니다. structured_output/.env.example 을 "
            ".env 로 복사한 뒤 API_KEY 값을 채워 주세요."
        )
