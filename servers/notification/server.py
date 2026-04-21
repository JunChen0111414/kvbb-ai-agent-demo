from __future__ import annotations

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from servers.notification.tools import preview_notification, send_notification

load_dotenv()

mcp = FastMCP("notification")


@mcp.tool(description="Send a normalized notification to a recipient.")
def send_notification_tool(
    recipient: str,
    template_id: str,
    variables: dict,
    channel: str = "email",
) -> dict:
    return send_notification(
        {
            "recipient": recipient,
            "channel": channel,
            "template_id": template_id,
            "variables": variables,
        }
    )


@mcp.tool(description="Preview a notification template with variables.")
def preview_notification_tool(template_id: str, variables: dict) -> dict:
    return preview_notification(
        {
            "template_id": template_id,
            "variables": variables,
        }
    )


if __name__ == "__main__":
    mcp.run()