"""Luồng phân tích: che PII → phân loại bằng LLM → kiểm tra bằng chứng → ghi nhận kết quả."""

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from src.llm import LLMError
from src.privacy import redact_pii
from src.schemas import (
    AnalysisReport,
    AnalyzedFeedback,
    Evaluation,
    FailedRecord,
    Feedback,
    FeedbackAnalysis,
)

logger = logging.getLogger(__name__)


class EvidenceError(ValueError):
    """Bằng chứng LLM trả về không dùng được."""


def check_evidence(evidence: str, text: str) -> None:
    if not evidence.strip():
        raise EvidenceError("Bằng chứng đang rỗng.")

    if evidence not in text:
        raise EvidenceError("Bằng chứng không có trong phản hồi gốc.")


def _evaluate(feedback: Feedback, analysis: FeedbackAnalysis) -> Evaluation | None:
    if feedback.expected_topic is None or feedback.expected_sentiment is None:
        return None

    return Evaluation(
        topic_correct=analysis.topic == feedback.expected_topic,
        sentiment_correct=analysis.sentiment == feedback.expected_sentiment,
    )


def analyze_feedbacks(
    feedbacks: Iterable[Feedback],
    classify: Callable[[str], FeedbackAnalysis],
) -> AnalysisReport:
    """Phân tích từng phản hồi. `classify` chỉ nhận văn bản đã che PII.

    Log chỉ ghi id và nhãn, không ghi nội dung phản hồi.
    """
    results: list[AnalyzedFeedback] = []
    failed: list[FailedRecord] = []

    for feedback in feedbacks:
        safe_text = redact_pii(feedback.text, feedback.customer_name)

        try:
            analysis = classify(safe_text)
            check_evidence(analysis.evidence, safe_text)
        except (LLMError, EvidenceError) as exc:
            failed.append(FailedRecord(id=feedback.id, error=str(exc)))
            logger.info("%s: phân tích thất bại: %s", feedback.id, exc)
            continue

        evaluation = _evaluate(feedback, analysis)

        results.append(AnalyzedFeedback(
            id=feedback.id,
            project=feedback.project,
            source=feedback.source,
            text=safe_text,
            analysis=analysis,
            evaluation=evaluation,
        ))

        logger.info(
            "%s: chủ đề=%s | cảm xúc=%s%s",
            feedback.id,
            analysis.topic,
            analysis.sentiment,
            ""
            if evaluation is None
            else (
                f" | khớp đáp án: chủ đề={evaluation.topic_correct}, "
                f"cảm xúc={evaluation.sentiment_correct}"
            ),
        )

    return AnalysisReport(results=results, errors=failed)


@dataclass(frozen=True)
class EvaluationSummary:
    labeled: int
    correct_topics: int
    correct_sentiments: int


def summarize_evaluation(report: AnalysisReport) -> EvaluationSummary:
    """Đếm số mẫu có nhãn và số mẫu phân loại đúng trong các phản hồi phân tích thành công."""
    evaluations = [
        record.evaluation
        for record in report.results
        if record.evaluation is not None
    ]

    return EvaluationSummary(
        labeled=len(evaluations),
        correct_topics=sum(item.topic_correct for item in evaluations),
        correct_sentiments=sum(item.sentiment_correct for item in evaluations),
    )
