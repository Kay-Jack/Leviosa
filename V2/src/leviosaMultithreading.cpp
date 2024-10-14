#include <Arduino.h>

#define IN1 4
#define IN2 3
#define IN3 7
#define IN4 8
#define ENA 6
#define ENB 5

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
unsigned long lastUpdateTime = 0;  // Last time PID was updated
unsigned long updateInterval = 20;  // Update frequency in milliseconds (50 Hz)

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
}

// Timer1 interrupt service routine (ISR) for sensor reading
ISR(TIMER1_COMPA_vect) {
  sensorX = analogRead(A1);  // Read X-axis sensor
  sensorY = analogRead(A0);  // Read Y-axis sensor
}

// Function for PID control on one axis (X or Y)
float calculatePID(float setpoint, float measurement, float &previousError, float &integral) {
  float error = setpoint - measurement;
  unsigned long currentTime = millis();
  float deltaTime = (currentTime - lastUpdateTime) / 1000.0;  // Time in seconds

  integral += error * deltaTime;
  float derivative = (error - previousError) / deltaTime;
  float output = Kp * error + Ki * integral + Kd * derivative;

  previousError = error;
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

void loop() {
  unsigned long currentMillis = millis();
  
  // Check if it's time to update PID and control outputs
  if (currentMillis - lastUpdateTime >= updateInterval) {
    // Calculate PID outputs for X and Y axes
    float outputX = calculatePID(setpointX, sensorX, previousErrorX, integralX);
    float outputY = calculatePID(setpointY, sensorY, previousErrorY, integralY);
    
    // Control electromagnets based on PID output
    controlElectromagnetX(outputX);
    controlElectromagnetY(outputY);
    
    lastUpdateTime = currentMillis;  // Update the last update time
  }

  // Other non-blocking code can go here
}
