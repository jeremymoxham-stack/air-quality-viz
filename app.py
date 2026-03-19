import streamlit as st
import pandas as pd
import requests

st.title("🌍 Global Breath Project: Phase 1")
st.subheader("Testing Air Quality Data Connection")

# A small list of cities to test the connection
city = st.selectbox("Select a city to test:", ["Shanghai", "London", "New York", "Delhi"])

# OpenAQ API Call (Fetching the most recent PM2.5 measurement)
url = f"https://api.openaq.org/v2/latest?city={city}&parameter=pm25"

if st.button('Fetch Latest Data'):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            # Pulling out the measurement and date
            measurements = data['results'][0]['measurements']
            df = pd.DataFrame(measurements)
            st.success(f"Successfully fetched data for {city}!")
            st.write(df)
        else:
            st.warning("No recent data found for this city.")
    else:
        st.error("Failed to connect to the OpenAQ database.")

st.info("Next Step: We will add the 10-year historical graph logic!")
