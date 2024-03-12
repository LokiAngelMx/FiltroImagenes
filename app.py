import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_filters(image_path):
    img = cv2.imread(image_path)
    filtered_images = []

    filters = [
         # Filtro Promediador
        np.ones((3, 3)) / 9.0, 
        # Filtro de Realce
        np.array([
            [-2, -1, 0],
            [-1,  1, 1],
            [ 0,  1, 2]
        ]),
         # Filtro Random
        np.ones((3, 3)) * 0.1, 
        # Filtro Sobel
        np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]
        ]),
        # Filtro de inversión otro
        np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]),
        # np.array([
        #     [-1, -1, -1],
        #     [-1,  9, -1],
        #     [-1, -1, -1]
        # ]),
        # Filtro Gaussiano
        np.array([[ 1, 1, 1], [ 1, 1, 1],[ 1, 1, 1]]),
        # Filtro Laplaciano
        np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ]),
        # Filtro de Detección de Bordes de Prewitt (horizontal) otro
        np.array([[1,1,1],[1,-2,1],[-1,-1,-1]]),
        # np.array([
        #     [-1, -1, -1],
        #     [0, 0, 0],
        #     [1, 1, 1]
        # ]),
        # Filtro de Detección de Bordes de Prewitt (vertical)
        np.array([
            [-1, 0, 1],
            [-1, 0, 1],
            [-1, 0, 1]
        ]),
        # Filtro de Afinamiento otro
        np.array([[0, -1, 0], [-1, 20, -1], [0, -1, 0]])
        # np.array([
        #     [0, -1, 0],
        #     [-1, 5, -1],
        #     [0, -1, 0]
        # ])
    ]

    for kernel in filters:
        filtered_img = cv2.filter2D(img, -1, kernel)

        # Convert the filtered image to base64 encoding
        _, img_encoded = cv2.imencode('.png', filtered_img)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')
        filtered_images.append(img_base64)

    return filtered_images


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        filtered_images = apply_filters(file_path)

        return render_template('result.html', original=file_path, filtered_images=filtered_images)

    return redirect(request.url)

@app.route('/upload_another')
def upload_another():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=500)