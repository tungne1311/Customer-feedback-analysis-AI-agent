"""Truy cập Gemini. Mọi lời gọi model đi qua `generate` để lỗi được xử lý thống nhất."""

import json

import httpx
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from src.config import Settings, get_api_key
from src.prompts import CLASSIFY_INSTRUCTIONS, INSIGHT_INSTRUCTIONS
from src.schemas import FeedbackAnalysis, describe_validation_error


class LLMError(Exception):
    """Gọi Gemini thất bại hoặc output không hợp lệ.

    Message không chứa nội dung phản hồi khách hàng nên có thể ghi vào báo cáo lỗi.
    """


def create_client(settings: Settings) -> genai.Client:
    return genai.Client(
        api_key=get_api_key(),
        http_options=types.HttpOptions(
            timeout=settings.request_timeout_ms,
            retry_options=types.HttpRetryOptions(
                attempts=settings.retry_attempts,
            ),
        ),
    )


def generate(client, *, model: str, contents, config: types.GenerateContentConfig):
    try:
        return client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
    except errors.APIError as exc:
        raise LLMError(f"Lỗi API Gemini (mã {exc.code}): {exc.message}") from exc
    except httpx.HTTPError as exc:
        # Gồm cả timeout. Không đưa chi tiết request vào message.
        raise LLMError(f"Lỗi kết nối tới Gemini: {type(exc).__name__}") from exc


def _minimal_thinking() -> types.ThinkingConfig:
    return types.ThinkingConfig(thinking_level="minimal")


def classify_feedback(client, text: str, settings: Settings) -> FeedbackAnalysis:
    """Phân loại chủ đề và cảm xúc của một phản hồi. `text` phải là bản đã che PII."""
    response = generate(
        client,
        model=settings.classifier_model,
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=CLASSIFY_INSTRUCTIONS,
            thinking_config=_minimal_thinking(),
            max_output_tokens=settings.max_output_tokens,
            response_mime_type="application/json",
            response_json_schema=FeedbackAnalysis.model_json_schema(),
        ),
    )

    if not response.text:
        raise LLMError("Gemini chưa trả về kết quả văn bản.")

    try:
        return FeedbackAnalysis.model_validate_json(response.text)
    except ValidationError as exc:
        raise LLMError(
            "Kết quả phân loại không đúng schema: "
            + describe_validation_error(exc)
        ) from exc


def generate_insight(client, stats_payload: dict, settings: Settings) -> str:
    """Viết bản nháp tóm tắt và đề xuất từ số liệu đã tính sẵn của một dự án."""
    response = generate(
        client,
        model=settings.insight_model,
        contents=json.dumps(stats_payload, ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=INSIGHT_INSTRUCTIONS,
            thinking_config=_minimal_thinking(),
            max_output_tokens=settings.max_output_tokens,
        ),
    )

    if not response.text:
        raise LLMError("Gemini chưa trả về báo cáo.")

    return response.text
