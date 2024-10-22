#include <Arduino.h>

#define IN1 6 //6
#define IN2 5 //5
#define IN3 4 //4
#define IN4 3 //3
#define ENA 10
#define ENB 9

volatile float sensorX = 0;  // Shared variable for X-axis Hall sensor reading
volatile float sensorY = 0;  // Shared variable for Y-axis Hall sensor reading

// PID constants for both axes
float Kp = 1, Ki = 0.0, Kd = 0.01; // 00.001, 0.0005
float previousErrorX = 0, previousErrorY = 0;
float integralX = 0, integralY = 0;

// Setpoint values for the sensor readings
float setpointX; // Midpoint of analog range (0-1023)
float setpointY;

// Timing variables
unsigned long lastUpdateTimeX = 0;  // Last time PID was updated for X-axis
unsigned long lastUpdateTimeY = 0;  // Last time PID was updated for Y-axis
unsigned long updateInterval = 1; // Update frequency in milliseconds (1000 Hz) /max 0.01

// Calibration parameters
const int calibrationSamples = 200; // Number of samples to average during calibration

// Function prototypes
void calibrateSensors();
float readSensorAverage(int pin, int numSamples);

void setup() { 
  // Pin setup for electromagnets
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  // Run calibration at startup
  calibrateSensors();
}

float readSensorAverage(int pin, int numSamples) {
  float total = 0;

  for (int i = 0; i < numSamples; i++) {
    total += analogRead(pin);  // Read sensor
  }
  return total / numSamples;  // Return average
}

// Function for PID control on one axis (X or Y)
float calculatePID(float setpoint, float measurement, float &previousError, float &integral, unsigned long &lastTime) {
  float error = setpoint - measurement;
  unsigned long currentTime = millis();
  float deltaTime = (currentTime - lastTime) / 1000.0;  // Time in seconds

  // Calculate integral and derivative
  integral += error * deltaTime;
  float derivative = (error - previousError) / deltaTime;
  float output = Kp * error + Ki * integral + Kd * derivative;

  // Update error and time for the next iteration
  previousError = error;
  lastTime = currentTime;

  return output;
}

void controlElectromagnetX(float output) {
  if (output > 0) {
    analogWrite(ENA, min(output, 255));  // Cap PWM signal to 50
    digitalWrite(IN1, HIGH); //low
    digitalWrite(IN2, LOW);
  } else {
    analogWrite(ENA, min(abs(output), 255));
    digitalWrite(IN1, LOW); //high
    digitalWrite(IN2, HIGH);
  }
}

void controlElectromagnetY(float output) {
  if (output > 0) {
    analogWrite(ENB, min(output, 255));  // Cap PWM signal to 50
    digitalWrite(IN3, HIGH); //low
    digitalWrite(IN4, LOW);
  } else {
    analogWrite(ENB, min(abs(output), 255));
    digitalWrite(IN3, LOW); //high
    digitalWrite(IN4, HIGH);
  }
}

// Calibration function to average sensor readings and set setpoints
void calibrateSensors() {
  setpointX = readSensorAverage(A1, calibrationSamples);  // X-axis
  setpointY = readSensorAverage(A0, calibrationSamples);  // Y-axis
}

void loop() {
  unsigned long currentMillis = millis();

  // Read live sensor values for X and Y axes
  sensorX = readSensorAverage(A1, 10); // Read X-axis sensor

  // Update X-axis PID and control
  if (currentMillis - lastUpdateTimeX >= updateInterval) {
    float outputX = calculatePID(setpointX, sensorX, previousErrorX, integralX, lastUpdateTimeX);
    controlElectromagnetX(outputX);
  }

  sensorY = readSensorAverage(A0, 10); // Read Y-axis sensor

  // Update Y-axis PID and control
  if (currentMillis - lastUpdateTimeY >= updateInterval) {
    float outputY = calculatePID(setpointY, sensorY, previousErrorY, integralY, lastUpdateTimeY);
    controlElectromagnetY(outputY);
  }
}
