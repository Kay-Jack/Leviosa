#include <Arduino.h>

int setPoint = 350;
int sensorPin = A2;
int sensorValue = 0;
int noMagnetPoint = 450;
int IN2 = 10;
int EN = 11;
int setPoint2 = setPoint - 61;

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
      if(sensorValue >= setPoint && sensorValue <= noMagnetPoint){
        digitalWrite(EN, HIGH);
        while (sensorValue >= setPoint2 && sensorValue <= noMagnetPoint){
          sensorValue = analogRead(sensorPin);
          //Serial.println(sensorValue);
        }
        digitalWrite(EN, LOW);
      }
 }