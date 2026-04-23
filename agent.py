from __future__ import annotations

import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# ===== 加载环境变量 =====
load_dotenv()

# ===== 导入工具（统一数据源：analytics → n8n）=====
from servers.analytics.tools import (
    get_case_statistics,
    get_cases_by_status
)
from servers.status.tools import (
    get_workflow_status,
    get_processing_summary
)

# ===== Azure OpenAI Client =====
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-02-01",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
)

MODEL = os.environ["AZURE_OPENAI_DEPLOYMENT"]

# ===== MCP TOOL REGISTRY =====
TOOLS = {
    "search_cases": get_cases_by_status,
    "get_case_statistics": get_case_statistics,
    "get_workflow_status": get_workflow_status,
    "get_processing_summary": get_processing_summary,
}

# ===== TOOL SCHEMAS（必须完全匹配TOOLS）=====
tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "search_cases",
            "description": "Get recent cases or filter by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_case_statistics",
            "description": "Get KPI statistics of cases",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_workflow_status",
            "description": "Get workflow processing status",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"}
                },
                "required": ["workflow_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_processing_summary",
            "description": "Get workflow summary for a case",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"}
                },
                "required": ["case_id"]
            }
        }
    }
]

# ===== TOOL 调用适配器（关键）=====
def execute_tool(tool_name, arguments):
    tool_func = TOOLS.get(tool_name)

    if not tool_func:
        return {"error": f"Tool '{tool_name}' not found"}

    try:
        # 🔥 参数适配（关键）
        if tool_name == "search_cases":
            return tool_func(arguments.get("status"))

        elif tool_name == "get_case_statistics":
            return tool_func()

        else:
            return tool_func(arguments)

    except Exception as e:
        return {"error": str(e)}


# ===== AGENT LOOP =====
def run_agent(user_input: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an enterprise workflow assistant.\n\n"
                "Always provide TWO layers:\n\n"

                "📊 Case Summary\n"
                "- Clear explanation\n\n"

                "📌 Key Info\n"
                "- Status\n"
                "- Decision\n"
                "- Next Step\n\n"

                "🔍 Raw Data\n"
                "- Show original fields\n"
            )
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

        # 👉 没有 tool call → 结束
        if not msg.tool_calls:
            return msg.content

        messages.append(msg)

        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")

            result = execute_tool(tool_name, arguments)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })


# ===== CLI 测试（可选）=====
if __name__ == "__main__":
    print("🚀 KVBB MCP Agent (Production Ready)")
    print("Type 'exit' to quit")

    while True:
        user_input = input("\n>>> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        result = run_agent(user_input)
        print("\n[Agent Response]:")
        print(result)