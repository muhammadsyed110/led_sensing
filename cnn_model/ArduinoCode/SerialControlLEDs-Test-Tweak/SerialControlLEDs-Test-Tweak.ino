#include "pin_defs.h"

// Define the pin connections
const int RESET_PIN = 2;
const int CLK_PIN   = 4;
const int DATA_PIN  = 5;
const int LATCH_PIN = 3;
const int PWM_PIN   = 9;  // Timer1 controlled PWM pin

// Initialize the 24-bit state variable
unsigned long state = 0xe893e0;

String DON_Buff;
String LOX_Buff;
String Overall_Buffer;

// Macros for bit manipulation
#define SET_BIT_HIGH(var, bit) (var |=  (1UL << bit))
#define SET_BIT_LOW( var, bit) (var &= ~(1UL << bit))

void setup() {
  // Set pin modes
  pinMode(RESET_PIN, OUTPUT);
  pinMode(CLK_PIN,   OUTPUT);
  pinMode(DATA_PIN,  OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(PWM_PIN,   OUTPUT);
  digitalWrite(PWM_PIN, HIGH); // Turn LEDs on if any

  // Start serial communication
  Serial.begin(115200);

  // Reset and setup shift register
  resetAndLatch();
  
  // Send initial state to shift register
  shiftOutState();

  // Setup Timer1 for 35 kHz PWM
  setupTimer1ForPWM();
}

void loop() {
  // Check for incoming Serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    // --- handle PD matrix ("DONxy") ---
    if (command.startsWith("DON")) {
      DON_Buff = command.substring(0, 5);
      int row = command.charAt(3) - '0';
      int col = command.charAt(4) - '0';
      if (row >= 1 && row <= 5 && col >= 1 && col <= 5) {
        // PD bit positions 10–19
        int rowBit = 10 + (row - 1);
        int colBit = 15 + (col - 1);
        // switch off all PD bits
        for (int b = 10; b <= 14; b++) SET_BIT_LOW(state, b);
        for (int b = 15; b <= 19; b++) SET_BIT_HIGH(state, b);
        // switch on requested PD
        SET_BIT_HIGH(state, rowBit);
        SET_BIT_LOW (state, colBit);
      }
    }

    // --- handle LED matrix ("LOXxy") ---
    if (command.startsWith("LOX")) {
      LOX_Buff = command.substring(0, 5);
      int row = command.charAt(3) - '0';
      int col = command.charAt(4) - '0';
      if (row >= 1 && row <= 5 && col >= 1 && col <= 5) {
        // LED bit positions 0–9
        int rowBit = (row - 1);
        int colBit = 5 + (col - 1);
        // switch off all LED bits
        for (int b = 0; b <= 4; b++) SET_BIT_LOW(state, b);
        for (int b = 5; b <= 9; b++) SET_BIT_HIGH(state, b);
        // switch on requested LED
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

    // --- update hardware & read sensor with software tweak ---
    shiftOutState();
    
    // (A) allow outputs to settle
    delayMicroseconds(200);
    
    // dummy read to clear any first-sample anomaly
    analogRead(A0);
    
    // true averaging loop
    float a   = 0.0;
    int   Num = 100; 
    for (int i = 0; i < Num; i++) {
      a += analogRead(A0);
    }
    float avg = a / Num;
    
    // convert to string and send back
    char str[10];
    dtostrf(avg, 3, 3, str);
    Overall_Buffer = LOX_Buff + "," + DON_Buff + "," + str;
    Serial.println(Overall_Buffer);
  }
}

// shift the 24-bit state out to the shift-register chain
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

// configure Timer1 for ~35 kHz PWM on pin 9
void setupTimer1ForPWM() {
  TCCR1A = 0; 
  TCCR1B = 0;
  TCCR1A |= _BV(WGM11);
  TCCR1B |= _BV(WGM12) | _BV(WGM13) | _BV(CS10);
  ICR1   = 454;      // TOP = (16MHz / 35kHz) – 1
  OCR1A  = 454;      // 50% duty
  TCCR1A |= _BV(COM1A1);
}

// reset the shift-register then latch low
void resetAndLatch() {
  digitalWrite(LATCH_PIN, LOW);
  digitalWrite(RESET_PIN, LOW);
  delayMicroseconds(10);
  digitalWrite(RESET_PIN, HIGH);
}
