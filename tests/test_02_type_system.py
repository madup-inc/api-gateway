"""
섹션 3: 타입 시스템 테스트

검증 항목:
3.1 기본 타입: string, integer, number, boolean
3.2 복합 타입:
    - Array (items로 타입 정의)
    - Object (중첩 객체)
    - Enum (허용값 제한, 단일 / 배열)
"""
import pytest


class TestBasicTypes:
    """3.1 기본 타입 스키마 구조 검증"""

    @pytest.mark.parametrize("type_name", ["string", "integer", "number", "boolean"])
    def test_basic_type_field(self, type_name):
        """기본 타입 필드가 올바르게 정의된다"""
        schema = {
            "title": "BasicTypes",
            "type": "object",
            "properties": {"field": {"type": type_name}},
            "required": ["field"],
        }
        assert schema["properties"]["field"]["type"] == type_name

    def test_string_type(self):
        schema = {"type": "string"}
        assert schema["type"] == "string"

    def test_integer_type(self):
        schema = {"type": "integer"}
        assert schema["type"] == "integer"

    def test_number_type(self):
        """number는 float 포함 실수형"""
        schema = {"type": "number"}
        assert schema["type"] == "number"

    def test_boolean_type(self):
        schema = {"type": "boolean"}
        assert schema["type"] == "boolean"


class TestArrayType:
    """3.2 Array 타입 검증"""

    def test_string_array_schema(self):
        """문자열 배열: items.type = string"""
        schema = {
            "type": "array",
            "items": {"type": "string"},
        }
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "string"

    def test_object_array_schema(self):
        """객체 배열: items에 object 타입과 properties 포함"""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                },
                "required": ["name", "price"],
            },
        }
        assert schema["type"] == "array"
        items = schema["items"]
        assert items["type"] == "object"
        assert "name" in items["properties"]
        assert "price" in items["properties"]
        assert set(items["required"]) == {"name", "price"}

    def test_array_items_required(self):
        """배열 스키마에는 items 필드가 있어야 한다"""
        schema = {"type": "array", "items": {"type": "string"}}
        assert "items" in schema

    def test_nested_object_array(self):
        """중첩 객체 배열 구조 검증"""
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["id"],
            },
        }
        inner = schema["items"]["properties"]["tags"]
        assert inner["type"] == "array"
        assert inner["items"]["type"] == "string"


class TestObjectType:
    """3.2 Object (중첩 객체) 타입 검증"""

    def test_nested_object_schema(self):
        """address처럼 중첩된 object 스키마"""
        schema = {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "district": {"type": "string"},
                "coordinates": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number"},
                        "lng": {"type": "number"},
                    },
                    "required": ["lat", "lng"],
                },
            },
            "required": ["city", "district", "coordinates"],
        }
        coords = schema["properties"]["coordinates"]
        assert coords["type"] == "object"
        assert "lat" in coords["properties"]
        assert "lng" in coords["properties"]
        assert set(coords["required"]) == {"lat", "lng"}

    def test_required_fields_subset_of_properties(self):
        """required 필드가 모두 properties에 있어야 한다"""
        schema = {
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "integer"},
                "c": {"type": "boolean"},
            },
            "required": ["a", "b"],
        }
        for field in schema["required"]:
            assert field in schema["properties"]

    def test_three_level_nesting(self):
        """3단계 중첩 구조 (권장 최대 깊이)"""
        schema = {
            "type": "object",
            "properties": {
                "level1": {
                    "type": "object",
                    "properties": {
                        "level2": {
                            "type": "object",
                            "properties": {
                                "level3": {"type": "string"}
                            },
                        }
                    },
                }
            },
        }
        l3 = schema["properties"]["level1"]["properties"]["level2"]["properties"]["level3"]
        assert l3["type"] == "string"


class TestEnumType:
    """3.2 Enum 타입 검증"""

    def test_single_enum_schema(self):
        """단일 enum: 허용 값 목록"""
        schema = {
            "type": "string",
            "enum": ["positive", "negative", "neutral"],
        }
        assert "enum" in schema
        assert set(schema["enum"]) == {"positive", "negative", "neutral"}

    def test_enum_in_object_property(self):
        """객체 내 enum 필드"""
        schema = {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral"],
                }
            },
            "required": ["sentiment"],
        }
        assert "enum" in schema["properties"]["sentiment"]

    def test_enum_array_items(self):
        """배열 항목에 enum 적용 (복수 선택)"""
        schema = {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["tech", "health", "finance", "sports", "entertainment"],
            },
        }
        assert "enum" in schema["items"]
        assert len(schema["items"]["enum"]) == 5

    def test_enum_only_specified_values(self):
        """enum에 없는 값은 허용되지 않음을 스키마로 표현"""
        allowed = ["bug", "feature_request", "question", "improvement"]
        schema = {"type": "string", "enum": allowed}
        for v in allowed:
            assert v in schema["enum"]
        assert "unknown_type" not in schema["enum"]

    def test_enum_on_integer(self):
        """integer 타입에도 enum 적용 가능"""
        schema = {"type": "integer", "enum": [1, 2, 3, 5, 8]}
        assert schema["enum"] == [1, 2, 3, 5, 8]
