#include "SevSeg.h"
SevSeg sevseg;

// Переменные для хранения состояний
String command = "";
bool newCommand = false;

void setup() {
  Serial.begin(9600);

  // Настройки для 4-значного сегментного дисплея
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
  // Чтение данных из последовательного порта
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
  // Пример команды: "4SEGMENT1:1234" или "4SEGMENT1:12.34"
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
