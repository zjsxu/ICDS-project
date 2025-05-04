# train.py (updated to v3)
import os, certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
import numpy as np

# 1. Load MNIST and preprocess (add channel dimension, use float32)
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train.astype('float32')[..., None]
x_test  = x_test.astype('float32')[..., None]

# 2. Build the CNN model with data augmentation layers
model = models.Sequential([
    layers.Input(shape=(28,28,1)),
    # Data Augmentation and normalization
    layers.Rescaling(1./255),                            # scale pixels to [0,1]
    layers.RandomRotation(0.0417),                       # ±15° rotation
    layers.RandomTranslation(0.1, 0.1),                  # up to 10% shift
    layers.RandomZoom(0.1, 0.1),                         # up to 10% zoom in/out
    # Conv Block 1 (32 filters)
    layers.Conv2D(32, (3,3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.Conv2D(32, (3,3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),
    # Conv Block 2 (64 filters)
    layers.Conv2D(64, (3,3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.Conv2D(64, (3,3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),
    # Conv Block 3 (128 filters)
    layers.Conv2D(128, (3,3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.Conv2D(128, (3,3), padding='same'),
    layers.BatchNormalization(),
    layers.Activation('relu'),
    layers.MaxPooling2D((2,2)),
    layers.Dropout(0.25),
    # Dense head
    layers.Flatten(),
    layers.Dense(256),
    layers.Activation('relu'),
    layers.Dropout(0.5),
    layers.Dense(128),
    layers.Activation('relu'),
    layers.Dropout(0.5),
    layers.Dense(10, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.summary()

# 3. Set up callbacks
callbacks_list = [
    callbacks.EarlyStopping(monitor='val_loss', patience=3),
    callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-5)
]

# 4. Train the model
model.fit(
    x_train, y_train,
    epochs=20,
    batch_size=64,
    validation_split=0.1,
    callbacks=callbacks_list
)

# 5. Evaluate on test data
test_loss, test_acc = model.evaluate(x_test, y_test)
print(f"Test accuracy: {test_acc:.4f}")

# 6. Save the trained model
# model.save('mnist_cnn_v3.keras')
model.export('mnist_cnn_v3')
# print("Model saved as 'mnist_cnn_v3.keras'")
print("Model exported to SavedModel directory 'mnist_cnn_v3/'")