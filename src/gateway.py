from fastapi import FastAPI
import pika
from proto import greenhouse_pb2
import threading
from collections import deque
import uvicorn


app = FastAPI()
RABBITMQ_HOST = "localhost"
SENSOR_QUEUES = ["queue_sensor_temperature", "queue_sensor_light", "queue_sensor_humidity"]

temp_sensor = deque(maxlen=20)
light_sensor = deque(maxlen=20)
humd_sensor = deque(maxlen=20)

def consume_sensors():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        
        def callback(ch, method, properties, body):
            status = greenhouse_pb2.DeviceStatus()
            try:
                status.ParseFromString(body)

                print(f"[GATEWAY] Message received from queue {method.routing_key}:")
                print(f"  - ID: {status.deviceId}")
                print(f"  - Name: {status.name}")
                print(f"  - Value: {round(status.value, 2)} {status.unit}")

                sensor_info = {
                    "id": status.deviceId,
                    "value": f"{round(status.value, 2)}",
                    "unit":  f"{status.unit}",
                    "name": status.name
                }

                if status.name == "sensor_temperature":
                    temp_sensor.append(sensor_info)
                elif status.name == "sensor_light":
                    light_sensor.append(sensor_info)
                elif status.name == "sensor_humidity":
                    humd_sensor.append(sensor_info)

            except Exception as e:
                print(f"Error parsing message: {e}")
        
        for queue in SENSOR_QUEUES:
            channel.queue_declare(queue=queue, durable=False)
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        
        print("[GATEWAY] Listening for sensor updates...")
        channel.start_consuming()
    except Exception as e:
        print(f"Error to connect to RabbitMQ")

@app.get("/sensors")
def get_sensors():
    return {
            "temperature_sensor": list(temp_sensor),
            "light_sensor": list(light_sensor),
            "humidity_sensor": list(humd_sensor)
    }
if __name__ == "__main__":
    threading.Thread(target=consume_sensors, daemon=True).start()

    uvicorn.run(app, host="0.0.0.0", port=8001)
