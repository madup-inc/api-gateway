"""
섹션 6: 에러 처리와 엣지 케이스 테스트

6.1 parsed=null → text 폴백 (클라이언트 로직 단위 테스트)
6.2 MAX_TOKENS → RuntimeError (클라이언트 로직 단위 테스트)
6.3 status != success → RuntimeError
6.3 인증 없이 요청 시 에러 응답 구조 확인
"""
import json
import pytest
import requests
from unittest.mock import MagicMock, patch

from src.structured_output.client import (
    BASE_URL,
    generate_structured,
    get_headers,
)

SIMPLE_SCHEMA = {
    "title": "Simple",
    "type": "object",
    "properties": {"value": {"type": "string"}},
    "required": ["value"],
}


# ── 클라이언트 로직 단위 테스트 (네트워크 불필요) ─────────────────────────────
class TestParsedNullFallback:
    """6.1 parsed=null 시 text 폴백 (클라이언트 코드 검증)"""

    def test_fallback_to_text_when_parsed_is_none(self):
        expected = {"value": "fallback"}
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "success",
            "result": {
                "parsed": None,
                "text": json.dumps(expected),
                "candidates": [{"finish_reason": "STOP"}],
            },
        }
        with patch("src.structured_output.client.requests.post", return_value=mock_resp):
            result = generate_structured(["test"], SIMPLE_SCHEMA)
        assert result == expected

    def test_returns_parsed_directly_when_not_none(self):
        mock_parsed = {"value": "direct"}
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "success",
            "result": {
                "parsed": mock_parsed,
                "text": json.dumps(mock_parsed),
                "candidates": [{"finish_reason": "STOP"}],
            },
        }
        with patch("src.structured_output.client.requests.post", return_value=mock_resp):
            result = generate_structured(["test"], SIMPLE_SCHEMA)
        assert result == mock_parsed

    def test_fallback_text_invalid_json_raises(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "success",
            "result": {
                "parsed": None,
                "text": "NOT VALID JSON",
                "candidates": [{"finish_reason": "STOP"}],
            },
        }
        with patch("src.structured_output.client.requests.post", return_value=mock_resp):
            with pytest.raises(json.JSONDecodeError):
                generate_structured(["test"], SIMPLE_SCHEMA)


class TestMaxTokensError:
    """6.2 MAX_TOKENS finish_reason (클라이언트 코드 검증)"""

    def test_max_tokens_raises_runtime_error(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "success",
            "result": {
                "parsed": None,
                "text": '{"value": "cut',
                "candidates": [{"finish_reason": "MAX_TOKENS"}],
            },
        }
        with patch("src.structured_output.client.requests.post", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="MAX_TOKENS"):
                generate_structured(["test"], SIMPLE_SCHEMA)

    def test_stop_reason_does_not_raise(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "success",
            "result": {
                "parsed": {"value": "ok"},
                "text": '{"value": "ok"}',
                "candidates": [{"finish_reason": "STOP"}],
            },
        }
        with patch("src.structured_output.client.requests.post", return_value=mock_resp):
            result = generate_structured(["test"], SIMPLE_SCHEMA)
        assert result == {"value": "ok"}


class TestAPIErrorResponse:
    """6.3 status != success (클라이언트 코드 검증)"""

    def test_error_status_raises_runtime_error(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "error",
            "error": {"type": "VALIDATION_ERROR", "message": "스키마 오류"},
        }
        with patch("src.structured_output.client.requests.post", return_value=mock_resp):
            with pytest.raises(RuntimeError, match="VALIDATION_ERROR"):
                generate_structured(["test"], SIMPLE_SCHEMA)

    def test_error_message_in_exception(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "status": "error",
            "error": {"type": "AUTH_ERROR", "message": "API 키가 유효하지 않습니다"},
        }
        with patch("src.structured_output.client.requests.post", return_value=mock_resp):
            with pytest.raises(RuntimeError) as exc_info:
                generate_structured(["test"], SIMPLE_SCHEMA)
        assert "AUTH_ERROR" in str(exc_info.value)
        assert "API 키가 유효하지 않습니다" in str(exc_info.value)


# ── 실제 API 에러 응답 테스트 ─────────────────────────────────────────────────
class TestUnauthorizedError:
    """인증 없이 요청 시 에러 응답 구조 확인"""

    def test_missing_token_returns_error_status(self):
        """X-Cognito-Token 없이 요청하면 status=error"""
        resp = requests.post(
            f"{BASE_URL}/v1/tasks/generate-text",
            headers={"Content-Type": "application/json"},
            timeout=10,
            json={
                "payload": {
                    "model": "gemini-3-flash-preview",
                    "contents": ["test"],
                    "config": {
                        "response_mime_type": "application/json",
                        "response_schema": SIMPLE_SCHEMA,
                    },
                }
            },
        )
        data = resp.json()
        assert data["status"] == "error"

    def test_unauthorized_error_has_error_field(self):
        """에러 응답에 error 필드가 있다"""
        resp = requests.post(
            f"{BASE_URL}/v1/tasks/generate-text",
            headers={"Content-Type": "application/json"},
            timeout=10,
            json={"payload": {}},
        )
        data = resp.json()
        assert "error" in data
        assert "type" in data["error"]
        assert "message" in data["error"]

    def test_unauthorized_error_type(self):
        """인증 오류 타입이 unauthorized"""
        resp = requests.post(
            f"{BASE_URL}/v1/tasks/generate-text",
            headers={"Content-Type": "application/json"},
            timeout=10,
            json={"payload": {}},
        )
        data = resp.json()
        assert data["error"]["type"] == "unauthorized"


# ── 실제 API 성공 경로 에러 처리 검증 ────────────────────────────────────────
class TestSuccessPathWithRealAPI:
    """성공 응답에서 에러 처리 패턴이 올바르게 동작"""

    def test_parsed_field_present_on_success(self):
        """성공 응답에 parsed 필드가 있다"""
        result = generate_structured(
            ["'hello'라고만 대답해줘."],
            SIMPLE_SCHEMA,
            temperature=0.0,
        )
        # generate_structured가 정상 반환하면 parsed or text 중 하나가 성공
        assert isinstance(result, dict)
        assert "value" in result

    def test_generate_structured_raises_on_api_error(self):
        """잘못된 모델명으로 요청하면 RuntimeError"""
        with pytest.raises(RuntimeError):
            generate_structured(
                ["test"],
                SIMPLE_SCHEMA,
                model="invalid-model-xyz",
            )
