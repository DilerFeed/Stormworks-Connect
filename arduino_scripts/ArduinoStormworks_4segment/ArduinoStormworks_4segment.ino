#include "SevSeg.h"
SevSeg sevseg;

// Variables for storing states
String command = "";
bool newCommand = false;

void setup() {
  Serial.begin(9600);

  // Settings for 4-digit segment display
  byte numDigits = 4;
  byte digitPins[] = {10, 11, 12, 13};
  byte segmentPins[] = {9, 2, 3, 5, 6, 8, 7, 4};

  bool resistorsOnSegments = true; 
  bool updateWithDelaysIn = true;
  byte hardwareConfig = COMMON_CATHODE; 
  sevseg.begin(hardwareConfig, numDigits, digitPins, segmentPins, resistorsOnSegments);
  sevseg.setBrightness(90);
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
}

void processCommand(String command) {
  // Example command: "4SEGMENT1:1234" or "4SEGMENT1:12.34"
  if (command.startsWith("4SEGMENT1:")) {
    String number = command.substring(10);
    int decimalPosition = number.indexOf('.');
    if (decimalPosition != -1) {
      number.remove(decimalPosition, 1); // Удалить точку из строки
      sevseg.setNumber(number.toInt(), number.length() - decimalPosition);
    } else {
      sevseg.setNumber(number.toInt());
    }
  }
}
