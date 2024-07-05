#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>

// Настройки для дисплея 1602 с I2C
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Настройки для клавиатуры 4x4
const byte ROWS = 4; 
const byte COLS = 4; 
char keys[ROWS][COLS] = {
  {'0','1','2','3'},
  {'4','5','6','7'},
  {'8','9','A','B'},
  {'C','D','E','F'}
};
byte rowPins[ROWS] = {5, 4, 3, 2}; 
byte colPins[COLS] = {6, 7, 8, 9}; 
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Настройки для остальных компонентов
const int buttonPin = 10;
const int passiveBuzzerPin = 11;
const int activeBuzzerPin = 12;
const int potentiometerPin = A0;
const int ledPin = 13;

// Переменные для хранения состояний
String command = "";
bool newCommand = false;

void setup() {
  Serial.begin(9600);

  // Настройки для дисплея 1602 с I2C
  lcd.init();
  lcd.backlight();

  // Настройки для остальных компонентов
  pinMode(buttonPin, INPUT);
  pinMode(passiveBuzzerPin, OUTPUT);
  pinMode(activeBuzzerPin, OUTPUT);
  pinMode(potentiometerPin, INPUT);
  pinMode(ledPin, OUTPUT);
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

  // Чтение данных с кнопки
  int buttonState = digitalRead(buttonPin);
  if (buttonState == HIGH) {
    Serial.println("BUTTON1:PRESSED");
  }

  // Чтение данных с клавиатуры
  char key = keypad.getKey();
  if (key) {
    Serial.print("KEYPAD1:");
    Serial.println(key);
  }

  // Чтение данных с потенциометра
  int potValue = map(analogRead(potentiometerPin), 0, 1023, 0, 100);
  Serial.print("POTENTIOMETER1:");
  Serial.println(potValue);

  delay(100);
}

void processCommand(String command) {
  // Пример команды: "LCD:Hello,World!"
  if (command.startsWith("LCD1:")) {
    lcd.clear();
    int commaIndex = command.indexOf(',');
    if (commaIndex != -1) {
      String line1 = command.substring(5, commaIndex);
      String line2 = command.substring(commaIndex + 1);
      lcd.setCursor(0, 0);
      lcd.print(line1);
      lcd.setCursor(0, 1);
      lcd.print(line2);
    } else {
      lcd.setCursor(0, 0);
      lcd.print(command.substring(5));
    }
  } else if (command.startsWith("LED1:")) {
    int state = command.substring(5).toInt();
    digitalWrite(ledPin, state);
  } else if (command.startsWith("PASSIVE_BUZZER1:")) {
    if (command.substring(16).equals("OFF")) {
      noTone(passiveBuzzerPin);
    } else {
      int toneValue = command.substring(16).toInt();
      tone(passiveBuzzerPin, toneValue, 2000);
    }
  } else if (command.startsWith("ACTIVE_BUZZER1:")) {
    int state = command.substring(15).toInt();
    if (state == 1) {
      digitalWrite(activeBuzzerPin, HIGH);
    } else {
      digitalWrite(activeBuzzerPin, LOW);
    }
  }
}
