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

user_input = st.chat_input("Ask about a case...")

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

                st.write(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

    except Exception as e:
        st.error(f"❌ UI Error: {str(e)}")

            # 👉 只保留最后回答（去掉 debug）
            if "[Agent Response]:" in output:
                answer = output.split("[Agent Response]:")[-1].strip()
            else:
                answer = output

            st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )


col1, col2, col3 = st.columns(3)

if col1.button("Check Status"):
    user_input = "status of KVBB-2026-K9G89"

if col2.button("Explain Rejection"):
    user_input = "Why was KVBB-2026-K9G89 rejected?"

if col3.button("Recent Cases"):
    user_input = "show me recent cases"
