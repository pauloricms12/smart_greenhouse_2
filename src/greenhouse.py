import argparse
import pika
import time
from proto import greenhouse_pb2
import threading
import random

RABBITMQ_HOST = 'localhost'

class Device:
    def __init__(self, id: int, name: str, value: float, unit: str) -> None:
        self.id = id
        self.name = name
        self.value = value
        self.unit = unit


class Sensor(Device):
    def __init__(self, id: int, name: str, value: float, unit: str) -> None:
        super().__init__(id, name, value, unit)

    def update_values(self):
        while True:
            self.value += random.normalvariate(0, 1)
            self.value = round(self.value, 2)
            time.sleep(5)

    def publish_status(self, queue_name):
        while True:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
                channel = connection.channel()
                channel.queue_declare(queue=queue_name)

                status = greenhouse_pb2.DeviceStatus(
                    deviceId=self.id,
                    name=self.name,
                    value=self.value,
                    unit=self.unit
                )
                
                channel.basic_publish(exchange='', routing_key=queue_name, body=status.SerializeToString())
                print(f"[{self.name}] Sent Status:\n{status}{queue_name=}\n\n")

                connection.close()
                time.sleep(2)

            except Exception as e:
                print(f"Error to connect to RabbitMQ: {e}")
                time.sleep(5) 


class Actuator(Device):
    def __init__(self, id: int, name: str, value: float, unit: str) -> None:
        super().__init__(id, name, value, unit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a greenhouse device.")
    parser.add_argument("type", choices=["Sensor", "Actuator"], help="Device type")
    parser.add_argument("port", type=int, help="Port number")
    parser.add_argument("id", type=int, help="Device ID")
    parser.add_argument("name", type=str, help="Device name")
    parser.add_argument("value", type=float, help="Initial Value")
    parser.add_argument("unit", type=str, help="Unit of measurement")
    args = parser.parse_args()

    if args.type == "Sensor":
        device = Sensor(id=args.id, name=args.name, unit=args.unit, value=args.value)

        threading.Thread(target=device.update_values).start()
        threading.Thread(target=device.publish_status, args=(f"queue_{args.name}",)).start()

        while True:
            time.sleep(1)

    else:
        device = Actuator(id=args.id, name=args.name, unit=args.unit, value=args.value)
