import streamlit as st
from agent import run_agent

st.set_page_config(page_title="KVBB AI Assistant", layout="wide")

st.title("🤖 KVBB AI Assistant")

# ===== KPI Dashboard =====
from servers.analytics.tools import get_case_statistics

try:
    stats = get_case_statistics()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🟡 Pending", stats["pending"])
    col2.metric("🔵 In Progress", stats["in_progress"])
    col3.metric("🟢 Approved", stats["approved"])
    col4.metric("🔴 Rejected", stats["rejected"])

except Exception as e:
    st.warning(f"KPI not available: {e}")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- 卡片渲染 ----------
def render_case(case):
    status = case.get("status", "").lower()

    if "pending" in status:
        color = "🟡"
    elif "progress" in status:
        color = "🔵"
    elif "approved" in status:
        color = "🟢"
    else:
        color = "⚪"

    st.markdown(f"""
    <div style="
        border:1px solid #ddd;
        border-radius:10px;
        padding:12px;
        margin-bottom:10px;
        background-color:#fafafa;
    ">
        <b>{color} {case.get('case_id')}</b><br>
        <small>Created: {case.get('created_at')}</small><br>
        <small>Status: {case.get('status')}</small>
    </div>
    """, unsafe_allow_html=True)

# ---------- 解析列表 ----------
def try_render_cases(answer: str):
    import json

    try:
        data = json.loads(answer)

        if isinstance(data, dict) and "items" in data:
            items = data["items"]

            pending = [c for c in items if "pending" in c["status"].lower()]
            progress = [c for c in items if "progress" in c["status"].lower()]

            if pending:
                st.header("🟡 Pending Review")
                for c in pending:
                    render_case(c)

            if progress:
                st.header("🔵 In Progress")
                for c in progress:
                    render_case(c)

            return True
    except:
        return False

    return False

# ---------- 显示历史 ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- 快捷按钮 ----------
col1, col2, col3 = st.columns(3)

if col1.button("Check Status"):
    st.session_state["preset"] = "status of KVBB-2026-K9G89"

if col2.button("Explain Rejection"):
    st.session_state["preset"] = "Why was KVBB-2026-K9G89 rejected?"

if col3.button("Recent Cases"):
    st.session_state["preset"] = "show me recent cases"

# ---------- 输入 ----------
user_input = st.chat_input("Ask about a case...")

if "preset" in st.session_state and not user_input:
    user_input = st.session_state.pop("preset")

# ---------- 主逻辑 ----------
if user_input:
    try:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                import io
                import sys

                buffer = io.StringIO()
                sys.stdout = buffer

                try:
                    run_agent(user_input)
                except Exception as e:
                    sys.stdout = sys.__stdout__
                    st.error(f"❌ Agent Error: {str(e)}")
                    st.stop()

                sys.stdout = sys.__stdout__
                output = buffer.getvalue()

                if "[Agent Response]:" in output:
                    answer = output.split("[Agent Response]:")[-1].strip()
                else:
                    answer = output

                # 👉 优先尝试卡片渲染
                rendered = try_render_cases(answer)

                if not rendered:
                    st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

    except Exception as e:
        st.error(f"❌ UI Error: {str(e)}")
