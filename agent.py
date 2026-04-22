from __future__ import annotations

import json
import os

from dotenv import load_dotenv
load_dotenv()

from openai import AzureOpenAI

from servers.business_data.tools import get_case_status, search_cases
from servers.status.tools import get_workflow_status, get_processing_summary
from servers.analytics.tools import get_case_statistics



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
    "get_case_statistics": get_case_statistics,
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
            "name": "get_workflow_status",
            "description": "Get workflow processing status from system",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"},
                },
                "required": ["workflow_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_processing_summary",
            "description": "Get summary of workflow including decision and next action",
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
            "description": "Search cases using filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "filters": {"type": "object"},
                    "limit": {"type": "integer"},
                },
            },
        },
    },
    {
    "type": "function",
    "function": {
        "name": "get_case_statistics",
        "description": "Get KPI statistics of cases (pending, in progress, approved, rejected)",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}
]


# ===== AGENT LOOP =====
def run_agent(user_input: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an enterprise workflow assistant.\n\n"

                "When answering about a case, you MUST provide TWO layers:\n\n"

                "1. Business Explanation (human readable)\n"
                "- Explain the situation clearly\n"
                "- Use natural language\n\n"

                "2. Structured Data (raw system values)\n"
                "- Show original fields from tools\n"
                "- Do NOT modify or reinterpret values\n\n"

                "Format your response like:\n\n"

                "📊 Case Summary\n"
                "<short explanation>\n\n"

                "📌 Key Info\n"
                "- Status: ...\n"
                "- Decision: ...\n"
                "- Next Step: ...\n\n"

                "🔍 Raw Data\n"
                "- bearbeitungsstatus: ...\n"
                "- ki_ergebnis: ...\n"
                "- human_review: ...\n"
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
            print("\n[Agent Response]:")
            print(msg.content)
            break

        # 👉 记录 assistant message（必须）
        messages.append(msg)

        # 👉 处理所有 tool_calls（关键）
        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"\n[Agent] Calling tool: {tool_name}")
            print(f"[Agent] Args: {arguments}")

            tool_func = TOOLS.get(tool_name)

            try:
                result = tool_func(arguments)
            except Exception as e:
                result = {"error": str(e)}

            print("[Tool Result]:", result)

            # 👉 必须逐个返回（关键修复点）
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

    # ===== FIRST CALL =====
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tool_definitions,
        tool_choice="auto",
    )

    msg = response.choices[0].message

    # ===== TOOL CALL =====
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print("\n[Agent] Tool selected:", tool_name)
        print("[Agent] Arguments:", arguments)

        tool_func = TOOLS.get(tool_name)

        try:
            result = tool_func(arguments)
        except Exception as e:
            result = {"error": str(e)}

        print("\n[Tool Result]:")
        print(result)

        # ===== FEEDBACK TO MODEL =====
        messages.append(msg)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            }
        )

        # ===== FINAL RESPONSE =====
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        print("\n[Agent Response]:")
        print(final_response.choices[0].message.content)

    else:
        print("\n[Agent Response]:")
        print(msg.content)


# ===== CLI =====
if __name__ == "__main__":
    print("🚀 KVBB MCP Agent (Azure OpenAI)")
    print("Type 'exit' to quit")

    while True:
        user_input = input("\n>>> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        run_agent(user_input)
