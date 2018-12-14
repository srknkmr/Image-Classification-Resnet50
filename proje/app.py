from __future__ import division, print_function
# coding=utf-8
import os
import numpy as np

# Keras
from keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
# ResNet50
from keras.applications.resnet50 import ResNet50
from keras.applications.imagenet_utils import preprocess_input as preprocess_input_resNet50, decode_predictions as decode_predictions_resNet50
# Define a flask app
app = Flask(__name__)

# You can also use pretrained model from Keras
# Check https://keras.io/applications/

modelResNet50 = ResNet50(weights='imagenet')
print('ResNet50 Model loaded.')
print('Running on http://localhost:5000')

def get_file_path_and_save(request):
    # Get the file from post request
    f = request.files['file']

    # Save the file to ./uploads
    basepath = os.path.dirname(__file__)
    file_path = os.path.join(
        basepath, 'uploads', secure_filename(f.filename))
    f.save(file_path)
    return file_path



@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predictResNet50', methods=['GET', 'POST'])
def predictResNet50():
    if request.method == 'POST':
        file_path = get_file_path_and_save(request)

        img = image.load_img(file_path, target_size=(224, 224))

        # Preprocessing the image
        x = image.img_to_array(img)
        # x = np.true_divide(x, 255)
        x = np.expand_dims(x, axis=0)

        # Be careful how your trained model deals with the input
        # otherwise, it won't make correct prediction!
        x = preprocess_input_resNet50(x, mode='caffe')
        # Make prediction
        preds = modelResNet50.predict(x)

        # Process your result for human
        # pred_class = preds.argmax(axis=-1)            # Simple argmax
        pred_class = decode_predictions_resNet50(preds, top=1)   # ImageNet Decode
        result = str(pred_class[0][0][1])               # Convert to string
        return result
    return None

if __name__ == '__main__':
    # Serve the app with gevent
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
