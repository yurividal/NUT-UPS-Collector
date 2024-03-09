# NUT-UPS-Collector
Script that collects data from a NUT-Monitored UPS and stores the data into an InfluxDB and into a PRTG Server

## How to setup
1. Connect your UPS(s) to a machine running linux. (Tested on Ubuntu 22.04)
   1.1 If you are connecting to a VM running in ESXi, you will need to passthrough the USB device to the VM.
   1.2 Check if the UPS is detected by the system by running `lsusb` and looking for the UPS device.
   1.3 When detected, run `lsusb -v` to get the serial number of your UPS.
   example:
   ````
        Bus 002 Device 004: ID 0463:ffff MGE UPS Systems UPS
        Couldn't open device, some information will be missing
        Device Descriptor:
        bLength                18
        bDescriptorType         1
        bcdUSB               1.10
        bDeviceClass            0 
        bDeviceSubClass         0 
        bDeviceProtocol         0 
        bMaxPacketSize0         8
        idVendor           0x0463 MGE UPS Systems
        idProduct          0xffff UPS
        bcdDevice            2.02
        iManufacturer           1 EATON
        iProduct                2 Eaton 5SC
        iSerial                 3 G148N26038
        bNumConfigurations      1
    ````
  1.4 Take note of the serial number of your UPS. In this case, it is `G148N26038`

2. Install NUT (Network UPS Tools) by running `sudo apt-get install nut nut-snmp nut-server nut-cgi`

3. Edit the file `/etc/nut/ups.conf` and add the following lines:
    ````
    [EatonUPS1]
        driver = usbhid-ups
        port = auto
        vendorid = 0463
        pollfreq = 30
        serial = G148N26038
    [EatonUPS2]
        driver = usbhid-ups
        port = auto
        vendorid = 0463
        pollfreq = 30
        serial = G148P34009
    ````
Replace `EatonUPS1` and `EatonUPS2` with the name of your UPS. Replace `0463` with the vendorid of your UPS. Replace `G148N26038` and `G148P34009` with the serial number of your UPS. To find the vendorid you can run `sudo nut-scanner` to help you find the vendorid and serial number of your UPS.

4. Edit the file `/etc/nut/upsd.users` and add the following lines:
    ```
            [upsmon]
                password = 12345678
                actions = SET FSD
                instcmds = ALL
    ```
Replace `12345678` with a password of your choice.

5. Edit the file `/etc/nut/upsd.conf` and add the following lines:
    ```
    LISTEN 0.0.0.0 3493

6. Edit the file `/etc/nut/nut.conf` and add the following lines:
    ```
    MODE=netserver
    ````
7. Restart the NUT service by running `sudo systemctl restart nut-server`
8. Test if the NUT service is running by running `upsc EatonUPS1@localhost` and `upsc EatonUPS2@localhost`. You should see the status of your UPS.
9. Once that's up, you should be able to run this script and it will collect data from your UPS and store it into an InfluxDB and into a PRTG Server.
    
    9.1 Install the required python packages by running `pip3 install -r requirements.txt` and `sudo pip3 install -r requirements.txt`

    9.2 Edit the file `ups-monitor.py` and change the following variables to match your environment, like the example bellow:
        ```
            PRTG_IP = "192.168.36.13"
            INFLUXDB_IP = "192.168.36.14"
            UPS_NAMES = ["EatonUPS1", "EatonUPS2"]
        ````
10. Setting UP PRTG

    10.1.  Create the Device in PRTG (you can use a generic IP for the device, like 127.0.0.1)

    10.2. Create a sensor for the device, and use the "HTTP Push Data Advanced" sensor.

    10.3. Keep the port on 5050

    10.4. Change the identification token to the name of your UPS (if you have more than one UPS, you will need to create a sensor for each UPS, or 2 separate devices)
        In this example, the identification token is `EatonUPS1`

    10.5. Set "No incoming data" to  " Switch to unknown status "  

    10.6. Set the scanning interval to 10 seconds

11. Start the script by running `python3 ups-monitor.py` and check if the data is being collected and stored into the InfluxDB and into the PRTG Server.

## How to run as a systemd service
```
sudo nano /etc/systemd/system/nut-ups-stats.service
```
```
[Unit]
Description=collects data from a NUT-Monitored UPS and stores the data into an InfluxDB and into a PRTG Server


[Service]
ExecStart=/usr/bin/python3 -u /home/sutadmin/NUT-UPS-Collector/ups-monitor.py
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=default.target
```
```
sudo systemctl daemon-reload
sudo systemctl start nut-ups-stats.service
sudo systemctl enable nut-ups-stats.service
```

Check logs at:   
````
sudo journalctl -u nut-ups-stats -f
````