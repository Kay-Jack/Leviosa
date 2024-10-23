#include <Arduino.h>
#include <TimerOne.h>
#include <QuickPID.h>

#define IN1 6
#define IN2 5
#define IN3 4
#define IN4 3
#define ENA 10
#define ENB 9

//PID Settings//
float Setpointx, Setpointy, Inputx, Inputy, Outputx, Outputy;
float Kp = 1.5, Ki = 0, Kd = 0.015;

QuickPID PIDy(&Inputy, &Outputy, &Setpointy);
QuickPID PIDx(&Inputx, &Outputx, &Setpointx);
const uint32_t sampleTimeUs = 1000; // 1ms
volatile bool computeNow = false; 

void runPid() {
  computeNow = true;
}

void calibrateSensors() {
  float totalX = 0, totalY = 0, calibrationSamples = 10;

  // Take multiple readings and compute average
  for (int i = 0; i < calibrationSamples; i++) {
    totalX += analogRead(A1);  // Read X-axis sensor
    totalY += analogRead(A0);  // Read Y-axis sensor
    delay(10);
  }

  // Calculate average values for setpoints
  Setpointx = totalX / calibrationSamples;
  Setpointy = totalY / calibrationSamples;

  // Optionally, print the setpoints for debugging
  Serial.begin(9600);
  Serial.print("Calibrated Setpoint X: ");
  Serial.println(Setpointx);
  Serial.print("Calibrated Setpoint Y: ");
  Serial.println(Setpointy);
  //Serial.end();
}


void setup()
{
  Timer1.initialize(sampleTimeUs); //initialize timer1, and set the time interval
  Timer1.attachInterrupt(runPid);  //attaches runPid() as a timer overflow interrupt
  PIDx.SetTunings(Kp, Ki, Kd);
  PIDy.SetTunings(Kp, Ki, Kd);
  PIDy.SetOutputLimits(-255,255);
  PIDx.SetOutputLimits(-255,255);
  PIDx.SetMode(1);
  PIDy.SetMode(1);


  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);
  pinMode(IN3,OUTPUT);
  pinMode(IN4,OUTPUT);
  pinMode(ENA,OUTPUT);
  pinMode(ENB,OUTPUT);
  digitalWrite(IN1,0);
  digitalWrite(IN2,0);
  digitalWrite(IN3,0);
  digitalWrite(IN4,0);
  analogWrite(ENA,0);
  analogWrite(ENB,0);

  calibrateSensors();
  Serial.println(Setpointy);
}

void turn_X(int a)
{
  if(a>=0)
  {
    digitalWrite(IN1,1);
    digitalWrite(IN2,0);
    analogWrite(ENA,a);
  }
  else
  {
    a=-a;
    digitalWrite(IN1,0);
    digitalWrite(IN2,1);
    analogWrite(ENA,a);
  }
}

void turn_Y(int a)
{
  if(a>=0)
  {
    digitalWrite(IN3,1);
    digitalWrite(IN4,0);
    analogWrite(ENB,a);
  }
  else
  {
    a=-a;
    digitalWrite(IN3,0);
    digitalWrite(IN4,1);
    analogWrite(ENB,a);
  }
}

void loop()
{  
  if (computeNow) {
    Inputx = analogRead(A1);
    Inputy = analogRead(A0);

    PIDx.Compute();
    PIDy.Compute();

    turn_X(Outputx);
    turn_Y(Outputy);

    computeNow = false;
    Serial.println(Outputx);
    Serial.println(Outputy);

  }

}