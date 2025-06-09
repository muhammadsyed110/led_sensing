import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split
from tensorflow.keras.metrics import MeanIoU
from tensorflow.keras.utils import load_img, img_to_array

# --- CONFIG ---
IMG_SIZE = 384
INPUT_PATH = 'train_data\X'
TARGET_PATH = 'train_data\Y'
BATCH_SIZE = 16
EPOCHS = 50
MODEL_SAVE_PATH = 'best_model.h5'

# --- LOAD IMAGES ---
def load_images(folder):
    files = sorted(os.listdir(folder))
    data = [img_to_array(load_img(os.path.join(folder, f), color_mode='grayscale', target_size=(IMG_SIZE, IMG_SIZE))) / 255.0 for f in files]
    return np.array(data)

print("Loading dataset...")
X = load_images(INPUT_PATH)
Y = load_images(TARGET_PATH)
# --- Visual debug (optional but highly recommended) ---
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Input Example")
plt.imshow(X[0].squeeze(), cmap='gray')

plt.subplot(1, 2, 2)
plt.title("Mask Example (Raw before binarization)")
plt.imshow(Y[0].squeeze(), cmap='gray')

plt.tight_layout()
plt.show()
Y = (Y > 0.5).astype(np.float32)  # binarize if it's mask

# --- TRAIN/VAL SPLIT ---
x_train, x_val, y_train, y_val = train_test_split(X, Y, test_size=0.2, random_state=42)

# --- DICE METRIC ---
def dice_coef(y_true, y_pred, smooth=1):
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

# --- MINI U-NET ---
def mini_unet(input_shape=(IMG_SIZE, IMG_SIZE, 1)):
    inputs = layers.Input(input_shape)

    # Encoder
    c1 = layers.Conv2D(16, 3, activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(16, 3, activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D()(c1)

    # Bottleneck
    b1 = layers.Conv2D(32, 3, activation='relu', padding='same')(p1)
    b1 = layers.Dropout(0.3)(b1)
    b1 = layers.Conv2D(32, 3, activation='relu', padding='same')(b1)

    # Decoder
    u1 = layers.UpSampling2D()(b1)
    u1 = layers.Concatenate()([u1, c1])
    c2 = layers.Conv2D(16, 3, activation='relu', padding='same')(u1)
    c2 = layers.Conv2D(16, 3, activation='relu', padding='same')(c2)

    outputs = layers.Conv2D(1, 1, activation='sigmoid', padding='same')(c2)

    model = models.Model(inputs, outputs)
    return model

# --- COMPILE ---
# model = mini_unet()
# model.compile(optimizer='adam',
#               loss='binary_crossentropy',
#               metrics=[
#                   'binary_accuracy',
#                   tf.keras.metrics.MeanSquaredError(name='mse'),
#                   dice_coef
#               ])

# # --- CALLBACKS ---
# checkpoint = ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_dice_coef', save_best_only=True, mode='max', verbose=1)

# --- TRAIN ---
# history = model.fit(
#     x_train, y_train,
#     validation_data=(x_val, y_val),
#     epochs=EPOCHS,
#     batch_size=BATCH_SIZE,
#     callbacks=[checkpoint]
# )

# # --- IoU on validation ---
# y_pred = model.predict(x_val) > 0.5
# iou = MeanIoU(num_classes=2)
# iou.update_state(y_val, y_pred)
# print(f"Mean IoU on validation set: {iou.result().numpy():.4f}")
