import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from pydantic import ValidationError
from llm_classifier import analyze_feedback, FeedbackAnalysis



def load_feedbacks():
    project_dir = Path(__file__).resolve().parent
    data_path = project_dir / "data" / "mock_feedback.json"

    with data_path.open("r", encoding="utf-8") as file:
        feedbacks = json.load(file)

    return feedbacks

def save_report(results, failed_records):
    project_dir = Path(__file__).resolve().parent
    output_dir = project_dir / "outputs"

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "analysis_report.json"

    report = {
        "results": results,
        "errors": failed_records,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return output_path


def main():
    load_dotenv(Path(__file__).resolve().parent / ".env")

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    feedbacks = load_feedbacks()

    if not feedbacks:
        print("File chưa có phản hồi.")
        return

    successful = 0
    correct_topics = 0
    correct_sentiments = 0
    
    results = []
    failed_records = []

    for feedback in feedbacks:
        print(f"\nĐang phân tích: {feedback['id']}")

        try:
            response = analyze_feedback(client, feedback["text"])

            result = FeedbackAnalysis.model_validate_json(response.text)

            if not result.evidence.strip():
                raise ValueError("Bằng chứng đang rỗng.")

            if result.evidence not in feedback["text"]:
                raise ValueError("Bằng chứng không có trong phản hồi gốc.")

        except (errors.APIError, ValidationError, ValueError, RuntimeError) as exc:
            failed_records.append({
                "id": feedback["id"],
                "error": str(exc),
            })

            print(f"Phân tích thất bại: {exc}")
            continue

        successful += 1

        topic_ok = result.topic == feedback["expected_topic"]
        sentiment_ok = result.sentiment == feedback["expected_sentiment"]

        if topic_ok:
            correct_topics += 1

        if sentiment_ok:
            correct_sentiments += 1
        
        results.append({
            "id": feedback["id"],
            "project": feedback["project"],
            "source": feedback["source"],
            "text": feedback["text"],
            "analysis": result.model_dump(),
            "evaluation": {
                "topic_correct": topic_ok,
                "sentiment_correct": sentiment_ok,
            },
        })

        print("Nội dung:", feedback["text"])
        print("Chủ đề:", result.topic, "| Khớp đáp án:", topic_ok)
        print("Cảm xúc:", result.sentiment, "| Khớp đáp án:", sentiment_ok)
        print("Bằng chứng:", result.evidence)

    print(f"\nTổng phản hồi: {len(feedbacks)}")
    print(f"Phân tích thành công: {successful}")
    print(f"Phân tích thất bại: {len(feedbacks) - successful}")

    if successful > 0:
        topic_accuracy = correct_topics / successful
        sentiment_accuracy = correct_sentiments / successful

        print(f"Tỷ lệ đúng chủ đề trên mẫu thành công: {topic_accuracy:.1%}")
        print(f"Tỷ lệ đúng cảm xúc trên mẫu thành công: {sentiment_accuracy:.1%}")
    report_path = save_report(results, failed_records)
    print(f"\nĐã lưu báo cáo tại: {report_path}")
if __name__ == "__main__":
    main()