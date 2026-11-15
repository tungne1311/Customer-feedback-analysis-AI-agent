from src.llm import LLMError
from src.pipeline import analyze_feedbacks, summarize_evaluation
from src.schemas import Feedback, FeedbackAnalysis


def _feedback(record_id, text, **extra):
    return Feedback(id=record_id, project="DuAnA", source="crm", text=text, **extra)


def test_pii_is_redacted_before_llm_and_in_report():
    feedback = _feedback(
        "f1",
        "Tôi là Trần Thị B, sale không gọi lại số 0901234567, mail b.tran@example.com.",
        customer_name="Trần Thị B",
    )
    seen_by_llm = []

    def classify(text):
        seen_by_llm.append(text)
        return FeedbackAnalysis(
            topic="sales_service", sentiment="negative", evidence="sale không gọi lại",
        )

    report = analyze_feedbacks([feedback], classify)

    expected = "Tôi là [NAME], sale không gọi lại số [PHONE], mail [EMAIL]."
    assert seen_by_llm == [expected]
    assert report.results[0].text == expected

    dumped = report.model_dump_json()
    for secret in ("Trần Thị B", "0901234567", "b.tran@example.com"):
        assert secret not in dumped


def test_bad_evidence_and_llm_errors_are_recorded_and_run_continues():
    answers = {
        "Giá cao quá.": FeedbackAnalysis(topic="price", sentiment="negative", evidence="  "),
        "Bàn giao trễ.": FeedbackAnalysis(
            topic="construction_progress", sentiment="negative", evidence="câu LLM tự viết",
        ),
        "Hồ bơi đẹp.": FeedbackAnalysis(
            topic="amenities", sentiment="positive", evidence="Hồ bơi đẹp",
        ),
    }

    def classify(text):
        if text == "Lỗi mạng.":
            raise LLMError("Lỗi kết nối tới Gemini: ReadTimeout")
        return answers[text]

    report = analyze_feedbacks(
        [
            _feedback("empty", "Giá cao quá."),
            _feedback("invented", "Bàn giao trễ."),
            _feedback("timeout", "Lỗi mạng."),
            _feedback("ok", "Hồ bơi đẹp."),
        ],
        classify,
    )

    assert [r.id for r in report.results] == ["ok"]
    assert {e.id: e.error for e in report.errors} == {
        "empty": "Bằng chứng đang rỗng.",
        "invented": "Bằng chứng không có trong phản hồi gốc.",
        "timeout": "Lỗi kết nối tới Gemini: ReadTimeout",
    }


def test_evaluation_only_for_labeled_feedback():
    def classify(text):
        return FeedbackAnalysis(topic="price", sentiment="negative", evidence="Giá")

    report = analyze_feedbacks(
        [
            _feedback("right", "Giá cao.", expected_topic="price", expected_sentiment="negative"),
            _feedback("wrong", "Giá ổn.", expected_topic="price", expected_sentiment="neutral"),
            _feedback("unlabeled", "Giá thế nào?"),
        ],
        classify,
    )

    by_id = {r.id: r.evaluation for r in report.results}
    assert by_id["right"].topic_correct and by_id["right"].sentiment_correct
    assert by_id["wrong"].topic_correct and not by_id["wrong"].sentiment_correct
    assert by_id["unlabeled"] is None

    summary = summarize_evaluation(report)
    assert (summary.labeled, summary.correct_topics, summary.correct_sentiments) == (2, 2, 1)
