# train.py (updated for mnist_cnn_v2.keras)
import os, certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np

# 1. Load & preprocess MNIST
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train.astype('float32')/255.0
x_test  = x_test.astype('float32')/255.0
# add channel dimension: (28,28) → (28,28,1)
x_train = x_train[..., None]
x_test  = x_test[..., None]

# 2. Build the CNN model (Version 2)
model = models.Sequential([
    layers.Input(shape=(28,28,1)),
    # Block 1: two Conv layers with 32 filters
    layers.Conv2D(32, (3,3), padding='same', activation='relu'),
    layers.BatchNormalization(),
    layers.Conv2D(32, (3,3), padding='same', activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),
    # Block 2: two Conv layers with 64 filters
    layers.Conv2D(64, (3,3), padding='same', activation='relu'),
    layers.BatchNormalization(),
    layers.Conv2D(64, (3,3), padding='same', activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),
    # Block 3: two Conv layers with 128 filters
    layers.Conv2D(128, (3,3), padding='same', activation='relu'),
    layers.BatchNormalization(),
    layers.Conv2D(128, (3,3), padding='same', activation='relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),
    # Dense classification head
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(10, activation='softmax')
])

# Compile (same settings as before)
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.summary()

# 3. Train (same hyperparameters)
model.fit(
    x_train, y_train,
    epochs=5,
    batch_size=64,
    validation_split=0.1
)

# 4. Evaluate (same as before)
test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc:.4f}")

# 5. Save updated model
# model.save('mnist_cnn_v2.keras')
model.export('mnist_cnn_v2')
# print("Model saved to 'mnist_cnn_v2.keras'")
print("Model exported to SavedModel directory 'mnist_cnn_v2/'")
