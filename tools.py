import json
from pathlib import Path

from project_summary import summarize_projects


def get_project_stats(project: str) -> dict:
    """Trả thống kê từ các phản hồi phân tích thành công của một dự án."""

    if not isinstance(project, str) or not project.strip():
        return {
            "status": "invalid_input",
            "message": "Tên dự án phải là chuỗi không rỗng.",
        }

    project = project.strip()

    report_path = (
        Path(__file__).resolve().parent
        / "outputs"
        / "analysis_report.json"
    )

    try:
        with report_path.open("r", encoding="utf-8") as file:
            report = json.load(file)

    except (OSError, json.JSONDecodeError):
        return {
            "status": "error",
            "message": "Chưa đọc được dữ liệu phân tích.",
        }

    summary = summarize_projects(report["results"])

    if project not in summary:
        return {
            "status": "not_found",
            "project": project,
            "message": "Chưa có kết quả phân tích cho dự án này.",
            "available_projects": list(summary.keys()),
        }

    stats = summary[project]

    return {
        "status": "ok",
        "project": project,
        "analyzed_feedback_count": stats["total"],
        "negative_feedback_count": stats["negative"],
        "negative_rate_percent": round(
            stats["negative"] / stats["total"] * 100,
            2,
        ),
        "negative_topics": stats["negative_topics"],
    }


def get_negative_feedback(
    project: str,
    topic: str = "",
    limit: int = 3,
) -> dict:
    """Lấy phản hồi tiêu cực đã phân tích của một dự án."""

    if not isinstance(project, str) or not project.strip():
        return {
            "status": "invalid_input",
            "message": "Tên dự án phải là chuỗi không rỗng.",
        }

    if not isinstance(topic, str):
        return {
            "status": "invalid_input",
            "message": "Chủ đề phải là chuỗi.",
        }

    if type(limit) is not int or not 1 <= limit <= 5:
        return {
            "status": "invalid_input",
            "message": "limit phải là số nguyên từ 1 đến 5.",
        }

    project = project.strip()
    topic = topic.strip()

    allowed_topics = (
        "price",
        "construction_progress",
        "amenities",
        "legal_process",
        "sales_service",
        "other",
    )

    if topic and topic not in allowed_topics:
        return {
            "status": "invalid_input",
            "message": "Chủ đề không hợp lệ.",
        }

    report_path = (
        Path(__file__).resolve().parent
        / "outputs"
        / "analysis_report.json"
    )

    try:
        with report_path.open("r", encoding="utf-8") as file:
            report = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {
            "status": "error",
            "message": "Chưa đọc được dữ liệu phân tích.",
        }

    matches = []
    project_found = False

    for record in report["results"]:
        if record["project"] != project:
            continue

        project_found = True
        analysis = record["analysis"]

        if analysis["sentiment"] != "negative":
            continue

        if topic and analysis["topic"] != topic:
            continue

        matches.append({
            "id": record["id"],
            "source": record["source"],
            "text": record["text"],
            "topic": analysis["topic"],
            "evidence": analysis["evidence"],
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

if __name__ == "__main__":
    result = get_negative_feedback(
        project="DuAnA",
        topic="sales_service",
        limit=3,
    )

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2,
    ))