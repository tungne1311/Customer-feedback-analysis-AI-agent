import json
from google.genai import types


REPORT_INSTRUCTIONS = """
Bạn là trợ lý phân tích phản hồi khách hàng bất động sản.

Dựa trên số liệu được cung cấp:
1. Tóm tắt vấn đề chính, kèm số liệu hỗ trợ.
2. Đề xuất tối đa hai hành động cụ thể để quản lý xem xét.

Quy tắc:
- Chỉ sử dụng số liệu được cung cấp.
- Các số liệu chỉ tính trên phản hồi phân tích thành công.
- Không suy đoán nguyên nhân thành sự thật.
- Không kết luận vấn đề đang gia tăng khi thiếu dữ liệu thời gian.
- Nếu không có phản hồi tiêu cực, nói rõ điều đó.
- Viết ngắn gọn bằng tiếng Việt.
"""


def generate_insight(client, project, stats):
    context = {
        "project": project,
        "analyzed_feedback_count": stats["total"],
        "negative_feedback_count": stats["negative"],
        "negative_rate_percent": round(
            stats["negative"] / stats["total"] * 100,
            1,
        ),
        "negative_topics": stats["negative_topics"],
    }

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=json.dumps(context, ensure_ascii=False),
        config=types.GenerateContentConfig(
            system_instruction=REPORT_INSTRUCTIONS,
            thinking_config=types.ThinkingConfig(
                thinking_level="minimal"
            ),
            max_output_tokens=1024,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini chưa trả về báo cáo.")

    return response.text