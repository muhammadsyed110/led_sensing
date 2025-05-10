import serial
import time
import numpy as np
import matplotlib.pyplot as plt

# Configuration
COM_PORT = 'COM3'  # 🔁 Change this to your actual port
BAUD_RATE = 115200
NUM_ROWS = 5
NUM_COLS = 5

# Open serial port
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Let Arduino reset

# Send command to activate a single LED
#ser.write(b'LOX11\n')
time.sleep(0.1)

# Store photodiode readings in a 5x5 matrix
matrix = np.zeros((NUM_ROWS, NUM_COLS))

for row in range(1, NUM_ROWS + 1):
    for col in range(1, NUM_COLS + 1):
        cmd = f'DON{row}{col}\n'.encode()
        ser.write(cmd)
        line = ser.readline().decode().strip()
        print(line)
        try:
            val = float(line.split(',')[-1])
        except:
            val = 0
        matrix[row - 1, col - 1] = val
        time.sleep(0.1)

ser.close()

# Plotting the matrix with annotations
fig, ax = plt.subplots()
im = ax.imshow(matrix, cmap='viridis')
plt.colorbar(im, ax=ax)

# Annotate values in each cell
for i in range(NUM_ROWS):
    for j in range(NUM_COLS):
        ax.text(j, i, f"{matrix[i, j]:.1f}",
                ha="center", va="center",
                color="white" if matrix[i, j] < matrix.max()/2 else "black")

ax.set_title("Photodiode Readings for LED LOX11")
ax.set_xlabel("Column")
ax.set_ylabel("Row")
plt.show()
