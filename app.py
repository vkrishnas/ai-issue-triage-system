import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="AI Triage | Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    [data-testid="stMetricValue"] { color: #00ffcc; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ AI Event-Driven Triage System")
st.caption(f"Connected to FastAPI Backend | Live Feed: {datetime.now().strftime('%H:%M:%S')}")
st.divider()

@st.fragment(run_every=5)
def dashboard_body():
    try:
        response = requests.get("http://localhost:8000/stats", timeout=2)
        data = response.json()

        col1, col2, col3, col4 = st.columns(4)
        dist_dict = data.get("distribution", {})
        total_logs = sum(dist_dict.values())
        urgent_count = data.get("urgency", {}).get("1", 0)

        col1.metric("Total Events", total_logs)
        col2.metric("Critical Alerts", urgent_count, delta=f"{urgent_count} Active", delta_color="inverse")
        col3.metric("System Health", "Optimal" if total_logs > 0 else "Idle")
        col4.metric("Engine", "Groq-LLM")

        st.write("###")

        left_chart, right_table = st.columns([1, 1.5])

        with left_chart:
            st.subheader("Classification Distribution")
            if dist_dict:
                df_dist = pd.DataFrame(list(dist_dict.items()), columns=["Category", "Count"])
                fig = px.bar(
                    df_dist, x="Count", y="Category",
                    orientation='h',
                    template="plotly_dark",
                    color="Count",
                    color_continuous_scale="Viridis"
                )
                fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Waiting for logs to process...")

        with right_table:
            st.subheader("Live Triage Feed (Recent Activity)")
            try:
                logs_res = requests.get("http://localhost:8000/logs", timeout=2)
                logs_df = pd.DataFrame(logs_res.json())
                st.dataframe(
                    logs_df,
                    use_container_width=True,
                    height=350,
                    column_config={
                        "is_urgent": st.column_config.CheckboxColumn("Urgent?"),
                        "created_at": st.column_config.DatetimeColumn("Timestamp", format="hh:mm:ss")
                    }
                )
            except:
                st.warning("Create a /logs endpoint in FastAPI to show the raw data here!")

    except Exception as e:
        st.error(f"Backend Connection Lost. Ensure FastAPI is running on port 8000. Error: {e}")

dashboard_body()
