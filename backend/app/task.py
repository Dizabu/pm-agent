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

    def list_tasks(self) -> list[Task]:
        return self._load()

    def create_task(self, title: str) -> Task:
        tasks = self._load()
        new_id = max((task.id for task in tasks), default=0) + 1
        task = Task(id=new_id, title=title)
        tasks.append(task)
        self._save(tasks)
        return task

    def update_task_status(self, task_id: int, status: str) -> Task:
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status {status!r}. Use one of: {', '.join(VALID_STATUSES)}")

        tasks = self._load()
        for task in tasks:
            if task.id == task_id:
                task.status = status
                self._save(tasks)
                return task

        raise ValueError(f"No task with id {task_id}")