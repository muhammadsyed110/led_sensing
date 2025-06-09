import sys
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

MODEL_PATH = 'regression_model.h5'
IMG_SIZE = (5, 5)

# Preprocess function (same as training)
def preprocess_image(image_path):
    img = Image.open(image_path).convert('L')
    img = img.resize(IMG_SIZE)
    arr = np.array(img).astype(np.float32) / 255.0
    return arr.flatten(), arr

def main(image_path):
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return
    # Load model
    model = load_model(MODEL_PATH)
    # Preprocess input
    x_flat, ground_truth = preprocess_image(image_path)
    x_input = np.expand_dims(x_flat, axis=0)  # Shape (1, 25)
    # Predict
    y_pred = model.predict(x_input)[0]  # Shape (25,)
    y_pred_img = (y_pred.reshape(IMG_SIZE) * 255).clip(0, 255).astype(np.uint8)
    # Show images
    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1)
    plt.title('Ground Truth')
    plt.imshow(ground_truth, cmap='gray', vmin=0, vmax=1)
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.title('Predicted')
    plt.imshow(y_pred_img, cmap='gray', vmin=0, vmax=255)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <image_file>")
    else:
        main(sys.argv[1])
