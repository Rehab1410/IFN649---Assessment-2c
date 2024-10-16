#include <OneWire.h>
#include <DallasTemperature.h>

// Pin definitions
#define ONE_WIRE_BUS 2         // DS18B20 data pin (temperature sensor)
#define HEARTBEAT_SENSOR_PIN 20 // Heartbeat sensor pin
#define SHOCK_SENSOR_PIN 9      // Shock sensor pin
#define BUZZER_PIN 4            // Buzzer pin for alerts

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Function prototypes
float readTemperature();
int readHeartRate();
int readShockSensor();
void checkForBluetoothCommands();

// Global Variables
float temperatureC;
int heartRate;
int shockDetected = 0; 
int debounceTime = 200; // Debounce time for shock sensor

// Bluetooth Communication via Serial1
#define BLUETOOTH Serial1

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);  // Set buzzer pin as output
  Serial1.begin(9600);          // Start Bluetooth communication via Serial1
  sensors.begin();              // Initialize DS18B20 temperature sensor

  pinMode(SHOCK_SENSOR_PIN, INPUT);  // Set shock sensor pin as input
  
  // Make sure the buzzer is off initially
  digitalWrite(BUZZER_PIN, LOW);
}

void loop() {
  // Read temperature from DS18B20
  temperatureC = readTemperature();

  // Read heart rate from heartbeat sensor
  heartRate = readHeartRate();

  // Read shock sensor for fall detection
  shockDetected = readShockSensor();

  // Print sensor data to Serial Monitor (for testing/debugging)
  Serial.print("Temperature: ");
  Serial.print(temperatureC);
  Serial.print(" C, Heart Rate: ");
  Serial.print(heartRate);
  Serial.print(" BPM, Shock Detected: ");
  Serial.println(shockDetected);

  // Send sensor data via Bluetooth (Serial1)
  Serial1.print("Temperature: ");
  Serial1.print(temperatureC);
  Serial1.print(" C, Heart Rate: ");
  Serial1.print(heartRate);
  Serial1.print(" BPM, Shock Detected: ");
  Serial1.println(shockDetected);

  // Check for incoming Bluetooth commands to control the buzzer
  checkForBluetoothCommands();

  delay(1000);  // Delay for 1 second before next reading
}

// Function to read temperature from DS18B20
float readTemperature() {
  sensors.requestTemperatures();    // Request temperature from sensor
  return sensors.getTempCByIndex(0); // Get the temperature in Celsius
}

// Function to read heart rate from the heartbeat sensor
int readHeartRate() {
  int heartbeatValue = analogRead(HEARTBEAT_SENSOR_PIN);
  return map(heartbeatValue, 0, 1023, 40, 150);  // Convert to heart rate range
}

// Function to read shock sensor with debounce for fall detection
int readShockSensor() {
  int shockState = digitalRead(SHOCK_SENSOR_PIN);

  if (shockState == HIGH) {
    delay(debounceTime);  // Debounce delay
    if (digitalRead(SHOCK_SENSOR_PIN) == HIGH) {
      return 1;  // Shock detected
    }
  }
  return 0;  // no shock detected
}

// Function to check for incoming Bluetooth commands to control the buzzer
void checkForBluetoothCommands() {
  if (Serial1.available() > 0) {
    String command = Serial1.readStringUntil('\n');
    command.trim();  // Remove leading and trailing whitespace

    if (command == "BUZZER_ON") {
      digitalWrite(BUZZER_PIN, HIGH);  // Turn the buzzer on
      Serial.println("The command received is BUZZER_ON");
    } else if (command == "BUZZER_OFF") {
      digitalWrite(BUZZER_PIN, LOW);   // Turn the buzzer off
      Serial.println("The command received is BUZZER_OFF");
    } else {
      Serial.println("Unknown command received");
    }
  }
}
