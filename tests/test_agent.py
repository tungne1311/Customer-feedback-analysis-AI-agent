from types import SimpleNamespace

from google.genai import types

from src.agent import run_agent


def _tool_call_response(name, args):
    call = types.FunctionCall(name=name, args=args, id=f"call-{name}")
    content = types.Content(role="model", parts=[types.Part(function_call=call)])

    return SimpleNamespace(
        candidates=[SimpleNamespace(content=content)],
        function_calls=[call],
        text=None,
    )


def _text_response(text):
    content = types.Content(role="model", parts=[types.Part.from_text(text=text)])

    return SimpleNamespace(
        candidates=[SimpleNamespace(content=content)],
        function_calls=None,
        text=text,
    )


def _tool_results(contents):
    return [
        part.function_response.response["result"]
        for content in contents
        for part in content.parts
        if part.function_response is not None
    ]


def test_agent_runs_tool_then_returns_answer(fake_client, settings, report_file):
    client = fake_client([
        _tool_call_response("get_project_stats", {"project": "DuAnA"}),
        _text_response("DuAnA có 3/4 phản hồi tiêu cực."),
    ])
    contents = [types.Content(role="user", parts=[types.Part.from_text(text="DuAnA thế nào?")])]

    answer = run_agent(client, contents, settings)

    assert answer == "DuAnA có 3/4 phản hồi tiêu cực."
    assert len(client.calls) == 2
    assert client.calls[0]["model"] == settings.agent_model
    assert [c.role for c in contents] == ["user", "model", "user", "model"]

    result = _tool_results(contents)[0]
    assert result["status"] == "ok"
    assert result["negative_feedback_count"] == 3


def test_agent_blocks_unknown_tools_and_bad_arguments(fake_client, settings, report_file):
    client = fake_client([
        _tool_call_response("delete_all_feedback", {}),
        _tool_call_response("get_project_stats", {"unexpected": "x"}),
        _text_response("Xong."),
    ])

    run_agent(client, contents := [], settings)

    blocked, bad_args = _tool_results(contents)
    assert blocked == {"status": "error", "message": "Tool này không được phép thực thi."}
    assert bad_args["status"] == "invalid_input"


def test_agent_stops_after_max_steps(fake_client, settings, report_file):
    client = fake_client([
        _tool_call_response("get_project_stats", {"project": "DuAnA"})
        for _ in range(settings.agent_max_steps + 2)
    ])

    answer = run_agent(client, [], settings)

    assert len(client.calls) == settings.agent_max_steps
    assert answer.startswith(f"Đã dừng sau {settings.agent_max_steps} lượt gọi Gemini")
