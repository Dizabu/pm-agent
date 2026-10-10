import asyncio

from app.agent import get_tool_specs, run_tool
from app.llm.base import ToolCall
from app.mcp_server import create_server
from app.task import TaskStore


def make_server(tmp_path):
    return create_server(TaskStore(tmp_path / "tasks.json"))


def test_get_tool_specs_lists_the_task_tools(tmp_path):
    specs = asyncio.run(get_tool_specs(make_server(tmp_path)))
    assert {s.name for s in specs} == {"create_task", "update_task_status", "list_tasks"}


def test_run_tool_returns_the_result_as_text(tmp_path):
    call = ToolCall(id="1", name="create_task", arguments={"title": "Write README"})
    result = asyncio.run(run_tool(make_server(tmp_path), call))
    assert "Write README" in result


def test_run_tool_turns_errors_into_text(tmp_path):
    call = ToolCall(id="1", name="update_task_status", arguments={"task_id": 99, "status": "done"})
    result = asyncio.run(run_tool(make_server(tmp_path), call))
    assert "No task with id 99" in result
