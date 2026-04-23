from __future__ import annotations

import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# ===== 加载环境变量 =====
load_dotenv()

# ===== 导入工具（统一数据源：n8n）=====
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

# ===== TOOL REGISTRY =====
TOOLS = {
    "search_cases": get_cases_by_status,
    "get_case_statistics": get_case_statistics,
    "get_workflow_status": get_workflow_status,
    "get_processing_summary": get_processing_summary,
}

# ===== TOOL SCHEMAS =====
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

# ===== TOOL EXECUTION（关键）=====
def execute_tool(tool_name, arguments):
    tool_func = TOOLS.get(tool_name)

    if not tool_func:
        return {"error": f"Tool '{tool_name}' not found"}

    try:
        if tool_name == "search_cases":
            data = tool_func(arguments.get("status"))

            # 🔥 标准化返回结构（关键）
            return {
                "count": len(data),
                "items": data[:10]
            }

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

                "When multiple cases are returned, you MUST:\n"
                "- Clearly list them in bullet points\n"
                "- Include case_id, status, created_at\n\n"

                "Format:\n\n"

                "📊 Case Summary\n"
                "Short explanation\n\n"

                "📌 Key Info\n"
                "- Total cases\n"
                "- Main status trend\n\n"

                "📋 Case List\n"
                "- case_id | status | created_at\n\n"

                "🔍 Raw Data\n"
                "- Show structured JSON\n"
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

        # 👉 无 tool 调用 → 直接返回
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


# ===== CLI 测试 =====
if __name__ == "__main__":
    print("🚀 KVBB MCP Agent (Final Version)")
    print("Type 'exit' to quit")

    while True:
        user_input = input("\n>>> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        result = run_agent(user_input)

        print("\n[Agent Response]:")
        print(result)