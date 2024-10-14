#include <Arduino.h>

#define IN1 4
#define IN2 3
#define IN3 7
#define IN4 8
#define ENA 6
#define ENB 5
#define BL 2

const int numSamples = 5; // Number of samples for averaging
const int tolerance = 10; // Adjusts the sensitivity of the hall effect sensor 0-1023 is the sensors ranage

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
  digitalWrite(ENA, LOW);  // Initially set ENA and ENB to LOW
  digitalWrite(ENB, LOW);
}

// Function to read sensor values and average them
float readSensor(int pin, int numSamples) {
  delay(50); //allows coils to get to saturation
  float total = 0;
  for (int i = 0; i < numSamples; i++) {
    total += analogRead(pin);
  }
  return total / numSamples;
}

void testAxis() {
  Serial.println("Tolerance set to " + tolerance);
  float Ynorm, Yread, Xnorm, Xread;
  // Grab the normal readings without interference from the coils (averaging multiple samples)
  Ynorm = readSensor(A0, numSamples);
  Xnorm = readSensor(A1, numSamples);

  // Y Coil check
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  digitalWrite(ENB, HIGH);  // Full power to Y coil

  // Read the hall sensor with the Y coil turned on
  Yread = readSensor(A0, numSamples);
  Xread = readSensor(A1, numSamples);

  // Check if Y coil is in the correct orientation (positive deviation from Ynorm, minimal X interference)
  if ((Yread >= (Ynorm + tolerance)) && (abs(Xread - Xnorm) < tolerance)) {
    Serial.println("Y coils are correct, minimal X interference");
  }
  // Check if Y coil is in reverse orientation (negative deviation from Ynorm, minimal X interference)
  else if ((Yread <= (Ynorm - tolerance)) && (abs(Xread - Xnorm) < tolerance)) {
    Serial.println("Y coil is reversed");
  }
  // Check for coils swapped (check if X is significantly affected)
  else if (abs(Xread - Xnorm) >= tolerance) {
    Serial.println("Coils 'X' and 'Y' need to be swapped");
  }

  // Turn off the Y coil to prevent overheating
  digitalWrite(ENB, LOW);
  delay(50);

  // Grab the normal readings again for the X coil check
  Ynorm = readSensor(A0, numSamples);
  Xnorm = readSensor(A1, numSamples);

  // X Coil check
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(ENA, HIGH);  // Full power to X coil

  // Read the hall sensor with the X coil turned on
  Yread = readSensor(A0, numSamples);
  Xread = readSensor(A1, numSamples);

  // Check if X coil is in the correct orientation (positive deviation from Xnorm, minimal Y interference)
  if ((Xread >= (Xnorm + tolerance)) && (abs(Yread - Ynorm) < tolerance)) {
    Serial.println("X coils are correct, minimal Y interference");
  }
  // Check if X coil is in reverse orientation (negative deviation from Xnorm, minimal Y interference)
  else if ((Xread <= (Xnorm - tolerance)) && (abs(Yread - Ynorm) < tolerance)) {
    Serial.println("X coil is reversed");
  }
  // Check for coils swapped (check if Y is significantly affected)
  else if (abs(Yread - Ynorm) >= tolerance) {
    Serial.println("Coils 'Y' and 'X' need to be swapped");
  }

  // Turn off the X coil to prevent overheating
  digitalWrite(ENA, LOW);

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
