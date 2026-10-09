from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from app.config import settings
from app.task import Task, TaskStore


def create_server(store: TaskStore) -> MCPServer:
    """Build an MCP server that exposes the task store as tools."""
    mcp = MCPServer("tasks")

    @mcp.tool()
    def list_tasks() -> list[Task]:
        """List all tasks in the project with their id, title and status."""
        return store.list_tasks()

    @mcp.tool()
    def create_task(title: str) -> Task:
        """Create a new task with the given title. New tasks start as 'todo'."""
        new_task = store.create_task(title)
        return new_task

    @mcp.tool()
    def update_task_status(task_id: int, status: str) -> Task:
        """Update a task's status. Valid statuses are: 'todo', 'in_progress', and 'done'."""
        try:
            return store.update_task_status(task_id, status)
        except ValueError as e:
            raise ToolError(str(e)) from e

    return mcp


if __name__ == "__main__":
    create_server(TaskStore(Path(settings.tasks_file))).run()