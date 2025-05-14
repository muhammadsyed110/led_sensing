import serial
import time
import numpy as np
import matplotlib.pyplot as plt

# Configuration
COM_PORT = 'COM3'  # Set to your serial port
BAUD_RATE = 115200
NUM_ROWS = 5
NUM_COLS = 5
READ_DELAY = 0.15  # Delay between LED ON, read, and LED OFF

def read_photodiodes_with_local_led():
    """
    For each PD(x,y), turn on LED(x,y), read value, turn off LED.
    Returns a 5x5 matrix of values.
    """
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    matrix = np.zeros((NUM_ROWS, NUM_COLS))

    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            # Turn on corresponding LED
            led_cmd = f'LOX{row+1}{col+1}\n'.encode()
            ser.write(led_cmd)
            time.sleep(READ_DELAY)

            # Read corresponding photodiode
            diode_cmd = f'DON{row+1}{col+1}\n'.encode()
            ser.write(diode_cmd)
            line = ser.readline().decode().strip()
            print(f"PD({row+1},{col+1}): {line}")

            try:
                val = float(line.split(',')[-1])
            except:
                val = 0.0

            matrix[row, col] = val

            # Turn off all LEDs
            ser.write(b'LAF\n')
            time.sleep(READ_DELAY)

    ser.close()
    return matrix

def show_heatmap(matrix):
    """Display the sensor readings as a heatmap."""
    flipped = np.flipud(matrix)
    fig, ax = plt.subplots()
    im = ax.imshow(flipped, cmap='viridis')
    plt.colorbar(im, ax=ax)

    for i in range(NUM_ROWS):
        for j in range(NUM_COLS):
            ax.text(j, i, f"{flipped[i, j]:.1f}",
                    ha="center", va="center",
                    color="white" if flipped[i, j] < flipped.max() / 2 else "black")

    ax.set_title("PD Readings (Each LED ON Before Its PD Read)")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    plt.show()

# === Main ===
if __name__ == "__main__":
    matrix = read_photodiodes_with_local_led()
    print("\n📊 Photodiode readings (LED matched):")
    print(matrix)
    show_heatmap(matrix)
