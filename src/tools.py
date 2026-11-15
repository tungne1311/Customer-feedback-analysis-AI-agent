"""Tool chỉ-đọc cho agent hội thoại. Dữ liệu lấy từ báo cáo phân tích đã lưu."""

from src.config import load_settings
from src.schemas import TOPICS, AnalysisReport
from src.stats import stats_payload, summarize_projects
from src.storage import DataFileError, load_report

MAX_FEEDBACK_LIMIT = 5

_REPORT_UNAVAILABLE = {
    "status": "error",
    "message": "Chưa đọc được dữ liệu phân tích.",
}

_INVALID_PROJECT = {
    "status": "invalid_input",
    "message": "Tên dự án phải là chuỗi không rỗng.",
}


def _load_report() -> AnalysisReport | None:
    try:
        return load_report(load_settings().report_path)
    except DataFileError:
        return None


def get_project_stats(project: str) -> dict:
    """Trả thống kê từ các phản hồi phân tích thành công của một dự án."""

    if not isinstance(project, str) or not project.strip():
        return dict(_INVALID_PROJECT)

    project = project.strip()

    report = _load_report()

    if report is None:
        return dict(_REPORT_UNAVAILABLE)

    summary = summarize_projects(report.results)

    if project not in summary:
        return {
            "status": "not_found",
            "project": project,
            "message": "Chưa có kết quả phân tích cho dự án này.",
            "available_projects": list(summary.keys()),
        }

    return {"status": "ok", **stats_payload(project, summary[project])}


def get_negative_feedback(
    project: str,
    topic: str = "",
    limit: int = 3,
) -> dict:
    """Lấy phản hồi tiêu cực đã phân tích của một dự án."""

    if not isinstance(project, str) or not project.strip():
        return dict(_INVALID_PROJECT)

    if not isinstance(topic, str):
        return {
            "status": "invalid_input",
            "message": "Chủ đề phải là chuỗi.",
        }

    if type(limit) is not int or not 1 <= limit <= MAX_FEEDBACK_LIMIT:
        return {
            "status": "invalid_input",
            "message": f"limit phải là số nguyên từ 1 đến {MAX_FEEDBACK_LIMIT}.",
        }

    project = project.strip()
    topic = topic.strip()

    if topic and topic not in TOPICS:
        return {
            "status": "invalid_input",
            "message": "Chủ đề không hợp lệ.",
        }

    report = _load_report()

    if report is None:
        return dict(_REPORT_UNAVAILABLE)

    matches = []
    project_found = False

    for record in report.results:
        if record.project != project:
            continue

        project_found = True
        analysis = record.analysis

        if analysis.sentiment != "negative":
            continue

        if topic and analysis.topic != topic:
            continue

        matches.append({
            "id": record.id,
            "source": record.source,
            "text": record.text,
            "topic": analysis.topic,
            "evidence": analysis.evidence,
        })

    if not project_found:
        return {
            "status": "not_found",
            "project": project,
            "message": "Chưa có kết quả phân tích cho dự án này.",
        }

    selected = matches[:limit]

    return {
        "status": "ok",
        "project": project,
        "topic_filter": topic,
        "matching_feedback_count": len(matches),
        "returned_feedback_count": len(selected),
        "feedbacks": selected,
    }
