import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import load_img, img_to_array
import matplotlib.pyplot as plt
from PIL import Image

# --- CONFIG ---
MODEL_PATH = 'best_model.h5'
INPUT_IMAGE_PATH = 'X\LED_Matrix_2025_05_02_04_13_40_1.png'  # must be 128x128 grayscale
OUTPUT_IMAGE_PATH = 'predicted_mask.png'
IMG_SIZE = 128
THRESHOLD = 0.5  # threshold for binary mask

# --- DEFINE CUSTOM LOSS + METRICS (used during training) ---
def dice_coef(y_true, y_pred, smooth=1):
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

def dice_loss(y_true, y_pred):
    return 1 - dice_coef(y_true, y_pred)

def dice_bce_loss(y_true, y_pred):
    bce = tf.keras.losses.binary_crossentropy(y_true, y_pred)
    return bce + dice_loss(y_true, y_pred)

# --- LOAD TRAINED MODEL WITH CUSTOM OBJECTS ---
model = tf.keras.models.load_model(
    MODEL_PATH,
    custom_objects={
        'dice_loss': dice_loss,
        'dice_bce_loss': dice_bce_loss,
        'dice_coef': dice_coef,
        'mse': tf.keras.metrics.MeanSquaredError()
    }
)

# --- LOAD TEST IMAGE ---
img = load_img(INPUT_IMAGE_PATH, color_mode='grayscale', target_size=(IMG_SIZE, IMG_SIZE))
img_array = img_to_array(img) / 255.0
input_tensor = np.expand_dims(img_array, axis=0)  # shape: (1, 128, 128, 1)

# --- PREDICT ---
prediction = model.predict(input_tensor)[0]  # shape: (128, 128, 1)
print("Prediction min/max:", prediction.min(), prediction.max())

# --- SHOW RAW PREDICTION ---
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.title("Input Image")
plt.imshow(img_array.squeeze(), cmap='gray')

plt.subplot(1, 2, 2)
plt.title("Raw Prediction")
plt.imshow(prediction.squeeze(), cmap='gray', vmin=0, vmax=1)
plt.colorbar()
plt.tight_layout()
plt.show()

# --- THRESHOLD + SAVE MASK ---
binary_mask = (prediction > THRESHOLD).astype(np.uint8) * 255  # convert to 0/255
Image.fromarray(binary_mask.squeeze(), mode='L').save(OUTPUT_IMAGE_PATH)

print(f"✅ Binary prediction saved to: {OUTPUT_IMAGE_PATH}")
