#include "pin_defs.h"

// Define the pin connections
const int RESET_PIN = 2;
const int CLK_PIN = 4;
const int DATA_PIN = 5;
const int LATCH_PIN = 3;
const int PWM_PIN = 9; // Timer1 controlled PWM pin, can be 9 or 10 on Uno

// Initialize the 24-bit state variable
unsigned long state = 0xe893e0;

String DON_Buff;
String LOX_Buff;
String Overall_Buffer;

// Macros for bit manipulation
#define SET_BIT_HIGH(var, bit) (var |= (1UL << bit))
#define SET_BIT_LOW(var, bit) (var &= ~(1UL << bit))

void setup() {
  // Set pin modes
  pinMode(RESET_PIN, OUTPUT);
  pinMode(CLK_PIN, OUTPUT);
  pinMode(DATA_PIN, OUTPUT);
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(PWM_PIN, OUTPUT);
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
  // Check if data is available to read from the serial port
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read the incoming command

    if(command.startsWith("DON")) {
        DON_Buff = command.substring(0, 4);
        int row = command.charAt(3) - '0'; // Convert ASCII to integer
        int col = command.charAt(4) - '0'; // Convert ASCII to integer
        if (row >= 1 && row <= 5 && col >= 1 && col <= 5) {
          // Calculate the bit positions based on row and column
          int rowBit = (10 + row - 1);
          int colBit = (15 + col - 1);
          // Switch off all PD bits in state
          SET_BIT_LOW(state, 10); SET_BIT_LOW(state, 11); SET_BIT_LOW(state, 12);
          SET_BIT_LOW(state, 13); SET_BIT_LOW(state, 14);
          SET_BIT_HIGH(state, 15); SET_BIT_HIGH(state, 16); SET_BIT_HIGH(state, 17);
          SET_BIT_HIGH(state, 18); SET_BIT_HIGH(state, 19);
          // now, switch on the requested PD  
          SET_BIT_HIGH(state, rowBit);
          SET_BIT_LOW(state, colBit);
        }
    }
    if(command.startsWith("LOX")) {
        LOX_Buff = command.substring(0, 4);
        int row = command.charAt(3) - '0'; // Convert ASCII to integer
        int col = command.charAt(4) - '0'; // Convert ASCII to integer
        if (row >= 1 && row <= 5 && col >= 1 && col <= 5) {
          // Calculate the bit positions based on row and column
          int rowBit = (row - 1);
          int colBit = (5 + col - 1);
          // Switch off all LED bits in state
          SET_BIT_LOW(state, 0); SET_BIT_LOW(state, 1); SET_BIT_LOW(state, 2); 
          SET_BIT_LOW(state, 3); SET_BIT_LOW(state, 4);
          SET_BIT_HIGH(state, 5); SET_BIT_HIGH(state, 6); SET_BIT_HIGH(state, 7); 
          SET_BIT_HIGH(state, 8); SET_BIT_HIGH(state, 9);
          // now, switch on the requested PD  
          SET_BIT_HIGH(state, rowBit);
          SET_BIT_LOW(state, colBit);
        }
    }
    
    // Turn all LEDs off
    if (command == "LAF") {
        // Switch off all LED bits in state
        SET_BIT_LOW(state, 0); SET_BIT_LOW(state, 1); SET_BIT_LOW(state, 2); 
        SET_BIT_LOW(state, 3); SET_BIT_LOW(state, 4);
        SET_BIT_HIGH(state, 5); SET_BIT_HIGH(state, 6); SET_BIT_HIGH(state, 7); 
        SET_BIT_HIGH(state, 8); SET_BIT_HIGH(state, 9);
    }
    // Turn specific LED on or off
    else if (command.length() == 5 && (command.startsWith("LON") || command.startsWith("LOF"))) {
      int row = command.charAt(3) - '0'; // Convert ASCII to integer
      int col = command.charAt(4) - '0'; // Convert ASCII to integer
      bool turnOn = command.startsWith("LON");

      // Check if row and column numbers are within the valid range
      if (row >= 1 && row <= 5 && col >= 1 && col <= 5) {
        // Calculate the bit positions based on row and column
        int rowBit = row - 1;
        int colBit = (5 + col - 1);

        // Set or clear the bits in the state variable
        if (turnOn) {
          SET_BIT_HIGH(state, rowBit);
          SET_BIT_LOW(state, colBit);
        } else {
          SET_BIT_LOW(state, rowBit);
          SET_BIT_HIGH(state, colBit);
        }
      }
    }

    // Output the updated state to the shift register
    shiftOutState();
	// (100,100), (100,5), (50,5), (10,5), (10,10),
    delay(100);
	float Avg_Number = 5.0;
    // Simple analog read average
    float a = 0.0;
    for(int i = 0; i < Avg_Number; i++) {
        a += analogRead(A0);
    }
    // Convert float to string with 3 decimal places
    char str[10];
    dtostrf(a / Avg_Number, 3, 3, str);
    Overall_Buffer = LOX_Buff + "," + DON_Buff + "," + str;
    Serial.println(Overall_Buffer);
  }

  //delay(25);
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
  // Stop Timer1
  TCCR1A = 0;
  TCCR1B = 0;
  
  // Set mode to Fast PWM top in ICR1
  TCCR1A |= _BV(WGM11);
  TCCR1B |= _BV(WGM12) | _BV(WGM13);
  
  // Set prescaler to 1 (no prescaling)
  TCCR1B |= _BV(CS10);
  
  // Set PWM frequency/top value
  ICR1 = 454; // 16 MHz / 35 kHz - 1 = 454
  
  // Set duty cycle to 50%
  OCR1A = 454; // 50% of ICR1
  
  // Enable PWM on Pin 9 or 10
  TCCR1A |= _BV(COM1A1);
}

void resetAndLatch() {
  digitalWrite(LATCH_PIN, LOW);
  digitalWrite(RESET_PIN, LOW);
  delayMicroseconds(10);
  digitalWrite(RESET_PIN, HIGH);
}
