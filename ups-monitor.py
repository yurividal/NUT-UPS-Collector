import subprocess
from influxdb import InfluxDBClient
import time
import requests
import xml.etree.ElementTree as ET

PRTG_IP = "192.168.36.13"
INFLUXDB_IP = "192.168.36.14"
UPS_NAMES = ["EatonUPS1", "EatonUPS2"]


def send_to_prtg(data, ups_name):
    print("Sending data to PRTG")
    try:
        # PRTG HTTP Push Data Advanced sensor URL
        sensor_url = "http://" + PRTG_IP + ":5050/" + ups_name

        # Prepare payload
        prtg_element = ET.Element("prtg")

        for key, value in data.items():
            if value.isdigit():
                result_element = ET.SubElement(prtg_element, "result")
                channel_element = ET.SubElement(result_element, "channel")
                channel_element.text = key
                value_element = ET.SubElement(result_element, "value")
                value_element.text = str(int(value))
            elif value.replace(".", "", 1).isdigit():
                result_element = ET.SubElement(prtg_element, "result")
                channel_element = ET.SubElement(result_element, "channel")
                channel_element.text = key
                value_element = ET.SubElement(result_element, "value")
                value_element.text = str(float(value))
                float_element = ET.SubElement(result_element, "float")
                float_element.text = "1"

        text_element = ET.SubElement(prtg_element, "text")
        if data.get("input.voltage") == "0":
            text_element.text = "UPS ON BATTERY POWER"
        else:
            text_element.text = "UPS healthy"

        payload = ET.tostring(prtg_element, encoding="utf-8", method="xml")

        # Send data to PRTG
        response = requests.post(
            sensor_url, data=payload, headers={"Content-Type": "application/xml"}
        )

        # Check response status
        if response.status_code == 200:
            print("Data sent to PRTG successfully")
        else:
            print(f"Failed to send data to PRTG. Error: {response.text}")
    except Exception as e:
        print(f"An error occurred while sending data to PRTG: {str(e)}")

    # print the formatted xml
    # print(ET.tostring(prtg_element, encoding="utf-8", method="xml"))


def write_to_influxdb(data, ups_name):
    print("Writing data to InfluxDB")
    try:
        # Configure InfluxDB connection
        client = InfluxDBClient(host=INFLUXDB_IP, port=8086)
        client.switch_database("telegraf")

        # Prepare data points
        points = []
        for key, value in data.items():
            # Convert value to appropriate data type
            if value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit():
                value = float(value)
            else:
                value = str(value)

            point = {
                "measurement": "ups_data",
                "tags": {"ups_name": ups_name},
                "fields": {key: value},
            }
            points.append(point)

        # Write data points to InfluxDB
        client.write_points(points)
    except Exception as e:
        print(f"An error occurred while writing data to InfluxDB: {str(e)}")


def parse_upsc_output(output, ups_name):
    print("Parsing results")
    try:
        # Parse the output here according to your requirements
        lines = output.split("\n")
        data = {}
        for line in lines:
            if line:
                key, value = line.split(": ")
                data[key] = value

        # Write data to InfluxDB
        write_to_influxdb(data, ups_name)

        send_to_prtg(data, ups_name)
    except Exception as e:
        print(f"An error occurred while parsing upsc output: {str(e)}")


def main():
    while True:
        try:
            for ups_name in UPS_NAMES:
                print("Getting data for " + ups_name)
                command = f"/usr/bin/upsc {ups_name}"
                process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                output, error = process.communicate()
                # Check for any errors
                if error:
                    print(f"Error: {error.decode()}")
                else:
                    # Parse the output
                    parse_upsc_output(output.decode(), ups_name)
            print("Sleeping for 10 seconds")
            time.sleep(10)
        except Exception as e:
            print(f"An error occurred in the main loop: {str(e)}")


if __name__ == "__main__":
    main()
