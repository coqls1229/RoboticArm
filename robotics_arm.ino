#include "HuemonelabKit.h"

Servo360 motor1;
Servo360 motor2;
Servo360 motor3;
int grap = 1;

void setup() {
  motor1.attach(5);
  motor2.attach(6);
  motor3.attach(7);
  motor1.write(90);
  motor2.write(90);
  motor3.write(90);
  Serial.begin(9600);
}

void loop() {
  if(Serial.available()) {
    char cmd = Serial.read();
    switch (cmd) {
    case 'a':
      motor2.write(motor2.read()-1, 30);
      break;
    case 'b':
      motor2.write(motor2.read()+1, 30);
      break;  
    case 'c':
      motor1.write(motor1.read()+1, 30);
      break;  
    case 'd':
      motor1.write(motor1.read()-1, 30);
      break;  
    case 'e':
      if (grap == 1) {
        motor3.write(40,800);
        grap = 0;
      } else if (grap ==0) {
        motor3.write(100,800);
        grap = 1;
      }
      break;
    }
  }
}
