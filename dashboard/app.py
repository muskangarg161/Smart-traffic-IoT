import time
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

BACKEND = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Traffic Dashboard", layout="wide")
st.title("🚦 Smart City Traffic Monitoring (Virtual IoT System)")

colA, colB = st.columns([1,1])
junction = colA.selectbox("Select Junction", ["ALL", "J1", "J2", "J3", "J4"])
limit = colB.slider("History (rows)", min_value=50, max_value=2000, value=400, step=50)
refresh_every = st.slider("Auto-refresh (seconds)", 2, 20, 5)

@st.cache_data(ttl=5)
def load_data(junc: str, limit: int):
    params = {"limit": limit}
    if junc != "ALL":
        params["junction_id"] = junc
    r = requests.get(f"{BACKEND}/readings", params=params, timeout=5)
    df = pd.DataFrame(r.json())
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
    return df

@st.cache_data(ttl=5)
def load_decisions(junc: str, limit: int):
    params = {"limit": limit}
    if junc != "ALL":
        params["junction_id"] = junc
    r = requests.get(f"{BACKEND}/decisions", params=params, timeout=5)
    df = pd.DataFrame(r.json())
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
    return df

tab1, tab2, tab3 = st.tabs(["📊 Live Traffic", "🟢 Signal Decisions", "🗂 Raw Data"])

with tab1:
    df = load_data(junction, limit)
    if df.empty:
        st.warning("No traffic data found. Start the simulator.")
    else:
        c1, c2 = st.columns(2)
        c1.metric("Latest Vehicle Count", int(df["vehicle_count"].iloc[-1]))
        c2.metric("Latest Avg Speed (km/h)", round(float(df["avg_speed_kmh"].iloc[-1]), 1))

        fig1 = px.line(df, x="timestamp", y="vehicle_count", color="junction_id",
                       title="Vehicle Count Over Time")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.line(df, x="timestamp", y="avg_speed_kmh", color="junction_id",
                       title="Average Speed (km/h) Over Time")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    dd = load_decisions(junction, limit)
    if dd.empty:
        st.info("No signal decisions recorded yet.")
    else:
        last = dd.iloc[-1]
        st.subheader("Most Recent Signal Decision")
        st.write(
            f"**Junction**: {last['junction_id']} | "
            f"**Green Time**: {last['green_seconds']} sec | "
            f"**Reason**: {last['reason']}"
        )
        fig3 = px.step(dd, x="timestamp", y="green_seconds", color="junction_id",
                       title="Green Signal Duration Over Time")
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.write("Traffic Readings")
    if not df.empty:
        st.dataframe(df.tail(50), use_container_width=True)

    st.write("Signal Decisions")
    if 'dd' in locals() and not dd.empty:
        st.dataframe(dd.tail(50), use_container_width=True)

time.sleep(refresh_every)
st.rerun()
