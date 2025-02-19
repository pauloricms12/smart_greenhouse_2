import pika
from proto import greenhouse_pb2

RABBITMQ_HOST = 'localhost'
SENSOR_QUEUES = ['queue_sensor_temperature', 'queue_sensor_light', 'queue_sensor_humidity']

def callback(ch, method, properties, body):
    status = greenhouse_pb2.DeviceStatus()

    try:
        status.ParseFromString(body)
        
        print(f"[GATEWAY] Message received from queue {method.routing_key}:")
        print(f"  - ID: {status.deviceId}")
        print(f"  - Name: {status.name}")
        print(f"  - Value: {round(status.value, 2)} {status.unit}")

    except Exception as e:
        print(f"[GATEWAY] Error to Parse: {e}")

def start_gateway():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()

    for queue in SENSOR_QUEUES:
        channel.queue_declare(queue=queue, durable=False)
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    print("[GATEWAY] Waiting messages. Press CTRL+C to quit.")
    channel.start_consuming()  

if __name__ == "__main__":
    start_gateway()
