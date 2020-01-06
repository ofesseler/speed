import paho.mqtt.client as mqtt
import datetime
import logging
import os
import time
from dotenv import load_dotenv
from influxdb import InfluxDBClient

logging.basicConfig(level=logging.INFO)

current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path="{}/.env".format(current_dir))

influxdb_host = os.getenv("INFLUXDB_HOST")
influxdb_port = os.getenv("INFLUXDB_PORT")
influxdb_database = os.getenv("INFLUXDB_DATABASE")

influx_client = InfluxDBClient(
    host=influxdb_host,
    port=influxdb_port,
    database=influxdb_database
)


def persists(measurement, fields, time):
    logging.info("{} {} {}".format(time, measurement, fields))

    influx_client.write_points([{
        "measurement": measurement,
        "time": time,
        "fields": fields
    }])


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("home/livingroom/temp")
    client.subscribe("home/livingroom/humidity")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    current_time = datetime.datetime.utcnow().isoformat()
    persists(measurement=msg.topic, fields={"value": msg.payload}, time=current_time)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.52", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()