from __future__ import annotations

import os
import re
from dotenv import load_dotenv
from openai import AzureOpenAI

# ===== 加载环境变量 =====
load_dotenv()

# ===== Azure OpenAI Client（GPT-5.x 必须用这个 version）=====
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2025-04-01-preview",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
)

MODEL = os.environ["AZURE_OPENAI_DEPLOYMENT"]

# ===== 导入工具 =====
from servers.analytics.tools import get_cases_by_status, get_rejection_cases
from servers.business_data.tools import get_case_status


# ===== AGENT =====
def run_agent(user_input: str) -> str:

    text = user_input.lower()

    # ==============================
    # 1️⃣ Case Detail（最高优先）
    # ==============================
    match = re.search(r"(kvbb-\d{4}-[a-z0-9]+)", text)
    if match:
        case_id = match.group(1).upper()

        data = get_case_status({"case_id": case_id})

        if not data:
            return f"❌ No data found for {case_id}"

        return f"""
📄 Case Detail: {case_id}

Status: {data.get('status')}
Substatus: {data.get('substatus')}
Owner: {data.get('owner_team')}
Updated: {data.get('updated_at')}
""".strip()

    # ==============================
    # 2️⃣ Recent Cases
    # ==============================
    if "recent" in text:
        data = get_cases_by_status()

        if not data:
            return "❌ No cases found."

        return "\n".join(
            f"{d['case_id']} | {d['status']} | {d['created_at']}"
            for d in data[:10]
        )

    # ==============================
    # 3️⃣ Pending Cases
    # ==============================
    if "pending" in text:
        data = get_cases_by_status("pending")
        if not data:
            return "❌ No pending cases."
        return "\n".join(
            f"{d['case_id']} | {d['status']} | {d['created_at']}"
            for d in data[:10]
        )

    # 4️⃣ Rejection Reasons
    # ==============================
    if "Ablehnung" in text or "Ablehnungsgründe " in text or "reject" in text or "rejection" in text or "abgelehnt" in text:
        data = get_rejection_cases()
        if not data:
            return "❌ No rejection reasons found."
        context = "\n".join(
            f"{d['case_id']} | {d.get('review_reason', '')}"
            for d in data[:20]
            if d.get("review_reason")
        )

        print("DEBUG review_reason context:", context[:500])

        prompt = f"""

    You are a KVBB case review analysis assistant.

    User question:
    {user_input}

    Below are real human review rejection reasons (review_reason):
    {context}

    Task:
    - Identify and summarize the main rejection reasons
    - Group similar reasons into clear categories
    - Reference relevant case IDs where appropriate
    - Base your answer only on the provided review_reason texts
    - Do NOT infer or assume reasons from case status
    - Respond in the same language as the user

    """

        response = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": "You analyze KVBB case review data."},
                {"role": "user", "content": prompt},
            ],
        )
        for item in response.output:
            if item.type == "message":
                return item.content[0].text
            
    # ==============================
    # 4️⃣ GPT Fallback（仅解释）
    # ==============================
    system_prompt = (
        "You are a KVBB workflow assistant.\n"
        "Answer clearly and concisely."
    )

    try:
        response = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )

        # 提取文本
        for item in response.output:
            if item.type == "message":
                return item.content[0].text

        return "⚠️ No response from model."

    except Exception as e:
        return f"❌ LLM Error: {str(e)}"


# ===== CLI 测试 =====
if __name__ == "__main__":
    print("🚀 KVBB Agent (Final Stable Version)")
    print("Type 'exit' to quit")

    while True:
        user_input = input("\n>>> ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = run_agent(user_input)

        print("\n[Agent]:")
        print(result)