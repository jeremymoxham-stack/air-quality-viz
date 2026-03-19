import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Real-World Air Quality", layout="wide")

# Access the secret key we just saved
API_KEY = st.secrets["OPENAQ_API_KEY"]

st.title("🌍 Global Breath Project: Real 10-Year Data")

# Mapping common cities to their OpenAQ Location IDs (Example IDs)
city_map = {
    "Shanghai": 65161, 
    "London": 2341, 
    "New York": 6051, 
    "Delhi": 8118
}

city_name = st.sidebar.selectbox("Select City", list(city_map.keys()))
location_id = city_map[city_name]

st.sidebar.info("Fetching data from OpenAQ API...")

@st.cache_data(ttl=3600)
def fetch_historical_data(loc_id):
    # Using the 'years' endpoint for a 10-year overview
    url = f"https://api.openaq.org/v3/locations/{loc_id}/years"
    headers = {"X-API-Key": API_KEY}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json().get('results', [])
        # Processing results into a DataFrame
        df = pd.DataFrame(results)
        return df
    else:
        return None

data = fetch_historical_data(location_id)

if data is not None and not data.empty:
    # Creating a clean time-series
    fig = px.bar(data, x='year', y='value', 
                 title=f"Annual Average PM2.5 in {city_name}",
                 labels={'year': 'Year', 'value': 'Avg Concentration (µg/m³)'},
                 color='value', color_continuous_scale='Reds')
    
    fig.add_hline(y=5, line_dash="dash", line_color="green", annotation_text="WHO Annual Target (5 µg/m³)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Could not fetch real-time data. Check your API key or city ID.")

st.write("---")
st.caption("Data provided by OpenAQ.org - Open-source air quality monitoring.")
