# ---------------------------------------------------------------------------- #
# This is the main application for the Smart Shopping Use Case in the context
# of the project CLEVER.
# The application is designed to work as a web application and allows for the
# virtual try-on as well as for collect and processe new users images using 
# openpose library.
# The application now supports communication between two servers through rdma
# and allows for multi-thread users requests.
# The initial script was prepared by Emilie le Rouzic.
#
#
# 11 2025, Michelangelo Guaitolini
# ---------------------------------------------------------------------------- #

# Include dependencies
from re import L, S
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from PIL import Image

import json
from pathlib import Path
import subprocess
import os
import io
import base64
import shutil
import cv2
import signal
import time
import sys
import uuid
import shutil

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})

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

server_process = None

# ---------------------------------------------------------------------------- #
# CAMERA STREAMING
# Functions to handle camera streaming. Camera is used to collect images from 
# the users. Functions here allow for start/stop a camera stream and handle
# the streaming.

def start_camera_stream():
    global server_process
    if server_process is None or server_process.poll() is not None:
        server_process = subprocess.Popen(["python3", "live.py"])
        print("Camera stream API started")

def stop_camera_stream():
    global server_process
    if server_process and server_process.poll() is None:
        server_process.terminate()
        server_process.wait()
        print("Camera stream API stopped")

def signal_handler(sig, frame):
    print('Interrupt received, stopping server...')
    stop_camera_stream()
    sys.exit(0)

# ---------------------------------------------------------------------------- #
# HOME PAGE FOR WEB APPLICATION
# This defines the "Home" page of the web application. Without this portion of
# the code, the web application is not loaded properly. 

@app.route('/', methods=['GET'])
def get_images_list():
    try:
        # Shows all the images in the images directory that start with "person"
        # and are in jpg format.
        images_list = [image for image in os.listdir(PUBLIC_IMAGES_DIR) if image.startswith('person') and image.endswith('.jpg')]
        return jsonify(images_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------------- #
# COMBINE GARMENT AND UPLOADED PICTURE [RDMA version]
# this script is necessary to generate the Virtual Try-On output, after that a 
# user's picture and a garment have been selected.
@app.route('/run-script_upl', methods=['POST'])
def run_script_upl():
    # Collects person and garment data, after interacting with the home page of
    # the web application (get_json).
    data = request.get_json()
    person = data.get('person')
    cloth = data.get('cloth')
    unique_id = data.get('sessionId')    

    print("UNIQUE ID: ", unique_id)

    if not cloth:
        return jsonify({'error': 'Cloth selection is missing'}), 422
    
    # The final image is not saved locally. Clean any possible previous result
    # from the folder.
    result_image_path = MAIN_DIR + "/shared-data-tmp/" + unique_id + "/results"
    result_image_path_rdma = BACK_DIR + "/shared-data-tmp/" + unique_id + "/results"
            
    try:
        # Run locally
        # script_path = MAIN_DIR + "/run_only_viton.sh"
        # subprocess.run(['bash', script_path, person, cloth], check=True)
        
        # This portion is for the RDMA version.
        # -------------------------------------------------------------------
        # Run VITON-HD on the other server.
        script_path_rdma = BACK_DIR + "/run_only_viton.sh"
        subprocess.run(["ssh -o StrictHostKeyChecking=no", 
                        f"{USER_BACK}@{IP_BACK}",
                        f"{script_path_rdma} {person} {cloth} {unique_id}"],
                       check=True, text=True)
        
        # RDMA transfer back the result image
        print("Executing RDMA transfer from back to main.")
        script_rdma = MAIN_DIR + "/rdma_service.sh"
        file_to_transfer = unique_id
        server = "main"
        client = "back"
        subprocess.run(['bash', script_rdma, file_to_transfer, server, client], check=True, text=True)        
        print("RDMA transfer done!")
        # -------------------------------------------------------------------

        result_image = None
        # Find the most recent .jpg file.
        jpg_files = [f for f in os.listdir(result_image_path) if f.endswith(".jpg")]
        if not jpg_files:
            return jsonify({'error': 'Result image not found'}), 401

        # Files full path
        jpg_files_full = [os.path.join(result_image_path, f) for f in jpg_files]

        # Select the most recent file.
        result_image = max(jpg_files_full, key=os.path.getmtime)

        # Encode the result image in base64 to return to frontend
        with open(result_image, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
                    
        return jsonify({
            'output': 'Script executed successfully',
            'person': person,
            'cloth': cloth,
            'image' : image_data,
        }), 600

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8') if e.stderr else ''
        return jsonify({'error': f"Script failed with error: {error_output}"}), 402

    except Exception as e:
        return jsonify({'error': str(e)}), 12345

# ---------------------------------------------------------------------------- #
# COMBINE GARMENT AND PICTURE FROM WEBCAM
# this script is necessary to generate the Virtual Try-On output, after that a 
# user's picture and a garment have been selected.
@app.route('/run-script', methods=['POST'])
def run_script():
    # Collects person and garment data, after interacting with the home page of
    # the web application (get_json).
    data = request.get_json()
    person = "webcam_image.jpg"
    cloth = data.get('cloth')
    unique_id = data.get('sessionId')    

    print("UNIQUE ID: ", unique_id)

    if not cloth:
        return jsonify({'error': 'Cloth selection is missing'}), 422

    # The final image is not saved locally. Clean any possible previous result
    # from the folder.
    result_image_path = MAIN_DIR + "/shared-data-tmp/" + unique_id + "/results"
    result_image_path_rdma = BACK_DIR + "/shared-data-tmp/" + unique_id + "/results"
        
    try:
        # Run locally
        # script_path = MAIN_DIR + "/run_only_viton.sh"
        # subprocess.run(['bash', script_path, person, cloth], check=True)
        
        # -------------------------------------------------------------------
        # Run VITON-HD on the other server.
        script_path_rdma = BACK_DIR + "/run_only_viton.sh"
        subprocess.run(["ssh", 
                        f"{USER_BACK}@{IP_BACK}",
                        f"{script_path_rdma} {person} {cloth} {unique_id}"],
                        check=True, text=True)
        
        # RDMA transfer back the result image
        print("Executing RDMA transfer from back to main.")
        script_rdma = MAIN_DIR + "/rdma_service.sh"
        file_to_transfer = unique_id
        server = "main"
        client = "back"
        subprocess.run(['bash', script_rdma, file_to_transfer, server, client], check=True, text=True)        
        print("RDMA transfer done!")
        # -------------------------------------------------------------------

        result_image = None
        # Find the most recent .jpg file.
        jpg_files = [f for f in os.listdir(result_image_path) if f.endswith(".jpg")]
        if not jpg_files:
            return jsonify({'error': 'Result image not found'}), 401

        # Files full path
        jpg_files_full = [os.path.join(result_image_path, f) for f in jpg_files]

        # Select the most recent file.
        result_image = max(jpg_files_full, key=os.path.getmtime)

        # Encode the result image in base64 to return to frontend
        with open(result_image, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
                    
        return jsonify({
            'output': 'Script executed successfully',
            'person': person,
            'cloth': cloth,
            'image' : image_data,
        }), 600

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8') if e.stderr else ''
        return jsonify({'error': f"Script failed with error: {error_output}"}), 402

    except Exception as e:
        return jsonify({'error': str(e)}), 403

# ---------------------------------------------------------------------------- #
# LOAD IMAGE
# This is to load a new image to the web application using the camera to take
# a picture from the user.
@app.route('/add-img', methods=['POST'])
def add_img():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = file.filename
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(save_path)
    try:
        file.save(save_path)
        with open(save_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        return jsonify({'message': 'File successfully uploaded', 'image': encoded_image,'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ---------------------------------------------------------------------------- #
# START PQC channel
# This function activates the PQC channel between the Jetson and Smartedge
# servers. 
# def start_pqc():
#     try:
#         print("Starting pqc channel on 10.30.7.210...")
#         subprocess.Popen([
#             "ssh",
#             f"{USER_JETSON}@{IP_JETSON}",
#             "nohup ./file-tests/run_server.sh > run_server.log 2>&1 &"
#         ])
#         print("PQ channel started!")
#     except Exception as e:
#         print("Error", str(e))

# ---------------------------------------------------------------------------- #
# PROCESS UPLOADED IMAGE [RDMA version + multithread]
# When a new image is loaded, it has to be processed before to be added to the
# home interface of the web application.
@app.route('/preprocess-upl', methods=['POST'])
def preprocess_upl():
    data = request.get_json()
    filename = data.get('filename');
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    try:
        # Get the path of the uploaded image
        upload_folder = app.config['UPLOAD_FOLDER']
        target_file_path = os.path.join(upload_folder, filename)

        # Ensure the target file exists
        if not os.path.isfile(target_file_path):
            return jsonify({'error': f'File {filename} does not exist'}), 400

        # Generate unique session directory
        unique_id = str(uuid.uuid4())
        session_dir = os.path.join(MAIN_DIR + "/shared-data-tmp", unique_id)
        os.makedirs(session_dir,exist_ok=True)

        # Copy necessary files in session_dir
        local_file_path = os.path.join(session_dir,filename)
        shutil.copy(target_file_path, local_file_path)

        # Run the preprocessing script
        script_path = "../parallel_process.sh"
        subprocess.run(['bash', script_path, session_dir], check=True)
        
        # Construct paths to generated images
        filename_without_ext = os.path.splitext(filename)[0]
        #vis_image_dir = session_dir + "/img_parse/train_parsing_vis/" + unique_id
        vis_image_dir = session_dir + "/img_parse/"
        vis_image_path = os.path.join(vis_image_dir, f"{filename_without_ext}_vis.png")

        openpose_img_dir = session_dir + "/openpose_img/"
        rendered_image_path = os.path.join(openpose_img_dir, f"{filename_without_ext}_rendered.png")

        # This portion is for the RDMA version.
        # -------------------------------------------------------------------
        # Transfer file to a second server
        script_rdma = "../rdma_service.sh" 
        file_to_transfer = unique_id
        server = "back"
        client = "main"
        print("Executing RDMA transfer")
        subprocess.run(['bash', script_rdma, file_to_transfer, server, client], check=True, text=True)        
        print("RDMA transfer done!")
        # -------------------------------------------------------------------

        # Ensure the generated images exist
        if not os.path.isfile(vis_image_path):
            return jsonify({'error': f'Generated image {vis_image_path} does not exist'}), 499
        if not os.path.isfile(rendered_image_path):
            return jsonify({'error': f'Generated image {rendered_image_path} does not exist'}), 501

        # Read and encode the images to include them in the response
        with open(target_file_path, "rb") as original_file:
            original_image = base64.b64encode(original_file.read()).decode('utf-8')
        with open(vis_image_path, "rb") as vis_file:
            vis_image = base64.b64encode(vis_file.read()).decode('utf-8')
        with open(rendered_image_path, "rb") as rendered_file:
            rendered_image = base64.b64encode(rendered_file.read()).decode('utf-8')

        print("Unique ID:",unique_id)
        return jsonify({
            'message': f'Image {filename} preprocessed successfully and script executed',
            'original_image': original_image,
            'vis_image': vis_image,
            'rendered_image': rendered_image,
            'sessionId': unique_id,
            'cpu': False
        }), 200
    except FileNotFoundError:
        return jsonify({'error': 'File or directory not found'}), 500
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8') if e.stderr else ''
        return jsonify({'error': f'Script failed with error: {error_output}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------------- #
# PROCESS PICTURE FROM WEBCAM [RDMA version + multithread]
# When a new picture is taken, it has to be processed before to be added to the
# home interface of the web application.
@app.route('/preprocess-img', methods=['POST'])
def preprocess_img():
    data = request.get_json()
    image_data = data.get('image_data')  # base64 image from frontend
    if not image_data:
        return jsonify({'error': 'No image_data provided'}), 423

    try:
        # Generate unique session directory
        unique_id = str(uuid.uuid4())
        session_dir = os.path.join(MAIN_DIR, "shared-data-tmp", unique_id)
        os.makedirs(session_dir, exist_ok=True)  # ensure the folder exists

        # Save the base64 image to a file
        filename = "webcam_image.jpg"
        image_path = os.path.join(session_dir, filename)

        # Strip off the header if it exists
        if ',' in image_data:
            _, encoded = image_data.split(',', 1)
        else:
            encoded = image_data

        # Decode and write to file
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(encoded))

        # Run the preprocessing script
        script_path = "../parallel_process.sh"
        subprocess.run(['bash', script_path, session_dir], check=True)
        
        # Construct paths to generated images
        filename_without_ext = os.path.splitext(filename)[0]
        vis_image_dir = session_dir + "/img_parse/"
        vis_image_path = os.path.join(vis_image_dir, f"{filename_without_ext}_vis.png")

        openpose_img_dir = session_dir + "/openpose_img/"
        rendered_image_path = os.path.join(openpose_img_dir, f"{filename_without_ext}_rendered.png")
        
        # This portion is for the RDMA version.
        # ---------------------------------------------------------
        # Transfer file to a second server
        script_rdma = "../rdma_service.sh" 
        file_to_transfer = unique_id
        server = "back"
        client = "main"
        print("Executing RDMA transfer")
        subprocess.run(['bash', script_rdma, file_to_transfer, server, client], check=True, text=True)        
        print("RDMA transfer done!")
        # ---------------------------------------------------------

        # Ensure the generated images exist
        if not os.path.isfile(vis_image_path):
            return jsonify({'error': f'Generated image {vis_image_path} does not exist'}), 499
        if not os.path.isfile(rendered_image_path):
            return jsonify({'error': f'Generated image {rendered_image_path} does not exist'}), 501

        # Read and encode the images to include them in the response
        with open(image_path, "rb") as original_file:
            original_image = base64.b64encode(original_file.read()).decode('utf-8')
        with open(vis_image_path, "rb") as vis_file:
            vis_image = base64.b64encode(vis_file.read()).decode('utf-8')
        with open(rendered_image_path, "rb") as rendered_file:
            rendered_image = base64.b64encode(rendered_file.read()).decode('utf-8')
        
        print("Unique ID:",unique_id)
        return jsonify({
            'message': f'Image {filename} preprocessed successfully and script executed',
            'original_image': original_image,
            'vis_image': vis_image,
            'rendered_image': rendered_image,
            'sessionId': unique_id,
            'cpu': False
        }), 200
    except FileNotFoundError:
        return jsonify({'error': 'File or directory not found'}), 500
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8') if e.stderr else ''
        return jsonify({'error': f'Script failed with error: {error_output}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

  
# ---------------------------------------------------------------------------- #
# TEST NEW IMAGES WITH GARMENT
# This application is to test uploaded and pre-processed images with VITON-HD
# functionalities, namely with garments available. This does not include new 
# images in the "Home" collection.
#
# note: this should be automatic. 
#
@app.route('/addViton', methods=['GET'])
def add_viton():
    try:
        cloth_images_source = [os.path.join(CLOTH_IMAGES_DIR, image) for image in os.listdir(CLOTH_IMAGES_DIR) if image.endswith('.jpg')]
        destination_dir = os.path.join(PUBLIC_IMAGES_DIR, 'cloths')

        cloth_images_destination = [os.path.join('cloths', image) for image in os.listdir(destination_dir) if image.endswith('.jpg')]
        print("destination dire :",destination_dir)
        return jsonify(cloth_images_destination), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------------- #
# CAMERA
# This section is to capture images from the camera. As long as the streaming
# is up, it is possible to use VideoCapture to capture an image from it. 
# Capturing an image from the streaming provides an image of the user that 
# can be used later for the Virtual Try-On app.
# Captured images need to be confirmed and after that they are download, to be
# then uploaded through the "New" page, processed and tested with desired 
# garment.
#
# Note: download/upload and preprocess should happen automatically.
#
import json


with open(config_path, 'r') as file:
    config = json.load(file)
ip_address = config.get("IP_MAIN")
camera_port = config.get("cameraPort")

camera_url = f"http://{ip_address}:{camera_port}/video_feed"

@app.route('/capture', methods=['GET'])
def capture_camera():
    video_capture = cv2.VideoCapture(camera_url)
    if not video_capture.isOpened():
        return jsonify({'error': 'Unable to open video stream'}), 500

    success, frame = video_capture.read()
    video_capture.release()

    if not success:
        return jsonify({'error': 'Unable to capture image from video stream'}), 500

    # h, w = frame.shape[:2]
    # top = (h - 1024) // 2
    # bottom = top + 1024
    # left = (w - 768) // 2
    # right = left + 768
    # cropped_frame = frame[top:bottom, left:right]

    # 
    ret, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'image': jpg_as_text}), 200

# @app.route('/camera-stream', methods=['POST'])
# def camera_stream():
#     data = request.get_json()
#     camera_open = data.get('cameraOpen')
#     try:
#         if camera_open:
#             start_camera_stream()
#             return jsonify("Camera stream started"), 200
#         else:
#             stop_camera_stream()
#             return jsonify("Camera stream stopped"), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# ---------------------------------------------------------------------------- #
# MAIN FUNCTION
if __name__ == '__main__':
    # Start PQC channel on Jetson
    # list_jetson_files()
    # start_pqc()
    
    # Register the signal handler to catch Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, signal_handler)
    try:
        app.run(host='0.0.0.0', port=5000, ssl_context=(os.path.join(MAIN_DIR,'web_app','backend-cert.pem'), os.path.join(MAIN_DIR,'web_app','backend-key.pem')))
    finally:
      stop_camera_stream()
