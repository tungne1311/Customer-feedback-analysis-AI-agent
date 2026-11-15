import json
from types import SimpleNamespace

import httpx
import pytest
from google.genai import errors

from src.llm import LLMError, classify_feedback, generate_insight


def _text_response(text):
    return SimpleNamespace(text=text)


def test_classify_returns_validated_analysis_using_classifier_model(fake_client, settings):
    payload = {"topic": "price", "sentiment": "negative", "evidence": "Giá cao"}
    client = fake_client([_text_response(json.dumps(payload))])

    analysis = classify_feedback(client, "Giá cao quá.", settings)

    assert analysis.model_dump() == payload
    assert client.calls[0]["model"] == settings.classifier_model
    assert client.calls[0]["contents"] == "Giá cao quá."
    assert client.calls[0]["config"].max_output_tokens == settings.max_output_tokens


def test_classify_rejects_empty_response(fake_client, settings):
    client = fake_client([_text_response("")])

    with pytest.raises(LLMError, match="chưa trả về"):
        classify_feedback(client, "Giá cao quá.", settings)


@pytest.mark.parametrize(
    "raw_output",
    [
        "Khách 0901234567 phàn nàn, không phải JSON",
        json.dumps({"topic": "0901234567", "sentiment": "negative", "evidence": "x"}),
        json.dumps({
            "topic": "price", "sentiment": "negative", "evidence": "x", "note": "0901234567",
        }),
    ],
)
def test_schema_errors_do_not_echo_model_output(fake_client, settings, raw_output):
    client = fake_client([_text_response(raw_output)])

    with pytest.raises(LLMError) as excinfo:
        classify_feedback(client, "văn bản", settings)

    assert "không đúng schema" in str(excinfo.value)
    assert "0901234567" not in str(excinfo.value)


def test_api_and_network_errors_become_llm_error(fake_client, settings):
    api_error = errors.APIError(
        429,
        {"error": {"message": "Quota exceeded", "status": "RESOURCE_EXHAUSTED"}},
    )
    client = fake_client([api_error, httpx.ReadTimeout("timed out")])

    with pytest.raises(LLMError, match="429"):
        classify_feedback(client, "văn bản", settings)

    with pytest.raises(LLMError, match="ReadTimeout"):
        classify_feedback(client, "văn bản", settings)


def test_insight_sends_only_computed_stats_to_insight_model(fake_client, settings):
    stats = {
        "project": "DuAnA",
        "analyzed_feedback_count": 4,
        "negative_feedback_count": 3,
        "negative_rate_percent": 75.0,
        "negative_topics": {"sales_service": 2, "price": 1},
    }
    client = fake_client([_text_response("Bản nháp.")])

    assert generate_insight(client, stats, settings) == "Bản nháp."
    assert client.calls[0]["model"] == settings.insight_model
    assert json.loads(client.calls[0]["contents"]) == stats
