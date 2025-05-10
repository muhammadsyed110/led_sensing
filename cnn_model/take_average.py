import serial
import time
import numpy as np
import matplotlib.pyplot as plt

# === CONFIGURATION ===
COM_PORT = 'COM3'        # Update this to your actual port
BAUD_RATE = 115200
NUM_ROWS = 5
NUM_COLS = 5
READ_DELAY = 0.1
REPEAT_COUNT = 1

# === PREPARE COMMANDS ===
led_commands = [f'LOX{r}{c}' for r in range(1, NUM_ROWS + 1) for c in range(1, NUM_COLS + 1)]
pd_commands = [f'DON{r}{c}' for r in range(1, NUM_ROWS + 1) for c in range(1, NUM_COLS + 1)]

# === PARSE VALUE FUNCTION ===
def parse_value(line):
    try:
        return float(line.split(',')[-1])
    except:
        return 0

# === READ FULL PD MATRIX FOR A GIVEN LED ===
def get_pd_matrix_for_led(ser, led_cmd):
    matrix = np.zeros((NUM_ROWS, NUM_COLS))
    ser.write(f'{led_cmd}\n'.encode())
    time.sleep(READ_DELAY)

    for pd_cmd in pd_commands:
        ser.write(f'{pd_cmd}\n'.encode())
        line = ser.readline().decode().strip()
        print(line)
        val = parse_value(line)
        x = int(pd_cmd[3]) - 1
        y = int(pd_cmd[4]) - 1
        matrix[x, y] = val
        time.sleep(READ_DELAY)

    return matrix

# === COLLECT SUM OF ALL LED ACTIVATIONS ===
def collect_average_pd_matrix():
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    total_matrix = np.zeros((NUM_ROWS, NUM_COLS))

    for led_cmd in led_commands:
        print(f"Activating {led_cmd}")
        for _ in range(REPEAT_COUNT):
            pd_matrix = get_pd_matrix_for_led(ser, led_cmd)
            total_matrix += pd_matrix

    ser.close()
    average_matrix = total_matrix / (NUM_ROWS * NUM_COLS)
    return average_matrix

# === RUN AND VISUALIZE ===
# Uncomment for real hardware
avg_matrix = collect_average_pd_matrix()

# Placeholder simulation
#np.random.seed(42)
#avg_matrix = np.random.normal(loc=300, scale=50, size=(5, 5))

# === PLOT SINGLE HEATMAP ===
fig, ax = plt.subplots(figsize=(6, 6))
im = ax.imshow(avg_matrix, cmap='viridis')
plt.colorbar(im, ax=ax)

for i in range(NUM_ROWS):
    for j in range(NUM_COLS):
        ax.text(j, i, f"{avg_matrix[i, j]:.0f}",
                ha="center", va="center",
                color="white" if avg_matrix[i, j] < np.max(avg_matrix)/2 else "black")

ax.set_title("Final Average 5x5 Photodiode Response Map")
ax.set_xlabel("Column")
ax.set_ylabel("Row")
plt.tight_layout()
plt.show()

