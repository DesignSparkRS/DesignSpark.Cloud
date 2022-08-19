from DesignSpark.Cloud import Metrics
from datetime import datetime, timedelta
from prometheus_api_client import PrometheusConnect, MetricsList

DSM_INSTANCE = ""
DSM_KEY = ""
DSM_URL = ""

m = Metrics.Metric(instance=DSM_INSTANCE, key=DSM_KEY, url=DSM_URL)

reader_uri = m.getReadURI()

reader = PrometheusConnect(reader_uri)

metricData = reader.get_metric_range_data(metric_name="test_metric", start_time=(datetime.now() - timedelta(hours=24, minutes=0)), end_time=datetime.now())

metricList = MetricsList(metricData)

for item in metricList:
	print(item)