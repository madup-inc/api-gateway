"""공통 fixtures — 실제 Cognito 인증 기반 (pytest-xdist 병렬 실행 지원)"""
import json
import os
import pytest

from src.structured_output.auth import _CACHED_TOKEN_ENV, get_cognito_token
from src.structured_output.client import BASE_URL, get_headers

DEFAULT_MODEL = "gemini-3-flash-preview"


# ── pytest-xdist 토큰 공유: 컨트롤러에서 한 번 발급 → 모든 워커에 주입 ─────────
def pytest_configure(config):
    """컨트롤러: 토큰 발급 / 워커: 컨트롤러에서 받은 토큰을 환경변수로 설정"""
    if hasattr(config, "workerinput"):
        # 워커 프로세스
        os.environ[_CACHED_TOKEN_ENV] = config.workerinput[_CACHED_TOKEN_ENV]
    else:
        # 컨트롤러(메인 프로세스): 토큰 한 번 발급
        os.environ[_CACHED_TOKEN_ENV] = get_cognito_token()


def pytest_configure_node(node):
    """컨트롤러 → 워커로 토큰 전달"""
    node.workerinput[_CACHED_TOKEN_ENV] = os.environ[_CACHED_TOKEN_ENV]


# ── fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def default_model():
    return DEFAULT_MODEL


# ── 단위 테스트용 헬퍼 (스트리밍 파싱 로직 테스트에만 사용) ─────────────────────
def make_mock_stream_lines(chunks: list[str], finish_status: str = "success") -> list[str]:
    lines = []
    for chunk in chunks:
        lines.append(f"data: {json.dumps({'chunk': {'text': chunk}})}")
    lines.append(f"data: {json.dumps({'status': finish_status})}")
    return lines
