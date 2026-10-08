import json
from dataclasses import asdict, dataclass
from pathlib import Path

VALID_STATUSES = ("todo", "in_progress", "done")


@dataclass
class Task:
    id: int
    title: str
    status: str = "todo"


class TaskStore:
    """Saves project tasks in a JSON file."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _load(self) -> list[Task]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text())
        return [Task(**d) for d in data]

    def _save(self, tasks: list[Task]) -> None:
        data = [asdict(t) for t in tasks]
        self.path.write_text(json.dumps(data, indent=2))
