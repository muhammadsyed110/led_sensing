#include "pin_defs.h"

// Define the pin connections
const int RESET_PIN = 2;
const int CLK_PIN   = 4;
const int DATA_PIN  = 5;
const int LATCH_PIN = 3;
const int PWM_PIN   = 9;

unsigned long state = 0xE893E0;

String DON_Buff;
String LOX_Buff;
String Overall_Buffer;

#define SET_BIT_HIGH(var, bit) (var |=  (1UL << bit))
#define SET_BIT_LOW( var, bit) (var &= ~(1UL << bit))

void setup() {
  pinMode(RESET_PIN, OUTPUT);
  pinMode(CLK_PIN,   OUTPUT);
  pinMode(DATA_PIN,  OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(PWM_PIN,   OUTPUT);
  digitalWrite(PWM_PIN, HIGH);

  Serial.begin(115200);

  resetAndLatch();
  shiftOutState();
  setupTimer1ForPWM();
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    // --- handle PD matrix ("DONxy") ---
    if (command.startsWith("DON")) {
      DON_Buff = command.substring(0, 5);
      int row = command.charAt(3) - '0';
      int col = command.charAt(4) - '0';
      if (row >= 1 && row <= 5 && col >= 1 && col <= 5) {
        for (int b = 10; b <= 14; b++) SET_BIT_LOW(state, b);
        for (int b = 15; b <= 19; b++) SET_BIT_HIGH(state, b);
        int rowBit = 10 + (row - 1);
        int colBit = 15 + (col - 1);
        SET_BIT_HIGH(state, rowBit);
        SET_BIT_LOW (state, colBit);
      }
    }

    // --- handle LED matrix ("LOXxy") — now cumulative ---
    if (command.startsWith("LOX")) {
      LOX_Buff = command.substring(0, 5);
      int row = command.charAt(3) - '0';
      int col = command.charAt(4) - '0';
      if (row >= 1 && row <= 5 && col >= 1 && col <= 5) {
        int rowBit = (row - 1);
        int colBit = 5 + (col - 1);
        SET_BIT_HIGH(state, rowBit);
        SET_BIT_LOW (state, colBit);
      }
    }

    // Turn all LEDs off ("LAF")
    if (command == "LAF") {
      for (int b = 0; b <= 4; b++) SET_BIT_LOW(state, b);
      for (int b = 5; b <= 9; b++) SET_BIT_HIGH(state, b);
    }

    // Turn specific LED on/off ("LONxy" / "LOFxy")
    else if (command.length() == 5 &&
             (command.startsWith("LON") || command.startsWith("LOF"))) {
      int row    = command.charAt(3) - '0';
      int col    = command.charAt(4) - '0';
      bool onOff = command.startsWith("LON");
      if (row >= 1 && row <= 5 && col >= 1 && col <= 5) {
        int rowBit = (row - 1);
        int colBit = 5 + (col - 1);
        if (onOff) {
          SET_BIT_HIGH(state, rowBit);
          SET_BIT_LOW (state, colBit);
        } else {
          SET_BIT_LOW (state, rowBit);
          SET_BIT_HIGH(state, colBit);
        }
      }
    }

    shiftOutState();
    delayMicroseconds(200);
    analogRead(A0);  // dummy

    float a = 0.0;
    for (int i = 0; i < 100; i++) {
      a += analogRead(A0);
    }
    float avg = a / 100;

    char str[10];
    dtostrf(avg, 3, 3, str);
    Overall_Buffer = LOX_Buff + "," + DON_Buff + "," + str;
    Serial.println(Overall_Buffer);
  }
}

void shiftOutState() {
  digitalWrite(LATCH_PIN, LOW);
  for (int i = 23; i >= 0; i--) {
    digitalWrite(CLK_PIN,  LOW);
    digitalWrite(DATA_PIN, (state & (1UL << i)) ? HIGH : LOW);
    digitalWrite(CLK_PIN,  HIGH);
  }
  digitalWrite(LATCH_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(LATCH_PIN, LOW);
}

void setupTimer1ForPWM() {
  TCCR1A = 0;
  TCCR1B = 0;
  TCCR1A |= _BV(WGM11);
  TCCR1B |= _BV(WGM12) | _BV(WGM13) | _BV(CS10);
  ICR1   = 454;
  OCR1A  = 454;
  TCCR1A |= _BV(COM1A1);
}

void resetAndLatch() {
  digitalWrite(LATCH_PIN, LOW);
  digitalWrite(RESET_PIN, LOW);
  delayMicroseconds(10);
  digitalWrite(RESET_PIN, HIGH);
}
