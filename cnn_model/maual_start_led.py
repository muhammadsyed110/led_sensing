import serial
import time

# === CONFIGURATION ===
COM_PORT = 'COM3'      # Change to your COM port
BAUD_RATE = 115200
NUM_ROWS = 5
NUM_COLS = 5

# === SELECT WHICH LED TO TURN ON ===
TARGET_LED_ROW = 1     # 1 = top row, 5 = bottom row (depending on hardware layout)
TARGET_LED_COL = 1     # 1 = leftmost column, 5 = rightmost

def open_serial():
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    return ser

def turn_on_led(ser, row, col):
    """Send command to turn ON a specific LED and leave it on."""
    cmd = f'LOX{row}{col}\n'.encode()
    print(f"🔆 Turning ON LED at Row {row}, Col {col}")
    ser.write(cmd)

def turn_off_all_leds(ser):
    """Turn off all LEDs."""
    ser.write(b'LAF\n')
    print("🟢 All LEDs turned OFF.")

def main():
    ser = open_serial()
    try:
        turn_off_all_leds(ser)
        turn_on_led(ser, TARGET_LED_ROW, TARGET_LED_COL)
        print("🕒 LED will stay ON for 10 seconds...")
        time.sleep(10)
        turn_off_all_leds(ser)
    finally:
        ser.close()
        print("🔌 Serial connection closed.")

if __name__ == "__main__":
    main()
