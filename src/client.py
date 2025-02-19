import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import time

GATEWAY_URL = "http://localhost:8001"

#buscar os dados dos sensores com cache
@st.cache_data(ttl=2) 
def get_sensor_data():
    try:
        response = requests.get(f"{GATEWAY_URL}/sensors")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error to connect to gateway: {e}")
        return {}

def plot_sensor_data(sensor_data, sensor_name):
    if not sensor_data:
        st.warning(f"No data fot {sensor_name}.")
        return
    
    values = [float(sensor["value"]) for sensor in sensor_data]
    times = np.arange(len(sensor_data))
    unit = sensor_data[0]["unit"] if "unit" in sensor_data[0] else ""

    plt.figure(figsize=(10, 5))
    plt.plot(times, values, marker ='o')
    plt.ylabel(f"{sensor_name} Value ({unit})")
    plt.grid(True, axis='y')
    plt.xlim(0, 20)
    plt.xticks([])
    st.pyplot(plt)

st.title("🌱 Smart Greenhouse Dashboard")

temperature_placeholder = st.empty()
light_placeholder = st.empty()
humidity_placeholder = st.empty()

while True:
    sensor_data = get_sensor_data()
    
    with temperature_placeholder.container():
        st.subheader("🌡️ Temperature Sensor")
        plot_sensor_data(sensor_data.get('temperature_sensor', []), 'Temperature')

    with light_placeholder.container():
        st.subheader("💡 Light Sensor")
        plot_sensor_data(sensor_data.get('light_sensor', []), 'Light')

    with humidity_placeholder.container():
        st.subheader("💧 Humidity Sensor")
        plot_sensor_data(sensor_data.get('humidity_sensor', []), 'Humidity')

    time.sleep(2)

