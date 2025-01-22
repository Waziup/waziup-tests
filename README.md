Waziup platform Tests
=====================

This repository defines tests for the full Waziup platform.


Development
===========


WaziDev
-------

WaziDev is permanently attached to the test server.
It can map to either /dev/ttyUSB0 or /dev/ttyUSB1.
In order to have a fixed "/dev" device, we can use udev rules.
Get USB serial number:

```
$ sudo udevadm info --query=property --name=/dev/ttyUSB0 | grep SERIAL
ID_SERIAL=1a86_USB2.0-Serial
```

Add a new udev rule named "/etc/udev/rules.d/99-usbserial.rules":
```
ACTION=="add",ENV{ID_BUS}=="usb",ENV{ID_SERIAL}=="1a86_USB2.0-Serial",SYMLINK+="ttyUSBWaziDev"
```
Restart udev:
```
sudo udevadm control --reload-rules
sudo udevadm trigger
```

This will add a device "/dev/ttyUSBWaziDev" attached to the WaziDev.


URLS
=====

nginx is running on the staging server with [this config](Staging/nginx-config).
The idea is to ventilate all the subdomains of `staging.waziup.io` to the various services.


Integration tests
=================

The goal of integration testing is to test the full chain:
WaziDev <-> WaziGate <-> WaziCloud
both ways (uplink and downlink paths) using components REST API.

You can find the tests in the folder IntegrationTests.
You can run them like this:

```
export WAZIGATE_IP=172.16.11.192 
export WAZICLOUD_URL=http://35.157.161.231:800/api/v2 
export WAZICLOUD_MQTT=mqtt://35.157.161.231:3883 
sudo -E python3 integration-tests.py
```

You can provide on the command line:
- the IP of you gateway
- the URL of the Cloud API
- the URL of the Cloud MQTT

You also need to have a WaziDev running this program:
https://github.com/Waziup/WaziDev/blob/master/tests/LoRaWAN-test/LoRaWAN-test.ino

The WaziDev needs to be connected to your Linux PC using a USB cable. It should be available under `/dev/ttyUSB0`
