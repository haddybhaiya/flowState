import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

from src.drought import drought_risk
from src.insights import generate_insights, recommend_actions

PRED_DIR = os.path.join(BASE_DIR, "predictions")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="flowState – Groundwater Intelligence",
    page_icon="🌊",
    layout="wide"
)

# ---------------- AUTH ----------------
def login():
    st.markdown("## 🔐 Login to flowState")
    st.caption("AI-powered groundwater forecasting platform")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if (
                username == st.secrets["auth"]["username"]
                and password == st.secrets["auth"]["password"]
            ):
                st.session_state.logged_in = True
                st.success("Login successful")
            else:
                st.error("Invalid credentials")

def require_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login()
        st.stop()

# ---------------- APP START ----------------
require_login()

# ---------------- HEADER ----------------
st.markdown("# flowState")
st.markdown(
    "### Groundwater Forecasting & Drought Risk Intelligence System"
)
st.caption(
    "Predict · Assess · Visualize · Act"
)

st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 📌 Project Overview")
st.sidebar.info(
    """
    **Model:** LSTM-based Forecasting  
    **Forecast Horizon:** 30 Days  
    **Risk Levels:** Normal · Warning · Drought · Severe  
    **Use Case:** Climate Resilience & Water Planning  
    """
)

st.sidebar.markdown("## 🔍 View Mode")
mode = st.sidebar.radio(
    "Choose Analysis Type",
    ["Single Well", "All Wells Overview"]
)

# ================= SINGLE WELL =================
if mode == "Single Well":

    st.sidebar.markdown("## 🛢️ Select Well")

    files = [f for f in os.listdir(PRED_DIR) if f.endswith("_forecast.csv")]
    well_names = [f.replace("_forecast.csv", "") for f in files]

    well = st.sidebar.selectbox("Well ID", well_names)

    df = pd.read_csv(os.path.join(PRED_DIR, f"{well}_forecast.csv"))
    df["risk"] = df["predicted_gwl"].apply(drought_risk)

    worst_risk = df["risk"].value_counts().idxmax()

    # -------- METRICS --------
    col1, col2, col3 = st.columns(3)

    col1.metric("Selected Well", well)
    col2.metric("Forecast Days", "30")
    col3.metric("Dominant Risk", worst_risk)

    st.divider()

    # -------- FORECAST --------
    st.markdown("## 📈 Groundwater Level Forecast")
    st.line_chart(df.set_index("day")["predicted_gwl"])

    with st.expander("📋 View Forecast Data"):
        st.dataframe(df[["day", "predicted_gwl", "risk"]], use_container_width=True)

    # -------- INSIGHTS --------
    st.markdown("## 🧠 Model Insights")
    for insight in generate_insights(df):
        st.info(insight)

    # -------- ACTIONS --------
    st.markdown("## 🛠️ Recommended Actions")
    for action in recommend_actions(worst_risk):
        st.warning(action)

    # -------- MAP --------
    st.markdown("## 🗺️ Well Location & Risk Map")

    meta = pd.read_csv(
        os.path.join(BASE_DIR, "data", "metadata", "wells.csv")
    )

    row = meta[meta["well"] == well].iloc[0]

    risk_color = {
        "Normal": "green",
        "Warning": "orange",
        "Drought": "red",
        "Severe Drought": "darkred"
    }

    m = folium.Map(
        location=[row.lat, row.lon],
        zoom_start=9,
        tiles="cartodbpositron"
    )

    folium.CircleMarker(
        location=[row.lat, row.lon],
        radius=12,
        color=risk_color[worst_risk],
        fill=True,
        fill_opacity=0.75,
        tooltip=f"{well} – {worst_risk}"
    ).add_to(m)

    st_folium(m, width=900, height=420)

# ================= ALL WELLS =================
else:
    st.markdown("## 🌍 Regional Groundwater Risk Overview")

    meta = pd.read_csv(
        os.path.join(BASE_DIR, "data", "metadata", "wells.csv")
    )

    records = []

    for f in os.listdir(PRED_DIR):
        if not f.endswith("_forecast.csv"):
            continue

        well = f.replace("_forecast.csv", "")
        df = pd.read_csv(os.path.join(PRED_DIR, f))
        df["risk"] = df["predicted_gwl"].apply(drought_risk)

        dominant = df["risk"].value_counts().idxmax()
        row = meta[meta["well"] == well].iloc[0]

        records.append({
            "Well": well,
            "Latitude": row.lat,
            "Longitude": row.lon,
            "Risk": dominant
        })

    overview = pd.DataFrame(records)

    m = folium.Map(
        location=[overview.Latitude.mean(), overview.Longitude.mean()],
        zoom_start=7,
        tiles="cartodbpositron"
    )

    risk_color = {
        "Normal": "green",
        "Warning": "orange",
        "Drought": "red",
        "Severe Drought": "darkred"
    }

    for _, r in overview.iterrows():
        folium.CircleMarker(
            location=[r.Latitude, r.Longitude],
            radius=8,
            color=risk_color[r.Risk],
            fill=True,
            fill_opacity=0.7,
            tooltip=f"{r.Well} – {r.Risk}"
        ).add_to(m)

    st_folium(m, width=1200, height=500)

    with st.expander("📋 View All Wells Data"):
        st.dataframe(overview, use_container_width=True)
