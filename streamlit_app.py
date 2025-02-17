import streamlit as st

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": [53.8683],
	"longitude": [8.699],
	"hourly": "wind_speed_120m",
	"wind_speed_unit": "ms",
	"start_date": "2025-02-08",
	"end_date": "2025-02-23"
}

st.title("🎈 Open Meteo Test")
st.write(
    "Just an example, how to retrieve data from OpenMeteo and display it as a graph."
    "Here we take the wind speed in 120 meter hight for northern germany coast side (Cuxhaven)."
)

responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")


# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
#st.write(hourly)
hourly_wind_speed_120m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["wind_speed_120m"] = hourly_wind_speed_120m

hourly_dataframe = pd.DataFrame(data = hourly_data)

st.line_chart(data=hourly_dataframe, x="date")

st.write(hourly_dataframe)
