import pyvisa
import time
from DesignSpark.Cloud import Metrics
import argparse
import logging

def main():
	logging.basicConfig(level=logging.INFO)
	parser = argparse.ArgumentParser(
		prog = 'BatteryTester',
		description = "Tests a battery using the RS-KEL103 electronic load connected over serial, publishes stats to DesignSpark Cloud")

	parser.add_argument('-d', '--device', type=str, help="PyVISA device string") # PyVISA device string
	parser.add_argument('-b', '--baud', type=int, help="PyVISA device baud rate")
	parser.add_argument('-c', '--capacity', type=int, help="The battery capacity in Ah")
	parser.add_argument('-a', '--amperage', type=float, help="The battery discharge rate in A")
	parser.add_argument('-v', '--voltage', type=float, help="The battery cutoff voltage")
	parser.add_argument('-t', '--time', type=int, help="Discharge cutoff time in minutes")
	parser.add_argument('-i', '--instance', type=str, help="DesignSpark Metrics instance")
	parser.add_argument('-u', '--url', type=str, help="DesignSpark Metrics URL")
	parser.add_argument('-k', '--key', type=str, help="DesignSpark Metrics key")
	parser.add_argument('-n', '--name', type=str, help="Battery name for label on dashboard", default="battery")

	args = parser.parse_args()

	try:
		rm = pyvisa.ResourceManager('@py')
		load = rm.open_resource(args.device)
		load.baud_rate = args.baud
		device_idn = load.query('*IDN?')
		logging.info("Device identifier: {}".format(device_idn[:-1]))
	except Exception as e:
		logging.error("Could not establish device connection, reason {}".format(e))
		exit()

	try:
		m = Metrics.Metric(instance=args.instance, key=args.key, url=args.url)
	except Exception as e:
		logging.error("Could not start DesignSpark Metrics, reason {}".format(e))

	try:
		batt_string = f":BATT 1,{args.amperage + 3}A,{args.amperage}A,{args.voltage}V,{args.capacity}AH,{args.time}M"
		logging.info("Setting battery mode to {}".format(batt_string))
		load.write(batt_string)
		time.sleep(1)
		load.write(':RCL:BATT 1')
		time.sleep(1)
		logging.info("Turning on input")
		load.write(':INP ON')
	except Exception as e:
		logging.error("Failed configuring and enabling instrument, reason {}".format(e))

	while load.query(':INP?') == 'ON\n':
		capacity_list = []
		voltage_list = []
		current_list = []
		for x in range(60):
			if load.query(':INP?') == 'ON\n':
				batt_capacity = float(load.query(':BATT:CAP?')[:-3])
				capacity_list.append(batt_capacity)
				batt_time = float(load.query(':BATT:TIM?')[:-2])
				batt_voltage = round(float(load.query(':MEAS:VOLT?')[:-2]), 2)
				voltage_list.append(batt_voltage)
				batt_current = round(float(load.query(':MEAS:CURR?')[:-2]), 2)
				current_list.append(batt_current)

				batt_mins = int((batt_time * 60) % 60)
				batt_secs = int((batt_time * 3600) % 60)
				logging.info("Capacity: {}Ah, voltage: {}, current: {}, time: {}:{}".format(batt_capacity, batt_voltage, batt_current, batt_mins, batt_secs))
				time.sleep(1)
			else:
				break

		# Publish metrics every minute
		if load.query(':INP?') == 'ON\n':
			capacity = sum(capacity_list) / len(capacity_list)
			status = m.write({"name":"batt_capacity", "value":capacity, "battery_name":args.name})
			if status:
				logging.info("Successfully published capacity to Prometheus")
			else:
				logging.error("Error publishing! Reason {}".format(status))

			voltage = sum(voltage_list) / len(voltage_list)
			status = m.write({"name":"batt_voltage", "value":voltage, "battery_name":args.name})
			if status:
				logging.info("Successfully published voltage to Prometheus")
			else:
				logging.error("Error publishing! Reason {}".format(status))

			current = sum(current_list) / len(current_list)
			status = m.write({"name":"batt_current", "value":current, "battery_name":args.name})
			if status:
				logging.info("Successfully published current to Prometheus")
			else:
				logging.error("Error publishing! Reason {}".format(status))



	batt_capacity = float(load.query(':BATT:CAP?')[:-3])
	batt_time = float(load.query(':BATT:TIM?')[:-2])
	batt_mins = int(batt_time)
	batt_secs = int((batt_time * 60) % 60)

	status = m.write({"name":"batt_capacity", "value":capacity, "battery_name":args.name})
	if status:
		logging.info("Successfully published capacity to Prometheus")
	else:
		logging.error("Error publishing! Reason {}".format(status))

	status = m.write({"name":"batt_time", "value":batt_mins, "battery_name":args.name})
	if status:
		logging.info("Successfully published total minutes to Prometheus")
	else:
		logging.error("Error publishing! Reason {}".format(status))

	logging.info("Discharge finished!")
	logging.info("Capacity: {}Ah, time: {}m {}s".format(batt_capacity, batt_mins, batt_secs))

if __name__ == '__main__':
	main()