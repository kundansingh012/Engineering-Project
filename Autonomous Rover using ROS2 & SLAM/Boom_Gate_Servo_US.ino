#include <Servo.h>

#define SERVO_PIN 9
#define TRIG_PIN_ENTER 10
#define ECHO_PIN_ENTER 11
#define TRIG_PIN_EXIT 5
#define ECHO_PIN_EXIT 6

Servo gateServo;

void setup() {
  Serial.begin(9600);
  gateServo.attach(SERVO_PIN);
  pinMode(TRIG_PIN_ENTER, OUTPUT);
  pinMode(TRIG_PIN_EXIT, OUTPUT);
  pinMode(ECHO_PIN_ENTER, INPUT);
  pinMode(ECHO_PIN_EXIT, INPUT);
  gateServo.write(0);  // start closed
  Serial.println("Dual Ultrasonic Boom Gate Ready");
}

void loop() 
{
  int distEnter = getDistance(TRIG_PIN_ENTER, ECHO_PIN_ENTER);
  delay(50);
  int distExit  = getDistance(TRIG_PIN_EXIT,  ECHO_PIN_EXIT);

  Serial.print("Entry: ");
  Serial.print(distEnter);
  Serial.print(" cm | Exit: ");
  Serial.print(distExit);
  Serial.println(" cm");

  if ((distEnter > 0 & distEnter <40) || (distExit > 0 & distExit <40))
  {
    gateServo.write(135);
    Serial.println("Rover detected: Gate open");
    delay(5000);
  }
  else
  {
    gateServo.write(45);
    Serial.println("Rover not detected: Gate close");
  }
  delay(30);
}
int getDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH, 30000);  // timeout after 30 ms
  int distance = duration * 0.034 / 2;            // Convert to cm

  if (distance <= 0 || distance > 400) return 400; // out of range
  return distance;
}