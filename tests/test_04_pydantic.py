"""
섹션 5: Pydantic으로 스키마 정의하기 테스트

5.1 기본 모델 → model_json_schema()
5.2 Enum 활용
5.3 중첩 모델
5.4 Optional 필드
5.5 실제 API 호출
"""
import pytest
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from src.structured_output.client import generate_structured


class CityInfo(BaseModel):
    city: str
    population: int
    area_km2: float


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class TicketAnalysis(BaseModel):
    title: str
    sentiment: Sentiment
    priority: Priority
    tags: list[str]


class Ingredient(BaseModel):
    name: str
    quantity: str
    category: str


class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[Ingredient]
    cooking_time: str


class RecipeBook(BaseModel):
    recipes: list[Recipe]


class ProductInfo(BaseModel):
    name: str
    price: float
    discount_rate: Optional[float] = None
    description: Optional[str] = None
    in_stock: bool


class TestBasicModel:
    """5.1 기본 모델 → model_json_schema()"""

    def test_schema_type_object(self):
        assert CityInfo.model_json_schema()["type"] == "object"

    def test_schema_title(self):
        assert CityInfo.model_json_schema()["title"] == "CityInfo"

    def test_city_type_string(self):
        assert CityInfo.model_json_schema()["properties"]["city"]["type"] == "string"

    def test_population_type_integer(self):
        assert CityInfo.model_json_schema()["properties"]["population"]["type"] == "integer"

    def test_area_type_number(self):
        prop = CityInfo.model_json_schema()["properties"]["area_km2"]
        assert prop.get("type") == "number" or "anyOf" in prop

    def test_required_fields_present(self):
        schema = CityInfo.model_json_schema()
        assert set(schema["required"]) == {"city", "population", "area_km2"}


class TestEnumModel:
    """5.2 Enum 활용"""

    def test_sentiment_enum_values(self):
        assert set(v.value for v in Sentiment) == {"positive", "negative", "neutral"}

    def test_priority_enum_values(self):
        assert set(v.value for v in Priority) == {"critical", "high", "medium", "low"}

    def test_enum_inherits_from_str(self):
        assert isinstance(Sentiment.positive, str)
        assert isinstance(Priority.high, str)

    def test_tags_is_array_in_schema(self):
        schema = TicketAnalysis.model_json_schema()
        assert schema["properties"]["tags"]["type"] == "array"


class TestNestedModel:
    """5.3 중첩 모델"""

    def test_ingredient_required_fields(self):
        schema = Ingredient.model_json_schema()
        assert set(schema["required"]) == {"name", "quantity", "category"}

    def test_recipe_has_ingredients(self):
        schema = Recipe.model_json_schema()
        assert "ingredients" in schema.get("properties", {})

    def test_recipe_book_schema_generated(self):
        schema = RecipeBook.model_json_schema()
        assert isinstance(schema, dict)
        assert "recipes" in schema.get("properties", {})

    def test_model_instantiation(self):
        recipe = Recipe(
            recipe_name="김치찌개",
            ingredients=[Ingredient(name="김치", quantity="200g", category="채소")],
            cooking_time="30분",
        )
        assert recipe.recipe_name == "김치찌개"
        assert recipe.ingredients[0].name == "김치"


class TestOptionalFields:
    """5.4 Optional 필드"""

    def test_optional_defaults_to_none(self):
        p = ProductInfo(name="노트북", price=1500000.0, in_stock=True)
        assert p.discount_rate is None
        assert p.description is None

    def test_required_field_missing_raises(self):
        with pytest.raises(Exception):
            ProductInfo(price=1000.0, in_stock=True)  # name 누락

    def test_optional_fields_not_in_required(self):
        schema = ProductInfo.model_json_schema()
        required = set(schema.get("required", []))
        assert "discount_rate" not in required
        assert "description" not in required
        assert "name" in required
        assert "in_stock" in required


class TestPydanticAPIIntegration:
    """5.5 Pydantic 스키마 → 실제 API 호출"""

    def test_city_info_api_response_structure(self):
        result = generate_structured(
            ["서울의 인구와 면적을 알려줘."],
            CityInfo.model_json_schema(),
            temperature=0.1,
        )
        city = CityInfo(**result)
        assert isinstance(city.city, str)
        assert isinstance(city.population, int)
        assert isinstance(city.area_km2, float)

    def test_pydantic_schema_accepted_by_api(self):
        """Pydantic model_json_schema()가 API에서 정상 수락된다"""
        result = generate_structured(
            ["도쿄의 인구와 면적을 알려줘."],
            CityInfo.model_json_schema(),
            temperature=0.1,
        )
        assert "city" in result
        assert "population" in result
        assert "area_km2" in result

    def test_ticket_analysis_enum_values_respected(self):
        """Pydantic Enum 모델 기반 스키마로 API 호출 시 enum 값이 지켜진다"""
        schema = TicketAnalysis.model_json_schema()
        result = generate_structured(
            ["배포 서버에 장애가 발생했습니다. 즉시 확인해주세요."],
            schema,
            temperature=0.1,
        )
        assert "sentiment" in result
        assert "priority" in result
        assert result["sentiment"] in [v.value for v in Sentiment]
        assert result["priority"] in [v.value for v in Priority]
