int Setpoint_X, Setpoint_Y;
void setup() {
Serial.begin(31250);
  Serial.print("Hello, This is program to get X Y setpoint value!\r\n");
}

void loop() {
  // read the value from the sensor:
  Serial.print("Setpoint_Y:");
  Serial.println(analogRead(A0));
  delay(100);
}
