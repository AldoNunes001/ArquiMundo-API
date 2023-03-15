import io
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as image_utils
from tensorflow.keras.applications import vgg16

app = Flask(__name__)
model = load_model('ArquiMundo001.h5')
feature_extraction_model = vgg16.VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

class_labels = [
    'Barroca',
    'Eclética',
    'Grega',
    'Moderna',
    'Renascentista'
]


def preprocess_image(image):
    img = Image.open(io.BytesIO(image)).resize((224, 224))
    image_array = image_utils.img_to_array(img)
    images = np.expand_dims(image_array, axis=0)
    return vgg16.preprocess_input(images)


@app.route('/classify', methods=['POST'])
def classify_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image'].read()
    preprocessed_image = preprocess_image(image)
    features = feature_extraction_model.predict(preprocessed_image)
    results = model.predict(features)
    single_result = results[0]
    most_likely_class_index = int(np.argmax(single_result))
    class_likelihood = single_result[most_likely_class_index]
    class_label = class_labels[most_likely_class_index]

    response = {
        'architecture': class_label,
        'likelihood': float(class_likelihood)
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)