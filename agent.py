import json
from pathlib import Path


def load_mcp_config(path: str = "mcp.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    config = load_mcp_config()
    servers = config.get("mcpServers", {})

    print("Loaded MCP servers:")
    for name, value in servers.items():
        print(f"- {name}")
        print(f"  command: {value.get('command')}")
        print(f"  args: {value.get('args')}")

    print("\nMCP config validation complete.")


if __name__ == "__main__":
    main()