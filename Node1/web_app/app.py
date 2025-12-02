# ---------------------------------------------------------------------------- #
# This is the main application for the Smart Shopping Use Case in the context
# of the project CLEVER.
# The application is designed to work as a web application and allows for the
# virtual try-on as well as for collect and processe new users images using 
# openpose library.
# The application now supports communication between two servers through rdma
# and allows for multi-thread users requests.
#
#
# 11 2025, Michelangelo Guaitolini
# ---------------------------------------------------------------------------- #

# Include dependencies
import os
import sys
import io
import uuid
import time
import json
import signal
import base64
import shutil
import subprocess
import threading

from pathlib import Path
from re import L, S
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from PIL import Image
import cv2
import ssl

import rdma
import numpy as np

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})

# ---------------------------------------------------------------------------- #
# Load definitions fron .config
base_dir = Path(__file__).resolve().parent.parent
config_path = base_dir / "env_config.json"
with open(config_path) as f:
    config = json.load(f)

MAIN_DIR = config["MAIN_DIR"]
BACK_DIR = config["BACK_DIR"]
HOST_DIR = config["HOST_DIR"]

USER_MAIN = config["USER_MAIN"]
USER_BACK = config["USER_BACK"]
USER_JETSON = config["USER_JETSON"]

IP_MAIN = config["IP_MAIN"]
IP_BACK = config["IP_BACK"]
IP_RDMA_BACK = config["PORT_BACK"]
IP_RDMA_MAIN = config["PORT_MAIN"]
IP_JETSON = config["IP_JETSON"]

DEPLOYMENT = config["DEPLOYMENT"]

UPLOAD_FOLDER = MAIN_DIR + '/shared-data/img_path'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PUBLIC_IMAGES_DIR = MAIN_DIR + '/shared-data/web_src/images'
CLOTH_IMAGES_DIR = MAIN_DIR + '/shared-data/web_src/cloths'

server_process = None

import os
import subprocess
from pathlib import Path


rdma_sink = None
rdma_src = None
rdma_send_buf = np.zeros(10 * 1024 * 1024, dtype=np.uint8)

# ---------------------------------------------------------------------------- #
def send_session_dir_via_rdma(session_dir: str):
    """
    Send all files in `session_dir` (and subfolders) via RDMA client executable.
    
    Args:
        session_dir: Root directory to send.
    """
    session_dir = Path(session_dir)
    if not session_dir.exists():
        raise FileNotFoundError(f"{session_dir} does not exist")

    # Send command 0 to indicate that we are sending a list of files.
    rdma_send_buf[0] = 0
    rdma_sink.send(rdma_send_buf[:1])
    
    # Loop through all files recursively
    for file_path in session_dir.rglob("*"):
        if file_path.is_file():
            # Relative path with respect to session_dir
            rel_path = file_path.relative_to(session_dir)
            # Command: RDMA client, file to send, server IP
            
            # Load file as-is into numpy array
            file_array = np.fromfile(file_path, dtype=np.uint8)
            
            # Convert file path to bytes and then to numpy array
            path_str = str(file_path)
            path_bytes = path_str.encode('utf-8')
            path_array = np.frombuffer(path_bytes, dtype=np.uint8)
            
            # Copy file path to RDMA send buffer
            rdma_send_buf[:len(path_array)] = path_array
            
            # Send header, which contains the size of the file in bytes
            rdma_sink.send(rdma_send_buf[:len(path_array)])
            
            # Copy file content to RDMA send buffer (after path)
            rdma_send_buf[:len(file_array)] = file_array
            
            # Send content (NOT full array, just the size of the file)
            rdma_sink.send(rdma_send_buf[:len(file_array)])
            
    rdma_sink.send(rdma_send_buf[:0])

# ---------------------------------------------------------------------------- #
# TIMER
# To be executed for parallel process and keep track of the latency of the 
# processing procedure.
def execute_with_timer(command,log_file=None):
    """Run a subprocess command showing real-time elapsed time and logging output."""
    start_time = time.time()
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        universal_newlines=True
    )

    with open(log_file, "w") if log_file else open(os.devnull, "w") as log:
        while True:
            line = proc.stdout.readline()
            if line:
                log.write(line)
                log.flush()

            if proc.poll() is not None:
                break

            elapsed = time.time() - start_time
            print(f"\rRunning time: {elapsed:.2f}s", end="")
            time.sleep(0.1)

    total_time = time.time() - start_time
    print(f"\nExecution finished. Total time: {total_time:.2f}s")
    return total_time

# ---------------------------------------------------------------------------- #
# PARALLEL_PROCESS
# This function runs Openpose (with GVirtus service integrated) and 2D Human
# Parsing, processing the uploaded image and providing all the necessary data
# to run VITON-HD. 
# Openpose and 2D-Human-Parsing are run in parallel, to optimize execution time. 
def preprocess_python(session_dir):
    session_dir = Path(session_dir)
    image_file = next(session_dir.glob("*.jpg"))  # first .jpg
    filename = image_file.name
    filename_noext = image_file.stem

    # Load config paths already loaded in your app.py
    global MAIN_DIR

    # Output folders
    output_json = session_dir / "openpose_json"
    output_img  = session_dir / "openpose_img"
    output_parse = session_dir / "img_parse"

    output_json.mkdir(exist_ok=True)
    output_img.mkdir(exist_ok=True)
    output_parse.mkdir(exist_ok=True)

    # HUMAN PARSING
    def run_human_parsing():
        img_list = session_dir / "img_list.txt"
        img_list.write_text(str(image_file) + "\n")

        model_path = (
            Path(MAIN_DIR) /
            "2D-Human-Parsing" / "pretrained" /
            "deeplabv3plus-xception-vocNov14_20-51-38_epoch-89.pth"
        )

        command = (
            f"cd {MAIN_DIR}/2D-Human-Parsing/inference && "
            f"python3 inference_acc.py "
            f"--loadmodel {model_path} "
            f"--img_list {img_list} "
            f"--output_dir {output_parse}"
        )

        log = session_dir / "human_parsing.log"
        time_log = session_dir / "human_parsing_time.log"

        total = execute_with_timer(command, log)
        time_log.write_text(f"Total time: {total:.2f}s\n")

    # OPENPOSE via GVirtuS
    def run_openpose():
        media_dir = Path(MAIN_DIR) / "GVirtuS/examples/openpose/media"
        tmp_input = media_dir / filename

        # Copy image
        subprocess.run(f"cp '{image_file}' '{tmp_input}'", shell=True)

        command = (
            f"cd {MAIN_DIR}/GVirtuS && "
            f"make run-openpose-test INPUT_FILE=/opt/openpose/examples/media/{filename}"
        )

        openpose_log = session_dir / "openpose.log"
        time_total = execute_with_timer(command, openpose_log)
        (session_dir / "openpose_time.log").write_text(f"Total time: {time_total:.2f}s\n")

        # Move outputs
        json_src = media_dir / f"{filename_noext}_keypoints.json"
        pose_src = media_dir / f"{filename_noext}_pose.png"

        if json_src.exists():
            target_json = output_json / json_src.name
            shutil.copy2(json_src, target_json)  # copy file with metadata
            json_src.unlink()                     # remove original

        if pose_src.exists():
            target_img = output_img / f"{filename_noext}_rendered.png"
            shutil.copy2(pose_src, target_img)
            pose_src.unlink()

        tmp_input.unlink(missing_ok=True)

    # Run in parallel
    t1 = threading.Thread(target=run_human_parsing)
    t2 = threading.Thread(target=run_openpose)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("Preprocessing complete.")

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

    # print("UNIQUE ID: ", unique_id)

    if not cloth:
        return jsonify({'error': 'Cloth selection is missing'}), 422

    # The final image is not saved locally. Clean any possible previous result
    # from the folder.
    result_image_path = MAIN_DIR + "/shared-data-tmp/" + unique_id + "/results"
    result_image_path_rdma = BACK_DIR + "/shared-data-tmp/" + unique_id + "/results"
        
    try:
        config_path = base_dir / "env_config.json"
        with open(config_path) as f:
            config = json.load(f)
            DEPLOYMENT=config["DEPLOYMENT"]
            
        if DEPLOYMENT == "LOCAL":
            # Run locally
            # ---------------------------------------------------------------
            docker_cmd = ("docker run --gpus all --rm --shm-size=2g "
                          f"-v /home/{USER_MAIN}/.ssh:/root/.ssh:ro "
                          "-v /var/run/docker.sock:/var/run/docker.sock "
                          f"-v {HOST_DIR}/shared-data/:/app/shared-data "
                          f"-v {HOST_DIR}/shared-data-tmp/:/app/shared-data-tmp "
                          f"smart-mirror-node_2 /app/run_only_viton.sh '{person}' '{cloth}' '{unique_id}'"
                         )
            # ----------------------------------------------------------------
            subprocess.run([docker_cmd], shell=True, check=True, text=True)
        else:
            # ---------------------------------------------------------------
            docker_cmd = ("docker run --gpus all --rm --shm-size=2g "
                          f"-v /home/{USER_BACK}/.ssh:/root/.ssh:ro "
                          "-v /var/run/docker.sock:/var/run/docker.sock "
                          f"-v {BACK_DIR}/shared-data/:/app/shared-data "
                          f"-v {BACK_DIR}/shared-data-tmp/:/app/shared-data-tmp "
                          f"smart-mirror-node_2 /app/run_only_viton.sh '{person}' '{cloth}' '{unique_id}'"
                         )
            # ----------------------------------------------------------------
            # Run VITON-HD on the other server.
            subprocess.run(["ssh",f"{USER_BACK}@{IP_BACK}",docker_cmd], check=True, text=True)
            
            # Send command 1 to indicate that we are fetching a list of files.
            rdma_send_buf[0] = 1
            rdma_sink.send(rdma_send_buf[:1])
            
            print("Command fetch sent")
            
            result_image_path_bytes = result_image_path.encode('utf-8')
            result_image_path_array = np.frombuffer(result_image_path_bytes, dtype=np.uint8)
            
            # Send the directory name to fetch
            rdma_send_buf[:len(result_image_path_array)] = result_image_path_array
            rdma_sink.send(rdma_send_buf[:len(result_image_path_array)])
            
            print(f"Directory name sent: {result_image_path}")
            
            # Receive the session directory.
            while True:
                    # First receive: file path (string)
                    print("Receiving file path...")
                    path_data = rdma_src.recv()
                    
                    if len(path_data) == 0:
                        # No more files to send.
                        break
                    
                    # Decode the path if it's bytes, or handle as string
                    if isinstance(path_data, bytes):
                        # image_path = path_data.decode('utf-8')
                        rel_path = path_data.decode('utf-8')
                    elif isinstance(path_data, np.ndarray):
                        # image_path = path_data.tobytes().decode('utf-8')
                        rel_path = path_data.tobytes().decode('utf-8')
                    else:
                        # image_path = str(path_data)
                        rel_path = str(path_data)
                    
                    image_path = Path(MAIN_DIR) / rel_path
                    print(f"Main dir: {MAIN_DIR}; Relative path: {rel_path}")
                    #print(f"Received path: {image_path}")
                    
                    # Second receive: file content (numpy array)
                    print("Receiving file content...")
                    content_array = rdma_src.recv()
                    
                    # Convert numpy array to bytes
                    if isinstance(content_array, np.ndarray):
                        content_bytes = content_array.tobytes()
                    else:
                        content_bytes = bytes(content_array)
                    
                    print(f"Received {len(content_bytes)} bytes")
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    
                    # Write to file
                    with open(image_path, "wb") as f:
                        f.write(content_bytes)
                    
                    print(f"Successfully wrote file to: {image_path}")
            
            print("RDMA transfer done!")
        # -------------------------------------------------------------------

        result_image = None

        # Find the file which name is {person}_{cloth}.jpg
        person_base = os.path.splitext(person)[0]      # "webcam_image" (no .jpg)
        person_trimmed = person_base.split("_")[0] 
        cloth_base = os.path.splitext(cloth)[0]

        target_filename = f"{person_trimmed}_{cloth_base}.jpg"

        # Files full path
        jpg_files_full = [os.path.join(result_image_path, target_filename)]

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
# COMBINE GARMENT AND UPLOADED PICTURE.
@app.route('/run-script-upl', methods=['POST'])
def run_script_upl():
    # Collects person and garment data, after interacting with the home page of
    # the web application (get_json).
    data = request.get_json()
    person = data.get('person')
    cloth = data.get('cloth')
    unique_id = data.get('sessionId')    

    if not cloth:
        return jsonify({'error': 'Cloth selection is missing'}), 422

    # The final image is not saved locally. Clean any possible previous result
    # from the folder.
    result_image_path = MAIN_DIR + "/shared-data-tmp/" + unique_id + "/results"
    result_image_path_rdma = BACK_DIR + "/shared-data-tmp/" + unique_id + "/results"
        
    try:
        config_path = base_dir / "env_config.json"
        with open(config_path) as f:
            config = json.load(f)
            DEPLOYMENT=config["DEPLOYMENT"]
            
        if DEPLOYMENT == "LOCAL":
            # Run locally
            # ---------------------------------------------------------------
            docker_cmd = ("docker run --gpus all --rm --shm-size=2g "
                          f"-v /home/{USER_MAIN}/.ssh:/root/.ssh:ro "
                          "-v /var/run/docker.sock:/var/run/docker.sock "
                          f"-v {HOST_DIR}/shared-data/:/app/shared-data "
                          f"-v {HOST_DIR}/shared-data-tmp/:/app/shared-data-tmp "
                          f"smart-mirror-node_2 /app/run_only_viton.sh '{person}' '{cloth}' '{unique_id}'"
                         )
            # ----------------------------------------------------------------
            subprocess.run([docker_cmd], shell=True, check=True, text=True)
        else:
            # ---------------------------------------------------------------
            docker_cmd = ("docker run --gpus all --rm --shm-size=2g "
                          f"-v /home/{USER_BACK}/.ssh:/root/.ssh:ro "
                          "-v /var/run/docker.sock:/var/run/docker.sock "
                          f"-v {BACK_DIR}/shared-data/:/app/shared-data "
                          f"-v {BACK_DIR}/shared-data-tmp/:/app/shared-data-tmp "
                          f"smart-mirror-node_2 /app/run_only_viton.sh '{person}' '{cloth}' '{unique_id}'"
                         )
            # ----------------------------------------------------------------
            # Run VITON-HD on the other server.
            subprocess.run(["ssh",f"{USER_BACK}@{IP_BACK}",docker_cmd], check=True, text=True)
            
            # Send command 1 to indicate that we are fetching a list of files.
            rdma_send_buf[0] = 1
            rdma_sink.send(rdma_send_buf[:1])
            
            print("Command fetch sent")
            
            result_image_path_bytes = result_image_path.encode('utf-8')
            result_image_path_array = np.frombuffer(result_image_path_bytes, dtype=np.uint8)
            
            # Send the directory name to fetch
            rdma_send_buf[:len(result_image_path_array)] = result_image_path_array
            rdma_sink.send(rdma_send_buf[:len(result_image_path_array)])
            
            print(f"Directory name sent: {result_image_path}")
            
            # Receive the session directory.
            while True:
                    # First receive: file path (string)
                    print("Receiving file path...")
                    path_data = rdma_src.recv()
                    
                    if len(path_data) == 0:
                        # No more files to send.
                        break
                    
                    # Decode the path if it's bytes, or handle as string
                    if isinstance(path_data, bytes):
                        # image_path = path_data.decode('utf-8')
                        rel_path = path_data.decode('utf-8')
                    elif isinstance(path_data, np.ndarray):
                        # image_path = path_data.tobytes().decode('utf-8')
                        rel_path = path_data.tobytes().decode('utf-8')
                    else:
                        # image_path = str(path_data)
                        rel_path = str(path_data)
                    
                    image_path = Path(MAIN_DIR) / rel_path
                    print(f"Main dir: {MAIN_DIR}; Relative path: {rel_path}")
                    #print(f"Received path: {image_path}")
                    
                    # Second receive: file content (numpy array)
                    print("Receiving file content...")
                    content_array = rdma_src.recv()
                    
                    # Convert numpy array to bytes
                    if isinstance(content_array, np.ndarray):
                        content_bytes = content_array.tobytes()
                    else:
                        content_bytes = bytes(content_array)
                    
                    print(f"Received {len(content_bytes)} bytes")
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    
                    # Write to file
                    with open(image_path, "wb") as f:
                        f.write(content_bytes)
                    
                    print(f"Successfully wrote file to: {image_path}")
            
            print("RDMA transfer done!")
        # -------------------------------------------------------------------

        result_image = None

        # Find the file which name is {person}_{cloth}.jpg
        person_base = os.path.splitext(person)[0]      # "webcam_image" (no .jpg)
        person_trimmed = person_base.split("_")[0] 
        cloth_base = os.path.splitext(cloth)[0]

        target_filename = f"{person_trimmed}_{cloth_base}.jpg"

        # Files full path
        jpg_files_full = [os.path.join(result_image_path, target_filename)]

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
# PROCESS PICTURE FROM WEBCAM
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
        preprocess_python(session_dir)
        
        # Construct paths to generated images
        filename_without_ext = os.path.splitext(filename)[0]
        vis_image_dir = session_dir + "/img_parse/"
        vis_image_path = os.path.join(vis_image_dir, f"{filename_without_ext}_vis.png")

        openpose_img_dir = session_dir + "/openpose_img/"
        rendered_image_path = os.path.join(openpose_img_dir, f"{filename_without_ext}_rendered.png")
        

        config_path = base_dir / "env_config.json"
        with open(config_path) as f:
            config = json.load(f)
            DEPLOYMENT=config["DEPLOYMENT"]

        if DEPLOYMENT != "LOCAL":
            # This portion is for the RDMA version.
            # ---------------------------------------------------------
            # Send data.
            print("Sending data")                   
            send_session_dir_via_rdma(session_dir)
            
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
# PROCESS UPLOADED PICTURE
# This is to handle pictures uploaded by the user.
@app.route('/preprocess-upl', methods=['POST'])
def preprocess_upl():
    data = request.get_json()
    filename = data.get('filename')
    #image_data = data.get('image_data')  # base64 image from frontend
    if not filename:
        return jsonify({'error': 'No filename provided'}), 423

    try:
        # 
        upload_folder = app.config['UPLOAD_FOLDER']
        image_path = os.path.join(upload_folder, filename)
        
        # Generate unique session directory
        unique_id = str(uuid.uuid4())
        session_dir = os.path.join(MAIN_DIR, "shared-data-tmp", unique_id)
        os.makedirs(session_dir, exist_ok=True)  # ensure the folder exists

        # Copy necessary files to session dir
        local_file_path = os.path.join(session_dir,filename)
        shutil.copy(image_path, local_file_path)

        # Run the preprocessing script
        preprocess_python(session_dir)
        
        # Construct paths to generated images
        filename_without_ext = os.path.splitext(filename)[0]
        vis_image_dir = session_dir + "/img_parse/"
        vis_image_path = os.path.join(vis_image_dir, f"{filename_without_ext}_vis.png")

        openpose_img_dir = session_dir + "/openpose_img/"
        rendered_image_path = os.path.join(openpose_img_dir, f"{filename_without_ext}_rendered.png")       

        config_path = base_dir / "env_config.json"
        with open(config_path) as f:
            config = json.load(f)
            DEPLOYMENT=config["DEPLOYMENT"]

        if DEPLOYMENT != "LOCAL":
            # This portion is for the RDMA version.
            # ---------------------------------------------------------
            # Send data.
            print("Sending data")                   
            send_session_dir_via_rdma(session_dir)
            
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
# LOAD SAMPLE CLOTHES
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

# ---------------------------------------------------------------------------- #
# MAIN FUNCTION
"""
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
"""
import ssl

if __name__ == '__main__':
    # ------------------------------------------------------------------------ #
    # Start rdma backend on Node 2.
    docker_node2 = ("docker run --rm --name virtual_mirror_container2 "
                    "--network host "
                    "--privileged "
                    f"-v /home/{USER_BACK}/.ssh:/home/root/.ssh:ro "
                    "-v /var/run/docker.sock:/var/run/docker.sock "
                    f"-v {BACK_DIR}/shared-data/:/app/shared-data "
                    f"-v {BACK_DIR}/shared-data-tmp/:/app/shared-data-tmp "
                    "-p 3000:3000 -p 5000:5000 -p 8000:8000 "
                    "virtual_mirror_node2:latest python3 web_app/app_backend.py "
                    f"> /home/{USER_BACK}/rdma_log 2>&1 & "
                    )
    
    subprocess.run(["ssh",f"{USER_BACK}@{IP_BACK}",docker_node2], check=True, text=True)
    # ------------------------------------------------------------------------ #
    signal.signal(signal.SIGINT, signal_handler)

    cert_path = os.path.join(MAIN_DIR, 'web_app', 'backend-cert.pem')
    key_path  = os.path.join(MAIN_DIR, 'web_app', 'backend-key.pem')

    # Create a TLS 1.3 server context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.maximum_version = ssl.TLSVersion.TLSv1_3
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    # Initialize rdma
    dev, rdma_port, gid_idx = rdma.find_device(IP_RDMA_BACK)
    
    # Configure arguments and create sender
    args = rdma.RdmaArgs()
    args.dev = dev                          # RDMA device name (e.g., "mlx5_0")
    args.ip = IP_RDMA_BACK                  # Server IP for TCP handshake
    args.port = 5555                        # TCP port for connection setup
    args.gid_idx = gid_idx                  # RDMA GID index (from find_device)
    args.is_client = True                   # Server mode
    args.max_msg_bytes = 10 * 1024 * 1024   # 10 MiB max message size
    rdma_sink = rdma.RdmaSink(args)
    rdma_src = rdma.RdmaSrc(args)

    rdma_send_lock = threading.Lock()

    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            ssl_context=context
        )
    finally:
        stop_camera_stream()

