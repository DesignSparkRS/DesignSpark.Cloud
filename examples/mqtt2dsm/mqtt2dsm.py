from DesignSpark.Cloud.Metrics import Metric
import json
import paho.mqtt.client as mqtt
import copy

CONFIG_FILE = "config.json"
TOPICS_CONFIG = {}

PROMETHEUS_CONFIG = {}

client = mqtt.Client()

def mqtt_connect(client, userdata, flags, rc):
	global TOPICS_CONFIG
	print("Successfully connected to MQTT broker")

	topics = list(TOPICS_CONFIG.keys())

	# Subscribe method expects a list of tuples containing (topic, QoS)
	client.subscribe([(topic, 0) for topic in topics])

	print("Successfully subscribed to all topics")

def mqtt_message(client, userdata, msg):
	global TOPICS_CONFIG
	payload = msg.payload
	print("Received MQTT message from topic {} with payload {}".format(msg.topic, payload))

	if msg.topic in TOPICS_CONFIG.keys():
		metricsData = copy.deepcopy(TOPICS_CONFIG[msg.topic])

		if "labels" in metricsData:
			labelData = metricsData["labels"]
		else:
			labelData = {}

		metricName = metricsData.pop("metric")

		prometheusData = {"name": metricName, "value": payload}
		prometheusData.update(labelData)

		status = writer.write(prometheusData)

		if status:
			print("Successfully published to Prometheus")
		else:
			print("Error publishing! Reason {}".format(status))


def main():
	global PROMETHEUS_CONFIG, TOPICS_CONFIG, MQTT_CONFIG, writer
	client.on_connect = mqtt_connect
	client.on_message = mqtt_message

	with open(CONFIG_FILE) as fileHandle:
		fileData = fileHandle.read()

	configData = json.loads(fileData)

	PROMETHEUS_CONFIG = configData['dsm']
	TOPICS_CONFIG = configData['topics']
	MQTT_CONFIG = configData['mqtt']

	writer = Metric.Metric(cloudConfig=PROMETHEUS_CONFIG)

	if "username" and "password" in MQTT_CONFIG.items():
		client.username_pw_set(MQTT_CONFIG["username"], MQTT_CONFIG["password"])

	client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], 60)

	client.loop_forever()

if __name__ == '__main__':
	main()