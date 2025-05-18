import numpy as np
import pandas as pd
import random
import os

# === Configuration ===
NUM_ROWS = 5
NUM_COLS = 5
NUM_SAMPLES = 1000
OUTPUT_PATH = 'simulated_dataset.csv'

# Column headers
LED_COLUMNS = [f'X{i}' for i in range(NUM_ROWS * NUM_COLS)]
SENSOR_COLUMNS = [f'Y{i}' for i in range(NUM_ROWS * NUM_COLS)]

def generate_random_led_mask():
    """Always generate a 2x2 block in the 5x5 grid."""
    mask = np.zeros((NUM_ROWS, NUM_COLS), dtype=int)
    i = random.randint(0, NUM_ROWS - 2)  # 0 to 3
    j = random.randint(0, NUM_COLS - 2)  # 0 to 3
    mask[i:i+2, j:j+2] = 1
    return mask

def simulate_sensor_matrix(led_mask):
    """Generate synthetic photodiode readings based on LED mask."""
    base_signal = led_mask * 100
    ambient_noise = np.random.uniform(10, 30, size=(NUM_ROWS, NUM_COLS))
    occlusion = (1 - led_mask) * np.random.uniform(0, 10, size=(NUM_ROWS, NUM_COLS))
    sensor_matrix = base_signal + ambient_noise - occlusion
    return np.clip(sensor_matrix, 0, 255)

def generate_dataset(num_samples=1000):
    data_rows = []
    for _ in range(num_samples):
        led_mask = generate_random_led_mask()
        sensor_matrix = simulate_sensor_matrix(led_mask)

        x_flat = led_mask.flatten()
        y_flat = sensor_matrix.flatten()

        row = np.concatenate([y_flat, x_flat])
        data_rows.append(row)

    columns = SENSOR_COLUMNS + LED_COLUMNS
    df = pd.DataFrame(data_rows, columns=columns)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Generated {num_samples} samples and saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    generate_dataset(NUM_SAMPLES)
