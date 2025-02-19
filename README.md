# Greenhouse Monitoring System

This project simulates an intelligent greenhouse system where sensors send real-time data to a central gateway using RabbitMQ. The system consists of two main components:

1. `greenhouse.py`: Simulates greenhouse devices (sensors and actuators).
2. `gateway.py`: Receives and processes messages from the sensors.

## Installation

### Prerequisites
Ensure you have the following installed on your system:
- Python 3.x
- RabbitMQ
- Required Python libraries (install using the command below)

```sh
pip install pika protobuf
```

## Usage

### Running RabbitMQ
Start RabbitMQ before running the system.

```sh
sudo systemctl start rabbitmq-server  # For Linux
rabbitmq-server  # For manual startup
```

### Running Sensors
Sensors simulate environmental data and send updates to the gateway. Each sensor runs in a separate terminal.

```sh
python greenhouse.py Sensor <port> <id> <name> <value> <unit>
```

#### Example:

```sh
python greenhouse.py Sensor 50000 1 sensor_temperature 20 °C
python greenhouse.py Sensor 50000 2 sensor_humidity 50 %
python greenhouse.py Sensor 50000 3 sensor_light 60 lux
```

Each sensor publishes data to its respective RabbitMQ queue, updating its value over time.

### Running the Gateway
The gateway listens for messages from sensors and displays the received data.

```sh
python gateway.py
```

#### Example Output:

```sh
[GATEWAY] Waiting messages. Press CTRL+C to quit.
[GATEWAY] Message received from queue queue_sensor_temperature:
  - ID: 1
  - Name: sensor_temperature
  - Value: 20.68 °C
[GATEWAY] Message received from queue queue_sensor_humidity:
  - ID: 2
  - Name: sensor_humidity
  - Value: 48.98 %
[GATEWAY] Message received from queue queue_sensor_light:
  - ID: 3
  - Name: sensor_light
  - Value: 59.45 lux
```

## System Overview

### greenhouse.py
- Implements `Sensor` and `Actuator` classes.
- Sensors continuously update their values and publish status to RabbitMQ queues.
- Uses `protobuf` to serialize sensor data.

### gateway.py
- Listens for messages from predefined sensor queues.
- Parses messages using `protobuf`.
- Displays received sensor data in the terminal.

## Notes
- Actuators are defined but not yet implemented with specific functionality.
- Ensure RabbitMQ is running before executing the scripts.

## Future Improvements
- Implement actuator functionalities.
- Add database storage for sensor data.
- Create a web dashboard for real-time monitoring.

