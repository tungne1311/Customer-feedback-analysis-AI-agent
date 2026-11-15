"""Agent hội thoại: Gemini quyết định gọi tool, code thực thi tool và trả kết quả lại."""

import json
import logging

from google.genai import types

from src.config import Settings
from src.llm import generate
from src.prompts import AGENT_INSTRUCTIONS
from src.schemas import TOPICS
from src.tools import MAX_FEEDBACK_LIMIT, get_negative_feedback, get_project_stats

logger = logging.getLogger(__name__)

TOOL_DEFINITIONS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_project_stats",
            description=(
                "Lấy số lượng phản hồi, tỷ lệ tiêu cực "
                "và thống kê chủ đề của một dự án."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Tên dự án, ví dụ DuAnA.",
                    }
                },
                "required": ["project"],
            },
        ),
        types.FunctionDeclaration(
            name="get_negative_feedback",
            description=(
                "Lấy các phản hồi tiêu cực cụ thể "
                "để làm bằng chứng cho một dự án."
            ),
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Tên dự án.",
                    },
                    "topic": {
                        "type": "string",
                        "description": (
                            "Chủ đề cần lọc. Để rỗng nếu lấy mọi chủ đề."
                        ),
                        "enum": ["", *TOPICS],
                    },
                    "limit": {
                        "type": "integer",
                        "description": (
                            f"Số phản hồi tối đa, từ 1 đến {MAX_FEEDBACK_LIMIT}. "
                            "Mặc định 3."
                        ),
                        "minimum": 1,
                        "maximum": MAX_FEEDBACK_LIMIT,
                    },
                },
                "required": ["project"],
            },
        ),
    ],
)

TOOL_REGISTRY = {
    "get_project_stats": get_project_stats,
    "get_negative_feedback": get_negative_feedback,
}


def _execute_tool(name: str, arguments: dict) -> dict:
    function = TOOL_REGISTRY.get(name)

    if function is None:
        return {
            "status": "error",
            "message": "Tool này không được phép thực thi.",
        }

    try:
        return function(**arguments)
    except (TypeError, ValueError) as exc:
        return {
            "status": "invalid_input",
            "message": str(exc),
        }


def run_agent(client, contents: list, settings: Settings) -> str:
    """Chạy một lượt hỏi đáp. `contents` là lịch sử hội thoại và được bổ sung tại chỗ.

    Có thể ném `src.llm.LLMError`; bên gọi quyết định cách khôi phục lịch sử.
    """
    config = types.GenerateContentConfig(
        system_instruction=AGENT_INSTRUCTIONS,
        tools=[TOOL_DEFINITIONS],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode="AUTO"
            ),
        ),
        thinking_config=types.ThinkingConfig(
            thinking_level="minimal"
        ),
        max_output_tokens=settings.max_output_tokens,
    )

    max_steps = settings.agent_max_steps

    for step in range(1, max_steps + 1):
        logger.info("--- Lượt gọi Gemini %d ---", step)

        response = generate(
            client,
            model=settings.agent_model,
            contents=contents,
            config=config,
        )

        if (
            not response.candidates
            or response.candidates[0].content is None
        ):
            return "Gemini chưa trả về nội dung để tiếp tục."

        # Lưu nguyên tin nhắn của Gemini vào lịch sử.
        contents.append(response.candidates[0].content)

        calls = response.function_calls or []

        # Không yêu cầu tool: lấy câu trả lời và kết thúc.
        if not calls:
            return response.text or "Gemini chưa trả về câu trả lời văn bản."

        tool_response_parts = []

        for call in calls:
            arguments = call.args or {}
            result = _execute_tool(call.name, arguments)

            logger.info(
                "Tool: %s | tham số: %s | trạng thái: %s",
                call.name,
                arguments,
                result.get("status"),
            )
            # Kết quả đầy đủ có nội dung phản hồi nên chỉ ghi ở mức DEBUG.
            logger.debug(
                "Kết quả:\n%s",
                json.dumps(result, ensure_ascii=False, indent=2),
            )

            tool_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=call.name,
                        response={"result": result},
                        id=call.id,
                    )
                )
            )

        # Lưu kết quả tool để Gemini đọc ở lượt tiếp theo.
        contents.append(
            types.Content(
                role="user",
                parts=tool_response_parts,
            )
        )

    return (
        f"Đã dừng sau {max_steps} lượt gọi Gemini "
        "vì chưa nhận được câu trả lời cuối cùng."
    )
