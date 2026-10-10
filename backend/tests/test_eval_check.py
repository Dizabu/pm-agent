from app.task import Task
from evals.check import check_case

CASE = {
    "id": "mark-done",
    "message": "Mark the README task as done",
    "tasks": [],
    "must_call": ["list_tasks", "update_task_status"],
    "must_not_call": ["create_task"],
    "expect_status": {"Write the README": "done"},
    "expect_count": 1,
}


def call(name: str) -> dict:
    """A fake tool_call event, like the ones run_events() yields."""
    return {"type": "tool_call", "name": name, "arguments": {}}


def test_perfect_run_has_no_failures():
    events = [call("list_tasks"), call("update_task_status")]
    tasks = [Task(1, "Write the README", "done")]
    assert check_case(CASE, events, tasks) == []


def test_reports_missing_tool_call():
    events = [call("update_task_status")]  # skipped list_tasks!
    tasks = [Task(1, "Write the README", "done")]
    assert check_case(CASE, events, tasks) == ["did not call list_tasks"]


def test_reports_wrong_final_status():
    # The agent "called" both tools, but the task is still "todo"
    # (like the bug where the model wrote the tool call as text instead of calling it).
    events = [call("list_tasks"), call("update_task_status")]
    tasks = [Task(1, "Write the README", "todo")]
    assert check_case(CASE, events, tasks) == ["'Write the README': expected done, got todo"]


def test_reports_forbidden_tool_and_wrong_count():
    # The task is correctly done, but the agent ALSO called create_task,
    # so there is an extra task.
    events = [call("list_tasks"), call("update_task_status"), call("create_task")]
    tasks = [Task(1, "Write the README", "done"), Task(2, "Fix login bug", "todo")]
    assert check_case(CASE, events, tasks) == [
        "called create_task but shouldn't have",
        "expected 1 tasks, got 2",
    ]
