import requests
import streamlit as st
import plotly.express as px


GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"
AIR_POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

AQI_CATEGORIES = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor",
}


def get_api_key():
    """Read the OpenWeather API key from Streamlit secrets."""
    try:
        api_key = st.secrets["OPENWEATHER_API_KEY"]
    except KeyError:
        st.error("OpenWeather API key not found. Please add it to secrets.toml")
        return None

    if not api_key:
        st.error("OpenWeather API key not found. Please add it to secrets.toml")
        return None

    return api_key


def get_city_coordinates(city, api_key):
    """Convert a city name into latitude and longitude."""
    params = {
        "q": city,
        "limit": 1,
        "appid": api_key,
    }

    try:
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        st.error("API failure while fetching city location. Please try again.")
        return None

    if not data:
        st.error("Invalid city. Please enter a valid city name.")
        return None

    city_data = data[0]
    return {
        "name": city_data.get("name", city),
        "country": city_data.get("country", ""),
        "lat": city_data["lat"],
        "lon": city_data["lon"],
    }


def get_air_pollution_data(lat, lon, api_key):
    """Fetch AQI and pollutant data for a latitude/longitude pair."""
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
    }

    try:
        response = requests.get(AIR_POLLUTION_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        st.error("API failure while fetching AQI data. Please try again.")
        return None

    records = data.get("list", [])
    if not records:
        st.warning("No AQI data available for this location.")
        return None

    return records[0]


def prepare_pollutants(components):
    """Pick the pollutants shown in the dashboard."""
    return {
        "PM2.5": components.get("pm2_5", 0),
        "PM10": components.get("pm10", 0),
        "CO": components.get("co", 0),
        "NO2": components.get("no2", 0),
    }


def show_aqi_metrics(aqi, pollutants):
    """Display AQI and pollutant values in Streamlit columns."""
    category = AQI_CATEGORIES.get(aqi, "Unknown")

    aqi_col, pm25_col, pm10_col = st.columns(3)
    with aqi_col:
        st.metric("AQI Index", aqi)
        st.caption(f"Category: {category}")
    with pm25_col:
        st.metric("PM2.5", pollutants["PM2.5"])
    with pm10_col:
        st.metric("PM10", pollutants["PM10"])

    co_col, no2_col = st.columns(2)
    with co_col:
        st.metric("CO", pollutants["CO"])
    with no2_col:
        st.metric("NO2", pollutants["NO2"])


def show_pollutant_chart(pollutants):
    """Draw a Plotly bar chart for pollutant values."""
    chart_data = {
        "Pollutant": list(pollutants.keys()),
        "Value": list(pollutants.values()),
    }

    fig = px.bar(
        chart_data,
        x="Pollutant",
        y="Value",
        color="Pollutant",
        text="Value",
        title="Pollutant Concentrations",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(page_title="AQI Dashboard", page_icon="🌍", layout="wide")

    st.title("🌍 AQI Dashboard")
    st.write("Check real-time air quality data for any city using the OpenWeather Air Pollution API.")

    api_key = get_api_key()
    if api_key is None:
        st.stop()

    city = st.text_input("Enter city name", placeholder="Example: Delhi")
    get_aqi_clicked = st.button("Get AQI")

    if not get_aqi_clicked:
        st.info("Enter a city name and click Get AQI to view air quality data.")
        return

    if not city.strip():
        st.error("Please enter a city name.")
        return

    location = get_city_coordinates(city.strip(), api_key)
    if location is None:
        return

    air_data = get_air_pollution_data(location["lat"], location["lon"], api_key)
    if air_data is None:
        return

    aqi = air_data["main"]["aqi"]
    pollutants = prepare_pollutants(air_data["components"])

    location_label = location["name"]
    if location["country"]:
        location_label = f"{location_label}, {location['country']}"

    st.subheader(f"Air Quality in {location_label}")
    st.caption(f"Latitude: {location['lat']:.4f} | Longitude: {location['lon']:.4f}")

    show_aqi_metrics(aqi, pollutants)
    show_pollutant_chart(pollutants)


if __name__ == "__main__":
    main()
