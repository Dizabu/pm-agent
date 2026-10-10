import asyncio

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from app.mcp_server import create_server
from app.task import TaskStore


def make_server(tmp_path):
    """A server plus its store, so tests can check both sides."""
    store = TaskStore(tmp_path / "tasks.json")
    return create_server(store), store


def test_exposes_the_three_task_tools(tmp_path):
    server, _ = make_server(tmp_path)
    tools = asyncio.run(server.list_tools())
    names = {tool.name for tool in tools}
    assert names == {
        "list_tasks",
        "create_task",
        "update_task_status",
    }


def test_update_tool_tells_the_llm_the_valid_statuses(tmp_path):
    server, _ = make_server(tmp_path)
    tools = asyncio.run(server.list_tools())
    update = next(t for t in tools if t.name == "update_task_status")
    for status in ("todo", "in_progress", "done"):
        assert status in update.description  # TODO 2: each status appears in update.description


def test_create_task_through_mcp_saves_it(tmp_path):
    server, store = make_server(tmp_path)
    result = asyncio.run(server.call_tool("create_task", {"title": "Write README"}))
    assert result.structured_content == {
        "id": 1,
        "title": "Write README",
        "status": "todo",
    }
    assert len(store.list_tasks()) == 1


def test_unknown_task_raises_tool_error(tmp_path):
    server, _ = make_server(tmp_path)
    with pytest.raises(ToolError, match="No task with id 99"):
        asyncio.run(server.call_tool("update_task_status", {"task_id": 99, "status": "done"}))
