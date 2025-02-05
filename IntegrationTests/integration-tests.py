## Waziup Platform Integration Tests
##
## The goal of integration testing is to test the full chain:
## WaziDev <-> WaziGate <-> WaziCloud
## both ways (uplink and downlink paths) using components REST API.

## Tests implemented comprise the following:
## - device synchronization
## - sensor synchronization

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
from simple_rpc import Interface
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

wazidev_port = os.getenv("WAZIDEV_PORT", '/dev/ttyUSB0')

#Get WaziDev RPC interface
interface = Interface(wazidev_port)

wazidev_sensor_id = 'temperatureSensor_1'
wazidev_sensor_value = 45.7
wazidev_actuator_id = 'act1'
wazidev_actuator_value = json.dumps(True)

wazigate_ip = os.environ.get('WAZIGATE_IP', '172.16.11.212')
wazigate_url = 'http://' + wazigate_ip
wazicloud_url = os.getenv('WAZICLOUD_URL', 'http://172.16.11.191:800/api/v2')
wazicloud_mqtt = os.getenv('WAZICLOUD_MQTT', 'mqtt://172.16.11.191:3883')

wazigate_device = {
  'name': 'test',
  'sensors': [],
  'actuators': []
}

meta = {
  "codec": "application/x-xlpp",
  "lorawan": {
    "appSKey": "23158D3BBC31E6AF670D195B5AED5525",
    "devAddr": "26011D22",
    "devEUI": "AA555A0026011D01",
    "nwkSEncKey": "23158D3BBC31E6AF670D195B5AED5525",
    "profile": "WaziDev"
  }
}

auth = {
  "username": "admin",
  "password": "loragateway"
}

class TestCloudSync(unittest.TestCase):

    token = None
    dev_id = None
    @classmethod
    def setUpClass(cls):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        token = {"Authorization": "Bearer " + resp.json()}
        # create Cloud sync
        resp = requests.post(wazigate_url + '/clouds/waziup/paused', json=True, headers = token)
        sleep(3)
        resp = requests.post(wazigate_url + '/clouds/waziup/rest', json=wazicloud_url, headers = token)
        resp = requests.post(wazigate_url + '/clouds/waziup/mqtt', json=wazicloud_mqtt, headers = token)
        resp = requests.post(wazigate_url + '/clouds/waziup/username', json="admin", headers = token)
        resp = requests.post(wazigate_url + '/clouds/waziup/token', json="admin", headers = token)
        sleep(3)
        resp = requests.post(wazigate_url + '/clouds/waziup/paused', json=False, headers = token)
        sleep(3)

    def setUp(self):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        self.token = {"Authorization": "Bearer " + resp.json()}

    # Test device creation upload to Cloud
    def test_device_upload(self):
        """ Test device sync from gateway to Cloud"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.json()
        self.assertEqual(resp.status_code, 200, "Can't create device on the gateway.")
        sleep(2)
        
        # Check WaziCloud for the presence of the new device
        resp = requests.get(wazicloud_url + '/devices/' + self.dev_id)
        self.assertEqual(resp.status_code, 200, "Device not created at the Cloud.")

    # Test sensor creation upload to Cloud
    def test_sensor_upload(self):
        """ Test sensor sync from gateway to Cloud"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.json()
        self.assertEqual(resp.status_code, 200)
        
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + '/sensors', json={'id':'testSen', 'name':'testSen'}, headers = self.token)
        self.act_id = resp.json()
        self.assertEqual(resp.status_code, 200)
        sleep(2)
        
        # Check WaziCloud for the presence of the new sensor
        resp = requests.get(wazicloud_url + '/devices/' + self.dev_id + '/sensors/' + self.act_id)
        self.assertEqual(resp.status_code, 200, "Sensor not created at the Cloud.")

    # Test actuator creation upload to Cloud
    def test_actuator_upload(self):
        """ Test actuator sync from gateway to Cloud"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.json()
        self.assertEqual(resp.status_code, 200)
        
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + '/actuators', json = {'id':'testAct', 'name':'testAct'}, headers = self.token)
        self.act_id = resp.json()
        self.assertEqual(resp.status_code, 200)
        sleep(2)
        # Check WaziCloud for the presence of the new actuator
        resp = requests.get(wazicloud_url + '/devices/' + self.dev_id + '/actuators/' + self.act_id)
        self.assertEqual(resp.status_code, 200, "Actuator not created at the Cloud.")


    # Remove resources that was created
    def tearDown(self):
        resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        resp = requests.delete(wazicloud_url + '/devices/' + self.dev_id)


class TestUplink(unittest.TestCase):

    token = None
    dev_id = None
    def setUp(self):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        self.token = {"Authorization": "Bearer " + resp.json()}
        # Delete test device if exists
        #resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)


    # Test value sent from WaziDev
    def test_wazidev_value_upload(self):
        """ Test value upload from WaziDev to gateway"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.json()
        self.assertEqual(resp.status_code, 200)

        # Add the LoRaWAN meta information
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + "/meta", json = meta, headers = self.token)
        self.assertEqual(resp.status_code, 200, "Cannot add the LoRaWAN meta information")
        
        # Send a value with WaziDev
        res = interface.sendLoRaWAN(62)
        print(res)
        time.sleep(24)

        # Check that the value has been received at the WaziGate
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id + "/sensors", headers = self.token)
        print(resp.json())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]['value'], 62, "Value not received by the gateway")
   
    def tearDown(self):
        # Delete the device (to free the DevAddr)
        requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
  

class TestDownlink(unittest.TestCase):

    token = None
    dev_id = None 
    def setUp(self):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        self.token = {"Authorization": "Bearer " + resp.json()}
        # Delete test device if exists
        #resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)


    # Test value receive on WaziDev
    def test_wazidev_value_downlink(self):
        """ Test value download from gateway to wazidev"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.json()
        self.assertEqual(resp.status_code, 200)

        # Add LoRaWAN meta information
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + "/meta", json = meta, headers = self.token)
        self.assertEqual(resp.status_code, 200)
       
        # Create the actuator
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + '/actuators', json={'name':'test'}, headers = self.token)
        self.assertEqual(resp.status_code, 200, "Cannot create the actuator")

        # Actuate on the Cloud 
        resp = requests.put(wazicloud_url + '/devices/' + self.dev_id + '/actuators/test/value', json=10)
        self.assertEqual(resp.status_code, 200, "Cannot actuate on the Cloud")

        # Check actuator value at gateway
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id + '/actuators/test', headers = self.token)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]['value'], 10, "Wrong or no actuator value at gateway")
        
        time.sleep(10)
        # Send a value with WaziDev to get the receive window
        (e, res) = interface.sendLoRaWAN(1)
        self.assertEqual(e, 0)
        self.assertEqual(res, 10)

  
    # Remove resources that was created
    def tearDown(self):
        requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)

def sendValueWaziDev(val: int) -> str:
    return interface.sendLoRaWAN(val)

if __name__ == '__main__':
    with open('results.xml', 'wb') as output:
        unittest.main(testRunner=xmlrunner.XMLTestRunner(output=output, verbosity=2),
                      failfast=False, 
                      buffer=False, 
                      catchbreak=False)
    sendValueWaziDev(1)
