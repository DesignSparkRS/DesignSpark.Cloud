# Copyright (c) 2022 RS Components Ltd
# SPDX-License-Identifier: MIT License

'''
Validator helper class
'''

import re

class Validator:
	def __init__(self, validatorType):
		if validatorType == "prometheus" or validatorType == "influxdb":
			self.validatorType = validatorType
		else:
			raise Exception("Invalid validator type provided")

	def validateMetricNames(self, dataDict):
		""" Function to check metric names/labels to ensure they're compliant with Prometheus or InfluxDB naming schemes
		"""

		# Compile appropriate regex
		if self.validatorType == "prometheus":
			keyRegex = re.compile('^[a-zA-Z0-9_]+$')
		elif self.validatorType == "influxdb":
			pass

		if self.validatorType == "prometheus":
			if "value" not in dataDict:
				raise Exception("Missing value key in data")
			if "name" not in dataDict:
				raise Exception("Missing name key in data")

		for key, value in dataDict.items():
			if self.validatorType == "prometheus":

				# Names starting with double underscore are reserved for Prometheus internal use
				if key[0:2] == "__":
					raise Exception("Double underscore metric names and labels are invalid, see https://prometheus.io/docs/concepts/data_model/")

				regexMatch = keyRegex.match(key)

				# Key name contains invalid characters
				if regexMatch == None:
					raise Exception("Metric name or label key contains invalid characters, see https://prometheus.io/docs/concepts/data_model/")

				# Check key values do not contain spaces
				regexMatch = re.search('\s', str(value))

				# Value contains invalid characters
				if regexMatch is not None:
					raise Exception("Metric name or label value contains space character")

			if self.validatorType == "influxdb":

				# Check that metric name is not in the list of InfluxDB reserved keywords
				if key in ['and', 'import', 'not', 'return', 'option', 'test', 'empty', 'in', 'or', 'package', 'builtin']:
					raise Exception("Metric name/label contains reserved keyword, see https://docs.influxdata.com/flux/v0.x/spec/lexical-elements/#keywords")


	def validateCloudConfig(self, cloudConfig):
		""" Function to check cloud configuration has required keys
		"""

		if self.validatorType == "prometheus":
			if "instance" not in cloudConfig:
				raise Exception("Missing DSM instance key")
			elif cloudConfig["instance"] == "":
				raise Exception("Empty DSM instance key")
			if "key" not in cloudConfig:
				raise Exception("Missing DSM authentication key")
			elif cloudConfig["key"] == "":
				raise Exception("Empty DSM authentication key")
			if "url" not in cloudConfig:
				raise Exception("Missing DSM server URL key")
			elif cloudConfig["url"] == "":
				raise Exception("Empty DSM server URL key")

		if self.validatorType == "influxdb":
			if "instance" not in cloudConfig:
				raise Exception("Missing InfluxDB instance key")
			if "key" not in cloudConfig:
				raise Exception("Missing InfluxDB authentication key")
			if "url" not in cloudConfig:
				raise Exception("Missing InfluxDB server URL key")
			if "bucket" not in cloudConfig:
				raise Exception("Missing InfluxDB bucket key")