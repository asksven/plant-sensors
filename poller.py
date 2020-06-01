from miflora.miflora_poller import MiFloraPoller
from btlewrap.bluepy import BluepyBackend
from bluepy.btle import BTLEDisconnectError
from btlewrap.base import BluetoothBackendException
from influxdb import InfluxDBClient
import json
from datetime import datetime
import sys
import os

MANDATORY_ENV_VARS = ["USER", "PASSWORD", "DBNAME", "HOST", "PORT"]

try:
    for var in MANDATORY_ENV_VARS:
        if var not in os.environ:
            raise EnvironmentError("Failed because {} is not set.".format(var))
except OSError as err:
    print("Aborting: ", format(err))
    exit(1) 

# Parse input.json
# Expected format is an array of objects with these attributes:
# [
#   {
#     "mac": "<sensor-mac-address>",
#     "plant": "<plant-name>",
#     "id": <sensor-number>
#   },
#   ...
# ]

try:
    input_file = open ('input.json')
    json_array = json.load(input_file)
    sensor_list = []
except json.decoder.JSONDecodeError as err:
    print("Parser error: ", format(err))
    exit(1)
except:
    print("An unexpected error occured reading input-file. Aborting")
    sys.exc_info()
    exit(1)

try:
    client = InfluxDBClient(
        os.getenv('HOST', ''),
        os.getenv('PORT', '8086'),
        os.getenv('USER', ''),
        os.getenv('PASSWORD', ''),
        os.getenv('DBNAME', ''),
        ssl=True, verify_ssl=True)
except:
    print("An unexpected error occured when connecting to the database. Aborting")
    sys.exc_info()
    exit(1)

for item in json_array:
    print('Id: ', item['id'])
    print('MAC: ', item['mac'])
    print('Plant: ', item['plant'])
    
    # As BLE is not 100% we need some retry-logic
    synced = False
    retries = 0
    while (not synced and (retries < 3)):
        try:
            poller = MiFloraPoller(item['mac'], BluepyBackend)
   
            print('Battery:', poller.battery_level())
            print('Firmware:', poller.firmware_version())
            print('Temperature:', poller.parameter_value('temperature'))
            print('Light:', poller.parameter_value('light'))
            print('Moisture:', poller.parameter_value('moisture'))
            print('Conductivity:', poller.parameter_value('conductivity'))
            synced = True
        except BTLEDisconnectError as err:
            print("!!! A BLE error occured: retrying", err)
        except BluetoothBackendException as err2:
            print("!!! A BLE error occured: retrying", err2)
        finally:
          retries += 1

    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    json_body = [ \
      {"measurement": "plant_sensor", \
      "tags": {"id": item['id'], "plant": item['plant'], "mac": item['mac']}, \
      "time": now, \
      "fields": { \
          "battery": poller.battery_level(), \
          "temperature": poller.parameter_value('temperature'), \
          "light": poller.parameter_value('light'), \
          "moisture": poller.parameter_value('moisture'), \
          "conductivity": poller.parameter_value('conductivity') \
      }}]

#    print(json_body)
    try:
        client.write_points(json_body)
        result = client.query('select temperature from plant_sensor;')
        print(">>> Written")
#        print("Result: {0}".format(result))
    except requests.exceptions.ConnectionError as err:
        print("!!! Connection error: ", format(err))
    except:
        print("!!! An unexpected error occured when connecting to the database. Aborting")
        sys.exc_info()
