#this code will looop over all leds one by one and on each led it will take all diode values then at the end average them

import serial
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuration
COM_PORT = 'COM3'
BAUD_RATE = 115200
NUM_ROWS = 5
NUM_COLS = 5
CSV_PATH = 'dataset.csv'
NUM_ITERATIONS = 1

# Ground truth matrix (adjust based on object position)
X = np.array([
    [1, 1, 0, 0, 0],
    [1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
])


def collect_sensor_matrix():
    """Turns on each LED one-by-one, reads all 25 diodes, then turns LED off."""
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    NUM_LEDS = 25
    readings = np.zeros((NUM_LEDS, NUM_ROWS, NUM_COLS))

    for led_index in range(1, NUM_LEDS + 1):
        row = (led_index - 1) // 5 + 1
        col = (led_index - 1) % 5 + 1

        # 🔆 Turn ON LED
        ser.reset_input_buffer()
        on_cmd = f'LOX{row}{col}\n'.encode()
        ser.write(on_cmd)
        time.sleep(0.1)

        # 🔎 Read from 25 diodes
        for diode_row in range(1, NUM_ROWS + 1):
            for diode_col in range(1, NUM_COLS + 1):
                ser.reset_input_buffer()
                d_cmd = f'DON{diode_row}{diode_col}\n'.encode()
                ser.write(d_cmd)
                time.sleep(0.02)

                line = ser.readline().decode(errors='ignore').strip()
                print(f"LED {row}{col} — {line}")
                try:
                    val = float(line.split(',')[-1])
                except:
                    val = 0
                readings[led_index - 1, diode_row - 1, diode_col - 1] = val
                time.sleep(0.005)

        # 🔻 Turn OFF LED
        ser.reset_input_buffer()
        off_cmd = f'LOF{row}{col}\n'.encode()
        ser.write(off_cmd)
        time.sleep(0.05)

    ser.close()

    # Final result
    matrix = np.mean(readings, axis=0)
    return matrix


def save_sample_to_csv(X, Y, path=CSV_PATH):
    """Saves one sample (flattened X and Y) to a CSV file."""
    X_flat = X.flatten()
    Y_flat = Y.flatten()
    sample = np.concatenate((X_flat, Y_flat))

    column_names = [f'X{i}' for i in range(25)] + [f'Y{i}' for i in range(25)]

    if not os.path.exists(path):
        df = pd.DataFrame([sample], columns=column_names)
        df.to_csv(path, index=False)
        print("✅ Created new dataset.csv and saved sample.")
    else:
        df = pd.read_csv(path)
        df.loc[len(df)] = sample
        df.to_csv(path, index=False)
        print("✅ Appended new sample to dataset.csv.")


def plot_overlay(X, Y):
    """Visualizes Y and overlays object position from X."""
    fig, ax = plt.subplots()
    im = ax.imshow(Y, cmap='viridis')
    plt.colorbar(im, ax=ax)

    for i in range(NUM_ROWS):
        for j in range(NUM_COLS):
            ax.text(j, i, f"{Y[i, j]:.1f}",
                    ha="center", va="center",
                    color="white" if Y[i, j] < Y.max()/2 else "black")

    for i in range(NUM_ROWS):
        for j in range(NUM_COLS):
            if X[i, j] == 1:
                rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                     edgecolor='red', facecolor='none', linewidth=2)
                ax.add_patch(rect)

    ax.set_title("Photodiode Readings with Object Overlay (Red Boxes)")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    plt.grid(False)
    plt.show()


def run_collection_loop(X, num_runs=1):
    """Main loop to collect multiple samples."""
    for i in range(num_runs):
        print(f"\n🔁 Sample {i + 1}/{num_runs}")
        Y = collect_sensor_matrix()
        save_sample_to_csv(X, Y)
        plot_overlay(X, Y)
        input("➡️ Press Enter to capture next sample...")

def activate_leds_from_matrix(X):
    """Takes a 5x5 numpy array (X) and turns ON LEDs where X[row, col] == 1"""
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            if X[row, col] == 1:
                # Convert to 1-based indexing for LOXxy
                cmd = f'LOX{row + 1}{col + 1}\n'.encode()
                print(f"🔆 Turning ON LED at Row {row+1}, Col {col+1}")
                ser.write(cmd)
                time.sleep(0.05)  # Allow time for shift register to latch

    ser.close()

if __name__ == "__main__":
    activate_leds_from_matrix(X)
    time.sleep(2)
    run_collection_loop(X, NUM_ITERATIONS)
