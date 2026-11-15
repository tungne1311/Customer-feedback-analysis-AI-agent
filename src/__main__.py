"""Giao diện dòng lệnh: python -m src <analyze|summary|chat>."""

import argparse
import logging
import sys
from pathlib import Path

from google.genai import types

from src.agent import run_agent
from src.config import ConfigError, Settings, load_settings
from src.llm import LLMError, classify_feedback, create_client, generate_insight
from src.pipeline import analyze_feedbacks, summarize_evaluation
from src.stats import stats_payload, summarize_projects
from src.storage import DataFileError, load_feedbacks, load_report, save_report

EXIT_WORDS = ("thoat", "thoát", "exit")


def _use_utf8_console() -> None:
    # Console Windows mặc định có thể không in được tiếng Việt.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def _configure_logging(verbose: bool) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    # Chỉ bật log của package này, không bật log của thư viện HTTP.
    package_logger = logging.getLogger("src")
    package_logger.addHandler(handler)
    package_logger.setLevel(logging.DEBUG if verbose else logging.INFO)


def cmd_analyze(args: argparse.Namespace, settings: Settings) -> int:
    input_path = args.input or settings.feedback_path
    output_path = args.output or settings.report_path

    feedbacks, rejected = load_feedbacks(input_path)
    total = len(feedbacks) + len(rejected)

    if total == 0:
        print("File chưa có phản hồi.")
        return 0

    client = create_client(settings)

    try:
        report = analyze_feedbacks(
            feedbacks,
            lambda text: classify_feedback(client, text, settings),
        )
    finally:
        client.close()

    report.errors[:0] = rejected

    successful = len(report.results)

    print(f"\nTổng phản hồi: {total}")
    print(f"Phân tích thành công: {successful}")
    print(f"Phân tích thất bại: {len(report.errors)}")

    if rejected:
        print(f"  Trong đó bị loại do dữ liệu đầu vào không hợp lệ: {len(rejected)}")

    evaluation = summarize_evaluation(report)

    if evaluation.labeled > 0:
        topic_accuracy = evaluation.correct_topics / evaluation.labeled
        sentiment_accuracy = evaluation.correct_sentiments / evaluation.labeled

        print(
            f"Tỷ lệ đúng chủ đề: {topic_accuracy:.1%} "
            f"({evaluation.correct_topics}/{evaluation.labeled} "
            "mẫu thành công có nhãn)"
        )
        print(
            f"Tỷ lệ đúng cảm xúc: {sentiment_accuracy:.1%} "
            f"({evaluation.correct_sentiments}/{evaluation.labeled} "
            "mẫu thành công có nhãn)"
        )

    report_path = save_report(report, output_path)
    print(f"\nĐã lưu báo cáo tại: {report_path}")

    return 0


def cmd_summary(args: argparse.Namespace, settings: Settings) -> int:
    report = load_report(args.report or settings.report_path)

    if not report.results:
        print("Chưa có kết quả phân tích thành công.")
        return 0

    summary = summarize_projects(report.results)

    print("Số phản hồi lỗi chưa đưa vào thống kê:", len(report.errors))

    for project, stats in summary.items():
        print(f"\nDự án: {project}")
        print(f"Tổng phản hồi đã phân tích: {stats.total}")
        print(f"Số phản hồi tiêu cực: {stats.negative}")
        print(f"Tỷ lệ tiêu cực: {stats.negative_rate_percent:.2f}%")

        for topic, count in stats.negative_topics.items():
            print(f"  - {topic}: {count}")

    if args.project is None:
        print("\nThêm --project <tên dự án> để tạo bản nháp insight.")
        return 0

    project = args.project.strip()

    if project not in summary:
        print(f"Không tìm thấy dữ liệu của dự án {project}.")
        return 1

    client = create_client(settings)

    try:
        draft = generate_insight(
            client,
            stats_payload(project, summary[project]),
            settings,
        )
    finally:
        client.close()

    print("\nBẢN NHÁP — CẦN QUẢN LÝ RÀ SOÁT")
    print(draft)

    return 0


def cmd_chat(args: argparse.Namespace, settings: Settings) -> int:
    client = create_client(settings)

    # Tạo lịch sử một lần cho cả phiên hội thoại.
    contents: list = []

    print("Trợ lý phân tích phản hồi khách hàng.")
    print("Nhập 'thoat' để kết thúc.")

    try:
        while True:
            try:
                query = input("\nBạn: ").strip()
            except EOFError:
                break

            if query.lower() in EXIT_WORDS:
                break

            if not query:
                continue

            # Ghi nhớ số tin nhắn trước câu hỏi mới.
            history_size = len(contents)

            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=query)],
                )
            )

            try:
                answer = run_agent(client, contents, settings)
            except LLMError as exc:
                # Bỏ các tin nhắn được thêm trong lượt bị lỗi.
                del contents[history_size:]

                print(f"\n{exc}")
                print("Lượt xử lý đã dừng. Bạn có thể nhập câu hỏi khác.")

                continue

            print("\nGemini:")
            print(answer)
    finally:
        client.close()

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src",
        description="Phân tích phản hồi khách hàng bất động sản.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="In log chi tiết, gồm toàn bộ kết quả tool của agent.",
    )

    commands = parser.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser(
        "analyze",
        help="Che PII, phân loại chủ đề/cảm xúc từng phản hồi và lưu báo cáo.",
    )
    analyze.add_argument("--input", type=Path, help="File JSON phản hồi đầu vào.")
    analyze.add_argument("--output", type=Path, help="Nơi lưu báo cáo phân tích.")
    analyze.set_defaults(handler=cmd_analyze)

    summary = commands.add_parser(
        "summary",
        help="In thống kê theo dự án; thêm --project để tạo bản nháp insight.",
    )
    summary.add_argument("--project", help="Dự án cần tạo bản nháp insight.")
    summary.add_argument("--report", type=Path, help="File báo cáo phân tích.")
    summary.set_defaults(handler=cmd_summary)

    chat = commands.add_parser(
        "chat",
        help="Hỏi đáp về kết quả phân tích qua agent dùng tool.",
    )
    chat.set_defaults(handler=cmd_chat)

    return parser


def main(argv: list[str] | None = None) -> int:
    # Phải chạy trước khi argparse in --help hoặc thông báo lỗi tham số.
    _use_utf8_console()

    args = build_parser().parse_args(argv)
    _configure_logging(args.verbose)

    try:
        return args.handler(args, load_settings())
    except (ConfigError, DataFileError, LLMError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
