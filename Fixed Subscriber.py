import paho.mqtt.client as mqtt
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

# I wanted to rename this file to something else, but I started working on it, and now I'm too worried it will break something

# Define MQTT broker parameters
BROKER_HOST = "localhost"
BROKER_PORT = 1883
BROKER_KEEPALIVE = 60

# Define topic for communication between publishers and subscribers
TOPIC = "Room sensors"

# Define a class for the subscriber
class Subscriber:
    def __init__(self, topic, location, plot):
        self.topic = topic
        self.location = location
        self.temperature = []
        self.humidity = []
        self.plot = plot

    # When the client successfully connects to the broker
    # userdata and flags are not used, but I think they had to be added
    def on_connect(self, client, userdata, flags, rc):
        # Originally used this for troubleshooting, we may not need it
        print("Connected to MQTT broker with result code " + str(rc))
        client.subscribe(self.topic)

    # Gets called when data is sent from the publisher (through the broker)
    # Once again userdata is not used
    # Neither is client, but I have not changed it as I think it will break something
    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode("utf-8"))
        self.temperature.append(payload["temperature"])
        self.humidity.append(payload["humidity"])
        self.update_plot()

    # Updating the plot with newly received data
    # Only runs once data has been received, so the labels take a second or so to show up
    # Temp and humidity are no long on the x and y-axis, instead they are both on the graph
    # with time as the y-axis
    # Lines never intersect because Temp can't go higher than 30 and humidity can't go lower than 40 (technically this doesn't make sense but it works for what we want)
    # Humidity should be a percentage, but the best I could do was add a percentage sign on the label
    def update_plot(self):
        self.plot.clear()
        # The legend changes location based on the graph (so it doesn't cover the graph)
        # To be honest I have no idea why this works the way it does
        self.plot.plot(self.temperature, label="Temperature")
        self.plot.plot(self.humidity, label="Humidity (%)")
        self.plot.set_xlabel("Time (In Seconds)")
        self.plot.set_ylabel("Value")
        self.plot.set_title(self.location)
        self.plot.legend()
        self.plot.figure.canvas.draw()


def create_plot(root, location):
    # fig an ax are an instances of a matplot class
    # fig and ax are used to represent the entire plot essentially
    # fig for figure and ax for axes respectively
    fig, ax = plt.subplots()
    # I never set a window size so the plots would just make it as big as they need it
    # This just happened to work out honestly
    # As this way the window can be resized manually if need be (literally click and drag)
    canvas = FigureCanvasTkAgg(fig, master=root)
    # Allows the plots to sit together horizontally in the frame rather than vertically
    # Which would cause the window to be too long to display on screen
    canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    return ax

# Create main Tkinter window
root = tk.Tk()
root.title("Sensor Data")

# Create a frame to contain the plots
frame = tk.Frame(root)
frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Create plots for each location and add them to the frame
plot1 = create_plot(frame, "Kitchen")
plot2 = create_plot(frame, "Living Room")
plot3 = create_plot(frame, "Bed Room")

# Create subscribers for each location
# Also assigns the 3 different rooms to each subscriber
# Has to use the TOPIC "room sensors" declared in the publisher and subscriber
sub1 = Subscriber(TOPIC, "Kitchen", plot1)
sub2 = Subscriber(TOPIC, "Living Room", plot2)
sub3 = Subscriber(TOPIC, "Bed Room", plot3)

# Connect subscribers to MQTT broker and start listening for messages
client = mqtt.Client()
client.on_connect = sub1.on_connect
client.on_message = sub1.on_message
client.connect(BROKER_HOST, BROKER_PORT, BROKER_KEEPALIVE)
# Starting separate threads for each subscriber, so they do not interfere with the main loop
client.loop_start()
# Subscribers are identical, didn't see a need to add comments for each one

client2 = mqtt.Client()
client2.on_connect = sub2.on_connect
client2.on_message = sub2.on_message
client2.connect(BROKER_HOST, BROKER_PORT, BROKER_KEEPALIVE)
client2.loop_start()

client3 = mqtt.Client()
client3.on_connect = sub3.on_connect
client3.on_message = sub3.on_message
client3.connect(BROKER_HOST, BROKER_PORT, BROKER_KEEPALIVE)
client3.loop_start()

# Start Tkinter event loop
# The main loop
root.mainloop()
