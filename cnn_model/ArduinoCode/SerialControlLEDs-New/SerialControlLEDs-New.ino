#include "pin_defs.h"

// Shift register pins
const int RESET_PIN = 2;
const int CLK_PIN = 4;
const int DATA_PIN = 5;
const int LATCH_PIN = 3;
const int PWM_PIN = 9;

// State variable for 24-bit shift register
unsigned long state = 0xe893e0;

String command;
int selected_led_row = -1;
int selected_led_col = -1;
int selected_pd_row = -1;
int selected_pd_col = -1;

#define SET_BIT_HIGH(var, bit) (var |= (1UL << bit))
#define SET_BIT_LOW(var, bit) (var &= ~(1UL << bit))

void setup() {
  pinMode(RESET_PIN, OUTPUT);
  pinMode(CLK_PIN, OUTPUT);
  pinMode(DATA_PIN, OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(PWM_PIN, OUTPUT);
  digitalWrite(PWM_PIN, HIGH);

  Serial.begin(115200);
  resetAndLatch();
  shiftOutState();
  setupTimer1ForPWM();
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("LOX")) {
      selected_led_row = command.charAt(3) - '0';
      selected_led_col = command.charAt(4) - '0';
      if (validIndex(selected_led_row) && validIndex(selected_led_col)) {
        selectLED(selected_led_row, selected_led_col);
      }
    }
    else if (command.startsWith("DON")) {
      selected_pd_row = command.charAt(3) - '0';
      selected_pd_col = command.charAt(4) - '0';
      if (validIndex(selected_pd_row) && validIndex(selected_pd_col)) {
        selectPhotodiode(selected_pd_row, selected_pd_col);
      }
    }
    else if (command == "LAF") {
      disableAllLEDs();
    }
    else if (command == "GETVAL") {
      float sum = 0.0;
      for (int i = 0; i < 5; i++) {
        sum += analogRead(A0);
        delay(5);
      }
      float avg = sum / 5.0;
      Serial.print("{\"LED\":\"");
      Serial.print(selected_led_row);
      Serial.print(",");
      Serial.print(selected_led_col);
      Serial.print("\",\"PD\":\"");
      Serial.print(selected_pd_row);
      Serial.print(",");
      Serial.print(selected_pd_col);
      Serial.print("\",\"val\":");
      Serial.print(avg, 2);
      Serial.println("}");
    }

    shiftOutState();
  }
}

bool validIndex(int i) {
  return i >= 1 && i <= 5;
}

void selectLED(int row, int col) {
  SET_BIT_LOW(state, 0); SET_BIT_LOW(state, 1); SET_BIT_LOW(state, 2); SET_BIT_LOW(state, 3); SET_BIT_LOW(state, 4);
  SET_BIT_HIGH(state, 5); SET_BIT_HIGH(state, 6); SET_BIT_HIGH(state, 7); SET_BIT_HIGH(state, 8); SET_BIT_HIGH(state, 9);
  SET_BIT_HIGH(state, row - 1);
  SET_BIT_LOW(state, 5 + col - 1);
}

void selectPhotodiode(int row, int col) {
  SET_BIT_LOW(state, 10); SET_BIT_LOW(state, 11); SET_BIT_LOW(state, 12); SET_BIT_LOW(state, 13); SET_BIT_LOW(state, 14);
  SET_BIT_HIGH(state, 15); SET_BIT_HIGH(state, 16); SET_BIT_HIGH(state, 17); SET_BIT_HIGH(state, 18); SET_BIT_HIGH(state, 19);
  SET_BIT_HIGH(state, 10 + row - 1);
  SET_BIT_LOW(state, 15 + col - 1);
}

void disableAllLEDs() {
  SET_BIT_LOW(state, 0); SET_BIT_LOW(state, 1); SET_BIT_LOW(state, 2); SET_BIT_LOW(state, 3); SET_BIT_LOW(state, 4);
  SET_BIT_HIGH(state, 5); SET_BIT_HIGH(state, 6); SET_BIT_HIGH(state, 7); SET_BIT_HIGH(state, 8); SET_BIT_HIGH(state, 9);
}

void shiftOutState() {
  digitalWrite(LATCH_PIN, LOW);
  for (int i = 23; i >= 0; i--) {
    digitalWrite(CLK_PIN, LOW);
    digitalWrite(DATA_PIN, (state & (1UL << i)) ? HIGH : LOW);
    digitalWrite(CLK_PIN, HIGH);
  }
  digitalWrite(LATCH_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(LATCH_PIN, LOW);
}

void setupTimer1ForPWM() {
  TCCR1A = 0;
  TCCR1B = 0;
  TCCR1A |= _BV(WGM11);
  TCCR1B |= _BV(WGM12) | _BV(WGM13);
  TCCR1B |= _BV(CS10);
  ICR1 = 454;
  OCR1A = 227; // 50% duty
  TCCR1A |= _BV(COM1A1);
}

void resetAndLatch() {
  digitalWrite(LATCH_PIN, LOW);
  digitalWrite(RESET_PIN, LOW);
  delayMicroseconds(10);
  digitalWrite(RESET_PIN, HIGH);
}
