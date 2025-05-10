import pickle

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import MeanAbsoluteError
from sklearn.model_selection import train_test_split
import os
from method_two_data import collect_sensor_matrix, plot_overlay  # ensure this returns a 25-element list

# Constants
NUM_ROWS, NUM_COLS = 5, 5
X_COLUMNS = [f'X{i}' for i in range(25)]
Y_COLUMNS = [f'Y{i}' for i in range(25)]
MODEL_FILE = 'regression_model.keras'


from sklearn.preprocessing import MinMaxScaler

def load_data(path='dataset.csv'):
    df = pd.read_csv(path)

    # ✅ Swap: now sensor readings are input, LED mask is output
    X = df[Y_COLUMNS].values.astype(np.float32)   # Sensor values as input
    Y = df[X_COLUMNS].values.astype(np.float32)   # LED mask as output

    # Normalize sensor readings (X), LED mask remains binary (Y)
    x_scaler = MinMaxScaler()
    X_scaled = x_scaler.fit_transform(X)

    # Save the input scaler
    with open('x_scaler.pkl', 'wb') as f:
        pickle.dump(x_scaler, f)

    return train_test_split(X_scaled, Y, test_size=0.2, random_state=42)

def build_regression_model():
    model = Sequential([
        Dense(256, activation='relu', input_shape=(25,)),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(25)
    ])

    model.compile(
        optimizer='adam',
        loss=MeanSquaredError(),
        metrics=[MeanAbsoluteError()]
    )
    return model


def train_and_evaluate():
    X_train, X_test, Y_train, Y_test = load_data()
    model = build_regression_model()

    model.fit(X_train, Y_train, epochs=100, batch_size=16, validation_split=0.1)
    loss, mae = model.evaluate(X_test, Y_test)
    print(f"✅ Test MAE: {mae:.2f}")

    model.save(MODEL_FILE)
    return model


import pickle

import pickle


def predict_new_sample(sensor_values):
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("Model not found. Train the model first.")

    model = load_model(MODEL_FILE)

    # Load input scaler
    with open('x_scaler.pkl', 'rb') as f:
        x_scaler = pickle.load(f)

    # Scale the sensor readings
    sensor_values = np.array(sensor_values).reshape(1, 25).astype(np.float32)
    sensor_scaled = x_scaler.transform(sensor_values)

    # Predict the LED mask
    prediction = model.predict(sensor_scaled)[0]

    # Round output to get binary prediction (optional)
    predicted_mask = (prediction > 0.5).astype(int)

    print("🔍 Predicted LED mask (X0–X24):")
    print(predicted_mask.reshape(NUM_ROWS, NUM_COLS))
    return predicted_mask


if __name__ == '__main__':
    # Uncomment to train and save model
    #train_and_evaluate()

    # Get live sensor matrix
    sensor_matrix = collect_sensor_matrix()  # shape: (5, 5)

    # Predict LED mask from sensor values
    predicted_led_mask = predict_new_sample(sensor_matrix.flatten())

    # Reshape predicted mask to 5x5 for overlay plot
    predicted_mask_2d = predicted_led_mask.reshape(NUM_ROWS, NUM_COLS)

    # 🟢 Show overlay: predicted LED mask on actual sensor values
    plot_overlay(predicted_mask_2d, sensor_matrix)