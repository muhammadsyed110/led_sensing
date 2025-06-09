import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split
from tensorflow.keras.metrics import MeanIoU
from tensorflow.keras.utils import load_img, img_to_array
import matplotlib.pyplot as plt

# --- CONFIG ---
IMG_SIZE = 128
INPUT_PATH = 'X'
TARGET_PATH = 'Y'
BATCH_SIZE = 8
EPOCHS = 50
MODEL_SAVE_PATH = 'best_model.h5'

# --- LOAD INPUT IMAGES (grayscale) ---
def load_input_images(folder):
    files = sorted(os.listdir(folder))
    data = [img_to_array(load_img(os.path.join(folder, f), color_mode='grayscale', target_size=(IMG_SIZE, IMG_SIZE))) / 255.0 for f in files]
    return np.array(data)

# --- LOAD MASKS (convert RGB to grayscale manually) ---
def load_masks(folder):
    files = sorted(os.listdir(folder))
    data = []
    for f in files:
        img = load_img(os.path.join(folder, f), color_mode='rgb', target_size=(IMG_SIZE, IMG_SIZE))
        arr = img_to_array(img) / 255.0  # RGB normalized
        gray = np.mean(arr, axis=-1, keepdims=True)  # convert to grayscale
        data.append(gray)
    return np.array(data)

# --- LOAD DATA ---
print("Loading dataset...")
X = load_input_images(INPUT_PATH)
Y = load_masks(TARGET_PATH)

# --- DEBUG IMAGE LOADING ---
print("Input shape:", X.shape)
print("Mask shape:", Y.shape)
print("Mask value range:", Y.min(), "to", Y.max())

# --- VISUAL DEBUG ---
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Sample Input")
plt.imshow(X[0].squeeze(), cmap='gray')
plt.subplot(1, 2, 2)
plt.title("Sample Mask (Raw Grayscale)")
plt.imshow(Y[0].squeeze(), cmap='gray')
plt.tight_layout()
plt.show()

# --- BINARIZE MASKS ---
# Y = (Y > 0.2).astype(np.float32)
# --- BINARIZE + INVERT MASKS ---
# Y = (Y > 0.2).astype(np.float32)
# Y = 1.0 - Y  # <-- Invert: black pixels become 1.0 (foreground)
Y = (Y > 0.3).astype(np.float32)  



# --- SPLIT TRAIN/VAL ---
x_train, x_val, y_train, y_val = train_test_split(X, Y, test_size=0.2, random_state=42)

# --- DICE METRIC + LOSS ---
def dice_coef(y_true, y_pred, smooth=1):
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

def dice_loss(y_true, y_pred):
    return 1 - dice_coef(y_true, y_pred)

# --- MINI U-NET ---
def mini_unet(input_shape=(IMG_SIZE, IMG_SIZE, 1)):
    inputs = layers.Input(input_shape)

    # Encoder
    c1 = layers.Conv2D(16, 3, activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(16, 3, activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D()(c1)

    c2 = layers.Conv2D(32, 3, activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(32, 3, activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D()(c2)

    # Bottleneck
    b1 = layers.Conv2D(64, 3, activation='relu', padding='same')(p2)
    b1 = layers.Dropout(0.3)(b1)
    b1 = layers.Conv2D(64, 3, activation='relu', padding='same')(b1)

    # Decoder
    u1 = layers.UpSampling2D()(b1)
    u1 = layers.Concatenate()([u1, c2])
    c3 = layers.Conv2D(32, 3, activation='relu', padding='same')(u1)
    c3 = layers.Conv2D(32, 3, activation='relu', padding='same')(c3)

    u2 = layers.UpSampling2D()(c3)
    u2 = layers.Concatenate()([u2, c1])
    c4 = layers.Conv2D(16, 3, activation='relu', padding='same')(u2)
    c4 = layers.Conv2D(16, 3, activation='relu', padding='same')(c4)

    outputs = layers.Conv2D(1, 1, activation='sigmoid')(c4)

    model = models.Model(inputs, outputs)
    return model

# --- COMPILE MODEL ---
model = mini_unet()
model.compile(
    optimizer='adam',
    loss=dice_loss,
    metrics=[
        'binary_accuracy',
        tf.keras.metrics.MeanSquaredError(name='mse'),
        dice_coef
    ]
)

# --- SAVE BEST MODEL ---
checkpoint = ModelCheckpoint(
    MODEL_SAVE_PATH,
    monitor='val_dice_coef',
    save_best_only=True,
    mode='max',
    verbose=1
)

# --- TRAIN ---
history = model.fit(
    x_train, y_train,
    validation_data=(x_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[checkpoint]
)

# --- IoU SCORE ---
print("Evaluating IoU on validation set...")
y_pred = model.predict(x_val)
y_pred_bin = (y_pred > 0.5).astype(np.uint8)

iou = MeanIoU(num_classes=2)
iou.update_state(y_val, y_pred_bin)
print(f"✅ Mean IoU on validation set: {iou.result().numpy():.4f}")
