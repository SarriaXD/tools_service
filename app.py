from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from device_mockup import embed_image_in_frame

app = Flask(__name__)
CORS(app, resources={r"/mockup-device": {"origins": "*"}})
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/mockup-device', methods=['POST'])
def mockup_device():

    if 'image' not in request.files:
        return 'No file part'
    image = request.files['image']
    if image.filename == '':
        return 'No selected file'
    if not image or not allowed_image(image.filename):
        return 'File type not allowed'

    image = request.files['image'].stream
    frame = request.form['frame']
    option = request.form['option']

    if not frame or not option:
        return jsonify({'error': 'Missing frame or option'}), 400

    try:
        image_io = embed_image_in_frame(image, frame, option)
    except:
        return jsonify({'error': 'Invalid base64 image data or Invalid frame'}), 400

    try:
        return send_file(image_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error processing image: {str(e)}")
        return jsonify(error=str(e)), 400


@app.route('/', methods=['GET'])
def index():
    return 'Welcome to the tools service!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)
