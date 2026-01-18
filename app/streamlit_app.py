import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)


import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os
from src.drought import drought_risk
from src.insights import generate_insights, recommend_actions

PRED_DIR = os.path.join(BASE_DIR, "predictions")

# ---------------- AUTH ----------------
def login():
    st.title("flowState – Groundwater Forecast")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if (
            username == st.secrets["auth"]["username"]
            and password == st.secrets["auth"]["password"]
        ):
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")

def require_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login()
        st.stop()

# -------------- APP ------------------
require_login()
st.sidebar.title("🔍 View Mode")

mode = st.sidebar.radio(
    "Choose View",
    ["Single Well", "All Wells Overview"]
)

if mode == "Single Well":

    st.sidebar.title("🔍 Select Well")

    files = [f for f in os.listdir(PRED_DIR) if f.endswith("_forecast.csv")]
    well_names = [f.replace("_forecast.csv", "") for f in files]

    well = st.sidebar.selectbox("Well", well_names)

    df = pd.read_csv(os.path.join(PRED_DIR, f"{well}_forecast.csv"))
    df["risk"] = df["predicted_gwl"].apply(drought_risk)

    st.subheader(f"📈 Groundwater Forecast – {well}")
    st.line_chart(df.set_index("day")["predicted_gwl"])

    st.subheader("🚨 Drought Risk (Next 30 days)")
    st.dataframe(df[["day", "predicted_gwl", "risk"]])

    worst_risk = df["risk"].value_counts().idxmax()
    st.metric("Dominant Risk Level", worst_risk)

    # -------- INSIGHTS --------
    st.subheader("🧠 Model Insights")
    for i in generate_insights(df):
        st.info(i)

    # -------- ACTIONS --------
    st.subheader("🛠️ Recommended Actions")
    for a in recommend_actions(worst_risk):
        st.warning(a)

    # -------- MAP --------
    st.subheader("🗺️ Well Location & Drought Risk")

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
        zoom_start=9
    )

    folium.CircleMarker(
        location=[row.lat, row.lon],
        radius=10,
        color=risk_color[worst_risk],
        fill=True,
        fill_opacity=0.7,
        tooltip=f"{well} – {worst_risk}"
    ).add_to(m)

    st_folium(m, width=700, height=400)
if mode == "All Wells Overview":

    st.subheader("🌍 All Wells – Drought Risk Overview")

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
            "well": well,
            "lat": row.lat,
            "lon": row.lon,
            "risk": dominant
        })

    overview = pd.DataFrame(records)

    m = folium.Map(
        location=[overview.lat.mean(), overview.lon.mean()],
        zoom_start=7
    )

    risk_color = {
        "Normal": "green",
        "Warning": "orange",
        "Drought": "red",
        "Severe Drought": "darkred"
    }

    for _, r in overview.iterrows():
        folium.CircleMarker(
            location=[r.lat, r.lon],
            radius=8,
            color=risk_color[r.risk],
            fill=True,
            fill_opacity=0.7,
            tooltip=f"{r.well} – {r.risk}"
        ).add_to(m)

    st_folium(m, width=900, height=500)
    st.dataframe(overview)
