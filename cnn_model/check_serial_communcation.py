import serial
import time
import numpy as np
import matplotlib.pyplot as plt

# === Step 1: Define the Ground Truth Matrix ===
# 1 where object is present, 0 otherwise
X = np.array([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0],
    [1, 1, 0, 0, 0]
])

# === Step 2: Serial Configuration ===
COM_PORT = 'COM3'  # Change this if needed
BAUD_RATE = 115200
NUM_ROWS = 5
NUM_COLS = 5

# === Step 3: Collect Photodiode Readings ===
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

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

# === Step 4: Show Both Matrices ===
print("X (Object Position):")
print(X)

print("\nY (Photodiode Readings):")
print(matrix)

# === Step 5: Plot the Input (X) Matrix ===
plt.figure(figsize=(5, 4))
plt.imshow(X, cmap='gray_r', interpolation='nearest')
plt.title("Input X (Object Position)")
plt.xlabel("Column")
plt.ylabel("Row")
plt.colorbar(label='Object (1=present)')
plt.grid(False)
plt.show()

# === Step 6: Plot the Output (Y) Matrix ===
fig, ax = plt.subplots()
im = ax.imshow(matrix, cmap='viridis')
plt.colorbar(im, ax=ax)

for i in range(NUM_ROWS):
    for j in range(NUM_COLS):
        ax.text(j, i, f"{matrix[i, j]:.1f}",
                ha="center", va="center",
                color="white" if matrix[i, j] < matrix.max()/2 else "black")

ax.set_title("Output Y (Photodiode Readings)")
ax.set_xlabel("Column")
ax.set_ylabel("Row")
plt.show()


# === Step 6: Plot Combined Y + X Overlay ===
fig, ax = plt.subplots()
im = ax.imshow(matrix, cmap='viridis')
plt.colorbar(im, ax=ax)

# Annotate values
for i in range(NUM_ROWS):
    for j in range(NUM_COLS):
        ax.text(j, i, f"{matrix[i, j]:.1f}",
                ha="center", va="center",
                color="white" if matrix[i, j] < matrix.max()/2 else "black")

# Overlay object positions (X == 1) as red rectangles
for i in range(NUM_ROWS):
    for j in range(NUM_COLS):
        if X[i, j] == 1:
            rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                 edgecolor='red', facecolor='none',
                                 linewidth=2)
            ax.add_patch(rect)

ax.set_title("Photodiode Readings with Object Overlay (Red Boxes)")
ax.set_xlabel("Column")
ax.set_ylabel("Row")
plt.grid(False)
plt.show()



import pandas as pd
import os

# Flatten both matrices
X_flat = X.flatten()
Y_flat = matrix.flatten()

# Combine into one row
sample = np.concatenate((X_flat, Y_flat))

# Define column names if first time
column_names = [f'X{i}' for i in range(25)] + [f'Y{i}' for i in range(25)]

# CSV path
csv_path = 'dataset.csv'

# Check if file exists
if not os.path.exists(csv_path):
    df = pd.DataFrame([sample], columns=column_names)
    df.to_csv(csv_path, index=False)
    print("✅ Created new dataset.csv and saved sample.")
else:
    df = pd.read_csv(csv_path)
    df.loc[len(df)] = sample
    df.to_csv(csv_path, index=False)
    print("✅ Appended new sample to dataset.csv.")
