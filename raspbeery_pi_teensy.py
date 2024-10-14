import json
import serial
import csv
from datetime import datetime
import paho.mqtt.client as mqtt

# Open serial connection to HC-05
ser = serial.Serial('/dev/rfcomm0', 9600)

# MQTT setup
broker_address = "a2zkrkeiuchfw0-ats.iot.ap-southeast-2.amazonaws.com"  # AWS IoT endpoint
publish_topic = "sensor/data"
subscribe_topic = "command/control"
mqtt_client = mqtt.Client("RaspberryPiPublisher")

# TLS/SSL certificates for secure communication
mqtt_client.tls_set(
    ca_certs="/home/pi/certs/AmazonRootCA1.pem",  # Root CA certificate path
    certfile="/home/pi/certs/certificate.pem.crt",  # Device certificate path
    keyfile="/home/pi/certs/private.pem.key"  # Private key path
)

# Function to handle connection to MQTT broker
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT")
    print("Connection returned result: " + str(rc))
    client.subscribe(subscribe_topic)

# Function to handle received messages from MQTT broker
def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " -> " + msg.payload.decode())
    ser.write((msg.payload.decode() + '\n').encode())  # Send the received MQTT message directly over Bluetooth

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to MQTT broker using port 8883 (the default for secure MQTT with TLS)
mqtt_client.connect(broker_address, 8883, 60)

# Start MQTT loop
mqtt_client.loop_start()

# Open a CSV file to log data
with open('sensor_data.csv', 'a', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Timestamp', 'Received Data'])

    try:
        while True:
            if ser.in_waiting > 0:  # Check if there is incoming data
                incoming_data = ser.readline().decode('utf-8').strip()  # Read and decode the data
                print("Received:", incoming_data)  # Print the received data
                csvwriter.writerow([datetime.now(), incoming_data])  # Log the data with a timestamp
                
                # Variables to check for buzzer activation
                buzzer_on = False  # Default state of buzzer (off)

                # Parse sensor data and thresholds
                sensor_data = {
                    "temperature": None,
                    "heart_rate": None,
                    "shock_detected": None
                }

                if "Temperature" in incoming_data:
                    try:
                        temperature = float(incoming_data.split("Temperature: ")[1].split(" ")[0])  # Extract temperature value
                        sensor_data["temperature"] = temperature
                        if temperature > 38:  # Example threshold for high temperature
                            buzzer_on = True  # Activate buzzer for high temperature
                            print("High temperature detected, activating buzzer.")
                    except ValueError:
                        print("Error parsing temperature")
                        
                if "Heart Rate" in incoming_data:
                    try:
                        heart_rate = int(incoming_data.split("Heart Rate: ")[1].split(" ")[0])  # Extract heart rate value
                        sensor_data["heart_rate"] = heart_rate
                        if heart_rate < 40 or heart_rate > 120:  # Example thresholds for abnormal heart rate
                            
                            print("Abnormal heart rate detected")
                    except ValueError:
                        print("Error parsing heart rate")
                
                if "Shock Detected" in incoming_data:
                    try:
                        shock_detected = int(incoming_data.split("Shock Detected: ")[1].strip())  # Extract shock detected value
                        sensor_data["shock_detected"] = shock_detected
                        if shock_detected == 1:  # Shock detected condition
                            
                            print("Shock detected")
                    except ValueError:
                        print("Error parsing shock detection")



                # Publish the sensor data to MQTT in JSON format
                sensor_data_json = json.dumps(sensor_data)
                mqtt_client.publish(publish_topic, sensor_data_json)
                print("Data published to MQTT broker:", sensor_data_json)
                
                # Publish the buzzer state to MQTT
                if buzzer_on:
                    mqtt_client.publish(subscribe_topic, "BUZZER_ON")  # Publish to MQTT to activate buzzer
                else:
                    mqtt_client.publish(subscribe_topic, "BUZZER_OFF")  # Publish to MQTT to deactivate buzzer
                    print("The Temperature normal, deactivating buzzer.")

    except KeyboardInterrupt:
        print("Program interrupted by user.")
    except serial.SerialException as e:
        print(f"Serial exception: {e}")
    finally:
        ser.close()
        mqtt_client.loop_stop()
