# NUT-UPS-Collector
Script that collects data from a NUT-Monitored UPS and stores the data into an InfluxDB and into a PRTG Server

## How to setup
1. Install NUT (Network UPS Tools) on the machine that is connected to the UPS
2. ...

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