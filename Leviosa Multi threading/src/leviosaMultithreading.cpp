#include <Arduino.h>

#define IN1 6
#define IN2 5
#define IN3 4
#define IN4 3
#define ENA 10
#define ENB 9

volatile float sensorX = 0;  // Shared variable for X-axis Hall sensor reading
volatile float sensorY = 0;  // Shared variable for Y-axis Hall sensor reading

// PID constants for both axes
float Kp = 0.5, Ki = 0.05, Kd = 0.01;
float previousErrorX = 0, previousErrorY = 0;
float integralX = 0, integralY = 0;

// Setpoint values for the sensor readings
float setpointX = 565; // Midpoint of analog range (0-1023)
float setpointY = 565;

// Timing variables
unsigned long lastUpdateTimeX = 0;  // Last time PID was updated for X-axis
unsigned long lastUpdateTimeY = 0;  // Last time PID was updated for Y-axis
unsigned long updateInterval = 20;  // Update frequency in milliseconds (50 Hz)

// Calibration parameters
const int calibrationSamples = 100; // Number of samples to average during calibration
const int calibrationDelay = 10;    // Delay between samples (in ms)

// Function prototypes
void calibrateSensors(); // Forward declaration
float readSensorAverage(int pin, int numSamples);

// Setup function
void setup() { 
  // Pin setup for electromagnets
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  // Timer1 for sensor reading at high frequency
  cli();  // Stop interrupts
  TCCR1A = 0;  // Clear Timer1 register
  TCCR1B = 0;
  TCNT1 = 0;   // Initialize counter to 0
  OCR1A = 1067;  // Compare value for 15kHz (16000000 / (15kHz * 8) - 1)
  TCCR1B |= (1 << WGM12);  // CTC mode
  TCCR1B |= (1 << CS11);   // Prescaler 8
  TIMSK1 |= (1 << OCIE1A); // Enable Timer1 compare interrupt
  sei();  // Enable interrupts

  // Run calibration at startup
  calibrateSensors();
}

// Timer1 interrupt service routine (ISR) for sensor reading
ISR(TIMER1_COMPA_vect) {
  sensorX = analogRead(A1);  // Read X-axis sensor
  sensorY = analogRead(A0);  // Read Y-axis sensor
}

// Define tolerance value for small changes in the sensor readings
float tolerance = 5.0;  // Adjust this value as needed

// Function for PID control on one axis (X or Y) with tolerance
float calculatePID(float setpoint, float measurement, float &previousError, float &integral, unsigned long &lastTime) {
  float error = setpoint - measurement;

  // Check if the error is within the tolerance range
  if (abs(error) < tolerance) {
    return 0;  // Output zero if the error is too small
  }

  unsigned long currentTime = millis();
  float deltaTime = (currentTime - lastTime) / 1000.0;  // Time in seconds

  if (deltaTime <= 0) {  // Avoid division by zero
    deltaTime = 0.001;   // Smallest possible time difference (1ms)
  }

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
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, min(output, 255));  // Cap PWM signal to 255
  } else {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, min(abs(output), 255));
  }
}

void controlElectromagnetY(float output) {
  if (output > 0) {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, min(output, 255));  // Cap PWM signal to 255
  } else {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, min(abs(output), 255));
  }
}

// Calibration function to average sensor readings and set setpoints
void calibrateSensors() {
  float totalX = 0, totalY = 0;

  // Take multiple readings and compute average
  for (int i = 0; i < calibrationSamples; i++) {
    totalX += analogRead(A1);  // Read X-axis sensor
    totalY += analogRead(A0);  // Read Y-axis sensor
    delay(calibrationDelay);
  }

  // Calculate average values for setpoints
  setpointX = totalX / calibrationSamples;
  setpointY = totalY / calibrationSamples;

  // Optionally, print the setpoints for debugging
  Serial.begin(9600);
  Serial.print("Calibrated Setpoint X: ");
  Serial.println(setpointX);
  Serial.print("Calibrated Setpoint Y: ");
  Serial.println(setpointY);
  Serial.end();
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Update X-axis PID and control
  if (currentMillis - lastUpdateTimeX >= updateInterval) {
    float outputX = calculatePID(setpointX, sensorX, previousErrorX, integralX, lastUpdateTimeX);
    controlElectromagnetX(outputX);
  }

  // Update Y-axis PID and control
  if (currentMillis - lastUpdateTimeY >= updateInterval) {
    float outputY = calculatePID(setpointY, sensorY, previousErrorY, integralY, lastUpdateTimeY);
    controlElectromagnetY(outputY);
  }

  // Other non-blocking code can go here
}
