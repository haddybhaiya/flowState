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

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="flowState - Groundwater Forecasting",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================
st.markdown("""
    <style>
    /* Main gradient background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Content cards */
    .stApp [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1f2937;
        font-weight: 600;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Info/Warning boxes */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        border-left: 4px solid;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Radio buttons */
    .stRadio > label {
        font-weight: 600;
        color: white;
    }
    
    /* Select box */
    .stSelectbox > label {
        font-weight: 600;
        color: white;
    }
    
    /* Title styling */
    .title-container {
        text-align: center;
        padding: 30px 0;
        margin-bottom: 20px;
    }
    
    .app-title {
        font-size: 56px;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 20px;
        color: rgba(255, 255, 255, 0.95);
        margin-top: 10px;
    }
    
    /* Risk badges */
    .risk-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        margin: 5px;
    }
    
    .risk-normal {
        background: #dcfce7;
        color: #166534;
    }
    
    .risk-warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    .risk-drought {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .risk-severe {
        background: #fecaca;
        color: #7f1d1d;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION
# ============================================================================
def login():
    """Display login form with professional styling"""
    
    # Create centered login container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="title-container">
                <h1 class="app-title">💧 FlowState</h1>
                <p class="app-subtitle">Groundwater Forecast & Analytics Platform</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 Login")
        st.markdown("Please enter your credentials to access the platform")
        
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter password")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Login", use_container_width=True):
                if (
                    username == st.secrets["auth"]["username"]
                    and password == st.secrets["auth"]["password"]
                ):
                    st.session_state.logged_in = True
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

def require_login():
    """Check authentication status"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        login()
        st.stop()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_risk_color(risk_level):
    """Return color mapping for risk levels"""
    risk_colors = {
        "Normal": "green",
        "Warning": "orange",
        "Drought": "red",
        "Severe Drought": "darkred"
    }
    return risk_colors.get(risk_level, "gray")

def display_risk_badge(risk_level):
    """Display a styled risk badge"""
    risk_class = {
        "Normal": "risk-normal",
        "Warning": "risk-warning",
        "Drought": "risk-drought",
        "Severe Drought": "risk-severe"
    }
    
    badge_class = risk_class.get(risk_level, "risk-normal")
    
    st.markdown(f"""
        <span class="risk-badge {badge_class}">
            {risk_level}
        </span>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================
require_login()

# App Header
st.markdown("""
    <div class="title-container">
        <h1 class="app-title">💧 FlowState</h1>
        <p class="app-subtitle">Advanced Groundwater Level Forecasting & Risk Assessment</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar Navigation
st.sidebar.markdown("### 🔍 Navigation")
st.sidebar.markdown("Select your view mode to explore groundwater data")

mode = st.sidebar.radio(
    "Choose View Mode",
    ["📍 Single Well Analysis", "🌍 All Wells Overview"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info("FlowState provides real-time groundwater forecasting and drought risk assessment for water resource management.")

# ============================================================================
# SINGLE WELL VIEW
# ============================================================================
if mode == "📍 Single Well Analysis":
    
    # Load available wells
    files = [f for f in os.listdir(PRED_DIR) if f.endswith("_forecast.csv")]
    well_names = sorted([f.replace("_forecast.csv", "") for f in files])
    
    # Well selector
    st.sidebar.markdown("### 🎯 Select Well")
    well = st.sidebar.selectbox(
        "Choose a monitoring well",
        well_names,
        help="Select a well to view detailed forecasts and risk assessment"
    )
    
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    # Load and process data
    df = pd.read_csv(os.path.join(PRED_DIR, f"{well}_forecast.csv"))
    df["risk"] = df["predicted_gwl"].apply(drought_risk)
    
    # Main content area
    st.markdown(f"## 📊 Analysis Dashboard - **{well}**")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_level = df["predicted_gwl"].iloc[0]
        st.metric(
            label="Current Forecast",
            value=f"{current_level:.2f} m",
            delta=f"{df['predicted_gwl'].iloc[-1] - current_level:.2f} m (30d)"
        )
    
    with col2:
        avg_level = df["predicted_gwl"].mean()
        st.metric(
            label="Average Forecast",
            value=f"{avg_level:.2f} m"
        )
    
    with col3:
        min_level = df["predicted_gwl"].min()
        st.metric(
            label="Minimum Forecast",
            value=f"{min_level:.2f} m",
            delta="Lowest point"
        )
    
    with col4:
        max_level = df["predicted_gwl"].max()
        st.metric(
            label="Maximum Forecast",
            value=f"{max_level:.2f} m",
            delta="Highest point"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts and Analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 30-Day Groundwater Forecast")
        st.line_chart(
            df.set_index("day")["predicted_gwl"],
            use_container_width=True,
            height=400
        )
    
    with col2:
        st.markdown("### 🚨 Risk Assessment")
        
        worst_risk = df["risk"].value_counts().idxmax()
        
        st.markdown(f"**Dominant Risk Level:**")
        display_risk_badge(worst_risk)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Risk distribution
        st.markdown("**Risk Distribution:**")
        risk_counts = df["risk"].value_counts()
        for risk, count in risk_counts.items():
            percentage = (count / len(df)) * 100
            st.markdown(f"- {risk}: {count} days ({percentage:.1f}%)")
    
    # Detailed Forecast Table
    st.markdown("### 📋 Detailed 30-Day Forecast")
    
    # Add color coding to the dataframe display
    display_df = df[["day", "predicted_gwl", "risk"]].copy()
    display_df.columns = ["Day", "Predicted GWL (m)", "Risk Level"]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Insights Section
    st.markdown("### 🧠 AI-Generated Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💡 Model Analysis")
        insights = generate_insights(df)
        for idx, insight in enumerate(insights, 1):
            st.info(f"**Insight {idx}:** {insight}")
    
    with col2:
        st.markdown("#### 🛠️ Recommended Actions")
        actions = recommend_actions(worst_risk)
        for idx, action in enumerate(actions, 1):
            st.warning(f"**Action {idx}:** {action}")
    
    # Map Section
    st.markdown("### 🗺️ Well Location & Risk Visualization")
    
    meta = pd.read_csv(os.path.join(BASE_DIR, "data", "metadata", "wells.csv"))
    row = meta[meta["well"] == well].iloc[0]
    
    # Create map
    m = folium.Map(
        location=[row.lat, row.lon],
        zoom_start=9,
        tiles="CartoDB positron"
    )
    
    folium.CircleMarker(
        location=[row.lat, row.lon],
        radius=15,
        color=get_risk_color(worst_risk),
        fill=True,
        fill_opacity=0.7,
        fill_color=get_risk_color(worst_risk),
        popup=f"<b>{well}</b><br>Risk: {worst_risk}<br>Level: {current_level:.2f}m",
        tooltip=f"{well} – {worst_risk}"
    ).add_to(m)
    
    st_folium(m, width=None, height=500, use_container_width=True)

# ============================================================================
# ALL WELLS OVERVIEW
# ============================================================================
elif mode == "🌍 All Wells Overview":
    
    st.markdown("## 🌍 Regional Groundwater Risk Overview")
    st.markdown("Comprehensive analysis of all monitoring wells in the network")
    
    # Load metadata
    meta = pd.read_csv(os.path.join(BASE_DIR, "data", "metadata", "wells.csv"))
    
    # Process all wells
    records = []
    
    with st.spinner("🔄 Loading data for all wells..."):
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
                "risk": dominant,
                "avg_gwl": df["predicted_gwl"].mean(),
                "min_gwl": df["predicted_gwl"].min(),
                "max_gwl": df["predicted_gwl"].max()
            })
    
    overview = pd.DataFrame(records)
    
    # Summary Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Wells", len(overview))
    
    with col2:
        critical_wells = len(overview[overview["risk"].isin(["Drought", "Severe Drought"])])
        st.metric("Critical Wells", critical_wells, delta=f"{(critical_wells/len(overview)*100):.1f}%")
    
    with col3:
        warning_wells = len(overview[overview["risk"] == "Warning"])
        st.metric("Warning Wells", warning_wells, delta=f"{(warning_wells/len(overview)*100):.1f}%")
    
    with col4:
        normal_wells = len(overview[overview["risk"] == "Normal"])
        st.metric("Normal Wells", normal_wells, delta=f"{(normal_wells/len(overview)*100):.1f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Regional Map
    st.markdown("### 🗺️ Regional Risk Map")
    st.markdown("Interactive map showing drought risk levels across all monitoring wells")
    
    m = folium.Map(
        location=[overview.lat.mean(), overview.lon.mean()],
        zoom_start=7,
        tiles="CartoDB positron"
    )
    
    for _, r in overview.iterrows():
        folium.CircleMarker(
            location=[r.lat, r.lon],
            radius=10,
            color=get_risk_color(r.risk),
            fill=True,
            fill_opacity=0.7,
            fill_color=get_risk_color(r.risk),
            popup=f"<b>{r.well}</b><br>Risk: {r.risk}<br>Avg GWL: {r.avg_gwl:.2f}m",
            tooltip=f"{r.well} – {r.risk}"
        ).add_to(m)
    
    st_folium(m, width=None, height=600, use_container_width=True)
    
    # Detailed Table
    st.markdown("### 📊 Comprehensive Well Data")
    
    display_overview = overview.copy()
    display_overview.columns = [
        "Well ID", "Latitude", "Longitude", "Risk Level",
        "Avg GWL (m)", "Min GWL (m)", "Max GWL (m)"
    ]
    
    # Format numeric columns
    display_overview["Avg GWL (m)"] = display_overview["Avg GWL (m)"].round(2)
    display_overview["Min GWL (m)"] = display_overview["Min GWL (m)"].round(2)
    display_overview["Max GWL (m)"] = display_overview["Max GWL (m)"].round(2)
    
    st.dataframe(
        display_overview,
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = overview.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Report (CSV)",
        data=csv,
        file_name="flowstate_all_wells_report.csv",
        mime="text/csv",
        use_container_width=False
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: white; padding: 20px;'>
        <p style='font-size: 14px;'>
            <b>FlowState v2.0</b> | Powered by Advanced ML Forecasting | 
            Built with ❤️ for sustainable water management
        </p>
        <p style='font-size: 12px; opacity: 0.8;'>
            © 2026 FlowState Analytics Platform
        </p>
    </div>
""", unsafe_allow_html=True)