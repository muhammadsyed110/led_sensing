import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import MeanAbsoluteError
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import os
import tkinter as tk
from method_two_data import collect_sensor_matrix, plot_overlay  # Your methods

# Constants
NUM_ROWS, NUM_COLS = 5, 5
SENSOR_COLUMNS = [f'Y{i}' for i in range(25)]
LED_COLUMNS = [f'X{i}' for i in range(25)]
MODEL_FILE = 'regression_model.keras'
SCALER_FILE = 'x_scaler.pkl'
buttons = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]

# === Data Load & Save ===
def load_data(path='dataset.csv'):
    df = pd.read_csv(path)
    X = df[SENSOR_COLUMNS].values.astype(np.float32)
    Y = df[LED_COLUMNS].values.astype(np.float32)
    x_scaler = MinMaxScaler()
    X_scaled = x_scaler.fit_transform(X)
    with open(SCALER_FILE, 'wb') as f:
        pickle.dump(x_scaler, f)
    return train_test_split(X_scaled, Y, test_size=0.2, random_state=42)

def save_feedback(sensor_matrix, correct_led_mask):
    flat_sensor = sensor_matrix.flatten().tolist()
    flat_led = correct_led_mask.flatten().tolist()
    row = flat_sensor + flat_led
    columns = SENSOR_COLUMNS + LED_COLUMNS
    df = pd.DataFrame([row], columns=columns)
    if not os.path.exists('new_feedback.csv'):
        df.to_csv('new_feedback.csv', index=False)
    else:
        df.to_csv('new_feedback.csv', mode='a', header=False, index=False)

# === Model ===
def build_regression_model():
    model = Sequential([
        Dense(256, activation='relu', input_shape=(25,)),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(25)
    ])
    model.compile(optimizer='adam', loss=MeanSquaredError(), metrics=[MeanAbsoluteError()])
    return model

def train_and_evaluate():
    X_train, X_test, Y_train, Y_test = load_data()
    model = build_regression_model()
    model.fit(X_train, Y_train, epochs=100, batch_size=16, validation_split=0.1)
    loss, mae = model.evaluate(X_test, Y_test)
    print(f"✅ Test MAE: {mae:.2f}")
    model.save(MODEL_FILE)
    return model

def retrain_with_feedback():
    original = pd.read_csv('dataset.csv')
    if os.path.exists('new_feedback.csv'):
        feedback = pd.read_csv('new_feedback.csv')
        feedback_augmented = pd.concat([feedback] * 3, ignore_index=True)
        combined = pd.concat([original, feedback_augmented], ignore_index=True)
        combined.to_csv('dataset_fixed.csv', index=False)
        os.remove('new_feedback.csv')
        print("📈 Retraining with feedback...")
        train_and_evaluate()
    else:
        print("ℹ️ No new feedback to retrain on.")

# === Prediction ===
def predict_new_sample(sensor_values):
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("Model not found. Train the model first.")
    model = load_model(MODEL_FILE)
    with open(SCALER_FILE, 'rb') as f:
        x_scaler = pickle.load(f)
    sensor_values = np.array(sensor_values).reshape(1, 25).astype(np.float32)
    sensor_scaled = x_scaler.transform(sensor_values)
    prediction = model.predict(sensor_scaled)[0]
    predicted_mask = (prediction > 0.5).astype(int)
    print("🔍 Predicted LED mask (5x5):")
    #print(predicted_mask.reshape(NUM_ROWS, NUM_COLS))

    # Flip vertically to match physical layout
    predicted_mask_grid = predicted_mask.reshape(NUM_ROWS, NUM_COLS)
    flipped = np.flipud(predicted_mask_grid)

    print("🔍 Predicted LED mask (5x5):")
    for row in flipped:
        print(" ".join(map(str, row)))
    return predicted_mask

# === GUI Feedback ===
def open_feedback_gui(sensor_matrix):
    selected = np.zeros((NUM_ROWS, NUM_COLS), dtype=int)

    def toggle(i, j):
        selected[i, j] = 1 - selected[i, j]
        buttons[i][j].config(bg="green" if selected[i, j] else "lightgray")

    def on_submit():
        save_feedback(sensor_matrix, selected)
        print("✅ Feedback saved via GUI.")
        root.destroy()

    root = tk.Tk()
    root.title("Select Correct LED Positions")

    for i in range(NUM_ROWS):
        for j in range(NUM_COLS):
            logical_row = NUM_ROWS - 1 - i  # Flip visual to logical
            buttons[logical_row][j] = tk.Button(root, text=f"{logical_row},{j}", width=6, height=2,
                                                bg="lightgray", command=lambda i=logical_row, j=j: toggle(i, j))
            buttons[logical_row][j].grid(row=i, column=j)

    submit_btn = tk.Button(root, text="✅ OK", command=on_submit)
    submit_btn.grid(row=NUM_ROWS, column=0, columnspan=NUM_COLS, pady=10)

    root.mainloop()

# === Updated plot_overlay() with flip inside ===
def plot_overlay(led_mask, sensor_matrix):
    """Visualize sensor values with overlay of LED mask (red boxes)."""
    flipped_matrix = np.flipud(sensor_matrix)
    flipped_mask = np.flipud(led_mask)

    import matplotlib.pyplot as plt
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

    ax.set_title("Photodiode Readings with LED Overlay (Matched Layout)")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    plt.grid(False)
    plt.show()

# === Main Execution ===
if __name__ == '__main__':
    #train_and_evaluate()

    # Get sensor matrix
    sensor_matrix = collect_sensor_matrix()  # Shape (5, 5)

    # Predict LED mask
    predicted_led_mask = predict_new_sample(sensor_matrix.flatten())
    predicted_mask_2d = predicted_led_mask.reshape(NUM_ROWS, NUM_COLS)

    # Visualize prediction (auto-flipped in plot)
    plot_overlay(predicted_mask_2d, sensor_matrix)

    # Ask for feedback
    user_input = input("❓ Is this prediction correct? (y/n): ").strip().lower()
    if user_input == 'n':
        print("🖱️ Open GUI to select correct LED positions...")
        open_feedback_gui(sensor_matrix)
