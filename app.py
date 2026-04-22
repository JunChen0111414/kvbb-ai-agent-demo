import streamlit as st
from agent import run_agent

st.set_page_config(page_title="KVBB AI Assistant", layout="wide")

st.title("🤖 KVBB AI Assistant")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 快捷按钮
col1, col2, col3 = st.columns(3)

if col1.button("Check Status"):
    st.session_state["preset"] = "status of KVBB-2026-K9G89"

if col2.button("Explain Rejection"):
    st.session_state["preset"] = "Why was KVBB-2026-K9G89 rejected?"

if col3.button("Recent Cases"):
    st.session_state["preset"] = "show me recent cases"

# 输入框
user_input = st.chat_input("Ask about a case...")

# 如果点了按钮，用 preset
if "preset" in st.session_state and not user_input:
    user_input = st.session_state.pop("preset")

# 主逻辑
if user_input:
    try:
        # 用户消息
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        # Agent 回复
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

                # 提取最终回答
                if "[Agent Response]:" in output:
                    answer = output.split("[Agent Response]:")[-1].strip()
                else:
                    answer = output

                st.markdown(answer)

                # 保存到历史
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

    except Exception as e:
        st.error(f"❌ UI Error: {str(e)}")
