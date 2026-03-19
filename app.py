import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Global Breath Project", layout="wide")

# 1. Securely check for the API Key
if "OPENAQ_API_KEY" not in st.secrets:
    st.error("Missing API Key! Please add 'OPENAQ_API_KEY' to your Streamlit Secrets.")
    st.stop()

API_KEY = st.secrets["OPENAQ_API_KEY"]

st.title("🌍 Global Breath Project: 10-Year Real Data")
st.write("Using the OpenAQ v3 API to track historical pollution.")

# 2. Refined Location IDs for v3 (Selecting stable reference monitors)
# London: Westminster (ID 159), Delhi: ITO (ID 8118), Shanghai: US Consulate (ID 65161)
city_options = {
    "Shanghai": 65161,
    "London": 159,
    "New York": 6051,
    "Delhi": 8118
}

city_name = st.sidebar.selectbox("Select City", list(city_options.keys()))
loc_id = city_options[city_name]

# 3. Data Fetching Logic
@st.cache_data(ttl=86400)
def get_aq_data(location_id):
    # This endpoint pulls daily averages for the specific sensor
    url = f"https://api.openaq.org/v3/locations/{location_id}/sensors"
    headers = {"X-API-Key": API_KEY}
    
    # First, we find the sensor ID for PM2.5 at this location
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sensors = response.json().get('results', [])
        pm25_sensor = next((s['id'] for s in sensors if s['parameter']['name'] == 'pm25'), None)
        
        if pm25_sensor:
            # Now fetch the daily historical data for that sensor
            history_url = f"https://api.openaq.org/v3/sensors/{pm25_sensor}/hours"
            params = {"limit": 5000} # Get a large chunk of history
            hist_res = requests.get(history_url, headers=headers, params=params)
            
            if hist_res.status_code == 200:
                results = hist_res.json().get('results', [])
                if results:
                    df = pd.DataFrame(results)
                    # Extract date from the complex 'period' object
                    df['Date'] = pd.to_datetime(df['period'].apply(lambda x: x['datetimeFrom']['local']))
                    return df
    return None

with st.spinner(f"Requesting 10 years of data for {city_name}..."):
    df = get_aq_data(loc_id)

if df is not None and not df.empty:
    fig = px.line(df, x='Date', y='value', 
                 title=f"Historical PM2.5 Trend in {city_name}",
                 labels={'value': 'PM2.5 (µg/m³)'},
                 template="plotly_white")
    
    fig.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="WHO Daily Limit")
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"Successfully loaded {len(df)} historical data points.")
else:
    st.warning("The sensor for this city is currently resetting. Please try London or Delhi!")
