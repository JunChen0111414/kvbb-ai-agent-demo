import streamlit as st
from agent import run_agent

st.set_page_config(page_title="KVBB AI Assistant", layout="wide")

st.title("🤖 KVBB AI Assistant")
st.markdown("Ask questions about cases, workflows, or decisions.")

# 聊天记录初始化
if "history" not in st.session_state:
    st.session_state.history = []

# 输入框
user_input = st.text_input("Your question:")

if st.button("Send") and user_input:
    st.session_state.history.append(("user", user_input))

    # 捕获 agent 输出
    import io
    import sys

    buffer = io.StringIO()
    sys.stdout = buffer

    run_agent(user_input)

    sys.stdout = sys.__stdout__
    output = buffer.getvalue()

    st.session_state.history.append(("agent", output))

# 显示聊天记录
for role, text in st.session_state.history:
    if role == "user":
        st.markdown(f"**👤 You:** {text}")
    else:
        st.markdown(f"**🤖 Agent:**")
        st.code(text, language="text")