import streamlit as st
from agent import run_agent

st.set_page_config(page_title="KVBB AI Assistant", layout="wide")

st.title("🤖 KVBB AI Assistant")

# ===== KPI Dashboard =====
from servers.analytics.tools import (
    get_case_statistics,
    get_case_trend,
    get_cases_by_status,
    get_ai_accuracy
)

stats = get_case_statistics()
ai_stats = get_ai_accuracy()

st.markdown("## 📊 KVBB Dashboard")

col1, col2, col3, col4, col5 = st.columns(5)

if col1.button(f"🟡 Pending ({stats['pending']})"):
    st.session_state["selected_status"] = "pending"

if col2.button(f"🔵 In Progress ({stats['in_progress']})"):
    st.session_state["selected_status"] = "in_progress"

if col3.button(f"🟢 Approved ({stats['approved']})"):
    st.session_state["selected_status"] = "approved"

if col4.button(f"🔴 Rejected ({stats['rejected']})"):
    st.session_state["selected_status"] = "rejected"

col5.metric("🧠 AI Accuracy", f"{ai_stats['accuracy']}%")

st.divider()

# ===== Charts =====
import pandas as pd

data = pd.DataFrame({
    "Status": ["Pending", "In Progress", "Approved", "Rejected"],
    "Count": [
        stats["pending"],
        stats["in_progress"],
        stats["approved"],
        stats["rejected"]
    ]
})

st.subheader("📊 Case Distribution")
st.bar_chart(data.set_index("Status"))

trend = get_case_trend()
df = pd.DataFrame(trend)

st.subheader("📈 Cases Over Time")
if not df.empty:
    st.line_chart(df.set_index("date"))

# ===== Case List =====
if "selected_status" in st.session_state:
    status = st.session_state["selected_status"]

    st.subheader(f"📂 Cases: {status.upper()}")

    cases = get_cases_by_status(status)

    for case in cases:
        if st.button(f"📄 {case['case_id']}"):
            st.session_state["selected_case"] = case["case_id"]

        st.markdown(f"""
        <div style="
            border:1px solid #ddd;
            border-radius:8px;
            padding:10px;
            margin-bottom:8px;
            background:#fafafa;
        ">
            <b>{case['case_id']}</b><br>
            Status: {case['status']}<br>
            Created: {case['created_at']}
        </div>
        """, unsafe_allow_html=True)

# ===== Case Detail =====
from servers.business_data.tools import get_case_status
from servers.status.tools import get_processing_summary

if "selected_case" in st.session_state:
    case_id = st.session_state["selected_case"]

    st.divider()
    st.subheader(f"📄 Case Detail: {case_id}")

    if st.button("⬅ Back"):
        del st.session_state["selected_case"]
        st.rerun()

    case_data = get_case_status({"case_id": case_id})
    summary = get_processing_summary({"case_id": case_id})

    # ==============================
    # 📊 Summary（更自然一点）
    # ==============================
    st.markdown("### 📊 Case Summary")

    st.markdown(f"""
This case is currently **{case_data.get("status")}**.

It is handled by **{case_data.get("owner_team") or "N/A"}**  
and was last updated on **{case_data.get("updated_at")}**.

{summary if summary else ""}
""")

    # ==============================
    # 📌 Key Info
    # ==============================
    st.markdown("### 📌 Key Info")

    st.markdown(f"""
- **Status:** {case_data.get("status")}
- **Substatus:** {case_data.get("substatus")}
- **Owner:** {case_data.get("owner_team")}
- **Updated:** {case_data.get("updated_at")}
""")

    # ==============================
    # 🔍 Raw Data（折叠）
    # ==============================
    with st.expander("🔍 Raw Data"):
        st.json(case_data)

    # ==============================
    # ⚙️ Processing Summary（结构化）
    # ==============================
    st.markdown("### ⚙️ Processing Summary")

    if isinstance(summary, dict):
        st.json(summary)
    else:
        st.write(summary)


# ===== Chat =====
st.divider()
st.subheader("💬 Chat Assistant")

# ==============================
# 渲染函数（核心）
# ==============================
def render_chat_answer(answer):
    lines = answer.split("\n")

    # 👉 Case List（卡片 UI）
    if "|" in answer:
        st.markdown("### 📋 Case List")

        for i, line in enumerate(lines):
            if line.strip():
                parts = line.split("|")

                if len(parts) == 3:
                    case_id, status, created = [p.strip() for p in parts]

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.markdown(f"""
                        <div style="
                            border:1px solid #ddd;
                            border-radius:8px;
                            padding:10px;
                            margin-bottom:6px;
                            background:#fafafa;
                        ">
                            <b>{case_id}</b><br>
                            Status: {status}<br>
                            Created: {created}
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        if st.button("Open", key=f"chat_{case_id}_{i}"):
                            st.session_state["selected_case"] = case_id
                            st.rerun()

                else:
                    st.write(line)

    # 👉 Case Detail（文本）
    elif "📄 Case Detail" in answer:
        st.markdown(answer.replace("\n", "  \n"))

    # 👉 普通回答
    else:
        st.markdown(answer)


# ==============================
# Session 初始化
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# 历史消息显示
# ==============================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_chat_answer(msg["content"])


# ==============================
# 快捷按钮
# ==============================
col1, col2, col3 = st.columns(3)

if col1.button("Check Status"):
    st.session_state["preset"] = "status of KVBB-2026-K9G89"

if col2.button("Explain Rejection"):
    st.session_state["preset"] = "Why was KVBB-2026-K9G89 rejected?"

if col3.button("Recent Cases"):
    st.session_state["preset"] = "show me recent cases"


# ==============================
# 输入框
# ==============================
user_input = st.chat_input("Ask about a case...")

if "preset" in st.session_state and not user_input:
    user_input = st.session_state.pop("preset")


# ==============================
# 处理输入
# ==============================
if user_input:
    try:
        # 👉 保存用户消息
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        # 👉 生成回答
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = run_agent(user_input)
                except Exception as e:
                    st.error(f"❌ Agent Error: {str(e)}")
                    st.stop()

                render_chat_answer(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

    except Exception as e:
        st.error(f"❌ UI Error: {str(e)}")