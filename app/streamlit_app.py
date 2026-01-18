import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os
from src.drought import drought_risk

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
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

# Summary
worst_risk = df["risk"].value_counts().idxmax()
st.metric("Dominant Risk Level", worst_risk)
# -------- MAP VIEW --------
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
