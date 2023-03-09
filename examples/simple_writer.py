from DesignSpark.Cloud import Metrics
import random
import time

DSM_INSTANCE = ""
DSM_KEY = ""
DSM_URL = ""

m = Metrics.Metric(instance=DSM_INSTANCE, key=DSM_KEY, url=DSM_URL)
for x in range(10):
	status = m.write({"name":"test_metric", "value":random.randint(1, 50), "label1":"this_label", "label2":"that_label"})
	if status == True:
		print("Successfully posted")
	elif status is not True:
		print("Unsuccessful post, result {}".format(status))
	time.sleep(1)