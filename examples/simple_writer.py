from DesignSpark.Cloud.Metrics import Metric
import random
import time

DSM_INSTANCE = ""
DSM_KEY = ""
DSM_URL = ""

m = Metric.Metric(cloudConfig={"instance":DSM_INSTANCE, "key":DSM_KEY, "url":DSM_URL})
for x in range(10):
	status = m.write({"name":"test_metric", "value":random.randint(1, 50), "label1":"this_label", "label2":"that_label"})
	if status:
		print("Successfully posted")
	else:
		print("Unsuccessful post, result {}".format(status))
	time.sleep(1)