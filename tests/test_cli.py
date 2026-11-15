import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_cli(*args, **env_overrides):
    # cp1252 là encoding mặc định của nhiều console Windows; tiếng Việt không in được ở đó.
    env = {**os.environ, "PYTHONIOENCODING": "cp1252", **env_overrides}

    return subprocess.run(
        [sys.executable, "-m", "src", *args],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        timeout=60,
    )


def test_help_prints_vietnamese_on_non_utf8_console():
    result = _run_cli("--help")

    assert result.returncode == 0
    assert "Phân tích phản hồi khách hàng" in result.stdout.decode("utf-8")


def test_summary_without_project_prints_stats_and_makes_no_llm_call(tmp_path, sample_report):
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(sample_report, ensure_ascii=False), encoding="utf-8")

    # Key rỗng: nếu lệnh cố gọi LLM thì sẽ thoát với mã lỗi.
    result = _run_cli("summary", "--report", str(report_path), GEMINI_API_KEY="")

    output = result.stdout.decode("utf-8")
    assert result.returncode == 0
    assert "Dự án: DuAnA" in output
    assert "Tỷ lệ tiêu cực: 75.00%" in output
    assert "BẢN NHÁP" not in output


def test_missing_api_key_gives_clear_error(tmp_path, sample_report):
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(sample_report, ensure_ascii=False), encoding="utf-8")

    result = _run_cli(
        "summary", "--report", str(report_path), "--project", "DuAnA", GEMINI_API_KEY="",
    )

    assert result.returncode == 1
    assert "Thiếu GEMINI_API_KEY" in result.stderr.decode("utf-8")
    assert "Traceback" not in result.stderr.decode("utf-8")
