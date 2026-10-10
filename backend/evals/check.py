from app.task import Task


def check_case(case: dict, events: list[dict], tasks: list[Task]) -> list[str]:
    """Grade one agent run against an eval case. Returns the failures ([] means it passed)."""
    called = {e["name"] for e in events if e["type"] == "tool_call"}
    failures = []

    for tool in case["must_call"]:
        if tool not in called:
            failures.append(f"did not call {tool}")

    for tool in case["must_not_call"]:
        if tool in called:
            failures.append(f"called {tool} but shouldn't have")

    statuses = {t.title: t.status for t in tasks}
    for title, expected in case["expect_status"].items():
        actual = statuses.get(title)
        if actual != expected:
            failures.append(f"{title!r}: expected {expected}, got {actual}")

    if len(tasks) != case["expect_count"]:
        failures.append(f"expected {case['expect_count']} tasks, got {len(tasks)}")

    return failures
