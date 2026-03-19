import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Global Breath Project", layout="wide")

# 1. API Key Check
if "OPENAQ_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

API_KEY = st.secrets["OPENAQ_API_KEY"]
headers = {"X-API-Key": API_KEY}

st.title("🌍 Global Breath Project: Real-World Data")

# 2. Updated City Selection (Using broad Location IDs)
cities = {
    "London": 159,
    "Delhi": 8118,
    "New York": 6051,
    "Shanghai": 65161
}

city_name = st.sidebar.selectbox("Select a City", list(cities.keys()))
loc_id = cities[city_name]

# 3. Robust Data Fetching
@st.cache_data(ttl=3600)
def get_data(location_id):
    # Step A: Get all sensors for this location
    sensor_url = f"https://api.openaq.org/v3/locations/{location_id}/sensors"
    try:
        r = requests.get(sensor_url, headers=headers)
        if r.status_code != 200: return None
        
        sensors = r.json().get('results', [])
        # Find the PM2.5 sensor
        pm25_sensor = next((s for s in sensors if s['parameter']['name'] == 'pm25'), None)
        
        if pm25_sensor:
            s_id = pm25_sensor['id']
            # Step B: Fetch measurements for that sensor
            # We use the generic /measurements endpoint which is more reliable than /days
            m_url = f"https://api.openaq.org/v3/sensors/{s_id}/measurements"
            params = {"limit": 1000} 
            mr = requests.get(m_url, headers=headers, params=params)
            
            if mr.status_code == 200:
                results = mr.json().get('results', [])
                if results:
                    df = pd.DataFrame(results)
                    # Handle the date nesting in v3
                    df['Date'] = pd.to_datetime(df['period'].apply(lambda x: x['datetimeTo']['local']))
                    # Sort by date so the line graph makes sense
                    df = df.sort_values('Date')
                    return df
        return None
    except:
        return None

# 4. Display Logic
with st.spinner(f"Searching for live sensors in {city_name}..."):
    df = get_data(loc_id)

if df is not None and not df.empty:
    fig = px.line(df, x='Date', y='value', 
                 title=f"Recent PM2.5 Levels: {city_name}",
                 labels={'value': 'PM2.5 (µg/m³)', 'Date': 'Time'},
                 template="plotly_white")
    
    fig.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="WHO Daily Limit")
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"Successfully connected! Showing latest {len(df)} records.")
    st.dataframe(df[['Date', 'value']].tail(10)) # Show a small table for verification
else:
    st.warning(f"⚠️ The sensors in {city_name} are currently not responding to the API request.")
    st.info("Try switching to **London** or **Delhi** - they usually have the most consistent uptime.")

st.caption("Data Source: OpenAQ.org v3 API")
