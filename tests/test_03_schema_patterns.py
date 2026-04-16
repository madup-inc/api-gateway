"""
섹션 4: 스키마 설계 패턴 테스트 (실제 API 호출)

4.1 분류 (Classification)
4.2 추출 (Extraction)
4.3 분석 (Analysis)
4.4 변환 (Transformation)
4.5 비교/평가 (Comparison)
"""
import pytest

from src.structured_output.client import generate_structured

# ── 스키마 정의 (description 추가로 모델 필드명 준수율 향상) ─────────────────────
TICKET_CLASSIFICATION_SCHEMA = {
    "title": "TicketClassification",
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["bug", "feature_request", "question", "improvement"],
            "description": "Type of the support ticket",
        },
        "priority": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"],
            "description": "Priority level of the ticket",
        },
        "assigned_team": {
            "type": "string",
            "enum": ["backend", "frontend", "infra", "data", "design"],
            "description": "Team responsible for handling this ticket",
        },
        "summary": {
            "type": "string",
            "description": "Brief one-sentence summary of the ticket",
        },
    },
    "required": ["category", "priority", "assigned_team", "summary"],
}

INVOICE_EXTRACTION_SCHEMA = {
    "title": "InvoiceExtraction",
    "type": "object",
    "properties": {
        "vendor_name": {"type": "string", "description": "Name of the vendor/supplier company"},
        "invoice_number": {"type": "string", "description": "Invoice identification number"},
        "date": {"type": "string", "description": "Invoice date in YYYY-MM-DD format"},
        "items": {
            "type": "array",
            "description": "List of line items in the invoice",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Item description"},
                    "quantity": {"type": "integer", "description": "Quantity of items"},
                    "unit_price": {"type": "number", "description": "Price per unit"},
                    "amount": {"type": "number", "description": "Total amount for this line item"},
                },
                "required": ["description", "quantity", "unit_price", "amount"],
            },
        },
        "subtotal": {"type": "number", "description": "Subtotal before tax"},
        "tax": {"type": "number", "description": "Tax amount"},
        "total": {"type": "number", "description": "Total amount including tax"},
    },
    "required": ["vendor_name", "invoice_number", "date", "items", "subtotal", "tax", "total"],
}

CONTENT_ANALYSIS_SCHEMA = {
    "title": "ContentAnalysis",
    "type": "object",
    "properties": {
        "overall_score": {"type": "number", "description": "Overall score from 0 to 10"},
        "aspects": {
            "type": "array",
            "description": "List of analyzed aspects",
            "items": {
                "type": "object",
                "properties": {
                    "aspect": {"type": "string", "description": "Name of the aspect being analyzed"},
                    "score": {"type": "number", "description": "Score for this aspect from 0 to 10"},
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "negative", "neutral", "mixed"],
                        "description": "Sentiment for this aspect",
                    },
                    "evidence": {"type": "string", "description": "Evidence from the text supporting this score"},
                },
                "required": ["aspect", "score", "sentiment", "evidence"],
            },
        },
        "strengths": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of positive points",
        },
        "weaknesses": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of negative points or areas for improvement",
        },
        "recommendation": {"type": "string", "description": "Overall recommendation based on the analysis"},
    },
    "required": ["overall_score", "aspects", "strengths", "weaknesses", "recommendation"],
}

ARTICLE_SUMMARY_SCHEMA = {
    "title": "ArticleSummary",
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Title of the article"},
        "summary": {"type": "string", "description": "2-3 sentence summary of the article"},
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of main points from the article",
        },
        "word_count": {"type": "integer", "description": "Approximate word count of the original article"},
        "reading_time_minutes": {"type": "integer", "description": "Estimated reading time in minutes"},
        "language": {
            "type": "string",
            "enum": ["ko", "en", "ja", "zh"],
            "description": "Language code of the article",
        },
        "topics": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Main topics covered in the article",
        },
    },
    "required": ["title", "summary", "key_points", "word_count", "reading_time_minutes", "language", "topics"],
}

PRODUCT_COMPARISON_SCHEMA = {
    "title": "ProductComparison",
    "type": "object",
    "properties": {
        "products": {
            "type": "array",
            "description": "List of products being compared",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Product name"},
                    "pros": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of advantages",
                    },
                    "cons": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of disadvantages",
                    },
                    "score": {"type": "number", "description": "Overall score from 0 to 10"},
                },
                "required": ["name", "pros", "cons", "score"],
            },
        },
        "winner": {"type": "string", "description": "Name of the winning product"},
        "reasoning": {"type": "string", "description": "Explanation for why the winner was chosen"},
    },
    "required": ["products", "winner", "reasoning"],
}


# ── 스키마 구조 단위 테스트 ────────────────────────────────────────────────────
class TestClassificationSchema:
    def test_category_enum_values(self):
        cat = TICKET_CLASSIFICATION_SCHEMA["properties"]["category"]
        assert set(cat["enum"]) == {"bug", "feature_request", "question", "improvement"}

    def test_priority_enum_values(self):
        pri = TICKET_CLASSIFICATION_SCHEMA["properties"]["priority"]
        assert set(pri["enum"]) == {"critical", "high", "medium", "low"}

    def test_assigned_team_enum_values(self):
        team = TICKET_CLASSIFICATION_SCHEMA["properties"]["assigned_team"]
        assert set(team["enum"]) == {"backend", "frontend", "infra", "data", "design"}

    def test_all_required_fields(self):
        assert set(TICKET_CLASSIFICATION_SCHEMA["required"]) == {
            "category", "priority", "assigned_team", "summary"
        }


class TestExtractionSchema:
    def test_items_array_with_object(self):
        items_schema = INVOICE_EXTRACTION_SCHEMA["properties"]["items"]
        assert items_schema["type"] == "array"
        assert items_schema["items"]["type"] == "object"

    def test_item_required_fields(self):
        item_required = INVOICE_EXTRACTION_SCHEMA["properties"]["items"]["items"]["required"]
        assert set(item_required) == {"description", "quantity", "unit_price", "amount"}

    def test_numeric_totals(self):
        for field in ["subtotal", "tax", "total"]:
            assert INVOICE_EXTRACTION_SCHEMA["properties"][field]["type"] == "number"


class TestAnalysisSchema:
    def test_aspect_sentiment_enum(self):
        sentiment = CONTENT_ANALYSIS_SCHEMA["properties"]["aspects"]["items"]["properties"]["sentiment"]
        assert set(sentiment["enum"]) == {"positive", "negative", "neutral", "mixed"}

    def test_strengths_weaknesses_string_arrays(self):
        for field in ["strengths", "weaknesses"]:
            s = CONTENT_ANALYSIS_SCHEMA["properties"][field]
            assert s["type"] == "array" and s["items"]["type"] == "string"


class TestTransformationSchema:
    def test_language_enum(self):
        lang = ARTICLE_SUMMARY_SCHEMA["properties"]["language"]
        assert set(lang["enum"]) == {"ko", "en", "ja", "zh"}

    def test_integer_fields(self):
        assert ARTICLE_SUMMARY_SCHEMA["properties"]["word_count"]["type"] == "integer"
        assert ARTICLE_SUMMARY_SCHEMA["properties"]["reading_time_minutes"]["type"] == "integer"


class TestComparisonSchema:
    def test_pros_cons_string_arrays(self):
        item_props = PRODUCT_COMPARISON_SCHEMA["properties"]["products"]["items"]["properties"]
        for field in ["pros", "cons"]:
            assert item_props[field]["type"] == "array"
            assert item_props[field]["items"]["type"] == "string"

    def test_all_required_fields(self):
        assert set(PRODUCT_COMPARISON_SCHEMA["required"]) == {"products", "winner", "reasoning"}


# ── 실제 API 호출 테스트 ──────────────────────────────────────────────────────
class TestClassificationAPI:
    def test_classification_required_fields(self):
        result = generate_structured(
            ["지원 티켓: '로그인 버튼 클릭 시 500 에러가 발생합니다.'"],
            TICKET_CLASSIFICATION_SCHEMA,
            temperature=0.0,
        )
        for field in TICKET_CLASSIFICATION_SCHEMA["required"]:
            assert field in result, f"Missing field: {field}, got: {list(result.keys())}"

    def test_category_value_within_enum(self):
        result = generate_structured(
            ["지원 티켓: '다크 모드를 지원해 주세요.'"],
            TICKET_CLASSIFICATION_SCHEMA,
            temperature=0.0,
        )
        allowed = TICKET_CLASSIFICATION_SCHEMA["properties"]["category"]["enum"]
        assert result["category"] in allowed

    def test_priority_value_within_enum(self):
        result = generate_structured(
            ["지원 티켓: '배포 서버가 다운됐습니다. 즉시 확인 부탁드립니다.'"],
            TICKET_CLASSIFICATION_SCHEMA,
            temperature=0.0,
        )
        allowed = TICKET_CLASSIFICATION_SCHEMA["properties"]["priority"]["enum"]
        assert result["priority"] in allowed

    def test_assigned_team_within_enum(self):
        result = generate_structured(
            ["지원 티켓: '버튼 색상이 디자인과 다릅니다.'"],
            TICKET_CLASSIFICATION_SCHEMA,
            temperature=0.0,
        )
        allowed = TICKET_CLASSIFICATION_SCHEMA["properties"]["assigned_team"]["enum"]
        assert result["assigned_team"] in allowed

    def test_summary_is_string(self):
        result = generate_structured(
            ["지원 티켓: 'API 응답 속도가 너무 느립니다.'"],
            TICKET_CLASSIFICATION_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["summary"], str) and len(result["summary"]) > 0


class TestExtractionAPI:
    INVOICE_TEXT = (
        "Invoice\n"
        "Vendor: ABC Software Co.\n"
        "Invoice No: INV-2026-001\n"
        "Date: 2026-04-16\n"
        "Item: Cloud Service License x1, unit price 100000 KRW, amount 100000 KRW\n"
        "Subtotal: 100000 KRW, Tax: 10000 KRW, Total: 110000 KRW"
    )

    def test_extraction_required_fields(self):
        result = generate_structured(
            [f"다음 청구서에서 정보를 추출해줘.\n\n{self.INVOICE_TEXT}"],
            INVOICE_EXTRACTION_SCHEMA,
            temperature=0.0,
        )
        for field in INVOICE_EXTRACTION_SCHEMA["required"]:
            assert field in result, f"Missing field: {field}, got: {list(result.keys())}"

    def test_items_is_list(self):
        result = generate_structured(
            [f"다음 청구서에서 정보를 추출해줘.\n\n{self.INVOICE_TEXT}"],
            INVOICE_EXTRACTION_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["items"], list) and len(result["items"]) > 0

    def test_item_fields_present(self):
        result = generate_structured(
            [f"다음 청구서에서 정보를 추출해줘.\n\n{self.INVOICE_TEXT}"],
            INVOICE_EXTRACTION_SCHEMA,
            temperature=0.0,
        )
        for field in ["description", "quantity", "unit_price", "amount"]:
            assert field in result["items"][0], f"Item missing field: {field}"

    def test_numeric_fields_are_numbers(self):
        result = generate_structured(
            [f"다음 청구서에서 정보를 추출해줘.\n\n{self.INVOICE_TEXT}"],
            INVOICE_EXTRACTION_SCHEMA,
            temperature=0.0,
        )
        for field in ["subtotal", "tax", "total"]:
            assert isinstance(result[field], (int, float))


class TestAnalysisAPI:
    REVIEW_TEXT = (
        "이 카페의 커피는 정말 맛있고 향이 좋습니다. "
        "가격도 적당하고 직원들도 친절합니다. "
        "다만 주차 공간이 부족하고 주말엔 너무 붐빕니다."
    )

    def test_analysis_required_fields(self):
        result = generate_structured(
            [f"다음 리뷰를 분석해줘.\n\n{self.REVIEW_TEXT}"],
            CONTENT_ANALYSIS_SCHEMA,
            temperature=0.0,
        )
        for field in CONTENT_ANALYSIS_SCHEMA["required"]:
            assert field in result, f"Missing field: {field}, got: {list(result.keys())}"

    def test_overall_score_is_number(self):
        result = generate_structured(
            [f"다음 리뷰를 분석해줘.\n\n{self.REVIEW_TEXT}"],
            CONTENT_ANALYSIS_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["overall_score"], (int, float))

    def test_aspects_is_list(self):
        result = generate_structured(
            [f"다음 리뷰를 분석해줘.\n\n{self.REVIEW_TEXT}"],
            CONTENT_ANALYSIS_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["aspects"], list)

    def test_aspect_sentiment_within_enum(self):
        result = generate_structured(
            [f"다음 리뷰를 분석해줘.\n\n{self.REVIEW_TEXT}"],
            CONTENT_ANALYSIS_SCHEMA,
            temperature=0.0,
        )
        allowed = {"positive", "negative", "neutral", "mixed"}
        for aspect in result["aspects"]:
            assert aspect["sentiment"] in allowed

    def test_strengths_weaknesses_are_lists(self):
        result = generate_structured(
            [f"다음 리뷰를 분석해줘.\n\n{self.REVIEW_TEXT}"],
            CONTENT_ANALYSIS_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["strengths"], list)
        assert isinstance(result["weaknesses"], list)


class TestTransformationAPI:
    ARTICLE_TEXT = (
        "2026년 인공지능 산업은 급속도로 발전하고 있습니다. "
        "특히 멀티모달 모델과 에이전트 기술이 주목받고 있으며, "
        "기업들의 AI 도입률도 크게 증가했습니다. "
        "전문가들은 향후 5년간 AI가 대부분의 산업을 변화시킬 것으로 전망합니다."
    )

    def test_transformation_required_fields(self):
        result = generate_structured(
            [f"다음 기사를 요약해줘.\n\n{self.ARTICLE_TEXT}"],
            ARTICLE_SUMMARY_SCHEMA,
            temperature=0.0,
        )
        for field in ARTICLE_SUMMARY_SCHEMA["required"]:
            assert field in result, f"Missing field: {field}, got: {list(result.keys())}"

    def test_language_within_enum(self):
        result = generate_structured(
            [f"다음 기사를 요약해줘.\n\n{self.ARTICLE_TEXT}"],
            ARTICLE_SUMMARY_SCHEMA,
            temperature=0.0,
        )
        assert result["language"] in ARTICLE_SUMMARY_SCHEMA["properties"]["language"]["enum"]

    def test_key_points_is_list_of_strings(self):
        result = generate_structured(
            [f"다음 기사를 요약해줘.\n\n{self.ARTICLE_TEXT}"],
            ARTICLE_SUMMARY_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["key_points"], list)
        assert all(isinstance(p, str) for p in result["key_points"])

    def test_word_count_is_positive_integer(self):
        result = generate_structured(
            [f"다음 기사를 요약해줘.\n\n{self.ARTICLE_TEXT}"],
            ARTICLE_SUMMARY_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["word_count"], int) and result["word_count"] > 0


class TestComparisonAPI:
    COMPARE_TEXT = (
        "제품A는 성능이 뛰어나고 디자인이 좋지만 가격이 비쌉니다. "
        "제품B는 저렴하고 내구성이 좋지만 디자인이 평범합니다."
    )

    def test_comparison_required_fields(self):
        result = generate_structured(
            [f"다음 두 제품을 비교해줘.\n\n{self.COMPARE_TEXT}"],
            PRODUCT_COMPARISON_SCHEMA,
            temperature=0.0,
        )
        for field in PRODUCT_COMPARISON_SCHEMA["required"]:
            assert field in result, f"Missing field: {field}, got: {list(result.keys()) if isinstance(result, dict) else result}"

    def test_products_is_list(self):
        result = generate_structured(
            [f"다음 두 제품을 비교해줘.\n\n{self.COMPARE_TEXT}"],
            PRODUCT_COMPARISON_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["products"], list) and len(result["products"]) >= 2

    def test_each_product_has_required_fields(self):
        result = generate_structured(
            [f"다음 두 제품을 비교해줘.\n\n{self.COMPARE_TEXT}"],
            PRODUCT_COMPARISON_SCHEMA,
            temperature=0.0,
        )
        for product in result["products"]:
            for field in ["name", "pros", "cons", "score"]:
                assert field in product

    def test_winner_is_string(self):
        result = generate_structured(
            [f"다음 두 제품을 비교해줘.\n\n{self.COMPARE_TEXT}"],
            PRODUCT_COMPARISON_SCHEMA,
            temperature=0.0,
        )
        assert isinstance(result["winner"], str) and len(result["winner"]) > 0
