## Waziup Platform Integration Tests
##
## The goal of integration testing is to test the full chain:
## WaziDev <-> WaziGate <-> WaziCloud
## both ways (uplink and downlink paths) using component’s REST API.

## Tests implemented comprise the following:
## - device synchronization
## - sensor synchronization
## - actuator synchronization

## Prerequisites:
## - a WaziDev device flashed with the “LoRaWAN/Actuation” sketch sending sensor and receiving actuator values:
##   https://www.waziup.io/documentation/wazigate/v2/lorawan/
## - a fully operational WaziGate gateway with a default installation:
##   https://www.waziup.io/documentation/wazigate/v2/install/
## - a test account on the WaziCloud platform:
##   https://dashboard.waziup.io


## Uplink path tests: WaziDev -> WaziGate -> WaziCloud
##
## Steps:
##     1. Power on WaziDev device flashed with the 'LoRaWAN/Actuation' sketch
##     2. Create a new LoRaWAN device on WaziGate
##     3. Check WaziGate for the presence of the new sensor and its value
## Expected result:
##     The new sensor and its value should be present on WaziGate (sensor is automatically created on WaziGate).
##
## Steps:
##     4. Check WaziCloud for the presence of the new LoRaWAN device, sensor and its value
## Expected result:
##     The new LoRaWAN device, sensor and its value should be present on WaziCloud (device and sensor are automatically synchronized with WaziCloud).
##
## Steps:
##     5. Create a new actuator on WaziGate
##     6. Check WaziCloud for the presence of the new actuator and set a value for it
## Expected result:
##     The new actuator should be present on WaziCloud and a value could be set for it (actuator is automatically synchronized with WaziCloud).

## Downlink path tests: WaziCloud -> WaziGate -> WaziDev
##
## Steps:
##     7. Check WaziGate for the presence of the actuator value
##     8. Check WaziDev for the presence of the actuator value
## Expected result:
##     The actuator value should be present on WaziGate and on WaziDev.


import json
import requests
from time import sleep


## Variable declaration

wazidev_sensor_id = 'temperatureSensor_1'
wazidev_sensor_value = 45.7
wazidev_actuator_id = 'act1'
wazidev_actuator_value = json.dumps(True)

wazigate_url = 'http://wazigate.local'
wazigate_device_id = 'test'
wazigate_create_device = {
  'id': 'test',
  'name': 'test',
  'meta': {
    'lorawan': {
      'appSKey': '23158D3BBC31E6AF670D195B5AED5544',
      'devAddr': '26011D22',
      'devEUI': 'AA555A0026011D01',
      'nwkSEncKey': '23158D3BBC31E6AF670D195B5AED5544',
      'profile': 'WaziDev'
    }
  },
  'sensors': [],
  'actuators': []
}
wazigate_create_actuator = {
  'id': 'act1',
  'name': 'act1'
}

wazicloud_url = 'https://api.waziup.io/api/v2'


## Function declaration

def get_request(request_url, request_json):

    response = requests.get(request_url, data=request_json)
    print(response)
    if (response.status_code == 200):
        return response.text
    else:
        return 'Error'

def post_request(request_url, request_json):

    response = requests.post(request_url, json=request_json)
    print(response)
    if (response.status_code == 200):
        return response.text
    else:
        return 'Error'

def put_request(request_url, request_data):

    request_headers = {'Content-Type': 'application/json;charset=utf-8'}
    
    response = requests.put(request_url, headers=request_headers, data=request_data)
    print(response)
    if (response.status_code == 204):
        return response.text
    else:
        return 'Error'


## Main application function

def main():
    
    no_data = ''
    
    ## Uplink path tests
    
    # Step 1: Power on WaziDev device flashed with the 'LoRaWAN/Actuation' sketch
    print("Step 1: Power on WaziDev device flashed with the 'LoRaWAN/Actuation' sketch")
    print("Connect the WaziDev to a computer USB port and start the Arduino IDE, then open the 'Serial Monitor' from the 'Tools' menu.")
    input("Press Enter when done to start integration tests...")
    print("Step 1: 'Power on WaziDev device flashed with the 'LoRaWAN/Actuation' sketch' completed successfully.")
    
    # Step 2: Create a new LoRaWAN device on WaziGate
    wazigate_request_url = '%s/devices' % (wazigate_url)
    wazigate_response = post_request(wazigate_request_url, wazigate_create_device)
    if (wazigate_response != 'Error'):
        print("Step 2: Request ‘Create a new LoRaWAN device on Wazigate’ completed successfully.")
    else:
        print("Step 2: Request ‘Create a new LoRaWAN device on Wazigate’ returned an error.")

    sleep(20)  # Wait for the LoRaWAN device to sync with WaziCloud

    # Step 3: Check WaziGate for the presence of the new sensor and its value
    wazigate_request_url = '%s/devices/%s/sensors/%s' % (wazigate_url, wazigate_device_id, wazidev_sensor_id)
    wazigate_response = get_request(wazigate_request_url, no_data)
    if (wazigate_response != 'Error'):
        wazigate_request_url = '%s/devices/%s/sensors/%s/value' % (wazigate_url, wazigate_device_id, wazidev_sensor_id)
        wazigate_response = get_request(wazigate_request_url, no_data)
        if (wazigate_response == str(wazidev_sensor_value)):
            print("Step 3: Requests ‘Check WaziGate for the presence of the new sensor and its value’ completed successfully.")
        else:
            print("Step 3: Request ‘Check WaziGate for the presence of the new sensor value’ returned an error.")
    else:
        print("Step 3: Request ‘Check WaziGate for the presence of the new sensor’ returned an error.")

    # Step 4: Check WaziCloud for the presence of the new LoRaWAN device, sensor and its value
    wazicloud_request_url = '%s/devices/%s' % (wazicloud_url, wazigate_device_id)
    wazicloud_response = get_request(wazicloud_request_url, no_data)
    if (wazicloud_response != 'Error'):
        wazicloud_request_url = '%s/devices/%s/sensors/%s' % (wazicloud_url, wazigate_device_id, wazidev_sensor_id)
        wazicloud_response = get_request(wazicloud_request_url, no_data)
        if (wazicloud_response != 'Error'):
            wazicloud_request_url = '%s/devices/%s/sensors/%s/values/?limit=1' % (wazicloud_url, wazigate_device_id, wazidev_sensor_id)
            wazicloud_response = get_request(wazicloud_request_url, no_data)
            if (wazicloud_response != 'Error'):
                data = json.loads(wazicloud_response)
                sensor_data = data[0]
                if (sensor_data['value'] == wazidev_sensor_value):
                    print("Step 4: Requests ‘Check WaziCloud for the presence of the new LoRaWAN device, sensor and its value’ completed successfully.")
                else:
                    print("Step 4: Request ‘Check WaziCloud for the presence of the new sensor value’ returned a value mismatch.")
            else:
                print("Step 4: Request ‘Check WaziCloud for the presence of the new sensor value’ returned an error.")
        else:
            print("Step 4: Request ‘Check WaziCloud for the presence of the new sensor’ returned an error.")
    else:
        print("Step 4: Request ‘Check WaziCloud for the presence of the new LoRaWAN device’ returned an error.")

    # Step 5: Create a new actuator on WaziGate
    wazigate_request_url = '%s/devices/%s/actuators' % (wazigate_url, wazigate_device_id)
    wazigate_response = post_request(wazigate_request_url, wazigate_create_actuator)
    if (wazigate_response != 'Error'):
        print("Step 5: Request ‘Create a new actuator on WaziGate’ completed successfully.")
    else:
        print("Step 5: Request ‘Create a new actuator on WaziGate’ returned an error.")

    sleep(10)  # Wait for the actuator to sync with WaziCloud

    # Step 6: Check WaziCloud for the presence of the new actuator and set a value for it
    wazicloud_request_url = '%s/devices/%s/actuators/%s' % (wazicloud_url, wazigate_device_id, wazidev_actuator_id)
    wazicloud_response = get_request(wazicloud_request_url, no_data)
    if (wazicloud_response != 'Error'):
        wazicloud_request_url = '%s/devices/%s/actuators/%s/value' % (wazicloud_url, wazigate_device_id, wazidev_actuator_id)
        wazicloud_response = put_request(wazicloud_request_url, wazidev_actuator_value)
        if (wazicloud_response != 'Error'):
            print("Step 6: Requests ‘Check WaziCloud for the presence of the new actuator and set a value for it’ completed successfully.")
        else:
            print("Step 6: Request ‘Check WaziCloud and set a value for the new actuator’ returned an error.")
    else:
        print("Step 6: Request ‘Check WaziCloud for the presence of the new actuator’ returned an error.")

    sleep(5)  # Wait for the actuator value to sync with WaziGate

    ## Downlink path tests

    # Step 7: Check WaziGate for the presence of the actuator value
    wazigate_request_url = '%s/devices/%s/actuators/%s/value' % (wazigate_url, wazigate_device_id, wazidev_actuator_id)
    wazigate_response = get_request(wazigate_request_url, no_data)
    if (wazigate_response != 'Error'):
        if (wazigate_response == wazidev_actuator_value):
            print("Step 7: Request ‘Check WaziGate for the presence of the actuator value’ completed successfully.")
        else:
            print("Step 7: Request ‘Check WaziGate for the presence of the actuator value’ returned a value mismatch.")
    else:
        print("Step 7: Request ‘Check WaziGate for the presence of the actuator value’ returned an error.")

    # Step 8: Check WaziDev for the presence of the actuator value
    print("Step 8: Check WaziDev for the presence of the actuator value")
    print("In the 'Serial Monitor' window a 'Payload: true' must be displayed for this step to complete successfully.")
    input("Press Enter when done to end integration tests...")
    print("Step 8: 'Check WaziDev for the presence of the actuator value' completed successfully.")

    print("Integration tests completed successfully.")


main()
