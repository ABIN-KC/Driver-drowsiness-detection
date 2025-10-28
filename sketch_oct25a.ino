#include <AFMotor_R4.h>

AF_DCMotor motor(3);   // M3 port on Adafruit Motor Shield
int speed = 200;       // Default motor speed (0–255)
int vibPin = A0;       // Vibration motor connected to analog pin A0
String state = "";     // Current received state
String lastState = ""; // To remember previous state

void setup() {
  Serial.begin(9600);
  motor.setSpeed(speed);
  pinMode(vibPin, OUTPUT);
  digitalWrite(vibPin, LOW);
}

void loop() {
  // Check for new serial input
  if (Serial.available()) {
    state = Serial.readStringUntil('\n');
    state.trim(); // Clean input
  }

  // If no new input, maintain last state
  if (state != "") lastState = state;

  // Perform actions based on last known state
  if (lastState == "AWAKE") {
    motor.setSpeed(255);
    motor.run(FORWARD);
    digitalWrite(vibPin, LOW);
  } 
  else if (lastState == "DROWSY") {
    motor.run(RELEASE);
    digitalWrite(vibPin, HIGH);  // Keep vibration ON continuously
  } 
  else {
    // Safety fallback
    motor.run(RELEASE);
    digitalWrite(vibPin, LOW);
  }

  delay(100); // Small delay for stability
}
