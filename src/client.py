import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import time

# Gateway URL for fetching sensor data and sending actuator commands
GATEWAY_URL = "http://localhost:8001"

# Cache the sensor data to avoid frequent API calls
@st.cache_data(ttl=2)
def get_sensor_data():
    """
    Fetches sensor data from the gateway API.

    Returns:
        dict: A dictionary containing sensor data for temperature, light, and humidity.
              Returns an empty dictionary if the request fails.
    """
    try:
        response = requests.get(f"{GATEWAY_URL}/sensors")
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        print(f"Error to connect to gateway: {e}")
        st.error("Error to connect to gateway.")
        return {}

def plot_sensor_data(sensor_data, sensor_name):
    """
    Plots sensor data using Matplotlib.

    Parameters:
        sensor_data (list): A list of sensor readings.
        sensor_name (str): The name of the sensor (e.g., "Temperature").
    """
    if not sensor_data:
        # Display a warning if no data is available
        st.warning(f"{sensor_name} Unavailable.")
        return
    
    # Extract values and times from the sensor data
    values = [float(sensor["value"]) for sensor in sensor_data]
    times = np.arange(len(sensor_data))
    unit = sensor_data[0]["unit"] if "unit" in sensor_data[0] else ""
    
    # Create a Matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot the sensor data
    ax.plot(times, values, marker='o', linestyle='-', color='b')
    ax.set_ylabel(f"{sensor_name} Value ({unit})", fontsize=15)
    
    # Customize the plot
    ax.grid(True, axis='y')
    ax.set_xlim(0, 20)
    ax.set_xticks([])  # Remove x-axis labels
    ax.tick_params(axis='y', labelsize=12)  # Set y-axis tick font size
    
    # Display the plot in the Streamlit app
    st.pyplot(fig)

def send_actuator_command(actuator_name, value):
    """
    Sends a command to an actuator via the gateway API.

    Parameters:
        actuator_name (str): The name of the actuator (e.g., "actuator_temperature").
        value (float): The value to set on the actuator.
    """
    try:
        # Send a POST request to the actuator endpoint
        response = requests.post(
            f"{GATEWAY_URL}/actuators/{actuator_name}",
            params={"value": value}  # Send the value as a query parameter
        )
        if response.status_code == 200:
            # Display a success message
            st.success(f"Command sent to {actuator_name} with value {value}")
        else:
            # Display an error message if the request fails
            st.error(f"Failed to send command to {actuator_name}. Error: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        st.error(f"Error to connect to gateway: {e}")

# Set the title of the Streamlit app
st.title("🌱 Smart Greenhouse Dashboard")

# Initialize session state for storing sensor data
if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = {}

def update_sensor_data():
    """
    Updates the sensor data in the session state.
    """
    st.session_state.sensor_data = get_sensor_data()

# Update sensor data every 2 seconds
if "last_update" not in st.session_state or time.time() - st.session_state.last_update > 2:
    update_sensor_data()
    st.session_state.last_update = time.time()

# Main UI loop
if "sensor_data" in st.session_state:
    # Temperature Sensor Section
    with st.container():
        st.subheader("🌡️ Temperature Sensor")
        # Plot temperature data
        plot_sensor_data(st.session_state.sensor_data.get('temperature_sensor', []), 'Temperature')
        
        # Temperature control slider and button
        temperature_value = st.slider("Set Temperature", min_value=0, max_value=50, value=25, key="temp_slider")
        if st.button("Send Temperature Command", key="temp_button"):
            send_actuator_command("actuator_temperature", temperature_value)

    # Light Sensor Section
    with st.container():
        st.subheader("💡 Light Sensor")
        # Plot light data
        plot_sensor_data(st.session_state.sensor_data.get('light_sensor', []), 'Light')
        
        # Light control slider and button
        light_value = st.slider("Set Light", min_value=0, max_value=100, value=50, key="light_slider")
        if st.button("Send Light Command", key="light_button"):
            send_actuator_command("actuator_light", light_value)

    # Humidity Sensor Section
    with st.container():
        st.subheader("💧 Humidity Sensor")
        # Plot humidity data
        plot_sensor_data(st.session_state.sensor_data.get('humidity_sensor', []), 'Humidity')
        
        # Humidity control slider and button
        humidity_value = st.slider("Set Humidity", min_value=0, max_value=100, value=50, key="humidity_slider")
        if st.button("Send Humidity Command", key="humidity_button"):
            send_actuator_command("actuator_humidity", humidity_value)

# Refresh the page every 3 seconds
time.sleep(3)
st.rerun()