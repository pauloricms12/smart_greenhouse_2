from fastapi import FastAPI, HTTPException
import pika
import threading
import grpc
import time
from collections import deque
from proto import greenhouse_pb2
from proto import greenhouse_pb2_grpc
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# RabbitMQ host address
RABBITMQ_HOST = "localhost"

# List of RabbitMQ queues for sensor data
SENSOR_QUEUES = ["queue_sensor_temperature", "queue_sensor_light", "queue_sensor_humidity"]

# Timeout for sensor updates (in seconds)
TIMEOUT_SENSOR = 10

# Deques to store the latest sensor data (max length = 20)
temp_sensor = deque(maxlen=20)
light_sensor = deque(maxlen=20)
humd_sensor = deque(maxlen=20)

# Dictionary to track the last update time for each sensor
last_update = {
    "sensor_temperature": time.time(),
    "sensor_light": time.time(),
    "sensor_humidity": time.time(),
}

# Dictionary mapping actuator names to their respective gRPC server ports
ACTUATOR_PORTS = {
    "actuator_temperature": 50051,
    "actuator_light": 50052,
    "actuator_humidity": 50053,
}

def consume_sensors():
    """
    Consumes messages from RabbitMQ queues and updates the sensor data.
    This function runs in a separate thread.
    """
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        
        def callback(ch, method, properties, body):
            """
            Callback function to process messages received from RabbitMQ.

            Parameters:
                ch: The channel object.
                method: The method frame.
                properties: Message properties.
                body: The message body (serialized protobuf).
            """
            status = greenhouse_pb2.DeviceStatus()
            try:
                # Parse the message body into a DeviceStatus protobuf object
                status.ParseFromString(body)

                # Print the received message
                print(f"[GATEWAY] Message received from queue {method.routing_key}:")
                print(f"  - ID: {status.deviceId}")
                print(f"  - Name: {status.name}")
                print(f"  - Value: {round(status.value, 2)} {status.unit}")

                # Create a dictionary with the sensor data
                sensor_info = {
                    "id": status.deviceId,
                    "value": f"{round(status.value, 2)}",
                    "unit":  f"{status.unit}",
                    "name": status.name
                }

                # Update the last update time for the sensor
                last_update[status.name] = time.time()

                # Append the sensor data to the appropriate deque
                if status.name == "sensor_temperature":
                    temp_sensor.append(sensor_info)
                elif status.name == "sensor_light":
                    light_sensor.append(sensor_info)
                elif status.name == "sensor_humidity":
                    humd_sensor.append(sensor_info)

            except Exception as e:
                # Handle errors during message parsing
                print(f"Error parsing message: {e}")
        
        # Declare and consume messages from each queue
        for queue in SENSOR_QUEUES:
            channel.queue_declare(queue=queue, durable=False)
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        
        print("[GATEWAY] Listening for sensor updates...")
        channel.start_consuming()  # Start consuming messages
    except Exception as e:
        # Handle RabbitMQ connection errors
        print(f"Error to connect to RabbitMQ: {e}")

def monitor_last_update():
    """
    Monitors the last update time for each sensor and clears the data if a timeout occurs.
    This function runs in a separate thread.
    """
    global last_update

    while True:
        for sensor_name, last_time in last_update.items():
            # Check if the sensor has timed out
            if time.time() - last_time > TIMEOUT_SENSOR:
                print(f"[WARNING] {sensor_name} except timeout: {TIMEOUT_SENSOR}sec")
                # Clear the sensor data if a timeout occurs
                if sensor_name == "sensor_temperature":
                    temp_sensor.clear()
                elif sensor_name == "sensor_light":
                    light_sensor.clear()
                elif sensor_name == "sensor_humidity":
                    humd_sensor.clear()
                
                # Reset the last update time
                last_update[sensor_name] = time.time()

        # Wait 10 seconds before the next check
        time.sleep(10)

def send_actuator_command(actuator_name: str, value: float):
    """
    Sends a command to an actuator via gRPC.

    Parameters:
        actuator_name (str): The name of the actuator (e.g., "actuator_temperature").
        value (float): The value to set on the actuator.

    Returns:
        str: A success message or an error message.
    """
    if actuator_name not in ACTUATOR_PORTS:
        raise ValueError(f"Actuator '{actuator_name}' not found.")

    port = ACTUATOR_PORTS[actuator_name]

    try:
        # Connect to the gRPC server
        with grpc.insecure_channel(f"localhost:{port}") as channel:
            stub = greenhouse_pb2_grpc.ActuatorServiceStub(channel)
            # Create a gRPC request
            request = greenhouse_pb2.ActuatorRequest(value=value)
            # Call the setValue method on the actuator
            response = stub.setValue(request)
            return response.success

    except Exception as e:
        # Handle gRPC communication errors
        print(f"Error to send command to {actuator_name}: {e}")
        return "Error to communicate with actuator"

def handle_client_request(actuator_name: str, value: float):
    """
    Handles a client request to control an actuator.

    Parameters:
        actuator_name (str): The name of the actuator.
        value (float): The value to set on the actuator.

    Returns:
        dict: A dictionary containing the status or an error message.
    """
    if not isinstance(value, (int, float)):
        return {"error": "O valor deve ser um número."}
    
    try:
        # Send the command to the actuator
        result = send_actuator_command(actuator_name, value)
        return {"status": result}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Intern Error to process request. {e}"}

@app.get("/sensors")
def get_sensors():
    """
    Returns the latest sensor data.

    Returns:
        dict: A dictionary containing the latest data for each sensor.
    """
    return {
            "temperature_sensor": list(temp_sensor),
            "light_sensor": list(light_sensor),
            "humidity_sensor": list(humd_sensor)
    }

@app.post("/actuators/{actuator_name}")
def control_actuator(actuator_name: str, value: float):
    """
    Handles a POST request to control an actuator.

    Parameters:
        actuator_name (str): The name of the actuator.
        value (float): The value to set on the actuator.

    Returns:
        dict: A dictionary containing the status or an error message.
    """
    response = handle_client_request(actuator_name, value)
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    return response


if __name__ == "__main__":
    # Start threads for consuming sensor data and monitoring timeouts
    threading.Thread(target=consume_sensors).start()
    threading.Thread(target=monitor_last_update).start()

    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8001)