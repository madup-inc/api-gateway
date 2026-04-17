# Structured Output Usage Guide

**AI API Gateway — Text Generation Service**  
http://ai-api-gateway.tech.madup  
2026년 4월

---

## 목차

1. [Structured Output이란?](#1-structured-output이란)
2. [Pydantic으로 스키마 정의하기](#2-pydantic으로-스키마-정의하기)
3. [JSON Schema 구조 참조](#3-json-schema-구조-참조)
4. [스키마 설계 패턴](#4-스키마-설계-패턴)
5. [에러 처리와 엣지 케이스](#5-에러-처리와-엣지-케이스)
6. [베스트 프랙티스](#6-베스트-프랙티스)
7. [빠른 참조 (스키마 템플릿)](#7-빠른-참조-스키마-템플릿)

---

## 1. Structured Output이란?

Structured Output은 LLM의 응답을 미리 정의한 JSON Schema에 맞춰 반환받는 기능입니다. 자연어 텍스트 대신 타입이 보장된 구조화 데이터를 받아 프로그래밍 방식으로 안전하게 처리할 수 있습니다.

### 일반 텍스트 vs Structured Output

| 일반 텍스트 응답 | Structured Output 응답 |
|---|---|
| 비빔밥은 한국의 대표 음식으로,<br>밥 위에 다양한 나물과<br>고추장을 얹어 먹습니다... | `{"name": "비빔밥", "category": "한식", "calories": 550, "is_spicy": true}` |
| 파싱 불확실, 형식 보장 없음 | 타입 보장, 즉시 파싱 가능 |

### 언제 사용하나요?

- API 응답을 프로그램에서 직접 처리해야 할 때
- 데이터베이스에 저장할 구조화된 데이터가 필요할 때
- 분류, 분석, 추출 결과를 일관된 포맷으로 받고 싶을 때
- 여러 모델 응답을 비교하거나 합치는 파이프라인에서

### 활용 예시

**예시 1 — 데이터 조회**

<table>
<tr><th colspan="2">Request</th></tr>
<tr><th>Prompt</th><td>"서울의 인구를 알려줘."</td></tr>
<tr><th>Pydantic Schema</th><td><pre><code>class CityInfo(BaseModel):
    city: str
    population: int</code></pre></td></tr>
<tr><th>CityInfo.model_json_schema()</th><td><pre><code>{
  "title": "CityInfo",
  "type": "object",
  "properties": {
    "city": {"type": "string"},
    "population": {"type": "integer"}
  },
  "required": ["city", "population"]
}</code></pre></td></tr>
<tr><th colspan="2">Response</th></tr>
<tr><th>Structured Output 응답</th><td><pre><code>{
  "city": "서울",
  "population": 9400000
}</code></pre></td></tr>
</table>

**예시 2 — 분류 (Classification)**

<table>
<tr><th colspan="2">Request</th></tr>
<tr><th>Prompt</th><td>"로그인 버튼 클릭 시 500 에러가 발생합니다."</td></tr>
<tr><th>Pydantic Schema</th><td><pre><code>class Category(str, Enum):
    bug = "bug"
    feature = "feature_request"

class Priority(str, Enum):
    critical = "critical"
    high = "high"

class Ticket(BaseModel):
    category: Category
    priority: Priority
    summary: str</code></pre></td></tr>
<tr><th>Ticket.model_json_schema()</th><td><pre><code>{
  "title": "Ticket",
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["bug", "feature_request"]
    },
    "priority": {
      "type": "string",
      "enum": ["critical", "high"]
    },
    "summary": {"type": "string"}
  },
  "required": ["category", "priority", "summary"]
}</code></pre></td></tr>
<tr><th colspan="2">Response</th></tr>
<tr><th>Structured Output 응답</th><td><pre><code>{
  "category": "bug",
  "priority": "critical",
  "summary": "로그인 버튼 클릭 시 500 에러"
}</code></pre></td></tr>
</table>

**예시 3 — 추출 (Extraction)**

<table>
<tr><th colspan="2">Request</th></tr>
<tr><th>Prompt</th><td>"Invoice: ABC Co., INV-001, 2026-04-16, 총액 110,000원"</td></tr>
<tr><th>Pydantic Schema</th><td><pre><code>class Invoice(BaseModel):
    vendor_name: str
    invoice_number: str
    total: float</code></pre></td></tr>
<tr><th>Invoice.model_json_schema()</th><td><pre><code>{
  "title": "Invoice",
  "type": "object",
  "properties": {
    "vendor_name": {"type": "string"},
    "invoice_number": {"type": "string"},
    "total": {"type": "number"}
  },
  "required": ["vendor_name", "invoice_number", "total"]
}</code></pre></td></tr>
<tr><th colspan="2">Response</th></tr>
<tr><th>Structured Output 응답</th><td><pre><code>{
  "vendor_name": "ABC Co.",
  "invoice_number": "INV-001",
  "total": 110000.0
}</code></pre></td></tr>
</table>

**예시 4 — 분석 (Analysis)**

<table>
<tr><th colspan="2">Request</th></tr>
<tr><th>Prompt</th><td>"커피가 맛있고 직원이 친절하지만 주차가 불편해요."</td></tr>
<tr><th>Pydantic Schema</th><td><pre><code>class Review(BaseModel):
    overall_score: float
    strengths: list[str]
    weaknesses: list[str]</code></pre></td></tr>
<tr><th>Review.model_json_schema()</th><td><pre><code>{
  "title": "Review",
  "type": "object",
  "properties": {
    "overall_score": {"type": "number"},
    "strengths": {
      "type": "array",
      "items": {"type": "string"}
    },
    "weaknesses": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["overall_score", "strengths", "weaknesses"]
}</code></pre></td></tr>
<tr><th colspan="2">Response</th></tr>
<tr><th>Structured Output 응답</th><td><pre><code>{
  "overall_score": 7.5,
  "strengths": ["맛", "친절한 서비스"],
  "weaknesses": ["주차 공간 부족"]
}</code></pre></td></tr>
</table>

**예시 5 — 변환 (Transformation)**

<table>
<tr><th colspan="2">Request</th></tr>
<tr><th>Prompt</th><td>"다음 기사를 요약해줘.<br><br>2026년 인공지능 산업은 급속도로 발전하고 있습니다. 특히 멀티모달 모델과 에이전트 기술이 주목받고 있으며, 기업들의 AI 도입률도 크게 증가했습니다. 전문가들은 향후 5년간 AI가 대부분의 산업을 변화시킬 것으로 전망합니다."</td></tr>
<tr><th>Pydantic Schema</th><td><pre><code>class Language(str, Enum):
    ko = "ko"
    en = "en"

class Summary(BaseModel):
    title: str
    key_points: list[str]
    language: Language</code></pre></td></tr>
<tr><th>Summary.model_json_schema()</th><td><pre><code>{
  "title": "Summary",
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "key_points": {
      "type": "array",
      "items": {"type": "string"}
    },
    "language": {
      "type": "string",
      "enum": ["ko", "en"]
    }
  },
  "required": ["title", "key_points", "language"]
}</code></pre></td></tr>
<tr><th colspan="2">Response</th></tr>
<tr><th>Structured Output 응답</th><td><pre><code>{
  "title": "2026 AI 산업 동향",
  "key_points": [
    "멀티모달 모델 부상",
    "에이전트 기술 주목",
    "기업 AI 도입 확대"
  ],
  "language": "ko"
}</code></pre></td></tr>
</table>

---

## 2. Pydantic으로 스키마 정의하기

Python에서 Structured Output을 사용하는 권장 방법입니다. Pydantic `BaseModel`로 원하는 응답 구조를 정의하고, `model_json_schema()`로 JSON Schema를 자동 생성하여 API에 전달합니다.

### 2.0 환경 설정

```python
import os
from src.structured_output.auth import get_cognito_token

BASE_URL = os.environ.get("AI_API_BASE_URL", "http://ai-api-gateway.tech.madup")

HEADERS = {
    "Content-Type": "application/json",
    "X-Cognito-Token": get_cognito_token(),  # Cognito 인증 토큰
}
```

`.env` 파일에 `AI_API_BASE_URL`을 설정하거나, 기본값(`http://ai-api-gateway.tech.madup`)이 사용됩니다. `get_cognito_token()`은 내부 인증 토큰을 자동으로 발급합니다.

### 2.1 기본 흐름

`generate_structured` 헬퍼를 사용하면 스키마 정의와 API 호출을 간결하게 처리할 수 있습니다.

```python
from pydantic import BaseModel
from src.structured_output.client import generate_structured

# 1. 원하는 응답 구조를 Pydantic 모델로 정의
class CityInfo(BaseModel):
    city: str
    population: int
    area_km2: float

# 2. generate_structured로 호출 — 내부적으로 model_json_schema()를 그대로 전달
result = generate_structured(
    ["서울의 인구와 면적을 알려줘."],
    CityInfo.model_json_schema(),
    temperature=0.3,
)

# 3. 결과를 Pydantic 모델로 파싱
city = CityInfo(**result)
print(f"{city.city}: 인구 {city.population:,}명")
```

**API 응답 구조** (내부적으로 `generate_structured`가 처리하는 raw response):

```json
{
  "status": "success",
  "result": {
    "parsed": {"city": "서울", "population": 9411260, "area_km2": 605.21},
    "text": "{\"city\": \"서울\", \"population\": 9411260, \"area_km2\": 605.21}",
    "candidates": [{"finish_reason": "STOP"}]
  }
}
```

`result.parsed`에 파싱된 딕셔너리가 있으면 그대로 반환하고, `null`이면 `result.text`를 직접 파싱합니다. `finish_reason`이 `STOP`이 아니면 오류로 처리합니다 (자세한 내용은 [섹션 5](#5-에러-처리와-엣지-케이스) 참조).

### 2.2 Enum 활용

enum 필드를 정의하면 모델이 반드시 지정한 값 중 하나로만 응답합니다.

```python
from enum import Enum
from pydantic import BaseModel

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

schema = TicketAnalysis.model_json_schema()
```

`model_json_schema()` 결과:

```json
{
  "title": "TicketAnalysis",
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "sentiment": {
      "type": "string",
      "enum": ["positive", "negative", "neutral"]
    },
    "priority": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"]
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["title", "sentiment", "priority", "tags"]
}
```

### 2.3 중첩 모델

다른 `BaseModel`을 필드 타입으로 사용하면 중첩 구조를 쉽게 표현할 수 있습니다.

```python
from pydantic import BaseModel

class Ingredient(BaseModel):
    name: str
    quantity: str
    category: str

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[Ingredient]   # 객체 배열
    cooking_time: str

schema = Recipe.model_json_schema()
```

`model_json_schema()` 결과:

```json
{
  "title": "Recipe",
  "type": "object",
  "properties": {
    "recipe_name": {"type": "string"},
    "ingredients": {
      "type": "array",
      "items": {"$ref": "#/$defs/Ingredient"}
    },
    "cooking_time": {"type": "string"}
  },
  "required": ["recipe_name", "ingredients", "cooking_time"],
  "$defs": {
    "Ingredient": {
      "title": "Ingredient",
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "quantity": {"type": "string"},
        "category": {"type": "string"}
      },
      "required": ["name", "quantity", "category"]
    }
  }
}
```

중첩 모델은 `$defs`에 정의되고 `$ref`로 참조됩니다. API는 이 구조를 그대로 해석합니다.

### 2.4 Optional 필드

`null`이 허용되는 필드는 `Optional`을 사용합니다. 모델이 해당 정보를 찾지 못할 경우 `null`을 반환합니다.

```python
from typing import Optional
from pydantic import BaseModel

class ProductInfo(BaseModel):
    name: str
    price: float
    discount_rate: Optional[float] = None    # 할인이 없을 수 있음
    description: Optional[str] = None        # 설명이 없을 수 있음
    in_stock: bool

schema = ProductInfo.model_json_schema()
```

`model_json_schema()` 결과:

```json
{
  "title": "ProductInfo",
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "price": {"type": "number"},
    "discount_rate": {
      "anyOf": [{"type": "number"}, {"type": "null"}],
      "default": null
    },
    "description": {
      "anyOf": [{"type": "string"}, {"type": "null"}],
      "default": null
    },
    "in_stock": {"type": "boolean"}
  },
  "required": ["name", "price", "in_stock"]
}
```

`Optional` 필드는 `anyOf: [type, null]`로 변환되고 `required`에서 제외됩니다.

---

## 3. JSON Schema 구조 참조

Pydantic 없이 JSON Schema를 직접 작성하거나, `model_json_schema()`가 생성하는 구조를 이해하고 싶을 때 참조합니다.

### 3.1 Schema 기본 구조

```json
"response_schema": {
  "title": "SchemaName",         // 스키마 이름 (권장)
  "type": "object",              // 최상위 타입 (생략 시 object)
  "properties": {                // 필드 정의 (필수)
    "field_name": {
      "type": "string",          // 필드 타입
      "description": "..."       // 모델이 필드 의도를 이해하는 데 도움
    }
  },
  "required": ["field_name"]     // 필수 필드 목록 (권장)
}
```

### 3.2 기본 타입

| 타입 | 스키마 표기 | 설명 |
|---|---|---|
| `string` | `{"type": "string"}` | 문자열. 가장 범용적인 타입 |
| `integer` | `{"type": "integer"}` | 정수. 소수점 없는 숫자 |
| `number` | `{"type": "number"}` | 실수. 소수점 포함 가능 |
| `boolean` | `{"type": "boolean"}` | `true` / `false` |

### 3.3 복합 타입

#### Array (배열)

`items` 필드로 배열 항목의 타입을 정의합니다.

```json
// 문자열 배열
"tags": {
  "type": "array",
  "items": { "type": "string" }
}
// → ["AI", "마케팅", "데이터"]

// 객체 배열
"products": {
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "price": { "type": "number" }
    },
    "required": ["name", "price"]
  }
}
// → [{"name": "A", "price": 1000}, {"name": "B", "price": 2000}]
```

#### Object (중첩 객체)

`properties` 내에 또 다른 `object`를 정의하여 계층 구조를 만듭니다.

```json
"address": {
  "type": "object",
  "properties": {
    "city": { "type": "string" },
    "district": { "type": "string" },
    "coordinates": {
      "type": "object",
      "properties": {
        "lat": { "type": "number" },
        "lng": { "type": "number" }
      },
      "required": ["lat", "lng"]
    }
  },
  "required": ["city", "district", "coordinates"]
}
```

#### Enum (허용값 제한)

특정 값만 허용합니다. 분류, 등급, 상태 필드에 핵심적입니다.

```json
// 단일 enum
"sentiment": {
  "type": "string",
  "enum": ["positive", "negative", "neutral"]
}

// enum 배열 (복수 선택)
"categories": {
  "type": "array",
  "items": {
    "type": "string",
    "enum": ["tech", "health", "finance", "sports", "entertainment"]
  }
}
```

---

## 4. 스키마 설계 패턴

### 4.1 분류 (Classification)

텍스트를 특정 카테고리로 분류하는 패턴입니다. `enum`을 활용하면 결과가 반드시 정해진 값 중 하나로 나옵니다. `Field(description=...)`을 추가하면 모델이 각 필드의 의도를 더 정확히 이해합니다.

**Pydantic**

```python
from enum import Enum
from pydantic import BaseModel, Field

class Category(str, Enum):
    bug = "bug"
    feature_request = "feature_request"
    question = "question"
    improvement = "improvement"

class Priority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class Team(str, Enum):
    backend = "backend"
    frontend = "frontend"
    infra = "infra"
    data = "data"
    design = "design"

class TicketClassification(BaseModel):
    category: Category = Field(description="Type of the support ticket")
    priority: Priority = Field(description="Priority level of the ticket")
    assigned_team: Team = Field(description="Team responsible for handling this ticket")
    summary: str = Field(description="Brief one-sentence summary of the ticket")
```

**JSON Schema** (`TicketClassification.model_json_schema()`)

```json
{
  "title": "TicketClassification",
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["bug", "feature_request", "question", "improvement"],
      "description": "Type of the support ticket"
    },
    "priority": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"],
      "description": "Priority level of the ticket"
    },
    "assigned_team": {
      "type": "string",
      "enum": ["backend", "frontend", "infra", "data", "design"],
      "description": "Team responsible for handling this ticket"
    },
    "summary": {
      "type": "string",
      "description": "Brief one-sentence summary of the ticket"
    }
  },
  "required": ["category", "priority", "assigned_team", "summary"]
}
```

### 4.2 추출 (Extraction)

비정형 텍스트에서 특정 정보를 구조화하여 추출하는 패턴입니다.

**Pydantic**

```python
from pydantic import BaseModel, Field

class LineItem(BaseModel):
    description: str = Field(description="Item description")
    quantity: int = Field(description="Quantity of items")
    unit_price: float = Field(description="Price per unit")
    amount: float = Field(description="Total amount for this line item")

class InvoiceExtraction(BaseModel):
    vendor_name: str = Field(description="Name of the vendor/supplier company")
    invoice_number: str = Field(description="Invoice identification number")
    date: str = Field(description="Invoice date in YYYY-MM-DD format")
    items: list[LineItem] = Field(description="List of line items")
    subtotal: float = Field(description="Subtotal before tax")
    tax: float = Field(description="Tax amount")
    total: float = Field(description="Total amount including tax")
```

**JSON Schema** (`InvoiceExtraction.model_json_schema()`)

```json
{
  "title": "InvoiceExtraction",
  "type": "object",
  "properties": {
    "vendor_name": {"type": "string", "description": "Name of the vendor/supplier company"},
    "invoice_number": {"type": "string", "description": "Invoice identification number"},
    "date": {"type": "string", "description": "Invoice date in YYYY-MM-DD format"},
    "items": {
      "type": "array",
      "description": "List of line items",
      "items": {"$ref": "#/$defs/LineItem"}
    },
    "subtotal": {"type": "number", "description": "Subtotal before tax"},
    "tax": {"type": "number", "description": "Tax amount"},
    "total": {"type": "number", "description": "Total amount including tax"}
  },
  "required": ["vendor_name", "invoice_number", "date", "items", "subtotal", "tax", "total"],
  "$defs": {
    "LineItem": {
      "type": "object",
      "properties": {
        "description": {"type": "string"},
        "quantity": {"type": "integer"},
        "unit_price": {"type": "number"},
        "amount": {"type": "number"}
      },
      "required": ["description", "quantity", "unit_price", "amount"]
    }
  }
}
```

### 4.3 분석 (Analysis)

분석 결과를 여러 관점으로 구조화하는 패턴입니다. 점수, 분류, 설명을 함께 받을 수 있습니다.

**Pydantic**

```python
from enum import Enum
from pydantic import BaseModel, Field

class AspectSentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    mixed = "mixed"

class Aspect(BaseModel):
    aspect: str = Field(description="Name of the aspect being analyzed")
    score: float = Field(description="Score for this aspect from 0 to 10")
    sentiment: AspectSentiment = Field(description="Sentiment for this aspect")
    evidence: str = Field(description="Evidence from the text supporting this score")

class ContentAnalysis(BaseModel):
    overall_score: float = Field(description="Overall score from 0 to 10")
    aspects: list[Aspect] = Field(description="List of analyzed aspects")
    strengths: list[str] = Field(description="List of positive points")
    weaknesses: list[str] = Field(description="List of negative points or areas for improvement")
    recommendation: str = Field(description="Overall recommendation based on the analysis")
```

**JSON Schema** (`ContentAnalysis.model_json_schema()`)

```json
{
  "title": "ContentAnalysis",
  "type": "object",
  "properties": {
    "overall_score": {"type": "number", "description": "Overall score from 0 to 10"},
    "aspects": {"type": "array", "items": {"$ref": "#/$defs/Aspect"}},
    "strengths": {"type": "array", "items": {"type": "string"}, "description": "List of positive points"},
    "weaknesses": {"type": "array", "items": {"type": "string"}, "description": "List of negative points"},
    "recommendation": {"type": "string", "description": "Overall recommendation"}
  },
  "required": ["overall_score", "aspects", "strengths", "weaknesses", "recommendation"],
  "$defs": {
    "Aspect": {
      "type": "object",
      "properties": {
        "aspect": {"type": "string"},
        "score": {"type": "number"},
        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral", "mixed"]},
        "evidence": {"type": "string"}
      },
      "required": ["aspect", "score", "sentiment", "evidence"]
    }
  }
}
```

### 4.4 변환 (Transformation)

입력 데이터를 다른 구조로 변환하는 패턴입니다. 예를 들어 원문을 요약하면서 메타데이터를 함께 생성하는 경우입니다.

**Pydantic**

```python
from enum import Enum
from pydantic import BaseModel, Field

class Language(str, Enum):
    ko = "ko"
    en = "en"
    ja = "ja"
    zh = "zh"

class ArticleSummary(BaseModel):
    title: str = Field(description="Title of the article")
    summary: str = Field(description="2-3 sentence summary of the article")
    key_points: list[str] = Field(description="List of main points from the article")
    word_count: int = Field(description="Approximate word count of the original article")
    reading_time_minutes: int = Field(description="Estimated reading time in minutes")
    language: Language = Field(description="Language code of the article")
    topics: list[str] = Field(description="Main topics covered in the article")
```

**JSON Schema** (`ArticleSummary.model_json_schema()`)

```json
{
  "title": "ArticleSummary",
  "type": "object",
  "properties": {
    "title": {"type": "string", "description": "Title of the article"},
    "summary": {"type": "string", "description": "2-3 sentence summary"},
    "key_points": {"type": "array", "items": {"type": "string"}, "description": "List of main points"},
    "word_count": {"type": "integer", "description": "Approximate word count"},
    "reading_time_minutes": {"type": "integer", "description": "Estimated reading time in minutes"},
    "language": {"type": "string", "enum": ["ko", "en", "ja", "zh"], "description": "Language code"},
    "topics": {"type": "array", "items": {"type": "string"}, "description": "Main topics"}
  },
  "required": ["title", "summary", "key_points", "word_count", "reading_time_minutes", "language", "topics"]
}
```

### 4.5 비교/평가 (Comparison)

여러 항목을 비교 분석하여 구조화하는 패턴입니다.

**Pydantic**

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(description="Product name")
    pros: list[str] = Field(description="List of advantages")
    cons: list[str] = Field(description="List of disadvantages")
    score: float = Field(description="Overall score from 0 to 10")

class ProductComparison(BaseModel):
    products: list[Product] = Field(description="List of products being compared")
    winner: str = Field(description="Name of the winning product")
    reasoning: str = Field(description="Explanation for why the winner was chosen")
```

**JSON Schema** (`ProductComparison.model_json_schema()`)

```json
{
  "title": "ProductComparison",
  "type": "object",
  "properties": {
    "products": {"type": "array", "items": {"$ref": "#/$defs/Product"}, "description": "List of products"},
    "winner": {"type": "string", "description": "Name of the winning product"},
    "reasoning": {"type": "string", "description": "Explanation for why the winner was chosen"}
  },
  "required": ["products", "winner", "reasoning"],
  "$defs": {
    "Product": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "pros": {"type": "array", "items": {"type": "string"}},
        "cons": {"type": "array", "items": {"type": "string"}},
        "score": {"type": "number"}
      },
      "required": ["name", "pros", "cons", "score"]
    }
  }
}
```

---

## 5. 에러 처리와 엣지 케이스

### 5.1 parsed가 null인 경우

API 응답의 `result.parsed`는 게이트웨이가 자동으로 JSON을 파싱한 결과입니다. 스키마를 완전히 준수하지 못한 경우 `null`이 반환될 수 있으므로, `result.text`를 폴백으로 직접 파싱해야 합니다.

```python
result = data["result"]

if result.get("parsed") is not None:
    # 정상 케이스: 파싱된 딕셔너리 반환
    return result["parsed"]

# 폴백: text 필드를 직접 파싱
return json.loads(result["text"])
```

### 5.2 MAX_TOKENS 처리

`candidates[0]["finish_reason"]`가 `"MAX_TOKENS"`이면 출력이 중간에 잘려 JSON이 불완전합니다. 이 경우 파싱을 시도하지 말고 즉시 오류를 발생시켜야 합니다.

```python
finish = result["candidates"][0].get("finish_reason")
if finish == "MAX_TOKENS":
    raise RuntimeError(
        "MAX_TOKENS: 스키마를 단순화하거나 max_output_tokens를 늘려주세요"
    )
```

### 5.3 generate_structured 내부 구현

섹션 2.1에서 소개한 `generate_structured` 헬퍼의 전체 구현입니다. 위의 에러 처리 패턴이 모두 포함되어 있습니다.

```python
import json
import requests

def generate_structured(contents, schema, **config_opts):
    """Structured Output 요청 및 결과 파싱 헬퍼"""
    response = requests.post(
        f"{BASE_URL}/v1/tasks/generate-text",
        headers=HEADERS,
        timeout=60,
        json={
            "payload": {
                "model": "gemini-3-flash-preview",
                "contents": contents,
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                    **config_opts,
                }
            }
        }
    )

    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")

    data = response.json()

    if data["status"] != "success":
        raise RuntimeError(
            f"{data['error']['type']}: {data['error']['message']}"
        )

    result = data["result"]

    # finish_reason 확인
    finish = result["candidates"][0].get("finish_reason")
    if finish == "MAX_TOKENS":
        raise RuntimeError("MAX_TOKENS: 스키마를 단순화하거나 "
                           "max_output_tokens를 늘려주세요")

    # parsed 확인
    if result.get("parsed") is not None:
        return result["parsed"]

    # 폴백: text 직접 파싱
    return json.loads(result["text"])
```

---

## 6. 베스트 프랙티스

### 6.1 스키마 설계

- 필드 이름을 명확하고 설명적으로 작성하세요 (`s` → `sentiment`, `desc` → `description`)
- `Field(description=...)`으로 각 필드의 의도를 명시하세요. 모델의 응답 품질이 높아집니다
- `required` 배열에 핵심 필드를 모두 명시하세요. 누락을 방지합니다
- `enum`을 적극 활용하세요. 모델이 예측 불가능한 값을 반환하는 것을 방지합니다
- 중첩은 3단계 이하로 유지하세요. 너무 깊으면 토큰 소모가 커집니다
- 불필요한 필드는 제거하세요. 스키마가 단순할수록 응답 품질이 높아집니다

### 6.2 성능 최적화

- 추출/분류 작업은 `thinking_level: "low"`로 속도를 높이세요
- `temperature`를 낮게 (0.0~0.3) 설정하면 스키마 준수율이 높아집니다
- `max_output_tokens`를 스키마 크기에 맞게 적절히 설정하세요

### 6.3 안정성

- `use_retry: true` (기본값)를 유지하여 일시적 오류에 대비하세요
- `finish_reason`을 항상 확인하여 `MAX_TOKENS` 및 `SAFETY`를 감지하세요
- `parsed`가 `null`인 경우를 대비한 폴백 로직을 구현하세요

---

## 7. 빠른 참조 (스키마 템플릿)

자주 사용되는 스키마 패턴을 복사하여 사용할 수 있습니다.

### 단일 객체

```python
class MySchema(BaseModel):
    name: str
    value: float
    active: bool
```

```json
{
  "title": "MySchema",
  "properties": {
    "name": { "type": "string" },
    "value": { "type": "number" },
    "active": { "type": "boolean" }
  },
  "required": ["name", "value", "active"]
}
```

### 객체 배열

```python
class Item(BaseModel):
    id: int
    name: str

class MyList(BaseModel):
    items: list[Item]
```

```json
{
  "title": "MyList",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "name": { "type": "string" }
        },
        "required": ["id", "name"]
      }
    }
  },
  "required": ["items"]
}
```

### 분류 + 점수

```python
class Cat(str, Enum):
    cat_a = "cat_a"
    cat_b = "cat_b"
    cat_c = "cat_c"

class Classification(BaseModel):
    category: Cat
    confidence: float
    reasoning: str
```

```json
{
  "title": "Classification",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["cat_a", "cat_b", "cat_c"]
    },
    "confidence": { "type": "number" },
    "reasoning": { "type": "string" }
  },
  "required": ["category", "confidence", "reasoning"]
}
```
