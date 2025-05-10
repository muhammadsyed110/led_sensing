
// pin_defs.h

// Define LED GND side (row) switches
#define L_RA1 0
#define L_RB1 1
#define L_RC1 2
#define L_RD1 3
#define L_RE1 4

// Define LED VDD side (column) switches
#define L_CA1 5
#define L_CB1 6
#define L_CC1 7
#define L_CD1 8
#define L_CE1 9

// Macros to manipulate the shift register
#define SET_BIT_HIGH(state, bit) ((state) |= (1UL << (bit)))
#define SET_BIT_LOW(state, bit) ((state) &= ~(1UL << (bit)))

// Macros to turn on and off a specific LED at row x, column y
#define TURN_ON_LED(state, row, col) do { \
  SET_BIT_HIGH(state, row-1); \
  SET_BIT_LOW(state, col+5-1); \
} while (0)

#define TURN_OFF_LED(state, row, col) do { \
  SET_BIT_LOW(state, row-1); \
  SET_BIT_HIGH(state, col+5-1); \
} while (0)

// LED row and column mapping to bits
#define LED_ROW_1 L_RA1
#define LED_ROW_2 L_RB1
#define LED_ROW_3 L_RC1
#define LED_ROW_4 L_RD1
#define LED_ROW_5 L_RE1

#define LED_COL_1 L_CA1
#define LED_COL_2 L_CB1
#define LED_COL_3 L_CC1
#define LED_COL_4 L_CD1
#define LED_COL_5 L_CE1
