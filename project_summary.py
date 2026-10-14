import json
from pathlib import Path
import os
from dotenv import load_dotenv
from google import genai
from insight_generator import generate_insight


def summarize_projects(records):
    summary = {}

    for record in records:
        project = record["project"]
        analysis = record["analysis"]

        if project not in summary:
            summary[project] = {
                "total": 0,
                "negative": 0,
                "negative_topics": {},
            }

        stats = summary[project]
        stats["total"] += 1

        if analysis["sentiment"] == "negative":
            stats["negative"] += 1

            topic = analysis["topic"]
            topic_counts = stats["negative_topics"]

            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    return summary


def main():
    project_dir = Path(__file__).resolve().parent
    report_path = project_dir / "outputs" / "analysis_report.json"

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    records = report["results"]

    if not records:
        print("Chưa có kết quả phân tích thành công.")
        return

    summary = summarize_projects(records)

    print("Số phản hồi lỗi chưa đưa vào thống kê:", len(report["errors"]))

    for project, stats in summary.items():
        negative_rate = stats["negative"] / stats["total"]

        print(f"\nDự án: {project}")
        print(f"Tổng phản hồi đã phân tích: {stats['total']}")
        print(f"Số phản hồi tiêu cực: {stats['negative']}")
        print(f"Tỷ lệ tiêu cực: {negative_rate:.1%}")

        for topic, count in stats["negative_topics"].items():
            print(f"  - {topic}: {count}")
    project = "DuAnA"

    if project not in summary:
        print(f"Không tìm thấy dữ liệu của dự án {project}.")
        return

    load_dotenv(project_dir / ".env")

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    draft = generate_insight(
        client,
        project,
        summary[project],
    )

    print("\nBẢN NHÁP — CẦN QUẢN LÝ RÀ SOÁT")
    print(draft)


if __name__ == "__main__":
    main()