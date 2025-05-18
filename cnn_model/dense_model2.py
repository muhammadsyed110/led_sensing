
import pickle
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.metrics import SparseCategoricalAccuracy
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import os

from cnn_model.method_two_data import collect_sensor_matrix

# Constants
NUM_ROWS, NUM_COLS = 5, 5
SENSOR_COLUMNS = [f'Y{i}' for i in range(25)]
MODEL_FILE = 'classification_model.keras'
SCALER_FILE = 'x_scaler.pkl'

# Load and prepare data
def load_data(path='Transformed_Dataset.csv'):
    df = pd.read_csv(path)
    X = df[SENSOR_COLUMNS].values.astype(np.float32)
    Y = df['class_id'].values.astype(np.int32) - 1  # classes 0-15
    x_scaler = MinMaxScaler()
    X_scaled = x_scaler.fit_transform(X)
    with open(SCALER_FILE, 'wb') as f:
        pickle.dump(x_scaler, f)
    return train_test_split(X_scaled, Y, test_size=0.2, random_state=42)

# Build classification model
def build_classification_model():
    model = Sequential([
        Dense(256, activation='relu', input_shape=(25,)),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(16, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss=SparseCategoricalCrossentropy(),
                  metrics=[SparseCategoricalAccuracy()])
    return model

# Train the model
def train_and_evaluate():
    X_train, X_test, Y_train, Y_test = load_data()
    model = build_classification_model()
    model.fit(X_train, Y_train, epochs=50, batch_size=16, validation_split=0.1)
    loss, acc = model.evaluate(X_test, Y_test)
    print(f"✅ Test Accuracy: {acc:.2f}")
    model.save(MODEL_FILE)
    return model

# Convert class ID to 5x5 mask
def class_id_to_mask(class_id):
    mask = np.zeros((5, 5), dtype=int)
    if 1 <= class_id <= 16:
        i, j = divmod(class_id - 1, 4)
        mask[i:i+2, j:j+2] = 1
    return mask

# Predict from a sensor sample
def predict_class(sensor_values):
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError("Model not found. Train the model first.")
    model = load_model(MODEL_FILE)
    with open(SCALER_FILE, 'rb') as f:
        x_scaler = pickle.load(f)
    sensor_values = np.array(sensor_values).reshape(1, 25).astype(np.float32)
    sensor_scaled = x_scaler.transform(sensor_values)
    prediction = model.predict(sensor_scaled)
    class_id = np.argmax(prediction) + 1
    return class_id, class_id_to_mask(class_id)

# Example usage
if __name__ == '__main__':
    #model = train_and_evaluate()

    sensor_matrix = collect_sensor_matrix()
    class_id, predicted_led_mask = predict_class(sensor_matrix.flatten())

    print(f"🔍 Predicted class ID: {class_id}")
    print(predicted_led_mask)

    # Optional: plot_overlay(predicted_led_mask, sensor_matrix)
    # Optional: feedback GUI
