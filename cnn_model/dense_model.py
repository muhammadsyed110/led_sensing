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
from method_two_data import collect_sensor_matrix, plot_overlay  # Returns (5, 5) sensor matrix

# Constants
NUM_ROWS, NUM_COLS = 5, 5
SENSOR_COLUMNS = [f'Y{i}' for i in range(25)]  # Sensor readings as input
LED_COLUMNS = [f'X{i}' for i in range(25)]  # LED pattern as output
MODEL_FILE = 'regression_model.keras'
SCALER_FILE = 'x_scaler.pkl'


# === Load and Prepare Data ===
def load_data(path='dataset_fixed.csv'):
    df = pd.read_csv(path)

    # Sensor readings as input, LED state as output
    X = df[SENSOR_COLUMNS].values.astype(np.float32)
    Y = df[LED_COLUMNS].values.astype(np.float32)

    # Normalize sensor inputs
    x_scaler = MinMaxScaler()
    X_scaled = x_scaler.fit_transform(X)

    # Save input scaler for use during prediction
    with open(SCALER_FILE, 'wb') as f:
        pickle.dump(x_scaler, f)

    return train_test_split(X_scaled, Y, test_size=0.2, random_state=42)


# === Build Model ===
def build_regression_model():
    model = Sequential([
        Dense(256, activation='relu', input_shape=(25,)),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(25)  # Output: 25 values for LED mask
    ])
    model.compile(
        optimizer='adam',
        loss=MeanSquaredError(),
        metrics=[MeanAbsoluteError()]
    )
    return model


# === Train & Save Model ===
def train_and_evaluate():
    X_train, X_test, Y_train, Y_test = load_data()
    model = build_regression_model()
    model.fit(X_train, Y_train, epochs=100, batch_size=16, validation_split=0.1)
    loss, mae = model.evaluate(X_test, Y_test)
    print(f"✅ Test MAE: {mae:.2f}")
    model.save(MODEL_FILE)
    return model


# === Predict LED Mask from Sensor Matrix ===
def predict_new_sample(sensor_values):
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("Model not found. Train the model first.")

    model = load_model(MODEL_FILE)

    with open(SCALER_FILE, 'rb') as f:
        x_scaler = pickle.load(f)

    sensor_values = np.array(sensor_values).reshape(1, 25).astype(np.float32)
    sensor_scaled = x_scaler.transform(sensor_values)

    prediction = model.predict(sensor_scaled)[0]
    predicted_mask = (prediction > 0.5).astype(int)  # Threshold to binary

    print("🔍 Predicted LED mask (5x5):")
    print(predicted_mask.reshape(NUM_ROWS, NUM_COLS))
    return predicted_mask


# === Main Execution ===
if __name__ == '__main__':
    # Optionally train the model
    #train_and_evaluate()

    # Get live 5x5 sensor readings
    sensor_matrix = collect_sensor_matrix()  # Shape (5, 5)

    # Predict corresponding LED mask
    predicted_led_mask = predict_new_sample(sensor_matrix.flatten())
    predicted_mask_2d = predicted_led_mask.reshape(NUM_ROWS, NUM_COLS)

    # Visualize
    plot_overlay(predicted_mask_2d, sensor_matrix)
