from __future__ import annotations

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from servers.business_data.tools import get_case_status, search_cases

load_dotenv()

mcp = FastMCP("business-data")


@mcp.tool(description="Get the normalized current status of a case by case_id.")
def get_case_status_tool(case_id: str) -> dict:
    return get_case_status({"case_id": case_id})


@mcp.tool(description="Search cases using normalized business filters.")
def search_cases_tool(filters: dict, limit: int = 20) -> dict:
    return search_cases({"filters": filters, "limit": limit})


if __name__ == "__main__":
    mcp.run()