#include <Arduino.h>

int setPoint = 115;
int sensorPin = A2;
int sensorValue = 0;
int noMagnetPoint = 350;
int IN2 = 10;
int EN = 11;
int set_point2 = set_point - 61;

void setup() {
  Serial.begin(9600);
  digitalWrite(IN2, LOW);
  pinMode(EN, OUTPUT);
  digitalWrite(EN, LOW);
}

void loop()
{
      sensorValue = analogRead(sensorPin);
      //Serial.println(sensorValue);
      if(sensorValue >= set_point && sensorValue <= noMagnetPoint){
        digitalWrite(EN, HIGH);
        while (sensorValue >= set_point2 && sensorValue <= noMagnetPoint){
          sensorValue = analogRead(sensorPin);
          //Serial.println(sensorValue);
        }
        digitalWrite(EN, LOW);
      }
 }