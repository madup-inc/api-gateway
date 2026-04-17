"""
섹션 6: 에러 처리와 엣지 케이스 테스트

6.1 API 응답 구조 — parsed / text 필드
6.2 MAX_TOKENS → RuntimeError (max_output_tokens=1로 실제 유발)
6.3 status != success → RuntimeError (잘못된 모델명으로 실제 유발)
6.3 인증 없이 요청 시 에러 응답 구조 확인
"""
import json
import pytest
import requests

from src.structured_output.client import BASE_URL, get_headers
from tests.utils import generate_structured

SIMPLE_SCHEMA = {
    "title": "Simple",
    "type": "object",
    "properties": {"value": {"type": "string", "description": "A simple string value"}},
    "required": ["value"],
}


# ── 6.1 API 응답 구조 ─────────────────────────────────────────────────────────
class TestParsedOrTextResponse:
    """6.1 실제 API 응답에 parsed / text 필드가 존재하고 generate_structured가 dict를 반환한다"""

    def test_generate_structured_returns_dict(self):
        """generate_structured가 dict를 반환한다"""
        result = generate_structured(["'ok'라고만 대답해줘."], SIMPLE_SCHEMA, temperature=0.0)
        assert isinstance(result, dict)

    def test_required_field_in_result(self):
        """반환된 dict에 required 필드가 있다"""
        result = generate_structured(["'ok'라고만 대답해줘."], SIMPLE_SCHEMA, temperature=0.0)
        assert "value" in result

    def test_raw_response_has_result_field(self):
        """실제 API 응답에 result 필드가 있다"""
        resp = requests.post(
            f"{BASE_URL}/v1/tasks/generate-text",
            headers=get_headers(),
            timeout=30,
            json={"payload": {
                "model": "gemini-3-flash-preview",
                "contents": ["'ok'라고만 대답해줘."],
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": SIMPLE_SCHEMA,
                },
            }},
        )
        data = resp.json()
        assert data["status"] == "success"
        assert "result" in data

    def test_raw_response_text_is_valid_json(self):
        """실제 API 응답의 text 필드가 유효한 JSON이다"""
        resp = requests.post(
            f"{BASE_URL}/v1/tasks/generate-text",
            headers=get_headers(),
            timeout=30,
            json={"payload": {
                "model": "gemini-3-flash-preview",
                "contents": ["'ok'라고만 대답해줘."],
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": SIMPLE_SCHEMA,
                },
            }},
        )
        data = resp.json()
        text = data["result"].get("text", "")
        if text:
            parsed = json.loads(text)
            assert isinstance(parsed, dict)

    def test_raw_response_has_candidates(self):
        """실제 API 응답에 candidates 필드가 있다"""
        resp = requests.post(
            f"{BASE_URL}/v1/tasks/generate-text",
            headers=get_headers(),
            timeout=30,
            json={"payload": {
                "model": "gemini-3-flash-preview",
                "contents": ["'ok'라고만 대답해줘."],
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": SIMPLE_SCHEMA,
                },
            }},
        )
        data = resp.json()
        assert "candidates" in data["result"]
        assert len(data["result"]["candidates"]) > 0


# ── 6.2 MAX_TOKENS ────────────────────────────────────────────────────────────
class TestMaxTokensError:
    """6.2 MAX_TOKENS finish_reason → RuntimeError"""

    def test_max_tokens_raises_runtime_error(self):
        """max_output_tokens=1로 강제 truncation → RuntimeError(MAX_TOKENS)"""
        with pytest.raises(RuntimeError, match="MAX_TOKENS"):
            generate_structured(
                ["서울의 인구, 역사, 문화, 관광지, 교통, 경제를 상세히 알려줘."],
                SIMPLE_SCHEMA,
                max_output_tokens=1,
            )

    def test_normal_call_does_not_raise(self):
        """충분한 토큰 한도에서는 MAX_TOKENS가 발생하지 않는다"""
        result = generate_structured(["'ok'라고만 대답해줘."], SIMPLE_SCHEMA, temperature=0.0)
        assert isinstance(result, dict)

    def test_finish_reason_stop_on_normal_call(self):
        """정상 응답의 finish_reason은 STOP이다"""
        resp = requests.post(
            f"{BASE_URL}/v1/tasks/generate-text",
            headers=get_headers(),
            timeout=30,
            json={"payload": {
                "model": "gemini-3-flash-preview",
                "contents": ["'ok'라고만 대답해줘."],
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": SIMPLE_SCHEMA,
                    "temperature": 0.0,
                },
            }},
        )
        data = resp.json()
        finish = data["result"]["candidates"][0].get("finish_reason")
        assert finish == "STOP"


# ── 6.3 status != success ────────────────────────────────────────────────────
class TestAPIErrorResponse:
    """6.3 status != success → RuntimeError"""

    def test_invalid_model_raises_runtime_error(self):
        """존재하지 않는 모델 사용 시 RuntimeError"""
        with pytest.raises(RuntimeError):
            generate_structured(["test"], SIMPLE_SCHEMA, model="invalid-model-xyz")

    def test_error_message_is_non_empty(self):
        """RuntimeError 메시지가 비어있지 않다"""
        with pytest.raises(RuntimeError) as exc_info:
            generate_structured(["test"], SIMPLE_SCHEMA, model="invalid-model-xyz")
        assert len(str(exc_info.value)) > 0


# ── 6.3 인증 없이 요청 ────────────────────────────────────────────────────────
class TestUnauthorizedError:
    """인증 없이 요청 시 에러 응답 구조 확인"""

    def test_missing_token_returns_error_status(self):
        """X-Cognito-Token 없이 요청하면 status=error"""
        resp = requests.post(
            f"{BASE_URL}/v1/tasks/generate-text",
            headers={"Content-Type": "application/json"},
            timeout=10,
            json={"payload": {
                "model": "gemini-3-flash-preview",
                "contents": ["test"],
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": SIMPLE_SCHEMA,
                },
            }},
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


# ── 성공 경로 종합 ────────────────────────────────────────────────────────────
class TestSuccessPathWithRealAPI:
    """성공 응답에서 에러 처리 패턴이 올바르게 동작"""

    def test_parsed_field_present_on_success(self):
        """성공 응답에 value 필드가 있다"""
        result = generate_structured(
            ["'hello'라고만 대답해줘."],
            SIMPLE_SCHEMA,
            temperature=0.0,
        )
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
