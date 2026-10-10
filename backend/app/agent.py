import json

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from app.llm.base import LLMProvider, Message, ToolCall, ToolSpec


async def get_tool_specs(server: MCPServer) -> list[ToolSpec]:
    """Ask the MCP server which tools exist, in the format our providers understand."""
    tools = await server.list_tools()
    return [
        ToolSpec(name=t.name, description=t.description, input_schema=t.input_schema) for t in tools
    ]


async def run_tool(server: MCPServer, call: ToolCall) -> str:
    """Run one tool call on the MCP server and return the result as text for the LLM."""
    try:
        result = await server.call_tool(call.name, call.arguments)
    except ToolError as e:
        return f"Error: {e}"
    return json.dumps(result.structured_content)


SYSTEM_PROMPT = (
    "You are a project manager assistant. Use the tools to read and change the project's tasks. "
    "If you don't know a task's id, call list_tasks first. "
    "When you are done, answer the user briefly."
)


def describe_calls(calls: list[ToolCall]) -> str:
    """Write down which tools the model called, so it can read it on the next step."""
    return "\n".join(f"[called {c.name}({json.dumps(c.arguments)})]" for c in calls)


class Agent:
    """Runs the LLM in a loop, executing the tools it asks for, until it gives a final answer."""

    def __init__(self, llm: LLMProvider, server: MCPServer, max_steps: int = 5) -> None:
        self.llm = llm
        self.server = server
        self.max_steps = max_steps

    async def run(self, user_message: str) -> str:
        tools = await get_tool_specs(self.server)
        messages = [Message(role="user", content=user_message)]

        for _ in range(self.max_steps):
            response = await self.llm.chat(messages, system=SYSTEM_PROMPT, tools=tools)

            if not response.tool_calls:
                return response.text

            messages.append(Message(role="assistant", content=describe_calls(response.tool_calls)))
            results = [
                f"{call.name} → {await run_tool(self.server, call)}" for call in response.tool_calls
            ]  # TODO 3
            messages.append(Message(role="user", content="Tool results:\n" + "\n".join(results)))

        return "Sorry, I couldn't finish that within the step limit."
