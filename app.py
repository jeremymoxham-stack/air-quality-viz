import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Global Breath: 10-Year Trends", layout="wide")

# API Key Check
if "OPENAQ_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

API_KEY = st.secrets["OPENAQ_API_KEY"]
headers = {"X-API-Key": API_KEY}

st.title("🌍 Global Breath: 10-Year Historical Analysis")
st.markdown("Comparing annual PM2.5 averages to track long-term environmental changes.")

# Verified v3 Location IDs
cities = {
    "London": 159,
    "Delhi": 8118,
    "New York": 6051,
    "Shanghai": 65161
}

city_name = st.sidebar.selectbox("Select a City", list(cities.keys()))
loc_id = cities[city_name]

@st.cache_data(ttl=86400)
def get_10_year_data(location_id):
    # Step 1: Find the PM2.5 sensor ID
    sensor_url = f"https://api.openaq.org/v3/locations/{location_id}/sensors"
    r = requests.get(sensor_url, headers=headers)
    if r.status_code != 200: return None
    
    sensors = r.json().get('results', [])
    pm25_sensor = next((s['id'] for s in sensors if s['parameter']['name'] == 'pm25'), None)
    
    if pm25_sensor:
        # Step 2: Use the /years endpoint for historical averages
        # This is the key to getting a decade of data in one call!
        year_url = f"https://api.openaq.org/v3/sensors/{pm25_sensor}/years"
        yr = requests.get(year_url, headers=headers)
        
        if yr.status_code == 200:
            results = yr.json().get('results', [])
            if results:
                df = pd.DataFrame(results)
                # v3 returns 'value' as the average for that 'period'
                # We extract the year from the period string
                df['Year'] = df['period'].apply(lambda x: x['label'])
                df = df.sort_values('Year')
                return df
    return None

with st.spinner(f"Retrieving decade-long trends for {city_name}..."):
    df = get_10_year_data(loc_id)

if df is not None and not df.empty:
    # Use a Bar Chart for annual averages - it's often clearer for students
    fig = px.bar(df, x='Year', y='value', 
                 title=f"Annual PM2.5 Average: {city_name} (2016-2026)",
                 labels={'value': 'Avg PM2.5 (µg/m³)', 'Year': 'Year'},
                 color='value', color_continuous_scale='Reds')
    
    # WHO Annual Limit is stricter than the daily limit!
    fig.add_hline(y=5, line_dash="dash", line_color="green", 
                  annotation_text="WHO Annual Safety Limit (5 µg/m³)")
    
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"Decade scan complete for {city_name}.")
else:
    st.warning("Historical records for this specific sensor are being migrated. Try London or Delhi!")
