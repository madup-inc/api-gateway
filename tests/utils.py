"""테스트 전용 유틸리티 — generate_structured 헬퍼"""
import json

import requests

from src.structured_output.client import BASE_URL, get_headers


def generate_structured(
    contents: list,
    schema: dict,
    model: str = "gemini-3-flash-preview",
    **config_opts,
) -> dict:
    response = requests.post(
        f"{BASE_URL}/v1/tasks/generate-text",
        headers=get_headers(),
        timeout=60,
        json={
            "payload": {
                "model": model,
                "contents": contents,
                "config": {
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                    **config_opts,
                },
            }
        },
    )
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:200]}")
    data = response.json()

    if data["status"] != "success":
        raise RuntimeError(f"{data['error']['type']}: {data['error']['message']}")

    result = data["result"]

    finish = result["candidates"][0].get("finish_reason")
    if finish == "MAX_TOKENS":
        raise RuntimeError("MAX_TOKENS: 스키마를 단순화하거나 max_output_tokens를 늘려주세요")

    if result.get("parsed") is not None:
        return result["parsed"]

    return json.loads(result["text"])
