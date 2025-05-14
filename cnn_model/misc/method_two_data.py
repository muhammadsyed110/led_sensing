import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# Configuration
COM_PORT = 'COM3'
BAUD_RATE = 115200
NUM_ROWS = 5
NUM_COLS = 5
CSV_PATH = '../dataset.csv'
NUM_ITERATIONS = 10

LED_TEXT = """
0 0 0 1 1
0 0 0 1 1
0 0 0 0 0
0 0 0 0 0
0 0 0 0 0
"""

def parse_led_text(text):
    lines = text.strip().splitlines()
    lines = lines[::-1]
    grid = [list(map(int, line.strip().split())) for line in lines]
    return np.array(grid)

LED_MASK = parse_led_text(LED_TEXT)

def collect_sensor_matrix():
    """Use new Arduino interface: send LOXxy + DONxy + GETVAL for each LED/PD pair."""
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    matrix = np.zeros((NUM_ROWS, NUM_COLS))

    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            led_cmd = f'LOX{row+1}{col+1}\n'.encode()
            pd_cmd = f'DON{row+1}{col+1}\n'.encode()

            ser.write(led_cmd)
            time.sleep(0.05)

            ser.write(pd_cmd)
            time.sleep(0.05)

            ser.write(b'GETVAL\n')
            line = ser.readline().decode().strip()
            print(line)

            try:
                data = json.loads(line)
                val = float(data['val'])
            except:
                val = 0.0  # fallback in case of error

            matrix[row, col] = val
            time.sleep(0.05)

            ser.write(b'LAF\n')
            time.sleep(0.05)

    ser.close()
    return matrix

def save_sample_to_csv(X, Y, path=CSV_PATH):
    x_flat = X.flatten()
    y_flat = Y.flatten()
    sample = np.concatenate((y_flat, x_flat))
    column_names = [f'Y{i}' for i in range(25)] + [f'X{i}' for i in range(25)]

    if not os.path.exists(path):
        df = pd.DataFrame([sample], columns=column_names)
        df.to_csv(path, index=False)
        print("✅ Created new dataset.csv and saved sample.")
    else:
        df = pd.read_csv(path)
        df.loc[len(df)] = sample
        df.to_csv(path, index=False)
        print("✅ Appended new sample to dataset.csv.")

def plot_overlay(led_mask, sensor_matrix):
    flipped_matrix = np.flipud(sensor_matrix)
    flipped_mask = np.flipud(led_mask)

    fig, ax = plt.subplots()
    im = ax.imshow(flipped_matrix, cmap='viridis')
    plt.colorbar(im, ax=ax)

    for i in range(NUM_ROWS):
        for j in range(NUM_COLS):
            ax.text(j, i, f"{flipped_matrix[i, j]:.1f}",
                    ha="center", va="center",
                    color="white" if flipped_matrix[i, j] < flipped_matrix.max() / 2 else "black")

    for i in range(NUM_ROWS):
        for j in range(NUM_COLS):
            if flipped_mask[i, j] == 1:
                rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                     edgecolor='red', facecolor='none', linewidth=2)
                ax.add_patch(rect)

    ax.set_title("Photodiode Readings with LED Overlay")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    plt.grid(False)
    plt.show()

def run_collection_loop(led_mask, num_runs=1):
    for i in range(num_runs):
        print(f"\n🔁 Sample {i + 1}/{num_runs}")
        sensor_matrix = collect_sensor_matrix()
        save_sample_to_csv(led_mask, sensor_matrix)
        plot_overlay(led_mask, sensor_matrix)

def activate_leds_from_matrix(led_mask):
    """Use LOX commands only for visual confirmation (if needed)."""
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            if led_mask[row, col] == 1:
                cmd = f'LOX{row + 1}{col + 1}\n'.encode()
                print(f"🔆 Turning ON LED at Row {row + 1}, Col {col + 1}")
                ser.write(cmd)
                time.sleep(0.05)

    time.sleep(1)
    ser.write(b'LAF\n')
    ser.close()

# === Main Execution ===
if __name__ == "__main__":
    activate_leds_from_matrix(LED_MASK)  # Optional visual confirm
    time.sleep(1)
    run_collection_loop(LED_MASK, NUM_ITERATIONS)
