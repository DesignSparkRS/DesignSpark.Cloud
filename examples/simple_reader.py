from DesignSpark.Cloud.Metrics import Metric
from datetime import datetime
from prometheus_api_client import MetricsList

DSM_INSTANCE = ""
DSM_KEY = ""
DSM_URL = ""

m = Metric.Metric(cloudConfig={"instance":DSM_INSTANCE, "key":DSM_KEY, "url":DSM_URL})

reader = m.getPrometheusConnect()

metricData = reader.get_metric_range_data(metric_name="test_metric", start_time=datetime(2020, 11, 17, 17, 38, 22, 784802), end_time=datetime.now())

metricList = MetricsList(metricData)

for item in metricList:
	print(item)