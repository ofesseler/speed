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


def shorten_topic(topic_name):
    return topic_name.split("/")[-1]


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("home/livingroom/temp")
    client.subscribe("home/livingroom/humidity")
    client.subscribe("home/office/temp")
    client.subscribe("home/office/humidity")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    current_time = datetime.datetime.utcnow().isoformat()
    persists(measurement=shorten_topic(msg.topic), fields={"value": float(msg.payload), "location": msg.topic.split("/")[1]}, time=current_time)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(os.getenv("MQTT_SERVER"), int(os.getenv("MQTT_PORT")), int(os.getenv("MQTT_TIMEOUT")))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
