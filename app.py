import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Global Breath: 10-Year Trends", layout="wide")

if "OPENAQ_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

API_KEY = st.secrets["OPENAQ_API_KEY"]
headers = {"X-API-Key": API_KEY}

st.title("🌍 Global Breath: 10-Year Historical Analysis")

cities = {
    "London": 159,
    "Delhi": 8118,
    "New York": 6051,
    "Shanghai": 65161
}

city_name = st.sidebar.selectbox("Select a City", list(cities.keys()))
loc_id = cities[city_name]

@st.cache_data(ttl=86400)
def get_decade_data(location_id):
    # 1. Find PM2.5 sensor
    sensor_url = f"https://api.openaq.org/v3/locations/{location_id}/sensors"
    r = requests.get(sensor_url, headers=headers)
    if r.status_code != 200: return None
    
    sensors = r.json().get('results', [])
    pm25_sensor = next((s['id'] for s in sensors if s['parameter']['name'] == 'pm25'), None)
    
    if pm25_sensor:
        # 2. Get yearly averages
        year_url = f"https://api.openaq.org/v3/sensors/{pm25_sensor}/years"
        yr = requests.get(year_url, headers=headers)
        
        if yr.status_code == 200:
            results = yr.json().get('results', [])
            if results:
                df = pd.DataFrame(results)
                
                # THE FIX: Extract the actual year from the 'period' start date
                # Instead of using the 'label' (which was "1year"), we use 'datetimeFrom'
                df['Year'] = pd.to_datetime(df['period'].apply(lambda x: x['datetimeFrom']['local'])).dt.year
                
                # Sort so 2016 comes before 2024
                df = df.sort_values('Year')
                return df
    return None

with st.spinner("Decoding the decade..."):
    df = get_decade_data(loc_id)

if df is not None and not df.empty:
    # Plotting individual bars for each year
    fig = px.bar(df, x='Year', y='value', 
                 title=f"Annual PM2.5 Average: {city_name}",
                 labels={'value': 'Avg PM2.5 (µg/m³)', 'Year': 'Year'},
                 color='value', 
                 color_continuous_scale='Reds')
    
    # Ensure every year shows up on the bottom axis
    fig.update_layout(xaxis_type='category')
    
    # WHO Annual Limit
    fig.add_hline(y=5, line_dash="dash", line_color="green", 
                  annotation_text="WHO Annual Limit (5 µg/m³)")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show the raw numbers for the students to see in a table
    st.write("### Data Table")
    st.dataframe(df[['Year', 'value']].set_index('Year'))
else:
    st.warning("Historical records are still loading for this station. Try London or Delhi!")
