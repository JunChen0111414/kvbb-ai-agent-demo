from __future__ import annotations

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from servers.human_review.tools import create_review_task, submit_review_decision

load_dotenv()

mcp = FastMCP("human-review")


@mcp.tool(description="Create a human review task for a case.")
def create_review_task_tool(case_id: str, review_type: str, payload: dict) -> dict:
    return create_review_task(
        {
            "case_id": case_id,
            "review_type": review_type,
            "payload": payload,
        }
    )


@mcp.tool(description="Submit a decision for a human review task.")
def submit_review_decision_tool(
    task_id: str,
    decision: str,
    comment: str | None = None,
) -> dict:
    return submit_review_decision(
        {
            "task_id": task_id,
            "decision": decision,
            "comment": comment,
        }
    )


if __name__ == "__main__":
    mcp.run()
