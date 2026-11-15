"""Thống kê theo dự án, tính trực tiếp từ dữ liệu đã phân tích (không dùng LLM)."""

from collections.abc import Iterable
from dataclasses import dataclass, field

from src.schemas import AnalyzedFeedback


@dataclass
class ProjectStats:
    total: int = 0
    negative: int = 0
    negative_topics: dict[str, int] = field(default_factory=dict)

    @property
    def negative_rate_percent(self) -> float:
        return round(self.negative / self.total * 100, 2)


def summarize_projects(records: Iterable[AnalyzedFeedback]) -> dict[str, ProjectStats]:
    summary: dict[str, ProjectStats] = {}

    for record in records:
        stats = summary.setdefault(record.project, ProjectStats())
        stats.total += 1

        if record.analysis.sentiment == "negative":
            stats.negative += 1

            topic = record.analysis.topic
            stats.negative_topics[topic] = stats.negative_topics.get(topic, 0) + 1

    return summary


def stats_payload(project: str, stats: ProjectStats) -> dict:
    """Số liệu của một dự án, dùng chung cho tool của agent và prompt tạo insight."""
    return {
        "project": project,
        "analyzed_feedback_count": stats.total,
        "negative_feedback_count": stats.negative,
        "negative_rate_percent": stats.negative_rate_percent,
        "negative_topics": stats.negative_topics,
    }
