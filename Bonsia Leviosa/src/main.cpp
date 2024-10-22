#include <Arduino.h>
#include <TimerOne.h>
#include <QuickPID.h>

#define IN1 4
#define IN2 3
#define IN3 7
#define IN4 8
#define ENA 6
#define ENB 5

//PID Settings//
float Setpointx, Setpointy, Inputx, Inputy, Outputx, Outputy;
float Kp = 1.5, Ki = 0, Kd = 0.015;

QuickPID PIDy(&Inputy, &Outputy, &Setpointy);
QuickPID PIDx(&Inputx, &Outputx, &Setpointx);
const uint32_t sampleTimeUs = 10000; // 10ms
volatile bool computeNow = false; 


void setup()
{
  Timer1.initialize(sampleTimeUs); //initialize timer1, and set the time interval
  Timer1.attachInterrupt(runPid);  //attaches runPid() as a timer overflow interrupt
  PIDx.SetTunings(Kp, Ki, Kd);
  PIDy.SetTunings(Kp, Ki, Kd);
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
    digitalWrite(IN3,0);
    digitalWrite(IN4,1);
    analogWrite(ENB,a);
  }
  else
  {
    a=-a;
    digitalWrite(IN3,1);
    digitalWrite(IN4,0);
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
  }
}

void runPid() {
  computeNow = true;
}