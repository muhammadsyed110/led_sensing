import serial
import json
import time
import numpy as np
import matplotlib.pyplot as plt

# Config
COM_PORT = 'COM3'  # Set to your port
BAUD_RATE = 115200
NUM_ROWS = 5
NUM_COLS = 5
DELAY = 0.05  # Delay between serial commands

# Open serial
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

matrix = np.zeros((NUM_ROWS * NUM_COLS, NUM_ROWS * NUM_COLS))  # 25 LEDs x 25 PDs

# Loop over each LED
for led_row in range(1, NUM_ROWS + 1):
    for led_col in range(1, NUM_COLS + 1):
        led_index = (led_row - 1) * NUM_COLS + (led_col - 1)

        # Activate LED
        ser.write(f'LOX{led_row}{led_col}\n'.encode())
        time.sleep(DELAY)

        # Read all PDs for this LED
        for pd_row in range(1, NUM_ROWS + 1):
            for pd_col in range(1, NUM_COLS + 1):
                pd_index = (pd_row - 1) * NUM_COLS + (pd_col - 1)

                ser.write(f'DON{pd_row}{pd_col}\n'.encode())
                time.sleep(DELAY)

                ser.write(b'GETVAL\n')
                line = ser.readline().decode().strip()

                try:
                    data = json.loads(line)
                    val = float(data['val'])
                except:
                    val = 0.0  # fallback
                    print("⚠️ Failed to parse:", line)

                matrix[led_index, pd_index] = val
                time.sleep(DELAY)

# All LEDs OFF
ser.write(b'LAF\n')
ser.close()

# ✅ Plot heatmap
plt.figure(figsize=(10, 8))
plt.imshow(matrix, cmap='viridis')
plt.colorbar(label='Photodiode Reading')
plt.title("25x25 LED-to-PD Response Matrix")
plt.xlabel("Photodiode Index (0–24)")
plt.ylabel("LED Index (0–24)")
plt.show()
