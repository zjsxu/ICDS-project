# train.py
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

# 2. Build the CNN model
model = models.Sequential([
    layers.Input(shape=(28,28,1)),
    layers.Conv2D(32, (3,3), activation='relu', padding='same'),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),
    layers.Conv2D(64, (3,3), activation='relu', padding='same'),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.summary()

# 3. Train
model.fit(
    x_train, y_train,
    epochs=5,
    batch_size=64,
    validation_split=0.1
)

# 4. Evaluate
test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc:.4f}")

# 5. Save
model.export('mnist_cnn')
print("Model exported to SavedModel directory 'mnist_cnn/'")
