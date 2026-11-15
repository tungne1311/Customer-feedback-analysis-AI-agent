from src.schemas import AnalysisReport
from src.stats import stats_payload, summarize_projects
from src.tools import get_negative_feedback, get_project_stats


def test_summarize_projects_counts_from_data(sample_report):
    report = AnalysisReport.model_validate(sample_report)

    summary = summarize_projects(report.results)

    assert list(summary) == ["DuAnA", "DuAnB"]
    assert stats_payload("DuAnA", summary["DuAnA"]) == {
        "project": "DuAnA",
        "analyzed_feedback_count": 4,
        "negative_feedback_count": 3,
        "negative_rate_percent": 75.0,
        "negative_topics": {"sales_service": 2, "price": 1},
    }
    assert summary["DuAnB"].negative == 0
    assert summary["DuAnB"].negative_rate_percent == 0.0


def test_get_project_stats(report_file):
    assert get_project_stats(" DuAnA ") == {
        "status": "ok",
        "project": "DuAnA",
        "analyzed_feedback_count": 4,
        "negative_feedback_count": 3,
        "negative_rate_percent": 75.0,
        "negative_topics": {"sales_service": 2, "price": 1},
    }

    missing = get_project_stats("DuAnC")
    assert missing["status"] == "not_found"
    assert missing["available_projects"] == ["DuAnA", "DuAnB"]

    assert get_project_stats("")["status"] == "invalid_input"
    assert get_project_stats(123)["status"] == "invalid_input"


def test_get_negative_feedback_filters_and_keeps_evidence_ids(report_file):
    result = get_negative_feedback("DuAnA", topic="sales_service", limit=1)

    assert result["status"] == "ok"
    assert result["matching_feedback_count"] == 2
    assert result["returned_feedback_count"] == 1
    assert result["feedbacks"] == [{
        "id": "a1",
        "source": "crm",
        "text": "Nhân viên trả lời chậm.",
        "topic": "sales_service",
        "evidence": "trả lời chậm",
    }]

    all_topics = get_negative_feedback("DuAnA")
    assert [f["id"] for f in all_topics["feedbacks"]] == ["a1", "a2", "a3"]

    assert get_negative_feedback("DuAnB")["matching_feedback_count"] == 0
    assert get_negative_feedback("DuAnC")["status"] == "not_found"


def test_get_negative_feedback_rejects_bad_arguments(report_file):
    assert get_negative_feedback("DuAnA", topic="bad_topic")["status"] == "invalid_input"
    assert get_negative_feedback("DuAnA", topic=5)["status"] == "invalid_input"
    assert get_negative_feedback("DuAnA", limit=0)["status"] == "invalid_input"
    assert get_negative_feedback("DuAnA", limit=6)["status"] == "invalid_input"
    assert get_negative_feedback("DuAnA", limit=3.0)["status"] == "invalid_input"


def test_tools_report_error_when_report_is_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("VOC_REPORT_PATH", str(tmp_path / "missing.json"))

    assert get_project_stats("DuAnA")["status"] == "error"
    assert get_negative_feedback("DuAnA")["status"] == "error"
