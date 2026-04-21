from __future__ import annotations

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from servers.status.tools import get_processing_summary, get_workflow_status

load_dotenv()

mcp = FastMCP("status")


@mcp.tool(description="Get the current status of a workflow.")
def get_workflow_status_tool(workflow_id: str) -> dict:
    return get_workflow_status({"workflow_id": workflow_id})


@mcp.tool(description="Get a normalized summary of current processing for a case.")
def get_processing_summary_tool(case_id: str) -> dict:
    return get_processing_summary({"case_id": case_id})


if __name__ == "__main__":
    mcp.run()
