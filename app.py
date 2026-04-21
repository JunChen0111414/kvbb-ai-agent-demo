import streamlit as st
from agent import run_agent

st.set_page_config(page_title="KVBB AI Assistant", layout="wide")

st.title("🤖 KVBB AI Assistant")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 输入框（ChatGPT风格）
user_input = st.chat_input("Ask about a case...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            import io
            import sys

            buffer = io.StringIO()
            sys.stdout = buffer

            run_agent(user_input)

            sys.stdout = sys.__stdout__
            output = buffer.getvalue()

            # 👉 只保留最后回答（去掉 debug）
            if "[Agent Response]:" in output:
                answer = output.split("[Agent Response]:")[-1].strip()
            else:
                answer = output

            st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
