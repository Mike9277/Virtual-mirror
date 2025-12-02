from flask import Flask, Response, jsonify
import cv2
from flask_cors import CORS
import threading
import os
import json

app = Flask(__name__)
CORS(app) 
CORS(app, resources={r"/*": {"origins": "*"}})

# ------------------------------------------------------------------
# Dynamically assess filepath
# Load definitions fron .config
base_dir = Path(__file__).resolve().parent.parent
config_path = base_dir / "env_config.json"
with open(config_path) as f:
    config = json.load(f)

MAIN_DIR = config["MAIN_DIR"]
BACK_DIR = config["BACK_DIR"]

USER_BACK = config["USER_BACK"]
USER_JETSON = config["USER_JETSON"]

IP_MAIN = config["IP_MAIN"]
IP_BACK = config["IP_BACK"]
IP_JETSON = config["IP_JETSON"]


UPLOAD_FOLDER = MAIN_DIR + '/shared-data/img_path'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PUBLIC_IMAGES_DIR = MAIN_DIR + '/shared-data/web_src/images'
CLOTH_IMAGES_DIR = MAIN_DIR + '/shared-data/web_src/cloths'
# ------------------------------------------------------------------

camera_index = 0
video_stream = cv2.VideoCapture(camera_index)
lock = threading.Lock()

def resize_and_crop(frame, target_width, target_height):
    h, w = frame.shape[:2]
    target_aspect = target_width / target_height
    input_aspect = w / h

    if input_aspect > target_aspect:
        
        new_width = int(target_aspect * h)
        frame = cv2.resize(frame, (new_width, h))
        left = (new_width - target_width) // 2
        right = left + target_width
        frame = frame[:, left:right]
    else:
        
        new_height = int(w / target_aspect)
        frame = cv2.resize(frame, (w, new_height))
        top = (new_height - target_height) // 2
        bottom = top + target_height
        frame = frame[top:bottom, :]

    frame = cv2.resize(frame, (target_width, target_height))
    return frame

def generate_frames():
    target_width = 768
    target_height = 1024
    while True:
        with lock:
            success, frame = video_stream.read()
        if not success:
            break
        else:
            resized_frame = resize_and_crop(frame, target_width, target_height)

            ret, buffer = cv2.imencode('.jpg', resized_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

"""
if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=4000, 
            ssl_context=(os.path.join(MAIN_DIR,'web_app','backend-cert.pem'), os.path.join(MAIN_DIR,'web_app','backend-key.pem')))
"""

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    cert_path = os.path.join(MAIN_DIR, "web_app", "backend-cert.pem")
    key_path  = os.path.join(MAIN_DIR, "web_app", "backend-key.pem")

    # TLS 1.3-only server context; PQ groups come from OpenSSL config
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.maximum_version = ssl.TLSVersion.TLSv1_3
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    app.run(
            host="0.0.0.0",
            port=4000,
            ssl_context=context)
