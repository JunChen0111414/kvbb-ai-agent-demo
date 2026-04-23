import streamlit as st
from agent import run_agent




st.set_page_config(page_title="KVBB AI Assistant", layout="wide")

st.title("🤖 KVBB AI Assistant")

# ===== KPI Dashboard =====
from servers.analytics.tools import (
    get_case_statistics,
    get_case_trend,
    get_cases_by_status
)

from servers.analytics.tools import get_ai_accuracy 
ai_stats = get_ai_accuracy()

stats = get_case_statistics()

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

col5.metric(
    "🧠 AI Accuracy",
    f"{ai_stats['accuracy']}%"
)
st.divider()

# ===== Chart =====
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

# ===== Case List (Drill-down) =====
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

# ===== Case Detail Page =====
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

    st.markdown("### 🧾 Case Info")
    st.markdown(f"""
    **Status:** {case_data.get("status")}  
    **Substatus:** {case_data.get("substatus")}  
    **Owner:** {case_data.get("owner_team")}  
    **Updated:** {case_data.get("updated_at")}  
    """)

    st.markdown("### ⚙️ Processing Summary")
    st.write(summary)

# ===== Chat =====
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

col1, col2, col3 = st.columns(3)

if col1.button("Check Status"):
    st.session_state["preset"] = "status of KVBB-2026-K9G89"

if col2.button("Explain Rejection"):
    st.session_state["preset"] = "Why was KVBB-2026-K9G89 rejected?"

if col3.button("Recent Cases"):
    st.session_state["preset"] = "show me recent cases"

user_input = st.chat_input("Ask about a case...")

if "preset" in st.session_state and not user_input:
    user_input = st.session_state.pop("preset")

if user_input:
    try:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                import io, sys

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

                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

    except Exception as e:
        st.error(f"❌ UI Error: {str(e)}")