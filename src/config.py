"""Cấu hình tập trung, đọc từ biến môi trường (xem .env.example)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_MODEL = "gemini-3.5-flash-lite"


class ConfigError(Exception):
    """Cấu hình thiếu hoặc không hợp lệ."""


@dataclass(frozen=True)
class Settings:
    feedback_path: Path
    report_path: Path
    # Mỗi tác vụ có model riêng để có thể phân tầng chi phí.
    # Hiện cả ba mặc định dùng chung một model nhỏ.
    classifier_model: str
    insight_model: str
    agent_model: str
    max_output_tokens: int
    request_timeout_ms: int
    # Tổng số lần thử, tính cả lần gọi đầu. SDK chỉ thử lại với 408, 429, 5xx.
    retry_attempts: int
    agent_max_steps: int


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name, "").strip()

    if not raw:
        return default

    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} phải là số nguyên.") from exc

    if value < minimum:
        raise ConfigError(f"{name} phải lớn hơn hoặc bằng {minimum}.")

    return value


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    return Path(raw) if raw else default


def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, "").strip() or default


def load_settings() -> Settings:
    # Biến môi trường đã đặt sẵn được ưu tiên hơn file .env.
    load_dotenv(PROJECT_ROOT / ".env")

    return Settings(
        feedback_path=_env_path(
            "VOC_FEEDBACK_PATH",
            PROJECT_ROOT / "data" / "mock_feedback.json",
        ),
        report_path=_env_path(
            "VOC_REPORT_PATH",
            PROJECT_ROOT / "outputs" / "analysis_report.json",
        ),
        classifier_model=_env_str("VOC_CLASSIFIER_MODEL", DEFAULT_MODEL),
        insight_model=_env_str("VOC_INSIGHT_MODEL", DEFAULT_MODEL),
        agent_model=_env_str("VOC_AGENT_MODEL", DEFAULT_MODEL),
        max_output_tokens=_env_int("VOC_MAX_OUTPUT_TOKENS", 1024),
        request_timeout_ms=_env_int("VOC_REQUEST_TIMEOUT_MS", 60_000),
        retry_attempts=_env_int("VOC_RETRY_ATTEMPTS", 3),
        agent_max_steps=_env_int("VOC_AGENT_MAX_STEPS", 5),
    )


def get_api_key() -> str:
    """Đọc API key khi cần tạo client; không lưu key vào Settings để tránh in nhầm."""
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise ConfigError(
            "Thiếu GEMINI_API_KEY. Tạo file .env từ .env.example "
            "hoặc đặt biến môi trường."
        )

    return api_key
