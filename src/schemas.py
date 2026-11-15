"""Schema dữ liệu trao đổi giữa các module. Đây là nguồn duy nhất cho topic, sentiment, source."""

from typing import Annotated, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

Topic = Literal[
    "price",
    "construction_progress",
    "amenities",
    "location_infrastructure",  # thêm ngày 15/11/2026, xem docs/EVAL_RESULTS.md
    "legal_process",
    "sales_service",
    "other",
]
Sentiment = Literal["positive", "negative", "neutral"]
Source = Literal["crm", "survey", "social"]

TOPICS: tuple[str, ...] = get_args(Topic)

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Feedback(BaseModel):
    """Một phản hồi đầu vào. Trường lạ bị bỏ qua, không đi tiếp vào pipeline."""

    model_config = ConfigDict(extra="ignore")

    id: NonEmptyStr
    project: NonEmptyStr
    source: Source
    text: NonEmptyStr
    # Chỉ dùng để che tên trong text; không được gửi tới LLM hay ghi vào báo cáo.
    customer_name: str | None = Field(default=None, repr=False)
    # Nhãn đúng, chỉ có ở dữ liệu đánh giá.
    expected_topic: Topic | None = None
    expected_sentiment: Sentiment | None = None


class FeedbackAnalysis(BaseModel):
    """Kết quả phân loại do LLM trả về cho một phản hồi."""

    model_config = ConfigDict(extra="forbid")

    topic: Topic
    sentiment: Sentiment
    evidence: str


class Evaluation(BaseModel):
    topic_correct: bool
    sentiment_correct: bool


class AnalyzedFeedback(BaseModel):
    """Một phản hồi đã phân tích thành công. `text` là bản đã che PII."""

    id: str
    project: str
    source: Source
    text: str
    analysis: FeedbackAnalysis
    # None khi phản hồi không có nhãn đúng để so sánh.
    evaluation: Evaluation | None = None


class FailedRecord(BaseModel):
    id: str
    error: str


class AnalysisReport(BaseModel):
    results: list[AnalyzedFeedback]
    errors: list[FailedRecord]


def describe_validation_error(exc: ValidationError) -> str:
    """Mô tả lỗi validation mà không kèm giá trị đầu vào (có thể chứa PII)."""
    parts = []

    for error in exc.errors(include_input=False, include_url=False):
        location = ".".join(str(item) for item in error["loc"]) or "(gốc)"
        parts.append(f"{location}: {error['msg']}")

    return "; ".join(parts)
