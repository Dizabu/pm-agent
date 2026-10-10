from fastapi.testclient import TestClient

from app.agent import Agent
from app.llm import get_provider
from app.llm.base import LLMResponse, ToolCall
from app.llm.fake import FakeProvider
from app.main import app, get_agent
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
