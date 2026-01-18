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
    page_title="FlowState - Groundwater Analytics",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING - Streamlit Compatible
# ============================================================================
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: white !important;
    }
    
    /* Main content area background */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 2rem 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        margin-top: 2rem;
    }
    
    /* Headers */
    h1 {
        color: #1f2937;
        font-weight: 800;
    }
    
    h2, h3 {
        color: #1f2937;
        font-weight: 700;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    /* Metric container styling */
    [data-testid="metric-container"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e5e7eb;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        width: 100%;
        font-size: 0.95rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        border: none;
    }
    
    /* Info/Warning boxes */
    .stAlert {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Radio buttons */
    .stRadio > label {
        font-weight: 600;
        color: white;
        font-size: 1rem;
    }
    
    .stRadio [data-baseweb="radio"] > div {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.3rem 0;
    }
    
    /* Select box */
    .stSelectbox > label {
        font-weight: 600;
        color: white;
        font-size: 0.95rem;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(107, 114, 128, 0.3), transparent);
    }
    
    /* Chart containers */
    [data-testid="stLineChart"] {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 3rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        color: #6b7280;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION
# ============================================================================
def login():
    """Display login form with professional styling"""
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 3rem 0 2rem 0;'>
            <h1 style='color: white; font-size: 3.5rem; font-weight: 800; text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3); margin-bottom: 0.5rem;'>
                💧 FlowState
            </h1>
            <p style='color: rgba(255, 255, 255, 0.95); font-size: 1.3rem; margin-top: 0.5rem;'>
                Groundwater Forecast & Analytics Platform
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create centered login container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🔐 Login")
        st.markdown("Please enter your credentials to access the platform")
        st.markdown("<br>", unsafe_allow_html=True)
        
        username = st.text_input("👤 Username", placeholder="Enter username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
    risk_styles = {
        "Normal": "background: #dcfce7; color: #166534; padding: 0.5rem 1.2rem; border-radius: 25px; font-weight: 600; display: inline-block;",
        "Warning": "background: #fef3c7; color: #92400e; padding: 0.5rem 1.2rem; border-radius: 25px; font-weight: 600; display: inline-block;",
        "Drought": "background: #fee2e2; color: #991b1b; padding: 0.5rem 1.2rem; border-radius: 25px; font-weight: 600; display: inline-block;",
        "Severe Drought": "background: #fecaca; color: #7f1d1d; padding: 0.5rem 1.2rem; border-radius: 25px; font-weight: 600; display: inline-block;"
    }
    
    style = risk_styles.get(risk_level, risk_styles["Normal"])
    
    st.markdown(f"""
        <div style='margin: 1rem 0;'>
            <span style='{style}'>{risk_level}</span>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================
require_login()

# App Header
st.markdown("""
    <div style='text-align: center; padding: 1rem 0 2rem 0;'>
        <h1 style='color: #1f2937; font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem;'>
            💧 FlowState
        </h1>
        <p style='color: #6b7280; font-size: 1.2rem;'>
            Advanced Groundwater Level Forecasting & Risk Assessment
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🔍 Navigation")
    st.markdown("Select your view mode to explore groundwater data")
    
    mode = st.radio(
        "Choose View Mode",
        ["📍 Single Well Analysis", "🌍 All Wells Overview"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("FlowState provides real-time groundwater forecasting and drought risk assessment for water resource management.")

# ============================================================================
# SINGLE WELL VIEW
# ============================================================================
if mode == "📍 Single Well Analysis":
    
    # Load available wells
    files = [f for f in os.listdir(PRED_DIR) if f.endswith("_forecast.csv")]
    well_names = sorted([f.replace("_forecast.csv", "") for f in files])
    
    # Well selector in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎯 Select Well")
        well = st.selectbox(
            "Choose a monitoring well",
            well_names,
            help="Select a well to view detailed forecasts and risk assessment"
        )
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Load and process data
    df = pd.read_csv(os.path.join(PRED_DIR, f"{well}_forecast.csv"))
    df["risk"] = df["predicted_gwl"].apply(drought_risk)
    
    # Main content area
    st.markdown(f"## 📊 Analysis Dashboard - **{well}**")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_level = df["predicted_gwl"].iloc[0]
        delta_30d = df["predicted_gwl"].iloc[-1] - current_level
        st.metric(
            label="Current Forecast",
            value=f"{current_level:.2f} m",
            delta=f"{delta_30d:.2f} m (30d)"
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
        st.markdown("<br>", unsafe_allow_html=True)
        
        worst_risk = df["risk"].value_counts().idxmax()
        
        st.markdown("**Dominant Risk Level:**")
        display_risk_badge(worst_risk)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Risk distribution
        st.markdown("**Risk Distribution:**")
        risk_counts = df["risk"].value_counts()
        for risk, count in risk_counts.items():
            percentage = (count / len(df)) * 100
            st.markdown(f"• {risk}: {count} days ({percentage:.1f}%)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Forecast Table
    st.markdown("### 📋 Detailed 30-Day Forecast")
    
    display_df = df[["day", "predicted_gwl", "risk"]].copy()
    display_df.columns = ["Day", "Predicted GWL (m)", "Risk Level"]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    st.markdown("<br>", unsafe_allow_html=True)
    
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
        percentage = (critical_wells/len(overview)*100) if len(overview) > 0 else 0
        st.metric("Critical Wells", critical_wells, delta=f"{percentage:.1f}%")
    
    with col3:
        warning_wells = len(overview[overview["risk"] == "Warning"])
        percentage = (warning_wells/len(overview)*100) if len(overview) > 0 else 0
        st.metric("Warning Wells", warning_wells, delta=f"{percentage:.1f}%")
    
    with col4:
        normal_wells = len(overview[overview["risk"] == "Normal"])
        percentage = (normal_wells/len(overview)*100) if len(overview) > 0 else 0
        st.metric("Normal Wells", normal_wells, delta=f"{percentage:.1f}%")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download button
    csv = overview.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Report (CSV)",
        data=csv,
        file_name="flowstate_all_wells_report.csv",
        mime="text/csv"
    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 1.5rem;'>
        <p style='color: #1f2937; font-size: 1rem; font-weight: 600; margin-bottom: 0.3rem;'>
            FlowState v2.0 | Powered by Advanced ML Forecasting
        </p>
        <p style='color: #6b7280; font-size: 0.9rem; margin-bottom: 0.3rem;'>
            Built with ❤️ for sustainable water management
        </p>
        <p style='color: #9ca3af; font-size: 0.85rem;'>
            © 2026 FlowState Analytics Platform
        </p>
    </div>
""", unsafe_allow_html=True)