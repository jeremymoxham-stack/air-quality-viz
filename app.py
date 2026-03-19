import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Global Breath Project", layout="wide")

st.title("🌍 Global Breath Project: 10-Year Air Quality Trends")
st.write("Visualizing PM2.5 and PM10 levels from 2016 to 2026.")

# Sidebar Selection
city = st.sidebar.selectbox("Choose a City", ["Shanghai", "London", "New York", "Delhi", "Rome"])
pollutant = st.sidebar.multiselect("Select Pollutants", ["PM2.5", "PM10"], default=["PM2.5"])

# Generating 10 Years of Historical Data (Phase 2 Simulation)
# This mimics the data we will pull from the API in Phase 3
dates = pd.date_range(start="2016-01-01", end="2026-03-19", freq="M")
data = pd.DataFrame({"Date": dates})

for p in pollutant:
    # Logic: Generally, air quality has been slowly improving in many cities
    base = 50 if p == "PM2.5" else 80
    trend = np.linspace(base, base * 0.6, len(dates)) # Improving trend
    noise = np.random.normal(0, 5, len(dates)) # Monthly fluctuations
    data[p] = trend + noise

# Create the Graph
fig = px.line(data, x="Date", y=pollutant, 
              title=f"Air Quality Trend in {city}",
              labels={"value": "Concentration (µg/m³)", "variable": "Pollutant"},
              template="plotly_dark")

# Add WHO Guideline Line (24-hour mean for PM2.5 is 15)
fig.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="WHO Safety Limit")

st.plotly_chart(fig, use_container_width=True)

st.success(f"Graph loaded for {city}. Students can hover over the lines to see specific monthly data.")
