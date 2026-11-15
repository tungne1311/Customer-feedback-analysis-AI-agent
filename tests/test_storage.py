import json

import pytest

from src.schemas import AnalysisReport
from src.storage import DataFileError, load_feedbacks, load_report, save_report


def _write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_load_feedbacks_accepts_labeled_and_unlabeled(tmp_path):
    path = _write(tmp_path / "fb.json", [
        {
            "id": "f1", "project": " DuAnA ", "source": "crm", "text": "Giá cao.",
            "expected_topic": "price", "expected_sentiment": "negative",
        },
        {"id": "f2", "project": "DuAnA", "source": "survey", "text": "Ổn."},
    ])

    feedbacks, rejected = load_feedbacks(path)

    assert rejected == []
    assert [f.id for f in feedbacks] == ["f1", "f2"]
    assert feedbacks[0].project == "DuAnA"
    assert feedbacks[1].expected_topic is None


def test_invalid_records_are_rejected_without_leaking_content(tmp_path):
    secret_text = "Gọi tôi 0901234567"
    path = _write(tmp_path / "fb.json", [
        {"id": "ok", "project": "DuAnA", "source": "crm", "text": "Tốt."},
        {"id": "bad_source", "project": "DuAnA", "source": "zalo", "text": secret_text},
        {"project": "DuAnA", "source": "crm", "text": secret_text},
        {"id": "empty_text", "project": "DuAnA", "source": "crm", "text": "   "},
        {"id": "ok", "project": "DuAnA", "source": "crm", "text": "Trùng id."},
        "không phải object",
    ])

    feedbacks, rejected = load_feedbacks(path)

    assert [f.id for f in feedbacks] == ["ok"]
    assert [r.id for r in rejected] == [
        "bad_source", "index_2", "empty_text", "ok", "index_5",
    ]
    assert all("0901234567" not in r.error for r in rejected)


def test_feedback_file_must_be_a_list(tmp_path):
    path = _write(tmp_path / "fb.json", {"id": "f1"})

    with pytest.raises(DataFileError):
        load_feedbacks(path)


def test_report_round_trip_keeps_contract(tmp_path, sample_report):
    report = AnalysisReport.model_validate(sample_report)
    path = save_report(report, tmp_path / "out" / "report.json")

    assert json.loads(path.read_text(encoding="utf-8")) == sample_report
    assert load_report(path) == report
    assert not path.with_name("report.json.tmp").exists()


@pytest.mark.parametrize(
    "content",
    ["{ không phải json", json.dumps({"results": [{"id": "x"}], "errors": []})],
)
def test_load_report_rejects_broken_files(tmp_path, content):
    path = tmp_path / "report.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(DataFileError):
        load_report(path)


def test_load_report_missing_file(tmp_path):
    with pytest.raises(DataFileError):
        load_report(tmp_path / "missing.json")
