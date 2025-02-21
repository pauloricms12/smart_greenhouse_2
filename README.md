# Greenhouse Monitoring System

This project simulates an intelligent greenhouse system where sensors send real-time data to a central gateway using RabbitMQ. The system consists of three main components:

1. `greenhouse.py`: Simulates greenhouse devices (sensors and actuators).
2. `gateway.py`: Receives and processes messages from the sensors.
3. `dashboard.py`: A Streamlit-based web interface for monitoring sensor data and controlling actuators.

## Installation

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.x
- RabbitMQ
- Required Python libraries (install using the command below)

```sh
pip install -r requirements.txt
```

## Running RabbitMQ

Start RabbitMQ before running the system:

```sh
sudo systemctl start rabbitmq-server  # For Linux
rabbitmq-server  # For manual startup
```

## Running Sensors

Sensors simulate environmental data and send updates to the gateway. Each sensor runs in a separate terminal.

```sh
python greenhouse.py Temperature 1 20 °C 50051
python greenhouse.py Light 1 60 lux 50052
python greenhouse.py Humidity 1 50 % 50053
```

Each sensor publishes data to its respective RabbitMQ queue, updating its value over time.

## Running the Gateway

The gateway listens for messages from sensors and displays the received data.

```sh
python gateway.py
```

### Example Output:

```sh
[GATEWAY] Waiting for messages. Press CTRL+C to quit.
[GATEWAY] Message received from queue queue_temperature:
  - ID: 1
  - Name: temperature_sensor
  - Value: 20.68 °C
[GATEWAY] Message received from queue queue_humidity:
  - ID: 2
  - Name: humidity_sensor
  - Value: 48.98 %
[GATEWAY] Message received from queue queue_light:
  - ID: 3
  - Name: light_sensor
  - Value: 59.45 lux
```

## Running the Streamlit Dashboard Client

The Streamlit dashboard provides a web interface for monitoring sensor data and sending actuator commands.

```sh
streamlit run client.py
```

### Features:
- Real-time visualization of temperature, humidity, and light sensor data.
- Ability to send control commands to actuators.
- Automatic data refresh every few seconds.

## System Overview

### `greenhouse.py`
- Implements `Sensor` and `Actuator` classes.
- Sensors continuously update their values and publish status to RabbitMQ queues.
- Uses `protobuf` to serialize sensor data.

### `gateway.py`
- Listens for messages from predefined sensor queues.
- Parses messages using `protobuf`.
- Displays received sensor data in the terminal.

### `client.py`
- Fetches sensor data from the gateway.
- Visualizes sensor readings using Matplotlib.
- Allows users to control actuators via an intuitive web interface.

