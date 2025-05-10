import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import os
import pickle
from check_serial_communcation import collect_sensor_matrix


# Constants
NUM_ROWS, NUM_COLS = 5, 5
X_COLUMNS = [f'X{i}' for i in range(25)]
Y_COLUMNS = [f'Y{i}' for i in range(25)]
LABEL_MAP_FILE = 'label_mapping.pkl'
MODEL_FILE = 'cnn_model.h5'


def load_data(path='dataset.csv'):
    df = pd.read_csv(path)
    X = df[Y_COLUMNS].values.reshape(-1, NUM_ROWS, NUM_COLS, 1)  # CNN expects 4D input
    y_raw = df[X_COLUMNS].values

    # Convert binary mask to class index (e.g., string to int label)
    y_labels = np.array([''.join(str(int(v)) for v in row) for row in y_raw])
    unique_labels = sorted(np.unique(y_labels))
    label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
    y = np.array([label_to_idx[label] for label in y_labels])

    y = to_categorical(y, num_classes=len(unique_labels))

    # Save label mapping for future predictions
    with open(LABEL_MAP_FILE, 'wb') as f:
        pickle.dump(label_to_idx, f)

    return train_test_split(X, y, test_size=0.2, random_state=42), len(unique_labels)


def build_cnn_model(num_classes):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(NUM_ROWS, NUM_COLS, 1), padding='same'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def train_and_evaluate():
    (X_train, X_test, y_train, y_test), num_classes = load_data()
    model = build_cnn_model(num_classes)

    model.fit(X_train, y_train, epochs=20, batch_size=16, validation_split=0.1)
    loss, acc = model.evaluate(X_test, y_test)
    print(f"✅ Test Accuracy: {acc:.2f}")

    model.save(MODEL_FILE)
    return model


def predict_new_sample(sensor_matrix):
    if not os.path.exists(MODEL_FILE) or not os.path.exists(LABEL_MAP_FILE):
        raise FileNotFoundError("Model or label mapping not found. Train the model first.")

    model = load_model(MODEL_FILE)
    with open(LABEL_MAP_FILE, 'rb') as f:
        label_to_idx = pickle.load(f)
    idx_to_label = {v: k for k, v in label_to_idx.items()}

    # Reshape input to 4D
    sensor_matrix = np.array(sensor_matrix).reshape(1, NUM_ROWS, NUM_COLS, 1)
    prediction = model.predict(sensor_matrix)
    predicted_idx = np.argmax(prediction)
    predicted_label = idx_to_label[predicted_idx]
    print(f"🔍 Predicted object mask: {predicted_label}")
    return predicted_label

def visualize_mask(mask_str):
    mask_array = np.array([int(c) for c in mask_str]).reshape(NUM_ROWS, NUM_COLS)
    print("📌 Predicted Object Position Mask:")
    print(mask_array)


if __name__ == '__main__':
    #model = train_and_evaluate()

    # Example use: Uncomment below to predict a sample
    # sample = np.random.rand(5, 5) * 500  # Replace with actual sensor reading
    # predict_new_sample(sample)

    live_matrix = collect_sensor_matrix()
    predict_new_sample(live_matrix)

    predicted_label = predict_new_sample(live_matrix)
    visualize_mask(predicted_label)

