import json

from fastapi.testclient import TestClient

from app.agent import Agent
from app.llm import get_provider
from app.llm.base import LLMResponse, ToolCall
from app.llm.fake import FakeProvider
from app.main import app, get_agent, get_store
from app.mcp_server import create_server
from app.task import TaskStore
from tests.test_agent import ScriptedLLM

app.dependency_overrides[get_provider] = FakeProvider
client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_chat_uses_provider():
    res = client.post("/chat", json={"message": "hello"})
    assert res.status_code == 200
    assert res.json() == {"reply": "echo: hello"}


def test_agent_endpoint_runs_the_agent(tmp_path):
    store = TaskStore(tmp_path / "tasks.json")
    llm = ScriptedLLM(
        LLMResponse(
            tool_calls=[ToolCall(id="1", name="create_task", arguments={"title": "Write README"})]
        ),
        LLMResponse(text="Created it!"),
    )
    app.dependency_overrides[get_agent] = lambda: Agent(llm, create_server(store))

    res = client.post("/agent", json={"message": "Create a task to write the README"})

    app.dependency_overrides.pop(get_agent)
    assert res.status_code == 200
    assert res.json() == {"reply": "Created it!"}
    assert len(store.list_tasks()) == 1


def test_agent_stream_sends_sse_events(tmp_path):
    store = TaskStore(tmp_path / "tasks.json")
    llm = ScriptedLLM(
        LLMResponse(
            tool_calls=[ToolCall(id="1", name="create_task", arguments={"title": "Write README"})]
        ),
        LLMResponse(text="Created it!"),
    )
    app.dependency_overrides[get_agent] = lambda: Agent(llm, create_server(store))

    res = client.post("/agent/stream", json={"message": "Create a task"})

    app.dependency_overrides.pop(get_agent)
    assert res.headers["content-type"].startswith("text/event-stream")  # TODO 4

    lines = [line for line in res.text.split("\n\n") if line]
    events = [json.loads(line.removeprefix("data: ")) for line in lines]
    assert [e["type"] for e in events] == ["tool_call", "tool_result", "text", "done"]


def test_tasks_endpoint_lists_tasks(tmp_path):
    store = TaskStore(tmp_path / "tasks.json")
    store.create_task("Write README")
    app.dependency_overrides[get_store] = lambda: store

    res = client.get("/tasks")

    app.dependency_overrides.pop(get_store)
    assert res.json() == [{"id": 1, "title": "Write README", "status": "todo"}]
