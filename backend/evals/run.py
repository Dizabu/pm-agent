"""Run every eval case against the real LLM configured in .env, and print a score."""

import asyncio
import json
import tempfile
from pathlib import Path

from app.agent import Agent
from app.llm import get_provider
from app.mcp_server import create_server
from app.task import Task, TaskStore
from evals.check import check_case

CASES_FILE = Path(__file__).parent / "cases.jsonl"


def load_cases() -> list[dict]:
    lines = CASES_FILE.read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


async def run_case(case: dict) -> list[str]:
    """Run the agent on one case, in a throwaway task store, and grade it."""
    with tempfile.TemporaryDirectory() as tmp:
        store = TaskStore(Path(tmp) / "tasks.json")
        store._save(
            [Task(i, t["title"], t["status"]) for i, t in enumerate(case["tasks"], start=1)]
        )
        agent = Agent(get_provider(), create_server(store))
        try:
            events = [event async for event in agent.run_events(case["message"])]
        except Exception as e:  # noqa: BLE001 - one crashing case must not stop the whole eval run
            return [f"crashed: {e!r}"]
        return check_case(case, events, store.list_tasks())


async def main() -> None:
    cases = load_cases()
    if not cases:
        raise SystemExit(f"No eval cases found in {CASES_FILE}")

    passed = 0
    for case in cases:
        failures = await run_case(case)
        if failures:
            print(f"❌ {case['id']}: " + "; ".join(failures))
        else:
            passed += 1
            print(f"✅ {case['id']}")

    print(
        f"Score: {passed}/{len(cases)} ({passed / len(cases) * 100:.0f}%)"
    )  # TODO 2: e.g. "Score: 6/8 (75%)"


if __name__ == "__main__":
    asyncio.run(main())
