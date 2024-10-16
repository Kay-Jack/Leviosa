#include <Arduino.h>

#define IN1 4
#define IN2 3
#define IN3 7
#define IN4 8
#define ENA 6
#define ENB 5
#define BL 2

const int numSamples = 5; // Number of samples for averaging
const int tolerance = 10; // Adjusts the sensitivity of the hall effect sensor 0-1023 is the sensors range

void setup() {
  Serial.begin(9600);  // Start the serial communication
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(BL, OUTPUT);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);  // Initially set ENA and ENB to LOW
  analogWrite(ENB, 0);
}

// Function to read sensor values and average them
float readSensor(int pin, int numSamples) {
  delay(50); // Allows coils to get to saturation
  float total = 0;
  for (int i = 0; i < numSamples; i++) {
    total += analogRead(pin);
  }
  return total / numSamples;
}

void testAxis() {
  delay(50);
  Serial.println(" \n Tolerance set to " + String(tolerance));
  float Ynorm, Yread, Xnorm, Xread;

  // Grab the normal readings without interference from the coils (averaging multiple samples)
  Ynorm = readSensor(A0, numSamples);
  Xnorm = readSensor(A1, numSamples);
  Serial.println("Initial Sensor Readings:");
  Serial.print("Ynorm: "); Serial.println(Ynorm);
  Serial.print("Xnorm: "); Serial.println(Xnorm);
  delay(500);

  // Y Coil check
  Serial.println("Activating Y coil...");
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, 255);  // Full power to Y coil
  delay(100);  // Delay to allow coil to activate

  // Read the hall sensor with the Y coil turned on
  Yread = readSensor(A0, numSamples);
  Xread = readSensor(A1, numSamples);
  Serial.println("Sensor Readings with Y Coil ON:");
  Serial.print("Yread: "); Serial.println(Yread);
  Serial.print("Xread: "); Serial.println(Xread);
  delay(500);

  // Check if Y coil is in the correct orientation
  if ((Yread >= (Ynorm + tolerance)) && (abs(Xread - Xnorm) < tolerance)) {
    Serial.println("Y coils are correct, minimal X interference");
  }
  else if ((Yread <= (Ynorm - tolerance)) && (abs(Xread - Xnorm) < tolerance)) {
    Serial.println("Y coil is reversed");
  }
  else if (abs(Xread - Xnorm) >= tolerance) {
    Serial.println("Coils 'X' and 'Y' need to be swapped");
  }
  else {
    Serial.println("Y coil test did not pass");
  }

  // Turn off the Y coil to prevent overheating
  Serial.println("Turning off Y coil...");
  analogWrite(ENB, 0);  
  delay(500);  // Increased delay to ensure coil has turned off

  // Grab the normal readings again for the X coil check
  Ynorm = readSensor(A0, numSamples);
  Xnorm = readSensor(A1, numSamples);
  Serial.println("Rechecking Sensor Readings:");
  Serial.print("Ynorm: "); Serial.println(Ynorm);
  Serial.print("Xnorm: "); Serial.println(Xnorm);
  delay(500);

  // X Coil check
  Serial.println("Activating X coil...");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, 255);    // Full power to X coil
  delay(500);  // Delay to allow coil to activate

  // Read the hall sensor with the X coil turned on
  Yread = readSensor(A0, numSamples);
  Xread = readSensor(A1, numSamples);
  Serial.println("Sensor Readings with X Coil ON:");
  Serial.print("Yread: "); Serial.println(Yread);
  Serial.print("Xread: "); Serial.println(Xread);
  delay(500);

  // Check if X coil is in the correct orientation
  if ((Xread >= (Xnorm + tolerance)) && (abs(Yread - Ynorm) < tolerance)) {
    Serial.println("X coils are correct, minimal Y interference");
  }
  else if ((Xread <= (Xnorm - tolerance)) && (abs(Yread - Ynorm) < tolerance)) {
    Serial.println("X coil is reversed");
  }
  else if (abs(Yread - Ynorm) >= tolerance) {
    Serial.println("Coils 'Y' and 'X' need to be swapped");
  }
  else {
    Serial.println("X coil test did not pass");
  }

  // Turn off the X coil to prevent overheating
  Serial.println("Turning off X coil...");
  analogWrite(ENA, 0);  
  delay(500);  // Increased delay to ensure coil has turned off

  Serial.println(  
    "  ____                      _      _        \n"
    " / ___|___  _ __ ___  _ __ | | ___| |_ ___  \n"
    "| |   / _ \\| '_ ` _ \\| '_ \\| |/ _ \\ __/ _ \\ \n"
    "| |__| (_) | | | | | | |_) | |  __/ ||  __/ \n"
    " \\____\\___/|_| |_| |_| .__/|_|\\___|\\__\\___| \n"
    "                     |_|                    \n"
  );
}

void takeInput() {
  // Prompt user for input
  Serial.println("Press Enter to start the test: ");
  
  // Wait for the user to press Enter (newline)
  while (Serial.available() == 0) {}  // Wait for input

  // Read the input but ignore the actual content, only care that Enter was pressed
  String userInput = Serial.readString();  // Reading the input, including the newline character

  // Once Enter is pressed, start the test
  Serial.println("Starting test...");
  testAxis();
}

void loop() {
  takeInput();
}
