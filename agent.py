from __future__ import annotations
import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

from openai import AzureOpenAI

from servers.business_data.tools import get_case_status, search_cases
from servers.status.tools import get_workflow_status, get_processing_summary


# ===== Azure OpenAI Client =====
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
)

MODEL = os.environ["AZURE_OPENAI_DEPLOYMENT"]


# ===== MCP TOOL REGISTRY =====
TOOLS = {
    "get_case_status": get_case_status,
    "search_cases": search_cases,
    "get_workflow_status": get_workflow_status,
    "get_processing_summary": get_processing_summary,
}


# ===== TOOL SCHEMAS =====
tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "get_case_status",
            "description": "Get detailed case status from business database",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                },
                "required": ["case_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_processing_summary",
            "description": "Get workflow summary of a case",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                },
                "required": ["case_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_cases",
            "description": (
                "Search cases. ALWAYS include filters.\n"
                "If user asks for recent → use last 7 days.\n"
                "If user asks for active → use pending_review + in_progress."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "properties": {
                            "statuses": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "created_after": {"type": "string"},
                        },
                    },
                    "limit": {"type": "integer"},
                },
                "required": ["filters"],
            },
        },
    },
]


# ===== HELPER: DEFAULT FILTER BUILDER =====
def build_default_filters(user_input: str):
    today = datetime.utcnow()

    if "recent" in user_input.lower() or "last 7 days" in user_input.lower():
        return {
            "created_after": (today - timedelta(days=7)).strftime("%Y-%m-%d")
        }

    if "active" in user_input.lower():
        return {
            "statuses": ["pending_review", "in_progress"]
        }

    return {}


# ===== AGENT LOOP =====
def run_agent(user_input: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an enterprise workflow assistant.\n"
                "Use tools whenever data is required.\n"
                "Never guess data.\n\n"

                "Rules:\n"
                "- Always use search_cases with filters\n"
                "- If user says 'recent', use last 7 days\n"
                "- If user says 'active', use pending_review + in_progress\n"
                "- Never call search_cases without filters\n"
                "- Output must be clean business language\n"
                "- Do NOT show technical fields or raw codes\n"
            ),
        },
        {"role": "user", "content": user_input},
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tool_definitions,
            tool_choice="auto",
        )

        msg = response.choices[0].message

        # 👉 没有 tool call → 输出结果
        if not msg.tool_calls:
            print("\n[Agent Response]:")
            print(msg.content)
            return

        messages.append(msg)

        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")

            # 👉 自动补 filters（关键优化）
            if tool_name == "search_cases":
                if not arguments.get("filters"):
                    arguments["filters"] = build_default_filters(user_input)

            print(f"\n[Agent] Calling tool: {tool_name}")
            print(f"[Agent] Args: {arguments}")

            tool_func = TOOLS.get(tool_name)

            try:
                result = tool_func(arguments)
            except Exception as e:
                result = {"error": str(e)}

            print("[Tool Result]:", result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })


# ===== CLI =====
if __name__ == "__main__":
    print("🚀 KVBB MCP Agent (Improved)")
    print("Type 'exit' to quit")

    while True:
        user_input = input("\n>>> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        run_agent(user_input)
