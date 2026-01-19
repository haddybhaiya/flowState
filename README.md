<img width="1597" height="317" alt="image" src="https://github.com/user-attachments/assets/a61d47bb-bed0-4bb6-a2c9-9bb85a6ad34f" />

### A impactful repository of project flowState , allowing AI-powered real -time groundwater forecasting and drought risk assessment platform built using Streamlit, Machine Learning, and Geospatial Visualization.
 - It helps governments, researchers, and planners anticipate groundwater stress and take early preventive actions.
---
# Live link 
 -  stremlit app : https://flowstates.streamlit.app
```
username : admin
password : flowstate123
```
---
# Problem Statement
Groundwater depletion and droughts pose serious risks to agriculture, drinking water supply, and ecosystems.
Traditional monitoring systems are hard to intrepret and not predictive.
---
## flowState solves this by:
 - Forecasting groundwater levels in advance

- Classifying drought risk levels

- Providing actionable insights & recommendations

 - Visualizing risk spatially on maps
   
---

# flowState combines:

 -  Time-series ML forecasting

 -  Drought risk classification

 -  Explainable insights

-  Interactive geospatial mapping

All in a single, easy-to-use web dashboard.

--- 

#  Model Insights

 - Trend analysis

- Risk concentration detection

- Forecast behavior explanation

## Action Recommendations

 - Risk-specific mitigation strategies

 - Policy & operational guidance

## Map-Based Visualization

 - Single well risk view

 - All-wells regional overview

 - Color-coded drought intensity
   
---

#  Project Structure
```
flowstate/
│
├── app/
│   └── streamlit_app.py
│
├── src/
│   ├── drought.py
│   └── insights.py
│
├── predictions/
│   └── *_forecast.csv
│
├── data/
│   └── metadata/
│       └── wells.csv
│
├── .streamlit/
│   └── secrets.toml
│
├── requirements.txt
└── README.md
```

#  Run Locally
 -  ## 1️ Clone the repository
``` 
git clone https://github.com/your-username/flowstate.git
cd flowstate
```

  - ## 2️ Install dependencies
``` 
pip install -r requirements.txt
```

 - ## 3️ Run Streamlit app
```
 streamlit run app/streamlit_app.py
```
---
# Data Sources

- Historical groundwater level data of Jaipur district wells from WRIS PORTAL

 - groundwater refill water patterns using spatial raining

- Well location metadata (latitude & longitude)
 
