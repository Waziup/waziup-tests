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

This will add a device "/dev/ttyUSBWaziDev" attached to the WaziDev.


URLS
=====

nginx is running on the staging server with [this config](Staging/nginx-config).
The idea is to ventilate all the subdomains of `staging.waziup.io` to the various services.

