"""
AI API Gateway — Structured Output 클라이언트
"""
import json
import os

import requests
from dotenv import load_dotenv

from .auth import get_cognito_token

load_dotenv()

BASE_URL = os.environ.get("AI_API_BASE_URL", "http://ai-api-gateway.tech.madup")


def get_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "X-Cognito-Token": get_cognito_token(),
    }



def generate_async(
    contents: list,
    schema: dict,
    model: str = "gemini-3-flash-preview",
    **config_opts,
) -> str:
    """비동기 요청 제출 후 task_id 반환 (문서 Section 6)"""
    response = requests.post(
        f"{BASE_URL}/v1/tasks/generate-text?async=true",
        headers=get_headers(),
        timeout=30,
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
    data = response.json()
    if data.get("status") == "error":
        raise RuntimeError(f"{data['error']['type']}: {data['error']['message']}")
    return data["task_id"]


def parse_stream(stream_response) -> dict:
    """스트리밍 응답을 누적하여 JSON 파싱 (문서 Section 6)"""
    accumulated_text = ""
    for line in stream_response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue
        payload = json.loads(line.removeprefix("data:").strip())
        if payload.get("status") in ("success", "error"):
            break
        text = payload.get("chunk", {}).get("text", "")
        if text:
            accumulated_text += text
    return json.loads(accumulated_text)


def stream_task(task_id: str) -> dict:
    """task_id로 스트리밍 결과 수신"""
    with requests.get(
        f"{BASE_URL}/v1/tasks/{task_id}/stream",
        headers=get_headers(),
        stream=True,
        timeout=300,
    ) as resp:
        return parse_stream(resp)


def build_request_payload(
    contents: list,
    schema: dict,
    model: str = "gemini-3-flash-preview",
    **config_opts,
) -> dict:
    """API 요청 payload 빌더"""
    return {
        "payload": {
            "model": model,
            "contents": contents,
            "config": {
                "response_mime_type": "application/json",
                "response_schema": schema,
                **config_opts,
            },
        }
    }
