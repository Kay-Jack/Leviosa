#include <Arduino.h>
#define IN1 6
#define IN2 5
#define IN3 4
#define IN4 3
#define ENA 10
#define ENB 9


int Setpoint_X, Setpoint_Y;
void setup() {
  Serial.begin(9600);
  Serial.print("Hello, This is program to get X Y setpoint value!\r\n");
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);  // Initially set ENA and ENB to LOW
  analogWrite(ENB, 0);
}

void loop() {
  // read the value from the sensor:
  Serial.print("Setpoint_Y:");
  Serial.println(analogRead(A0));
  Serial.print("Setpoint_X:");
  Serial.println(analogRead(A1));
  delay(100);
}
