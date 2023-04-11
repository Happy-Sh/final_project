import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime
from threading import Thread

# Define MQTT broker parameters
BROKER_HOST = "localhost"
BROKER_PORT = 1883
BROKER_KEEPALIVE = 60

# Define topic for communication between publishers and subscribers
TOPIC = "Room sensors"


# Define a class for the publisher
class Publisher:
    def __init__(self, device_id, location):
        self.device_id = device_id
        self.location = location
        self.client = mqtt.Client(client_id=self.device_id)
        self.client.connect(BROKER_HOST, BROKER_PORT, BROKER_KEEPALIVE)

    def generate_data(self):
        # Generate random data
        data = {
            "timestamp": str(datetime.now()),
            "location": self.location,
            "temperature": random.randint(20, 30),
            "humidity": random.randint(40, 60),
        }
        return json.dumps(data)

    def start(self):
        # Send data at regular intervals
        while True:
            try:
                # Generate and publish data
                data = self.generate_data()
                self.client.publish(TOPIC, data)
                print(f"{self.device_id} published: {data}")
            except:
                pass
            time.sleep(5)


# Create and start three publishers
pub1 = Publisher("pub1", "Kitchen")
pub2 = Publisher("pub2", "Living Room")
pub3 = Publisher("pub3", "Bed Room")
Thread(target=pub1.start).start()
Thread(target=pub2.start).start()
Thread(target=pub3.start).start()
