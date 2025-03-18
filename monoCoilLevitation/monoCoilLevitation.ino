#include <Arduino.h>

int set_point = 125;//125  // 260 stable with new separated magnets50 stable with old magnet ring & floating magnet pen | change 280 is stable; 210 is stable. Lower values OK too, slightly better for 2 magnet arrangement 150 worked for 1 
// separated magnets work better for ensuring floating in the center
int sensorPin = A2;
int sensorValue = 0;
int noMagnetPoint = 450;
int IN2 = 10;
int EN = 11;
int set_point2 = set_point - 10;

// hall sensor reads ~560-570 passively with just permanent magnets. smaller magnet ring reads ~10-20 lower
// reading drops to ~450-460 when electromagnet is ON

void setup() {
  Serial.begin(9600);
  //digitalWrite(IN1, LOW);
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
        while (sensorValue >= set_point2 && sensorValue <= noMagnetPoint){ // may not need second condition
          sensorValue = analogRead(sensorPin);
          //Serial.println(sensorValue);
        }
        digitalWrite(EN, LOW);
      }// system turns on
      //else {
      //  digitalWrite(EN, LOW);
      //}
 }