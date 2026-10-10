import asyncio
import json

from app.agent import Agent, get_tool_specs, run_tool
from app.llm.base import LLMResponse, ToolCall
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


class ScriptedLLM:
    """A fake LLM that returns the given responses in order and records what it was sent."""

    def __init__(self, *responses: LLMResponse) -> None:
        self.responses = list(responses)
        self.calls = []

    async def chat(self, messages, system="", tools=None) -> LLMResponse:
        self.calls.append(list(messages))
        return self.responses.pop(0)


def test_answers_directly_when_no_tools_are_needed(tmp_path):
    llm = ScriptedLLM(LLMResponse(text="Hello!"))
    answer = asyncio.run(Agent(llm, make_server(tmp_path)).run("hi"))
    assert answer == "Hello!"
    assert len(llm.calls) == 1


def test_runs_a_tool_then_answers(tmp_path):
    store = TaskStore(tmp_path / "tasks.json")
    llm = ScriptedLLM(
        LLMResponse(
            tool_calls=[ToolCall(id="1", name="create_task", arguments={"title": "Write README"})]
        ),
        LLMResponse(text="Done! I created task #1."),
    )
    answer = asyncio.run(Agent(llm, create_server(store)).run("Create a task to write the README"))

    assert answer == "Done! I created task #1."
    assert [t.title for t in store.list_tasks()] == ["Write README"]
    second_call = llm.calls[1]
    assert "Write README" in second_call[-1].content


def test_stops_after_max_steps(tmp_path):
    llm = ScriptedLLM(
        LLMResponse(tool_calls=[ToolCall(id="1", name="list_tasks", arguments={})]),
        LLMResponse(tool_calls=[ToolCall(id="2", name="list_tasks", arguments={})]),
        LLMResponse(tool_calls=[ToolCall(id="3", name="list_tasks", arguments={})]),
    )
    answer = asyncio.run(
        Agent(llm, make_server(tmp_path), max_steps=3).run("What tasks are there?")
    )
    assert "step limit" in answer
    assert len(llm.calls) == 3


async def collect(agent: Agent, message: str) -> list[dict]:
    """Run the agent and gather all its events into a list."""
    return [event async for event in agent.run_events(message)]


def test_run_events_reports_each_step(tmp_path):
    llm = ScriptedLLM(
        LLMResponse(
            tool_calls=[ToolCall(id="1", name="create_task", arguments={"title": "Write README"})]
        ),
        LLMResponse(text="Done!"),
    )
    events = asyncio.run(collect(Agent(llm, make_server(tmp_path)), "Create a task"))

    assert [e["type"] for e in events] == ["tool_call", "tool_result", "text"]
    assert events[0]["name"] == "create_task"
    assert events[1]["name"] == "create_task"
    assert events[-1]["text"] == "Done!"
    json.dumps(events)  # every event must be JSON-safe, because it is sent to the browser
