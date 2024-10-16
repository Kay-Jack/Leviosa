#include <Arduino.h>

int Setpoint_X, Setpoint_Y;
void setup() {
Serial.begin(9600);
  Serial.print("Hello, This is program to get X Y setpoint value!\r\n");
}

void loop() {
  // read the value from the sensor:
  Serial.print("Setpoint_Y:");
  Serial.println(analogRead(A0));
  Serial.print("Setpoint_X:");
  Serial.println(analogRead(A1));
  delay(100);
}
