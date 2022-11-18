Example Applications
====================

``simple_writer.py``
--------------------

This application demonstrates the use of the ``Metric`` module to publish ten random values to the specified DesignSpark Cloud database.

.. literalinclude:: ../examples/simple_writer.py

The application first imports the necessary modules, then configures an instance of the ``Metric`` class with provided DSM credentials. Ten data points with random values and a metric name of "test_metric" are published over the course of ten seconds.

The write function expects a dictionary containing at the bare minimum keys called "name" and "value" which hold the metric name and value. Labels can be included where the key name is the label name — in this example two keys with names "label1" and "label2" are included.

A success message is printed on every successful post, otherwise an error message containing the status from ``metric.write`` is printed.

``simple_reader.py``
--------------------

This application demonstrates the use of the prometheus-api-client_ module to read metrics from DesignSpark Cloud.

.. literalinclude:: ../examples/simple_reader.py

The application imports both the ``Metric`` module and also ``prometheus_api_client`` which provides functions for retrieving and manipulating metrics.

The metric class is instantiated just as before in the ``simple_writer.py`` example, and the function ``metric.getReadURI()`` is called. This function returns a URI that can be passed into an instance of ``prometheus_api_client.prometheus_connect.PrometheusConnect()`` that will then connect to the DesignSpark Cloud using the provided credentials.

A metric series called "test_metric" (the same as what is written in ``simple_writer.py``) is retrieved with a start and end date provided. A number of additional arguments are available, which are described in the prometheus_api_client_ documentation.

``mqtt2dsm.py``
---------------

This application demonstrates a practical use of the Metric module to write data from specified MQTT topics to DesignSpark Cloud, utilising the ``paho-mqtt`` library to connect to a broker.

.. literalinclude:: ../examples/mqtt2dsm/mqtt2dsm.py
	:lines: 47-68

The ``main()`` function in the program first registers two callbacks with the instantiated MQTT client for when a successful connection is made, and when an MQTT message is received. A JSON formatted configuration file is then loaded, and the Metric object and MQTT client configured based on provided values. The MQTT client then connects and spins in a loop waiting for incoming messages on subscribed topics.

.. literalinclude:: ../examples/mqtt2dsm/mqtt2dsm.py
	:lines: 13-22

The ``mqtt_connect`` callback handles subscribing to the provided topics using list comprehension to create a list of tuples as required by the ``subscribe`` method.

.. literalinclude:: ../examples/mqtt2dsm/mqtt2dsm.py
	:lines: 24-47

The ``mqtt_message`` function publishes MQTT values to the DesignSpark Cloud. A sanity check is first performed to ensure the topic is present in the configuration file, then a copy of the topic data is made ready to have values inserted and removed. The ``metric`` key from the configuration is popped and inserted into a new dictionary under the correct ``name`` key required by the ``Metric`` module. The ``value`` key is then set to the received MQTT message payload, and the data point then published to the cloud.

.. literalinclude:: ../examples/mqtt2dsm/config.json
	:lines: 2-5

Within the configuration file multiple JSON objects are present. The ``mqtt`` object at minimum needs to include keys called ``broker`` and ``port`` which sets the MQTT broker address and port. Optional keys include ``username`` and ``password`` should the broker require authentication.

.. literalinclude:: ../examples/mqtt2dsm/config.json
	:lines: 6-10

A section called ``dsm`` is mandatory and must contains keys called ``url``, ``instance`` and ``key`` which are provided by DesignSpark Cloud when registering. The authentication key must have permission to write data.

.. literalinclude:: ../examples/mqtt2dsm/config.json
	:lines: 11-20

The final section is called ``topics`` and contains a number of objects where the object key is the MQTT topic to be subscribed to — in the example we've used ``sensors/bedroom/temperature``. Each topic object must contain a key called ``metric`` which is the name of the metric. An optional section called ``labels`` can be included which then becomes labels on the data point within DesignSpark Cloud.

``BatteryTest.py``
------------------

This application interfaces with an RS Pro electronic load to perform battery discharge tests and logs data to DesignSpark Cloud.

Command line switches
~~~~~~~~~~~~~~~~~~~~~

A number of command line switches are present

+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| Short name | Long name  | Description                                       | Type    | Example                                               |
+============+============+===================================================+=========+=======================================================+
| -d         | --device   | The PyVISA device string                          | String  | -d "ASRL6::INSTR"                                     |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -b         | --baud     | The PyVISA device baud rate                       | Integer | -b 115200                                             |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -c         | --capacity | The battery capacity to discharge to in amp-hours | Integer | -c 110                                                |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -a         | --amperage | The discharge current in amps                     | Float   | -a 5                                                  |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -v         | --voltage  | The low voltage cut off point in volts            | Float   | -v 10.5                                               |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -t         | --time     | Time to discharge cut off in minutes              | Integer | -t 10                                                 |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -i         | --instance | DesignSpark Cloud instance                        | String  | -i 123456                                             |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -u         | --url      | DesignSpark Cloud URL                             | String  | -u "https://prometheus-prod-01-eu-west-0.grafana.net" |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -k         | --key      | DesignSpark Cloud key                             | String  | -k "YOUR_AUTHENTICATION_KEY"                          |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+
| -n         | --name     | Battery name label                                | String  | -n "Battery123"                                       |
+------------+------------+---------------------------------------------------+---------+-------------------------------------------------------+

An example command: ``python3 BatteryTest.py -d "ASRL6::INSTR" -b 115200 -c 10 -a 2.5 -t 10 -v 10.5 -i 123456 -k "YOUR_AUTH_KEY" -u "https://prometheus-prod-01-eu-west-0.grafana.net" -n "batterytest"``

Code explanation
~~~~~~~~~~~~~~~~

.. literalinclude:: ../examples/BatteryTest.py
	:lines: 26-34

The script first attempts to parse all the required command line arguments, then creates an object for communicating with the instrument. An instrument query ``*IDN?`` is executed that asks the instrument to identify itself, which is then printed to the console.

.. literalinclude:: ../examples/BatteryTest.py
	:lines: 41-51

A string is compiled that attempts to program a battery test regime on the electronic load, sent to the instrument and the input turned on which starts the discharge programme.

.. literalinclude:: ../examples/BatteryTest.py
	:lines: 53-72

The instrument is polled once every second whilst the input is switched on, with readings of current capacity, voltage and current added to a list to be averaged. All the information is logged to the console.

.. literalinclude:: ../examples/BatteryTest.py
	:lines: 75-95

Once every minute an average of the last sixty seconds of data points is computed and published to DesignSpark Cloud.

The while loop exits once the input is turned off, which is automatically performed by the instrument when a cut off point is achieved (one or more of voltage, capacity or time). After the loop exits one last set of queries is made to the instrument to get capacity and time, which is then published to DesignSpark Cloud. This information is also mirrored to the console.

.. _prometheus-api-client: https://pypi.org/project/prometheus-api-client/
.. _prometheus_api_client: https://prometheus-api-client-python.readthedocs.io/en/master/source/prometheus_api_client.html