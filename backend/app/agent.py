import json

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from app.llm.base import ToolCall, ToolSpec


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
