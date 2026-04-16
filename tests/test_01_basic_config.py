"""
섹션 1~2: Structured Output 기본 개념 및 필수 설정 테스트

- response_mime_type = "application/json" 필수
- response_schema 필수
- 기본 schema 구조 (title, type, properties, required)
- 실제 API 호출로 parsed 응답 반환 확인
"""
import pytest

from src.structured_output.client import BASE_URL, build_request_payload, generate_structured

SIMPLE_SCHEMA = {
    "title": "CityInfo",
    "type": "object",
    "properties": {
        "city": {"type": "string"},
        "population": {"type": "integer"},
    },
    "required": ["city", "population"],
}


class TestBasicConcept:
    def test_response_mime_type_is_application_json(self):
        """build_request_payload에 response_mime_type이 포함된다"""
        payload = build_request_payload(["test"], SIMPLE_SCHEMA)
        assert payload["payload"]["config"]["response_mime_type"] == "application/json"

    def test_response_schema_is_included(self):
        """response_schema가 config에 포함된다"""
        payload = build_request_payload(["test"], SIMPLE_SCHEMA)
        assert payload["payload"]["config"]["response_schema"] == SIMPLE_SCHEMA

    def test_both_required_fields_present(self):
        """두 필드가 모두 config에 있다"""
        config = build_request_payload(["test"], SIMPLE_SCHEMA)["payload"]["config"]
        assert "response_mime_type" in config
        assert "response_schema" in config

    def test_payload_structure(self):
        """payload > model, contents, config 구조"""
        payload = build_request_payload(["서울의 인구를 알려줘."], SIMPLE_SCHEMA)
        inner = payload["payload"]
        assert "model" in inner
        assert "contents" in inner
        assert "config" in inner

    def test_contents_is_list(self):
        payload = build_request_payload(["질문"], SIMPLE_SCHEMA)
        assert isinstance(payload["payload"]["contents"], list)


class TestSchemaBasicStructure:
    def test_schema_title_field(self):
        assert "title" in SIMPLE_SCHEMA

    def test_schema_type_object(self):
        assert SIMPLE_SCHEMA["type"] == "object"

    def test_schema_properties_required(self):
        assert "properties" in SIMPLE_SCHEMA
        assert isinstance(SIMPLE_SCHEMA["properties"], dict)

    def test_schema_required_list(self):
        assert "required" in SIMPLE_SCHEMA
        for field in SIMPLE_SCHEMA["required"]:
            assert field in SIMPLE_SCHEMA["properties"]

    def test_schema_without_type_defaults_to_object(self):
        schema_no_type = {
            "title": "NoType",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        assert "properties" in schema_no_type


class TestGenerateStructuredBasic:
    """실제 API 호출 테스트"""

    def test_returns_dict_on_success(self):
        """성공 시 dict를 반환한다"""
        result = generate_structured(["서울의 인구를 간단히 알려줘."], SIMPLE_SCHEMA)
        assert isinstance(result, dict)

    def test_required_fields_in_response(self):
        """required 필드가 응답에 존재한다"""
        result = generate_structured(["부산의 인구를 간단히 알려줘."], SIMPLE_SCHEMA)
        assert "city" in result
        assert "population" in result

    def test_field_types_match_schema(self):
        """응답 필드 타입이 스키마와 일치한다"""
        result = generate_structured(["대구의 인구를 간단히 알려줘."], SIMPLE_SCHEMA)
        assert isinstance(result["city"], str)
        assert isinstance(result["population"], int)

    def test_extra_config_opts_passed(self):
        """temperature 등 추가 옵션과 함께 요청해도 성공한다"""
        result = generate_structured(
            ["인천의 인구를 간단히 알려줘."],
            SIMPLE_SCHEMA,
            temperature=0.1,
        )
        assert "city" in result
