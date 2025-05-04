# app.py
from flask import Flask, request, jsonify, send_from_directory
import tensorflow as tf
from PIL import Image
import io, base64, numpy as np
import os
from tensorflow import keras

app = Flask(__name__, static_folder='static')

# Wrap the SavedModel at 'mnist_cnn' as a Keras layer
# --- READ HERE ---
# Change the file name here to load v1, v2 or v3: mnist_cnn, mnist_cnn_v2, mnist_cnn_v3
# Before running v3, uncomment line 39-49 and comment line 41-42
sml = keras.layers.TFSMLayer('mnist_cnn_v3', call_endpoint='serve')

# Build a tiny model that just calls that layer
model = keras.Sequential([keras.Input((28,28,1)), sml])

@app.route('/')
def index():
    # Serve the index.html
    return send_from_directory('static', 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'error':'No image provided'}), 400

    # 1. Decode base64 PNG
    header, encoded = data['image'].split(',', 1)
    img_bytes = base64.b64decode(encoded)
    # 2. Open as grayscale PIL image
    img = Image.open(io.BytesIO(img_bytes)).convert('L')
    # 3. Resize to 28×28
    img = img.resize((28,28), Image.LANCZOS)
    # 4. To NumPy, normalize, invert colors
# when running v3, change here
#     arr = np.array(img).astype('float32') / 255.0
#     arr = 1.0 - arr
    arr = np.array(img).astype('float32')
    arr = 255.0 - arr
    arr = arr.reshape((1,28,28,1))

    # 5. Predict
    preds = model.predict(arr)[0]      # length-10 vector
    label = int(np.argmax(preds))

    return jsonify({
        'label': label,
        'probabilities': preds.tolist()
    })

if __name__ == '__main__':
    # Use port 5000 by default
    app.run(debug=True)
