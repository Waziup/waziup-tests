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

nginx is running on the staging server with this config:

```
server {
	listen 80;
	server_name staging.waziup.io;

	location / {
		autoindex on;
		root /var/www/Staging;
	}
}
server {
	listen 80;
	server_name jenkins.staging.waziup.io;

	location / {
        	proxy_pass http://localhost:8123/;
		proxy_set_header Host $host;
	}
}
server {
	listen 80;
	server_name wazicloud-dashboard.staging.waziup.io;
	location / {
        	proxy_pass http://localhost:3000/;
		proxy_redirect     off;
		proxy_set_header   Host $host;
	}
}
server {
	listen 80;
	server_name wazicloud-api.staging.waziup.io;
	location / {
        	proxy_pass http://localhost:800/;
	}
}
server {
	listen 80;
	server_name wazicloud-keycloak.staging.waziup.io;

	location / {
        	proxy_pass http://localhost:8080/;
		proxy_set_header Host $host;
	}
}
server {
	listen 80;
	server_name wazigate-dashboard.staging.waziup.io;

	location / {
        	proxy_pass http://172.16.11.208:80/;
	}
}
server {
	listen 80;
	server_name wazigate-dashboard-stable.staging.waziup.io;

	location / {
        	proxy_pass http://172.16.11.161:80/;
	}
}
server {
	listen 80;
	server_name wazigate-chirpstack.staging.waziup.io;

	location / {
        	proxy_pass http://172.16.11.208:8080/;
	}
}
server {
	listen 80;
	server_name wazidev-api.staging.waziup.io;
	location / {
        	proxy_pass http://localhost:5000/;
	}
}
server {
	listen 80;
	server_name lab.staging.waziup.io;
	location / {
        	proxy_pass http://localhost:8467/;
	}
}
server {
	listen 80;
	server_name website.staging.waziup.io;
	location / {
        	proxy_pass http://localhost:81/;
	}
}
server {
	listen 80;
	server_name webhook.staging.waziup.io;
	location / {
        	proxy_pass http://localhost:9000/;
	}
}
