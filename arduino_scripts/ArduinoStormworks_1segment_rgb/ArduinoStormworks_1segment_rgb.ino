#include <Wire.h>
#include "SevSeg.h"

// Settings for 1-digit segment display
SevSeg sevseg; 

// Settings for RGB LED
int redPin = 10;
int greenPin = 11;
int bluePin = 12;

// Variables for storing states
String command = "";
bool newCommand = false;

void setup() {
  Serial.begin(9600);

  // Settings for segment display
  byte numDigits = 1;
  byte digitPins[] = {};
  byte segmentPins[] = {6, 5, 2, 3, 4, 7, 8, 9}; // Update your pins to the ones you use.

  bool resistorsOnSegments = true;
  byte hardwareConfig = COMMON_CATHODE; 
  sevseg.begin(hardwareConfig, numDigits, digitPins, segmentPins, resistorsOnSegments);
  sevseg.setBrightness(90);

  // Settings for RGB LED
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void loop() {
  // Reading data from a serial port
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      newCommand = true;
      break;
    } else {
      command += inChar;
    }
  }

  if (newCommand) {
    processCommand(command);
    command = "";
    newCommand = false;
  }

  sevseg.refreshDisplay();
  delay(100);
}

void processCommand(String command) {
  // Example command: "1SEGMENT1:1" or "RGB1:255,0,0"
  if (command.startsWith("1SEGMENT1:")) {
    int number = command.substring(10).toInt();
    sevseg.setNumber(number);
  } else if (command.startsWith("RGB1:")) {
    if (command.substring(5).equals("OFF")) {
      setRGB(0, 0, 0);
    } else {
      int commaIndex1 = command.indexOf(',');
      int commaIndex2 = command.indexOf(',', commaIndex1 + 1);
      int red = command.substring(5, commaIndex1).toInt();
      int green = command.substring(commaIndex1 + 1, commaIndex2).toInt();
      int blue = command.substring(commaIndex2 + 1).toInt();
      setRGB(red, green, blue);
    }
  }
}

void setRGB(int red, int green, int blue) {
  analogWrite(redPin, red);
  analogWrite(greenPin, green);
  analogWrite(bluePin, blue);
}
