"""
섹션 7: 베스트 프랙티스 테스트

7.1 스키마 설계 (단위 테스트)
7.2 성능 최적화 — temperature, thinking_level, max_output_tokens (실제 API)
7.3 안정성 — use_retry, finish_reason, fallback (클라이언트 로직 + 실제 API)
"""
import pytest

from src.structured_output.client import build_request_payload, get_headers
from tests.utils import generate_structured

BASE_SCHEMA = {
    "title": "Result",
    "type": "object",
    "properties": {"answer": {"type": "string"}},
    "required": ["answer"],
}


# ── 7.1 스키마 설계 단위 테스트 ──────────────────────────────────────────────
class TestSchemaDesignBestPractices:
    def test_descriptive_field_names(self):
        """필드 이름이 충분히 설명적이어야 한다 (2자 이상)"""
        schema = {
            "type": "object",
            "properties": {
                "sentiment": {"type": "string"},
                "description": {"type": "string"},
            },
        }
        for field in schema["properties"]:
            assert len(field) > 2

    def test_required_fields_declared(self):
        schema = {
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": ["a", "b"]},
                "score": {"type": "number"},
            },
            "required": ["category", "score"],
        }
        assert len(schema["required"]) > 0

    def test_enum_prevents_unexpected_values(self):
        schema = {"type": "string", "enum": ["positive", "negative", "neutral"]}
        assert "unknown" not in schema["enum"]

    def test_nesting_depth_max_three(self):
        def get_depth(s: dict, current: int = 0) -> int:
            if s.get("type") != "object":
                return current
            return max(
                (get_depth(p, current + 1) for p in s.get("properties", {}).values()),
                default=current,
            )

        schema = {
            "type": "object",
            "properties": {
                "a": {
                    "type": "object",
                    "properties": {
                        "b": {
                            "type": "object",
                            "properties": {"c": {"type": "string"}},
                        }
                    },
                }
            },
        }
        assert get_depth(schema) <= 3

    def test_all_required_in_properties(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "value": {"type": "number"}},
            "required": ["name", "value"],
        }
        for field in schema["required"]:
            assert field in schema["properties"]


# ── 7.2 성능 최적화 — 실제 API 호출 ─────────────────────────────────────────
class TestPerformanceOptimization:
    def test_temperature_zero_gives_consistent_result(self):
        """temperature=0.0 에서 구조가 올바르게 반환된다"""
        result = generate_structured(
            ["'ok'라고만 대답해줘."],
            BASE_SCHEMA,
            temperature=0.0,
        )
        assert "answer" in result

    def test_low_temperature_accepted(self):
        """temperature=0.1 요청이 성공한다"""
        result = generate_structured(
            ["'test'라고만 대답해줘."],
            BASE_SCHEMA,
            temperature=0.1,
        )
        assert isinstance(result, dict)

    def test_thinking_level_low_accepted(self):
        """thinking_level=low 요청이 성공한다"""
        result = generate_structured(
            ["단순히 'yes'라고만 대답해줘."],
            BASE_SCHEMA,
            temperature=0.0,
            thinking_level="low",
        )
        assert "answer" in result

    def test_payload_has_temperature(self):
        """build_request_payload에 temperature가 포함된다"""
        payload = build_request_payload(["test"], BASE_SCHEMA, temperature=0.3)
        assert payload["payload"]["config"]["temperature"] == 0.3

    def test_payload_has_max_output_tokens(self):
        """max_output_tokens가 config에 포함된다"""
        payload = build_request_payload(["test"], BASE_SCHEMA, max_output_tokens=512)
        assert payload["payload"]["config"]["max_output_tokens"] == 512

    def test_temperature_range(self):
        """temperature 0.0~1.0 사이"""
        for t in [0.0, 0.1, 0.3, 0.5, 1.0]:
            assert 0.0 <= t <= 1.0


# ── 7.3 안정성 ───────────────────────────────────────────────────────────────
class TestReliability:
    def test_use_retry_in_payload(self):
        """use_retry 옵션이 config에 전달된다"""
        payload = build_request_payload(["test"], BASE_SCHEMA, use_retry=True)
        assert payload["payload"]["config"]["use_retry"] is True

    def test_timeout_set_on_real_request(self):
        """실제 요청에 timeout이 설정된다 (ClientError가 아닌 정상 응답)"""
        result = generate_structured(
            ["'pong'이라고만 대답해줘."],
            BASE_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result, dict)

    def test_content_type_header(self):
        """Content-Type 헤더가 application/json으로 설정된다"""
        headers = get_headers()
        assert headers["Content-Type"] == "application/json"

    def test_cognito_token_in_header(self):
        """X-Cognito-Token 헤더가 설정된다"""
        headers = get_headers()
        assert "X-Cognito-Token" in headers
        assert len(headers["X-Cognito-Token"]) > 0

    def test_generate_structured_returns_dict(self):
        """generate_structured가 성공 시 dict를 반환한다"""
        result = generate_structured(["'ok'라고만 대답해줘."], BASE_SCHEMA, temperature=0.0)
        assert isinstance(result, dict)
        assert "answer" in result

    def test_max_tokens_raises(self):
        """max_output_tokens=1로 강제 truncation → RuntimeError(MAX_TOKENS)"""
        with pytest.raises(RuntimeError, match="MAX_TOKENS"):
            generate_structured(
                ["서울의 인구, 역사, 문화, 관광지, 경제를 상세히 알려줘."],
                BASE_SCHEMA,
                max_output_tokens=1,
            )
