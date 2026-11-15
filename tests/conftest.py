import copy
import json
from types import SimpleNamespace

import pytest

from src.config import Settings

# Dữ liệu trong test đều là dữ liệu giả, không phải thông tin định danh thật.


def _record(record_id, project, source, text, topic, sentiment, evidence):
    return {
        "id": record_id,
        "project": project,
        "source": source,
        "text": text,
        "analysis": {"topic": topic, "sentiment": sentiment, "evidence": evidence},
        "evaluation": None,
    }


SAMPLE_REPORT = {
    "results": [
        _record(
            "a1", "DuAnA", "crm", "Nhân viên trả lời chậm.",
            "sales_service", "negative", "trả lời chậm",
        ),
        _record(
            "a2", "DuAnA", "survey", "Sale hẹn rồi không gọi lại.",
            "sales_service", "negative", "không gọi lại",
        ),
        _record("a3", "DuAnA", "social", "Giá quá cao.", "price", "negative", "Giá quá cao"),
        _record("a4", "DuAnA", "survey", "Hồ bơi đẹp.", "amenities", "positive", "Hồ bơi đẹp"),
        _record(
            "b1", "DuAnB", "social", "Thủ tục nhanh gọn.",
            "legal_process", "positive", "nhanh gọn",
        ),
    ],
    "errors": [{"id": "a5", "error": "Bằng chứng đang rỗng."}],
}


@pytest.fixture
def sample_report():
    return copy.deepcopy(SAMPLE_REPORT)


@pytest.fixture
def settings(tmp_path):
    return Settings(
        feedback_path=tmp_path / "feedback.json",
        report_path=tmp_path / "report.json",
        classifier_model="model-nho",
        insight_model="model-tong-hop",
        agent_model="model-agent",
        max_output_tokens=256,
        request_timeout_ms=1000,
        retry_attempts=1,
        agent_max_steps=3,
    )


@pytest.fixture
def report_file(tmp_path, monkeypatch):
    """Ghi báo cáo mẫu và trỏ cấu hình tới nó (tool của agent đọc qua VOC_REPORT_PATH)."""
    path = tmp_path / "report.json"
    path.write_text(json.dumps(SAMPLE_REPORT, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setenv("VOC_REPORT_PATH", str(path))
    return path


class FakeClient:
    """Client giả: trả lần lượt các response đã chuẩn bị và ghi lại lời gọi."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.models = SimpleNamespace(generate_content=self._generate_content)

    def _generate_content(self, *, model, contents, config):
        self.calls.append({"model": model, "contents": contents, "config": config})
        response = self._responses.pop(0)

        if isinstance(response, Exception):
            raise response

        return response


@pytest.fixture
def fake_client():
    return FakeClient
