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

wazidev_port = os.getenv("WAZIDEV_PORT", '/dev/ttyUSB0')

interface = Interface(wazidev_port)

wazidev_sensor_id = 'temperatureSensor_1'
wazidev_sensor_value = 45.7
wazidev_actuator_id = 'act1'
wazidev_actuator_value = json.dumps(True)

wazigate_ip = os.environ.get('WAZIGATE_IP', '172.16.11.212')
wazigate_url = 'http://' + wazigate_ip
wazicloud_url = os.getenv('WAZICLOUD_URL', 'http://localhost:800/api/v2')

wazigate_device = {
#  'id': 'testDev',
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

def_cloud = {
  "rest": "//api.waziup.io/api/v2",
  "mqtt": "",
  "credentials": {
      "username": "my username",
      "token": "my password"
  }
}

class TestCloudSync(unittest.TestCase):

    token = None
    dev_id = None
    def setUp(self):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        self.token = {"Authorization": "Bearer " + resp.text.strip('"')}
        # Delete test device if exists
        #resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        
        # create Cloud sync
        #resp = requests.post(wazigate_url + '/clouds', json=def_cloud, headers = self.token)
        #self.assertEqual(resp.status_code, 200)

    # Test device creation upload to Cloud
    def test_device_upload(self):
        """ Test device sync from gateway to Cloud"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.text
        self.assertEqual(resp.status_code, 200)
        
        # Check WaziCloud for the presence of the new device
        resp = requests.get(wazicloud_url + '/devices/' + self.dev_id)
        self.assertEqual(resp.status_code, 200)

    # Test sensor creation upload to Cloud
    def test_sensor_upload(self):
        """ Test sensor sync from gateway to Cloud"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.text
        self.assertEqual(resp.status_code, 200)
        
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + '/sensors', json={'id':'testSen', 'name':'testSen'}, headers = self.token)
        self.assertEqual(resp.status_code, 200)
        
        # Check WaziCloud for the presence of the new sensor
        resp = requests.get(wazicloud_url + '/devices/' + self.dev_id + '/sensors/testSen')
        self.assertEqual(resp.status_code, 200)

    # Test sensor creation upload to Cloud
    def test_actuator_upload(self):
        """ Test actuator sync from gateway to Cloud"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.text
        self.assertEqual(resp.status_code, 200)
        
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + '/actuators', json = {'id':'testAct', 'name':'testSen'}, headers = self.token)
        self.act_id = resp.text
        self.assertEqual(resp.status_code, 200)
        print(self.dev_id)
        print(self.act_id)
        
        # Check WaziCloud for the presence of the new actuator
        resp = requests.get(wazicloud_url + '/devices/testDev/actuators/testAct' + self.act_id)
        self.assertEqual(resp.status_code, 200)


    # Remove resources that was created
   # def tearDown(self):
        #resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
        #resp = requests.delete(wazicloud_url + '/devices/' + self.dev_id)


class TestUplink(unittest.TestCase):

    token = None
    dev_id = None
    def setUp(self):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        self.token = {"Authorization": "Bearer " + resp.text.strip('"')}
        # Delete test device if exists
        #resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)


    # Test value sent from WaziDev
    def test_wazidev_value_upload(self):
        """ Test value upload from WaziDev to gateway"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.text
        self.assertEqual(resp.status_code, 200)

        # Add the LoRaWAN meta information
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + "/meta", json = meta, headers = self.token)
        self.assertEqual(resp.status_code, 200)
        
        # Send a value with WaziDev
        sendValueWaziDev("62\n")
        time.sleep(12)

        # Check that the value has been received in the Cloud
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id + "/sensors", headers = self.token)
        print(resp.json())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]['value'], 62)
  
    # Remove resources that was created
    #def tearDown(self):
    #    resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
    #    resp = requests.delete(wazicloud_url + '/devices/' + self.dev_id)

class TestDownlink(unittest.TestCase):

    token = None
    dev_id = None 
    def setUp(self):
        # Get WaziGate token
        resp = requests.post(wazigate_url + '/auth/token', json = auth) 
        self.token = {"Authorization": "Bearer " + resp.text.strip('"')}
        # Delete test device if exists
        #resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)


    # Test value sent from WaziDev
    def test_wazidev_value_upload(self):
        """ Test value upload from WaziDev to gateway"""

        # Create a new device on WaziGate
        resp = requests.post(wazigate_url + '/devices', json = wazigate_device, headers = self.token)
        self.dev_id = resp.text
        self.assertEqual(resp.status_code, 200)

        # Add LoRaWAN meta information
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + "/meta", json = meta, headers = self.token)
        self.assertEqual(resp.status_code, 200)
       
        # Create the actuator
        resp = requests.post(wazigate_url + '/devices/' + self.dev_id + '/actuators', json={'name':'test'}, headers = self.token)
        self.assertEqual(resp.status_code, 200)

        # Actuate on the Cloud 
        resp = requests.post(wazicloud_url + '/devices/' + self.dev_id + '/actuators/test/value', json=10)
        self.assertEqual(resp.status_code, 200)

        # Check actuator value at gateway
        resp = requests.get(wazigate_url + '/devices/' + self.dev_id + '/actuators/test', headers = self.token)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]['value'], 10)
        
        time.sleep(1)
        # Send a value with WaziDev to get the receive window
        res = sendValueWaziDev(0)
        self.assertEqual(res, 10)

  
    # Remove resources that was created
    #def tearDown(self):
    #    resp = requests.delete(wazigate_url + '/devices/' + self.dev_id, headers = self.token)
    #    resp = requests.delete(wazicloud_url + '/devices/' + self.dev_id)

def sendValueWaziDev(val: int) -> str:
    return interface.sendLoRaWAN(val)

if __name__ == '__main__':
    with open('results.xml', 'wb') as output:
        unittest.main(testRunner=xmlrunner.XMLTestRunner(output=output, verbosity=2),
                      failfast=False, 
                      buffer=False, 
                      catchbreak=False)
