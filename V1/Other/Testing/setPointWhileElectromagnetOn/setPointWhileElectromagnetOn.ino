#define IN1 6
#define IN2 5
#define IN3 4
#define IN4 3
#define ENA 2
#define ENB 7

#define lv1 50

int eAve_X, eAve_Y;
int timeReadings = 2;
float beta = 0.2;

void setup() {
  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);
  pinMode(IN3,OUTPUT);
  pinMode(IN4,OUTPUT);
  pinMode(ENA,OUTPUT);
  pinMode(ENB,OUTPUT);
  // pinMode(BL,OUTPUT);
  digitalWrite(IN1,0);
  digitalWrite(IN2,0);
  digitalWrite(IN3,0);
  digitalWrite(IN4,0);
  analogWrite(ENA,0);
  analogWrite(ENB,0);

  eAve_X = analogRead(A1);
  eAve_Y = analogRead(A0);


  Serial.begin(31250);
  Serial.print("Hello, This is program to understand impacts of electromagnet positioning on hall effect readings\r\n");

}

void loop() {
  // read the value from the sensor:

  digitalWrite(IN3,0);
  digitalWrite(IN4,0);
  analogWrite(ENB,0);
  for (int i = 0; i <= lv1; i++) {
    Serial.print("electromagnet:");
    Serial.print(550);
    Serial.print(",");
    Serial.print("Setpoint_Y:");
    Serial.print(analogRead(A0));
    Serial.print(",");

    eAve_Y = beta * eAve_Y + (1 - beta) * analogRead(A0);
    Serial.print("exp_ave_Y:");
    Serial.println(eAve_Y);
    delay(timeReadings);
  }

  digitalWrite(IN3,1);
  digitalWrite(IN4,0);
  analogWrite(ENB,1);
  for (int i = 0; i <= lv1; i++) {
    Serial.print("electromagnet:");
    Serial.print(600);
    Serial.print(",");
    Serial.print("Setpoint_Y:");
    Serial.print(analogRead(A0));
    Serial.print(",");

    eAve_Y = beta * eAve_Y + (1 - beta) * analogRead(A0);
    Serial.print("exp_ave_Y:");
    Serial.println(eAve_Y);
    delay(timeReadings);
  }
  
  digitalWrite(IN3,0);
  digitalWrite(IN4,1);
  analogWrite(ENB,1);
  for (int i = 0; i <= lv1; i++) {
    Serial.print("electromagnet:");
    Serial.print(500);
    Serial.print(",");
    Serial.print("Setpoint_Y:");
    Serial.print(analogRead(A0));
    Serial.print(",");

    eAve_Y = beta * eAve_Y + (1 - beta) * analogRead(A0);
    Serial.print("exp_ave_Y:");
    Serial.println(eAve_Y);
    delay(timeReadings);
  }
}
