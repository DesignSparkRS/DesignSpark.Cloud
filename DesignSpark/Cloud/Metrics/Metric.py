# Copyright (c) 2022 RS Components Ltd
# SPDX-License-Identifier: MIT License

'''
DesignSpark Cloud metrics interface
'''

import requests
import snappy
from . import prometheus_pb2
from datetime import datetime
from urllib.parse import urlparse
import calendar
import copy
from prometheus_api_client import PrometheusConnect
from . import validator

class Metric:
    """ This class handles interfacing with the DesignSpark Cloud.

    :param cloudType: A string containing either "prometheus" or "influxdb". Defaults to "prometheus".
    :type cloudType: string, optional

    :param cloudConfig: A dictionary containing the following configuration data:

    .. code-block:: text

        {
            "instance": "123456",
            "key": "authentication key",
            "url": "DSM URL",
            "bucket": "InfluxDB bucket name"
        }

    .. note:: The "bucket" key is only necessary when cloudType is set to "influxdb"

    :type cloudConfig: dict
    """
    def __init__(self, cloudType="prometheus", cloudConfig=None):
        if cloudConfig == None:
            raise Exception("No cloud connection configuration provided")
        else:
            if cloudType == "prometheus":
                self.cloudType = "prometheus"
                self.cloudConfig = cloudConfig
                self.validator = validator.Validator("prometheus")
                self.validator.validateCloudConfig(cloudConfig)
            elif cloudType == "influxdb":
                raise Exception("InfluxDB support not implemented")
                self.cloudType = "influxdb"
                self.validator = validator.Validator("influxdb")

    def __dt2ts(self, dt):
        """Converts a datetime object to UTC timestamp
        naive datetime will be considered UTC.
        """
        return calendar.timegm(dt.utctimetuple())

    def write(self, data):
        """ Writes a single data point to the specfied cloud.

        :param data: A dictionary containing the metric data to be published. Labels are optional and can have multiple, 'name' and 'value' keys are mandatory.

        .. code-block:: text

            {
                "name": "metric name",
                "value": 123,
                "label1": "a label",
                "label2": "another label"
            }

        :return: True on successful publish, a list containing False, status code and reason on unsuccessful publish.
        :rtype: boolean, list

        """
        if self.cloudType == "prometheus":
            self.validator.validateMetricNames(data)

            writeRequest = prometheus_pb2.WriteRequest()
            series = writeRequest.timeseries.add()

            dataCopy = copy.deepcopy(data)

            for key, value in dataCopy.items():
                # "value" and "name" should be reserved keywords to add the actual metric name and value
                if key == "name":
                    label = series.labels.add()
                    label.name = "__name__"
                    label.value = str(value)
                elif key == "value":
                    sample = series.samples.add()
                    sample.value = int(value)
                    sample.timestamp = self.__dt2ts(datetime.utcnow()) * 1000
                elif key not in ['name', 'value']:
                    label = series.labels.add()
                    label.name = key
                    label.value = str(value)

            uncompressedRequest = writeRequest.SerializeToString()
            compressedRequest = snappy.compress(uncompressedRequest)

            username = self.cloudConfig["instance"]
            password = self.cloudConfig["key"]
            baseUrl = self.cloudConfig["url"]
            splitUrl = urlparse(baseUrl)

            # Rebuild URL
            url = "{scheme}://{user}:{password}@{url}{path}/api/prom/push".format(scheme=splitUrl.scheme, \
                user=username, \
                password=password, \
                url=splitUrl.netloc, \
                path=splitUrl.path)

            headers = {
                "Content-Encoding": "snappy",
                "Content-Type": "application/x-protobuf",
                "X-Prometheus-Remote-Write-Version": "0.1.0",
                "User-Agent": "metrics-worker"
            }

            response = requests.post(url, headers=headers, data=compressedRequest)
            # Check for valid success code (not using response.ok as this includes 2xx and 3xx codes)
            if 200 <= response.status_code <= 299:
                return True
            else:
                return False, response.status_code, response.text

        if self.cloudType == "influxdb":
            pass

    def getPrometheusConnect(self):
        """ Helper function that creates an instance of PrometheusConnect.
        
        :return: An instance of PrometheusConnect configured with DesignSpark Cloud connection details
        :rtype: PrometheusConnect

        """

        if self.cloudType != "prometheus":
            raise Exception("Wrong cloud type configured to be able to call getPrometheusConnect")
        else:
            username = self.cloudConfig["instance"]
            password = self.cloudConfig["key"]
            baseUrl = self.cloudConfig["url"]
            splitUrl = urlparse(baseUrl)

            # Rebuild URL
            url = "{scheme}://{user}:{password}@{url}{path}/api/prom".format(scheme=splitUrl.scheme, \
                user=username, \
                password=password, \
                url=splitUrl.netloc, \
                path=splitUrl.path)

            return PrometheusConnect(url=url)