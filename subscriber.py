import paho.mqtt.client as mqtt
import json
from tkinter import *
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Define MQTT broker parameters
BROKER_HOST = "localhost"
BROKER_PORT = 1883
BROKER_KEEPALIVE = 60

# Define topic for communication between publishers and subscribers
TOPIC = "Room sensors"


class Subscriber:
    def __init__(self, device_id, location):
        self.humidity_bars = None
        self.humidity_data = None
        self.humidity_canvas = None
        self.temp_line = None
        self.temp_canvas = None
        self.temp_data = None
        self.device_id = device_id
        self.location = location
        self.client = mqtt.Client(client_id=self.device_id)
        self.client.connect(BROKER_HOST, BROKER_PORT, BROKER_KEEPALIVE)
        self.root = None
        self.temp_label = None
        self.humidity_label = None
        self.temp_fig = None
        self.humidity_fig = None

    def on_connect(self):
        # Subscribe to the topic on connection
        self.client.subscribe(TOPIC)

    def on_message(self, message):
        # Handle received data
        data = json.loads(message.payload.decode())
        if data["location"] == self.location:
            temp_str = f"Temperature: {data['temperature']}"
            humidity_str = f"Humidity: {data['humidity']}"
            if self.temp_label:
                self.temp_label.config(text=temp_str)
                self.temp_data.append(data['temperature'])
                self.temp_line.set_data(range(len(self.temp_data)), self.temp_data)
                self.temp_fig.canvas.draw()
            if self.humidity_label:
                self.humidity_label.config(text=humidity_str)
                self.humidity_data.append(data['humidity'])
                for i, bar in enumerate(self.humidity_bars):
                    bar.set_height(self.humidity_data[i])
                self.humidity_fig.canvas.draw()
            print(f"{self.device_id} received: {message.payload.decode()}")

    def start(self):
        # Set up the GUI
        self.root = Tk()
        self.root.geometry("700x400")
        self.root.title(f"Subscriber - {self.device_id}")
        self.temp_label = Label(self.root, text="Temperature: N/A")
        self.temp_label.pack()

        self.temp_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.temp_data = []
        self.temp_line, = plt.plot(self.temp_data)
        self.temp_canvas = FigureCanvasTkAgg(self.temp_fig, self.root)
        self.temp_canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)

        self.humidity_label = Label(self.root, text="Humidity: N/A")
        self.humidity_label.pack()

        self.humidity_fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.humidity_data = []
        self.humidity_bars = plt.bar(range(len(self.humidity_data)), self.humidity_data)
        self.humidity_canvas = FigureCanvasTkAgg(self.humidity_fig, self.root)
        self.humidity_canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()

        # Start the GUI loop in a separate thread
        gui_thread = threading.Thread(target=self.root.mainloop)
        gui_thread.start()

        # Start the MQTT loop in a separate thread
        mqtt_thread = threading.Thread(target=self.client.loop_forever)
        mqtt_thread.start()

        # Start the GUI loop in the main thread
        self.root.mainloop()


# Create multiple subscribers
sub1 = Subscriber("sub1", "Kitchen")
sub2 = Subscriber("sub2", "Living Room")
sub3 = Subscriber("sub3", "Bed Room")

# Start the subscribers
t1 = threading.Thread(target=sub1.start)
t2 = threading.Thread(target=sub2.start)
t3 = threading.Thread(target=sub3.start)
t1.start()
t2.start()
t3.start()

plt.show()
