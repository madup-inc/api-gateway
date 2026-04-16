"""
섹션 8: 빠른 참조 (스키마 템플릿) 테스트

단일 객체 / 객체 배열 / 분류+점수 템플릿
스키마 구조 단위 테스트 + 실제 API 호출
"""
import pytest

from src.structured_output.client import generate_structured

SINGLE_OBJECT_SCHEMA = {
    "title": "MySchema",
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Name or title"},
        "value": {"type": "number", "description": "Numeric value or score"},
        "active": {"type": "boolean", "description": "Whether it is active or enabled"},
    },
    "required": ["name", "value", "active"],
}

OBJECT_LIST_SCHEMA = {
    "title": "MyList",
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "description": "List of items",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Unique identifier"},
                    "name": {"type": "string", "description": "Item name"},
                },
                "required": ["id", "name"],
            },
        }
    },
    "required": ["items"],
}

CLASSIFICATION_SCORE_SCHEMA = {
    "title": "Classification",
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["cat_a", "cat_b", "cat_c"],
            "description": "Category label for the input",
        },
        "confidence": {"type": "number", "description": "Confidence score between 0.0 and 1.0"},
        "reasoning": {"type": "string", "description": "Explanation for the classification decision"},
    },
    "required": ["category", "confidence", "reasoning"],
}


# ── 스키마 구조 단위 테스트 ───────────────────────────────────────────────────
class TestSingleObjectTemplate:
    def test_name_is_string(self):
        assert SINGLE_OBJECT_SCHEMA["properties"]["name"]["type"] == "string"

    def test_value_is_number(self):
        assert SINGLE_OBJECT_SCHEMA["properties"]["value"]["type"] == "number"

    def test_active_is_boolean(self):
        assert SINGLE_OBJECT_SCHEMA["properties"]["active"]["type"] == "boolean"

    def test_all_fields_required(self):
        assert set(SINGLE_OBJECT_SCHEMA["required"]) == {"name", "value", "active"}


class TestObjectListTemplate:
    def test_items_is_array(self):
        assert OBJECT_LIST_SCHEMA["properties"]["items"]["type"] == "array"

    def test_item_id_integer(self):
        props = OBJECT_LIST_SCHEMA["properties"]["items"]["items"]["properties"]
        assert props["id"]["type"] == "integer"

    def test_item_name_string(self):
        props = OBJECT_LIST_SCHEMA["properties"]["items"]["items"]["properties"]
        assert props["name"]["type"] == "string"

    def test_item_required_fields(self):
        required = OBJECT_LIST_SCHEMA["properties"]["items"]["items"]["required"]
        assert set(required) == {"id", "name"}


class TestClassificationScoreTemplate:
    def test_category_enum(self):
        assert set(CLASSIFICATION_SCORE_SCHEMA["properties"]["category"]["enum"]) == {"cat_a", "cat_b", "cat_c"}

    def test_confidence_is_number(self):
        assert CLASSIFICATION_SCORE_SCHEMA["properties"]["confidence"]["type"] == "number"

    def test_reasoning_is_string(self):
        assert CLASSIFICATION_SCORE_SCHEMA["properties"]["reasoning"]["type"] == "string"


class TestAllTemplatesStructure:
    @pytest.mark.parametrize("schema", [
        SINGLE_OBJECT_SCHEMA, OBJECT_LIST_SCHEMA, CLASSIFICATION_SCORE_SCHEMA
    ])
    def test_has_title(self, schema):
        assert "title" in schema

    @pytest.mark.parametrize("schema", [
        SINGLE_OBJECT_SCHEMA, OBJECT_LIST_SCHEMA, CLASSIFICATION_SCORE_SCHEMA
    ])
    def test_has_properties(self, schema):
        assert "properties" in schema

    @pytest.mark.parametrize("schema", [
        SINGLE_OBJECT_SCHEMA, OBJECT_LIST_SCHEMA, CLASSIFICATION_SCORE_SCHEMA
    ])
    def test_required_in_properties(self, schema):
        for field in schema["required"]:
            assert field in schema["properties"]


# ── 실제 API 호출 ─────────────────────────────────────────────────────────────
class TestSingleObjectAPI:
    def test_required_fields_in_response(self):
        result = generate_structured(
            ["Python 언어에 대한 정보를 알려줘."],
            SINGLE_OBJECT_SCHEMA,
            temperature=0.0,
        )
        for field in SINGLE_OBJECT_SCHEMA["required"]:
            assert field in result, f"Missing: {field}, got: {list(result.keys())}"

    def test_field_types_correct(self):
        result = generate_structured(
            ["Go 언어에 대한 정보를 알려줘."],
            SINGLE_OBJECT_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["name"], str)
        assert isinstance(result["value"], (int, float))
        assert isinstance(result["active"], bool)


class TestObjectListAPI:
    def test_items_is_list(self):
        result = generate_structured(
            ["대표적인 프로그래밍 언어 3가지를 나열해줘."],
            OBJECT_LIST_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["items"], list) and len(result["items"]) > 0

    def test_items_have_required_fields(self):
        result = generate_structured(
            ["대표적인 데이터베이스 3가지를 나열해줘."],
            OBJECT_LIST_SCHEMA,
            temperature=0.0,
        )
        for item in result["items"]:
            assert "id" in item and isinstance(item["id"], int)
            assert "name" in item and isinstance(item["name"], str)


class TestClassificationScoreAPI:
    def test_category_within_enum(self):
        result = generate_structured(
            ["'안녕하세요'를 분류해줘."],
            CLASSIFICATION_SCORE_SCHEMA,
            temperature=0.0,
        )
        assert result["category"] in CLASSIFICATION_SCORE_SCHEMA["properties"]["category"]["enum"]

    def test_confidence_is_number(self):
        result = generate_structured(
            ["'오늘 날씨가 좋네요'를 분류해줘."],
            CLASSIFICATION_SCORE_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["confidence"], (int, float))

    def test_reasoning_is_non_empty_string(self):
        result = generate_structured(
            ["'에러가 발생했습니다'를 분류해줘."],
            CLASSIFICATION_SCORE_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["reasoning"], str) and len(result["reasoning"]) > 0
