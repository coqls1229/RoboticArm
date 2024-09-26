#include "HuemonelabKit.h"

Servo360 motor1;
Servo360 motor2;
Servo360 motor3;
JoyStick joystick1(A0, A1);
JoyStick joystick2(A2, A3);

int check(Servo360 mot, int x) {
  int i = mot.read();
  if (x < 100) {
    i = i - 1;
  }
  if (x > 950) {
    i = i + 1;
  }
  return i;
}

void setup() {
  motor1.attach(5);
  motor2.attach(6);
  motor3.attach(7);
  motor1.write(90);
  motor2.write(90);
  motor3.write(90);
}

void loop() {
  int x = joystick1.read('x');
  int y = joystick1.read('y');
  int clamp = joystick2.read('x');
  motor1.write(check(motor1, x));
  motor2.write(check(motor2, y));
  motor3.write(check(motor3,clamp));
  delay(20);
}
