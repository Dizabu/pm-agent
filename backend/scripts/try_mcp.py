"""Start the tasks MCP server and use it like an AI client would."""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BACKEND_DIR = Path(__file__).resolve().parents[1]


async def main() -> None:
    # Start the server as a separate process (from backend/, so `app` is found)
    # and talk to it through stdin/stdout.
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server"],
        cwd=BACKEND_DIR,
    )

    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()  # the MCP "handshake"

        tools = await session.list_tools()  # what the AI sees first
        for tool in tools.tools:
            print(f"🔧 {tool.name}: {tool.description}")
            print(f"   inputs: {tool.input_schema['properties']}\n")

        result = await session.call_tool("create_task", {"title": "Try MCP"})
        print("create_task →", result.structured_content)

        result = await session.call_tool("update_task_status", {"task_id": 999, "status": "done"})
        print("error case  →", result.is_error, result.content[0].text)


asyncio.run(main())