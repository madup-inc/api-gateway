# Structured Output Usage Guide

**AI API Gateway — Text Generation Service**  
http://ai-api-gateway.tech.madup  
2026년 4월

---

## 목차

1. [Structured Output이란?](#1-structured-output이란)
2. [기본 구조](#2-기본-구조)
3. [타입 시스템](#3-타입-시스템)
4. [스키마 설계 패턴](#4-스키마-설계-패턴)
5. [Pydantic으로 스키마 정의하기](#5-pydantic으로-스키마-정의하기)
6. [에러 처리와 엣지 케이스](#6-에러-처리와-엣지-케이스)
7. [베스트 프랙티스](#7-베스트-프랙티스)
8. [빠른 참조 (스키마 템플릿)](#8-빠른-참조-스키마-템플릿)

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

---

## 2. 기본 구조

### 2.1 필수 설정

Structured Output을 활성화하려면 `config` 내에 두 필드를 함께 설정합니다:

```json
"config": {
  "response_mime_type": "application/json",   // 필수: JSON 출력 활성화
  "response_schema": { ... }                  // 필수: 응답 JSON Schema 정의
}
```

`response_mime_type`을 `"application/json"`으로 설정하면, 모델은 반드시 `response_schema`에 정의된 구조로 응답합니다.

### 2.2 Schema 기본 구조

```json
"response_schema": {
  "title": "SchemaName",         // 스키마 이름 (권장)
  "type": "object",              // 최상위 타입 (생략 시 object)
  "properties": {                // 필드 정의 (필수)
    "field_name": {
      "type": "string"           // 필드 타입
    }
  },
  "required": ["field_name"]     // 필수 필드 목록 (권장)
}
```

---

## 3. 타입 시스템

### 3.1 기본 타입

| 타입 | 스키마 표기 | 설명 |
|---|---|---|
| `string` | `{"type": "string"}` | 문자열. 가장 범용적인 타입 |
| `integer` | `{"type": "integer"}` | 정수. 소수점 없는 숫자 |
| `number` | `{"type": "number"}` | 실수. 소수점 포함 가능 |
| `boolean` | `{"type": "boolean"}` | `true` / `false` |

### 3.2 복합 타입

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

텍스트를 특정 카테고리로 분류하는 패턴입니다. `enum`을 활용하면 결과가 반드시 정해진 값 중 하나로 나옵니다.

```json
{
  "title": "TicketClassification",
  "properties": {
    "category": {
      "type": "string",
      "enum": ["bug", "feature_request", "question", "improvement"]
    },
    "priority": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"]
    },
    "assigned_team": {
      "type": "string",
      "enum": ["backend", "frontend", "infra", "data", "design"]
    },
    "summary": { "type": "string" }
  },
  "required": ["category", "priority", "assigned_team", "summary"]
}
```

### 4.2 추출 (Extraction)

비정형 텍스트에서 특정 정보를 구조화하여 추출하는 패턴입니다.

```json
{
  "title": "InvoiceExtraction",
  "properties": {
    "vendor_name": { "type": "string" },
    "invoice_number": { "type": "string" },
    "date": { "type": "string" },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "description": { "type": "string" },
          "quantity": { "type": "integer" },
          "unit_price": { "type": "number" },
          "amount": { "type": "number" }
        },
        "required": ["description", "quantity", "unit_price", "amount"]
      }
    },
    "subtotal": { "type": "number" },
    "tax": { "type": "number" },
    "total": { "type": "number" }
  },
  "required": ["vendor_name", "invoice_number", "date", "items",
               "subtotal", "tax", "total"]
}
```

### 4.3 분석 (Analysis)

분석 결과를 여러 관점으로 구조화하는 패턴입니다. 점수, 분류, 설명을 함께 받을 수 있습니다.

```json
{
  "title": "ContentAnalysis",
  "properties": {
    "overall_score": { "type": "number" },
    "aspects": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "aspect": { "type": "string" },
          "score": { "type": "number" },
          "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "neutral", "mixed"]
          },
          "evidence": { "type": "string" }
        },
        "required": ["aspect", "score", "sentiment", "evidence"]
      }
    },
    "strengths": {
      "type": "array",
      "items": { "type": "string" }
    },
    "weaknesses": {
      "type": "array",
      "items": { "type": "string" }
    },
    "recommendation": { "type": "string" }
  },
  "required": ["overall_score", "aspects", "strengths",
               "weaknesses", "recommendation"]
}
```

### 4.4 변환 (Transformation)

입력 데이터를 다른 구조로 변환하는 패턴입니다. 예를 들어 원문을 요약하면서 메타데이터를 함께 생성하는 경우입니다.

```json
{
  "title": "ArticleSummary",
  "properties": {
    "title": { "type": "string" },
    "summary": { "type": "string" },
    "key_points": {
      "type": "array",
      "items": { "type": "string" }
    },
    "word_count": { "type": "integer" },
    "reading_time_minutes": { "type": "integer" },
    "language": {
      "type": "string",
      "enum": ["ko", "en", "ja", "zh"]
    },
    "topics": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["title", "summary", "key_points", "word_count",
               "reading_time_minutes", "language", "topics"]
}
```

### 4.5 비교/평가 (Comparison)

여러 항목을 비교 분석하여 구조화하는 패턴입니다.

```json
{
  "title": "ProductComparison",
  "properties": {
    "products": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "pros": { "type": "array", "items": { "type": "string" } },
          "cons": { "type": "array", "items": { "type": "string" } },
          "score": { "type": "number" }
        },
        "required": ["name", "pros", "cons", "score"]
      }
    },
    "winner": { "type": "string" },
    "reasoning": { "type": "string" }
  },
  "required": ["products", "winner", "reasoning"]
}
```

---

## 5. Pydantic으로 스키마 정의하기

Python에서는 JSON Schema를 직접 작성하는 대신 Pydantic `BaseModel`을 사용하면 타입 안전성과 자동 스키마 생성을 모두 얻을 수 있습니다.

### 5.1 기본 모델

```python
from pydantic import BaseModel

class CityInfo(BaseModel):
    city: str
    population: int
    area_km2: float

# API 요청 시:
schema = CityInfo.model_json_schema()
# → {"title": "CityInfo", "properties": {...}, "required": [...], "type": "object"}
```

### 5.2 Enum 활용

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
```

### 5.3 중첩 모델

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

class RecipeBook(BaseModel):
    recipes: list[Recipe]           # 중첩 배열

# 자동 생성된 스키마가 모든 중첩 구조를 포함합니다
schema = RecipeBook.model_json_schema()
```

### 5.4 Optional 필드

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
```

### 5.5 요청 예제

```python
import requests
from pydantic import BaseModel

class CityInfo(BaseModel):
    city: str
    population: int
    area_km2: float

response = requests.post(
    f"{BASE_URL}/v1/tasks/generate-text",
    headers=HEADERS,
    json={
        "payload": {
            "model": "gemini-3-flash-preview",
            "contents": ["서울의 인구와 면적을 알려줘."],
            "config": {
                "response_mime_type": "application/json",
                "response_schema": CityInfo.model_json_schema(),
                "temperature": 0.3
            }
        }
    }
)

data = response.json()
if data["status"] == "success":
    city = CityInfo(**data["result"]["parsed"])
    print(f"{city.city}: 인구 {city.population:,}명")
```

---

## 6. 에러 처리와 엣지 케이스

### 6.1 parsed가 null인 경우

API 응답의 `result.parsed`는 게이트웨이가 자동으로 JSON을 파싱한 결과입니다. 스키마를 완전히 준수하지 못한 경우 `null`이 반환될 수 있으므로, `result.text`를 폴백으로 직접 파싱해야 합니다.

```python
result = data["result"]

if result.get("parsed") is not None:
    # 정상 케이스: 파싱된 딕셔너리 반환
    return result["parsed"]

# 폴백: text 필드를 직접 파싱
return json.loads(result["text"])
```

### 6.2 MAX_TOKENS 처리

`candidates[0]["finish_reason"]`가 `"MAX_TOKENS"`이면 출력이 중간에 잘려 JSON이 불완전합니다. 이 경우 파싱을 시도하지 말고 즉시 오류를 발생시켜야 합니다.

```python
finish = result["candidates"][0].get("finish_reason")
if finish == "MAX_TOKENS":
    raise RuntimeError(
        "MAX_TOKENS: 스키마를 단순화하거나 max_output_tokens를 늘려주세요"
    )
```

### 6.3 권장 에러 처리 패턴

```python
import json
import requests

def generate_structured(contents, schema, **config_opts):
    """Structured Output 요청 및 결과 파싱 헬퍼"""
    response = requests.post(
        f"{BASE_URL}/v1/tasks/generate-text",
        headers=HEADERS,
        timeout=30,
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

## 7. 베스트 프랙티스

### 7.1 스키마 설계

- 필드 이름을 명확하고 설명적으로 작성하세요 (`s` → `sentiment`, `desc` → `description`)
- `required` 배열에 핵심 필드를 모두 명시하세요. 누락을 방지합니다
- `enum`을 적극 활용하세요. 모델이 예측 불가능한 값을 반환하는 것을 방지합니다
- 중첩은 3단계 이하로 유지하세요. 너무 깊으면 토큰 소모가 커집니다
- 불필요한 필드는 제거하세요. 스키마가 단순할수록 응답 품질이 높아집니다

### 7.2 성능 최적화

- 추출/분류 작업은 `thinking_level: "low"`로 속도를 높이세요
- `temperature`를 낮게 (0.0~0.3) 설정하면 스키마 준수율이 높아집니다
- `max_output_tokens`를 스키마 크기에 맞게 적절히 설정하세요

### 7.3 안정성

- `use_retry: true` (기본값)를 유지하여 일시적 오류에 대비하세요
- `finish_reason`을 항상 확인하여 `MAX_TOKENS` 및 `SAFETY`를 감지하세요
- `parsed`가 `null`인 경우를 대비한 폴백 로직을 구현하세요

---

## 8. 빠른 참조 (스키마 템플릿)

자주 사용되는 스키마 패턴을 복사하여 사용할 수 있습니다.

### 단일 객체

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
