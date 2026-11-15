"""Đọc dữ liệu phản hồi đầu vào và đọc/ghi báo cáo phân tích (file JSON)."""

import json
import os
from pathlib import Path

from pydantic import ValidationError

from src.schemas import (
    AnalysisReport,
    FailedRecord,
    Feedback,
    describe_validation_error,
)


class DataFileError(Exception):
    """Không đọc được file dữ liệu hoặc file sai cấu trúc."""


def _read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except OSError as exc:
        raise DataFileError(f"Không đọc được file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DataFileError(f"File không phải JSON hợp lệ: {path}") from exc


def load_feedbacks(path: Path) -> tuple[list[Feedback], list[FailedRecord]]:
    """Trả về (phản hồi hợp lệ, bản ghi bị loại).

    Bản ghi sai schema hoặc trùng id bị loại và được ghi nhận,
    thay vì làm dừng cả lượt chạy.
    """
    raw_records = _read_json(path)

    if not isinstance(raw_records, list):
        raise DataFileError("File phản hồi phải là một danh sách JSON.")

    feedbacks: list[Feedback] = []
    rejected: list[FailedRecord] = []
    seen_ids: set[str] = set()

    for index, raw in enumerate(raw_records):
        raw_id = raw.get("id") if isinstance(raw, dict) else None
        has_id = isinstance(raw_id, str) and raw_id.strip()
        record_id = raw_id.strip() if has_id else f"index_{index}"

        try:
            feedback = Feedback.model_validate(raw)
        except ValidationError as exc:
            rejected.append(FailedRecord(
                id=record_id,
                error="Dữ liệu đầu vào không hợp lệ: " + describe_validation_error(exc),
            ))
            continue

        if feedback.id in seen_ids:
            rejected.append(FailedRecord(
                id=feedback.id,
                error=f"Trùng id với một phản hồi trước đó (vị trí {index}).",
            ))
            continue

        seen_ids.add(feedback.id)
        feedbacks.append(feedback)

    return feedbacks, rejected


def load_report(path: Path) -> AnalysisReport:
    try:
        return AnalysisReport.model_validate(_read_json(path))
    except ValidationError as exc:
        raise DataFileError(
            "Báo cáo phân tích sai cấu trúc: " + describe_validation_error(exc)
        ) from exc


def save_report(report: AnalysisReport, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)

    # Ghi ra file tạm rồi đổi tên để không để lại báo cáo dở dang khi bị ngắt.
    temp_path = path.with_name(path.name + ".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(report.model_dump(), file, ensure_ascii=False, indent=2)

    os.replace(temp_path, path)

    return path
