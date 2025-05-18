import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import pickle

# === Config
MODEL_FILE = 'regression_model.keras'
SCALER_FILE = 'x_scaler.pkl'
DATASET_PATH = 'simulated_dataset.csv'
NUM_ROWS, NUM_COLS = 5, 5
SENSOR_COLUMNS = [f'Y{i}' for i in range(25)]
LED_COLUMNS = [f'X{i}' for i in range(25)]

# === Load model and scaler
model = load_model(MODEL_FILE)
with open(SCALER_FILE, 'rb') as f:
    scaler = pickle.load(f)

# === Load dataset
df = pd.read_csv(DATASET_PATH)
X = df[SENSOR_COLUMNS].values
Y_true = df[LED_COLUMNS].values

# === Pick a random sample
idx = np.random.randint(0, len(X))
x_sample = X[idx]
y_true = Y_true[idx]

# === Predict
x_scaled = scaler.transform([x_sample])
y_pred = model.predict(x_scaled)[0]
y_pred_binary = (y_pred > 0.5).astype(int)

# === Reshape
true_mask = y_true.reshape(NUM_ROWS, NUM_COLS)
pred_mask = y_pred_binary.reshape(NUM_ROWS, NUM_COLS)

# === Visualization
def show_prediction_grid(true_mask, pred_mask):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    axs[0].imshow(true_mask, cmap='Greens')
    axs[0].set_title("✅ Ground Truth (2x2 Block)")
    axs[0].set_xticks(range(NUM_COLS))
    axs[0].set_yticks(range(NUM_ROWS))
    axs[0].grid(False)
    axs[0].set_xlabel("Cols")
    axs[0].set_ylabel("Rows")

    axs[1].imshow(pred_mask, cmap='Reds')
    axs[1].set_title("🔍 Predicted Mask")
    axs[1].set_xticks(range(NUM_COLS))
    axs[1].set_yticks(range(NUM_ROWS))
    axs[1].grid(False)
    axs[1].set_xlabel("Cols")
    axs[1].set_ylabel("Rows")

    plt.tight_layout()
    plt.show()

# === Show result
print("\n🎯 Ground Truth LED mask (5x5):")
print(np.flipud(true_mask))

print("\n🔍 Predicted LED mask (5x5):")
print(np.flipud(pred_mask))

show_prediction_grid(true_mask, pred_mask)
