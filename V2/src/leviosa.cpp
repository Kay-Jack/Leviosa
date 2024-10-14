#include <Arduino.h>

#define IN1 4  // X-axis coil pins
#define IN2 3
#define ENA 6  // X-axis enable pin

#define IN3 7  // Y-axis coil pins
#define IN4 8
#define ENB 5  // Y-axis enable pin

#define BL 2   // Optional for other control (e.g., LED)

// PID Constants
float Kp = 1.0;  // Ballpark values, to be tuned
float Ki = 0.1;
float Kd = 0.05;

// Variables for PID
float errorX, errorY;
float lastErrorX = 0, lastErrorY = 0;
float integralX = 0, integralY = 0;
float derivativeX, derivativeY;

int targetX = 565;  // Target values (center position)
int targetY = 565;

const int numSamples = 5; // Number of samples for averaging
const int tolerance = 10; // Sensor sensitivity tolerance

// Timing variables
unsigned long lastUpdateTime = 0;  // Last time PID was updated
unsigned long updateInterval = 20;  // Update frequency in milliseconds (50Hz)

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
  
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

float readSensor(int pin) {
  float total = 0;
  for (int i = 0; i < numSamples; i++) {
    total += analogRead(pin);
  }
  return total / numSamples;
}

void controlAxis(float error, float& integral, float& lastError, float& output, int INa, int INb, int EN) {
  integral += error;  // Sum of errors (Integral)
  float derivative = error - lastError;  // Change in error (Derivative)
  output = Kp * error + Ki * integral + Kd * derivative;  // PID output
  lastError = error;  // Store last error
  
  // Control coils based on PID output
  if (output > 0) {
    digitalWrite(INa, HIGH);  // Set the correct polarity
    digitalWrite(INb, LOW);
  } else {
    digitalWrite(INa, LOW);
    digitalWrite(INb, HIGH);
  }
  analogWrite(EN, constrain(abs(output), 0, 255));  // Control the power (PWM)
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Check if it's time to update PID and control outputs
  if (currentMillis - lastUpdateTime >= updateInterval) {
    // Read sensor values for both axes
    float sensorX = readSensor(A1);
    float sensorY = readSensor(A0);

    // Calculate error for both axes
    errorX = targetX - sensorX;
    errorY = targetY - sensorY;

    // PID control for X and Y axis
    float outputX, outputY;
    controlAxis(errorX, integralX, lastErrorX, outputX, IN1, IN2, ENA);
    controlAxis(errorY, integralY, lastErrorY, outputY, IN3, IN4, ENB);
    
    lastUpdateTime = currentMillis;  // Update the last update time
  }

  // Other non-blocking code can go here
}
