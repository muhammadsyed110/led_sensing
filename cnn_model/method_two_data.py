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
NUM_ITERATIONS = 10

# Ground truth matrix (you can update as needed)
X = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1],
    [0, 0, 0, 1, 1]
])





def collect_sensor_matrix():
    """Turn on each LED, read its corresponding photodiode, turn off LED."""
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    matrix = np.zeros((NUM_ROWS, NUM_COLS))

    for row in reversed(range(1, NUM_ROWS + 1)):
        for col in reversed(range(1, NUM_COLS + 1)):
            # Turn on specific LED
            led_cmd = f'LOX{row}{col}\n'.encode()
            ser.write(led_cmd)
            time.sleep(0.1)

            # Read the matching photodiode
            diode_cmd = f'DON{row}{col}\n'.encode()
            ser.write(diode_cmd)
            line = ser.readline().decode().strip()
            print(line)
            try:
                val = float(line.split(',')[-1])
            except:
                val = 0
            matrix[row - 1, col - 1] = val
            time.sleep(0.1)

            # Turn off all LEDs
            ser.write(b'LAF\n')
            time.sleep(0.1)

    ser.close()
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
    """Shows sensor reading with ground truth object overlay."""
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


def run_collection_loop(X, num_runs=20):
    """Main loop to collect multiple samples."""
    for i in range(num_runs):
        print(f"\n🔁 Sample {i + 1}/{num_runs}")
        Y = collect_sensor_matrix()
        save_sample_to_csv(X, Y)
        plot_overlay(X, Y)


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