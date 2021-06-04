## Waziup Platform Integration Tests
##
## The goal of integration testing is to test the full chain:
## WaziDev <-> WaziGate <-> WaziCloud
## both ways (uplink and downlink paths) using components REST API.

## Tests implemented comprise the following:
## - device synchronization
## - sensor synchronization
## - actuator synchronization

## Prerequisites:
##   https://www.waziup.io/documentation/wazigate/v2/lorawan/
## - a fully operational WaziGate gateway with a default installation:
##   https://www.waziup.io/documentation/wazigate/v2/install/
## - a test account on the WaziCloud platform:
##   https://dashboard.waziup.io


import json
import requests
from time import sleep
import unittest
import xmlrunner
import random
import logging
import serial
import time
import os
import sys
from xmlrunner import XMLTestRunner

wazidev_port = server = os.getenv("WAZIDEV_PORT", '/dev/ttyUSB0')
print ("WaziDev port:" + wazidev_port)
wazidev_speed = 38400

wazidev_serial = serial.Serial(wazidev_port, wazidev_speed)
wazidev_serial.flushInput()

#try:
#    import http.client as http_client
#except ImportError:
#    # Python 2
#    import httplib as http_client
##http_client.HTTPConnection.debuglevel = 1
#
# You must initialize logging, otherwise you'll not see debug output.
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.INFO)
#requests_log.propagate = True

## Variable declaration

wazidev_sensor_id = 'temperatureSensor_1'
wazidev_sensor_value = 45.7
wazidev_actuator_id = 'act1'
wazidev_actuator_value = json.dumps(True)

wazigate_url = 'http://172.16.11.186/'

wazigate_device = {
  'id': 'test000',
  'name': 'test',
  'meta': {
    'codec': 'application/x-xlpp',
    'lorawan': {
      'appSKey': '23158D3BBC31E6AF670D195B5AED5525',
      'devAddr': '26011D22',
      'devEUI': 'AA555A0026011D01',
      'nwkSEncKey': '23158D3BBC31E6AF670D195B5AED5525',
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

auth = {
  "username": "admin",
  "password": "loragateway"
}

wazicloud_url = 'https://api.waziup.io/api/v2'

class TestWaziGateBasic(unittest.TestCase):

    token = None
    dev_id = wazigate_device['id']
    def setUp(self):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        self.token = {"Token": resp.text.strip('"')}
        # Delete test device if exists
        resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)

    def test_create_device_wazigate(self):
        """ Test simple device creation on the gateway"""

        # Create a new LoRaWAN device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.assertEqual(resp.status_code, 200)
        
        # Check that it's effectively created
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        self.assertEqual(resp.status_code, 200)
    
    def test_create_device_wazigate(self):
        """ Test simple device deletion on the gateway"""

        # Create a new LoRaWAN device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        
        # Delete it 
        resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        self.assertEqual(resp.status_code, 200)
        
        # Check that it's effectively deleted
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        self.assertEqual(resp.status_code, 404)
    
    # Remove any resources that was created
    def tearDown(self):
        resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)

class TestUplink(unittest.TestCase):

    token = None
    dev_id = wazigate_device['id']
    def setUp(self):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        self.token = {"Token": resp.text.strip('"')}
        # Delete test device if exists
        resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)

    def test_device_wazigate(self):
        """ Test simple device creation and deletion on the gateway"""

        # Create a new LoRaWAN device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.assertEqual(resp.status_code, 200)
        
        # Check that it's effectively created
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        self.assertEqual(resp.status_code, 200)

        # Delete it 
        resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        self.assertEqual(resp.status_code, 200)
        
        # Check that it's effectively deleted
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        self.assertEqual(resp.status_code, 404)

    # Test device upload to Cloud
    def test_device_creation_upload(self):

        # Create a new LoRaWAN device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.text
        self.assertEqual(resp.status_code, 200)
        
        # Check WaziCloud for the presence of the new LoRaWAN device, sensor and its value
        resp = requests.get(wazicloud_url + '/devices/' + self.dev_id)
        self.assertEqual(resp.status_code, 200)

    # Test value sent from WaziDev
    def test_wazidev_value_upload(self):

        # Create a new LoRaWAN device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.text
        self.assertEqual(resp.status_code, 200)

        msg = wazidev_serial.readline()
        print (msg.decode())
        msg = wazidev_serial.readline()
        print (msg.decode())
        wazidev_serial.write("62\n".encode())
        #print ("done")
        while ("OK" not in msg.decode('unicode_escape')):
          msg = wazidev_serial.readline()
          print (msg.decode('unicode_escape'), end='', flush=True)

        time.sleep(2)
        # Check that it's effectively created
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id + "/sensors/temperatureSensor_1/value", headers = self.token) #
        print(resp.text)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, "62")
  
    # Remove resources that was created
    def tearDown(self):
        resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        resp = requests.delete(wazicloud_url + '/devices/' + self.dev_id)

#suite = unittest.TestSuite()
#suite.addTest(TestDeviceSync('Uplink tests'))

if __name__ == '__main__':
    with open('results.xml', 'wb') as output:
        unittest.main(verbosity=2,
                      testRunner=xmlrunner.XMLTestRunner(output=output),
                      failfast=False, 
                      buffer=False, 
                      catchbreak=False)

