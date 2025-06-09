import tensorflow as tf
from tensorflow.keras import layers, models

def create_model():
    model = models.Sequential([
        # Encoder
        layers.Input(shape=(25, 25, 1)),
        layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2), padding='same'),
        layers.Conv2D(8, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2), padding='same'),

        # Decoder
        layers.Conv2DTranspose(8, (3, 3), strides=2, activation='relu', padding='same'),
        layers.Conv2DTranspose(16, (3, 3), strides=2, activation='relu', padding='same'),
        layers.Conv2D(1, (3, 3), activation='sigmoid', padding='same')
    ])
    return model


model = create_model()
model.compile(optimizer='adam', loss='mse')

# Assuming X and Y are your input and output arrays shaped as (num_samples, 25, 25, 1)
model.fit(X, Y, epochs=20, batch_size=32)
