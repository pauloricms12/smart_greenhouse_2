import argparse
import pika
import time
import threading
import random
import grpc
from concurrent import futures
from proto import greenhouse_pb2, greenhouse_pb2_grpc

# RabbitMQ host address
RABBITMQ_HOST = 'localhost'

class Sensor():
    """
    Represents a sensor in the greenhouse system.
    Simulates sensor behavior by updating its value randomly and publishing its status to a RabbitMQ queue.
    """
    def __init__(self, id: int, name: str, value: float, unit: str) -> None:
        """
        Initializes a sensor with an ID, name, initial value, and unit of measurement.

        Parameters:
            id (int): The unique identifier for the sensor.
            name (str): The name of the sensor (e.g., "sensor_temperature").
            value (float): The initial value of the sensor.
            unit (str): The unit of measurement for the sensor (e.g., "°C").
        """
        self.id = id
        self.name = name
        self.value = value
        self.unit = unit

    def update_values(self):
        """
        Continuously updates the sensor's value by adding a random normal variate (mean=0, standard deviation=0.5) every 5 seconds.
        This simulates real-world sensor behavior.
        """
        while True:
            self.value += random.normalvariate(0, 0.5)  # Add random noise to the value
            self.value = round(self.value, 2)  # Round to 2 decimal places
            time.sleep(5)  # Wait 5 seconds before the next update

    def publish_status(self, queue_name: str):
        """
        Publishes the sensor's status to a RabbitMQ queue every 2 seconds.

        Parameters:
            queue_name (str): The name of the RabbitMQ queue to publish the status to.
        """
        while True:
            try:
                # Connect to RabbitMQ
                connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
                channel = connection.channel()
                channel.queue_declare(queue=queue_name)  # Declare the queue

                # Create a DeviceStatus message
                status = greenhouse_pb2.DeviceStatus(
                    deviceId=self.id,
                    name=self.name,
                    value=self.value,
                    unit=self.unit
                )
                
                # Publish the status to the queue
                channel.basic_publish(exchange='', routing_key=queue_name, body=status.SerializeToString())
                print(f"[{self.name}] Sent Status:\n{status}{queue_name=}\n\n")

                # Close the connection
                connection.close()
                time.sleep(2)  # Wait 2 seconds before the next publish

            except Exception as e:
                # Handle connection errors
                print(f"Error to connect to RabbitMQ: {e}")
                time.sleep(10)  # Wait 10 seconds before retrying

class Actuator(greenhouse_pb2_grpc.ActuatorService):
    """
    Represents an actuator in the greenhouse system.
    Implements the gRPC service to receive commands and update the sensor's value.
    """
    def __init__(self, sensor):
        """
        Initializes the actuator with a sensor.

        Parameters:
            sensor (Sensor): The sensor associated with this actuator.
        """
        self.sensor = sensor

    def setValue(self, request, context):
        """
        Receives a command to set the sensor's value via gRPC.

        Parameters:
            request (greenhouse_pb2.ActuatorRequest): The request containing the new value.
            context: gRPC context.

        Returns:
            greenhouse_pb2.ActuatorResponse: A response indicating success or failure.
        """
        print(f"[{self.sensor.name}] Received command: Set value to {request.value} {self.sensor.unit}")
        self.sensor.value = request.value  # Update the sensor's value
        return greenhouse_pb2.ActuatorResponse(success="Success")  # Return success response
    
def run_actuator_server(actuator, port: int):
    """
    Starts a gRPC server for the actuator.

    Parameters:
        actuator (Actuator): The actuator to be served.
        port (int): The port on which the gRPC server will listen.
    """
    try:
        # Create a gRPC server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        # Add the actuator service to the server
        greenhouse_pb2_grpc.add_ActuatorServiceServicer_to_server(actuator, server)
        # Bind the server to the specified port
        server.add_insecure_port(f"[::]:{port}")
        print(f"[{actuator.sensor.name}] Actuator gRPC Server running on port {port}")
        # Start the server
        server.start()
        # Keep the server running
        server.wait_for_termination()
    except Exception as e:
        # Handle server errors
        print(f"Error starting gRPC server: {e}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Create a greenhouse feature.")
    parser.add_argument("feature", choices=["Temperature", "Light", "Humidity"], help="Feature type")
    parser.add_argument("sensor_id", type=int, help="Sensor ID")
    parser.add_argument("sensor_value", type=float, help="Initial Sensor Value")
    parser.add_argument("sensor_unit", type=str, help="Unit of measurement")
    parser.add_argument("actuator_port", type=int, help="Port for Actuator gRPC")
    args = parser.parse_args()

    # Create the sensor and actuator
    feature_name = f"sensor_{args.feature.lower()}"
    
    sensor = Sensor(id=args.sensor_id, name=feature_name, value=args.sensor_value, unit=args.sensor_unit)
    actuator = Actuator(sensor)

    # Start threads for sensor updates, status publishing, and gRPC server
    threading.Thread(target=sensor.update_values, daemon=True).start()  # Update sensor values
    threading.Thread(target=sensor.publish_status, args=(f"queue_{feature_name}",), daemon=True).start()  # Publish status to RabbitMQ
    threading.Thread(target=run_actuator_server, args=(actuator, args.actuator_port), daemon=True).start()  # Start gRPC server

    # Keep the main program running
    while True:
        time.sleep(1)