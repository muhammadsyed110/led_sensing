import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import MeanAbsoluteError
from tensorflow.keras.callbacks import ModelCheckpoint

# Hardcoded paths
X_PATH = 'X'  # Folder containing all PNG images (inputs and labels)
IMG_SIZE = (5, 5)  # 5x5 = 25 features
MODEL_SAVE_PATH = 'regression_model.h5'

def load_image(filepath):
    """Load an image, convert to grayscale, resize, and flatten to 25 features."""
    img = Image.open(filepath).convert('L')  # Grayscale
    img = img.resize(IMG_SIZE)
    arr = np.array(img).astype(np.float32) / 255.0  # Normalize
    return arr.flatten()  # Shape: (25,)

def load_dataset(x_dir):
    X_list, Y_list = [], []
    for fname in os.listdir(x_dir):
        fp = os.path.join(x_dir, fname)
        if os.path.isfile(fp) and fname.lower().endswith('.png'):
            # Use the same image as both input and label (if that's your setup)
            # If you have a way to distinguish input/label, adjust here
            X_list.append(load_image(fp))
            Y_list.append(load_image(fp))
    return np.array(X_list), np.array(Y_list)

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

def main():
    # Load all images from X_PATH
    if not os.path.exists(X_PATH):
        print(f"Error: {X_PATH} does not exist.")
        return
    X, Y = load_dataset(X_PATH)
    print(f"Loaded {X.shape[0]} samples from {X_PATH}.")

    # Build model
    model = build_regression_model()

    # Train on all data (no validation split)
    checkpoint = ModelCheckpoint(MODEL_SAVE_PATH, save_best_only=True, monitor='loss', mode='min')
    history = model.fit(
        X, Y,
        epochs=50,
        batch_size=32,
        callbacks=[checkpoint],
        verbose=1
    )
    print(f"Model saved to {MODEL_SAVE_PATH}")

    # Optionally evaluate on the same data (since no separate test set)
    test_loss, test_mae = model.evaluate(X, Y, verbose=1)
    print(f"Final Loss: {test_loss:.4f}, Final MAE: {test_mae:.4f}")

if __name__ == '__main__':
    main()
