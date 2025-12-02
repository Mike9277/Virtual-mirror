# ---------------------------------------------------------------------------- #
# Backend RDMA Receiver Application
# Receives image path and content via RDMA, then writes to file
# Based on app.py sender implementation
#
# 11 2025, Michelangelo Guaitolini
# ---------------------------------------------------------------------------- #

import os
import json
import signal
import sys
from pathlib import Path
import rdma
import numpy as np

# Load configuration
base_dir = Path(__file__).resolve().parent.parent
config_path = base_dir / "env_config.json"
with open(config_path) as f:
    config = json.load(f)

MAIN_DIR = config["MAIN_DIR"]
BACK_DIR = config["BACK_DIR"]
IP_RDMA_BACK = config["PORT_BACK"]

rdma_sink = None
rdma_src = None
rdma_send_buf = np.zeros(10 * 1024 * 1024, dtype=np.uint8)

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\nShutting down RDMA receiver...")
    sys.exit(0)

def send_session_dir_via_rdma(session_dir: str):
    """
    Send all files in `session_dir` (and subfolders) via RDMA client executable.
    
    Args:
        session_dir: Root directory to send.
    """
    session_dir = Path(session_dir)
    if not session_dir.exists():
        raise FileNotFoundError(f"{session_dir} does not exist")

    print(f"Fetching directory: {session_dir}")
     
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
            
            
def receive_and_write_file():
    """
    Main loop to receive file path and content via RDMA
    """
    print("Waiting for incoming RDMA data...")
    
    try:
        while True:
            
            # First receive the command
            command = rdma_src.recv()
            
            # Command is 1 byte.
            # - 0 means: remote wants to send a list of files.
            # -          after all files are sent, sends a zero-byte send.
            # - 1 means: remote wants to fetch a list of files.
            # -          after all files are sent, sends a zero-byte send.
            
            if command[0] == 0:
                print("Received command: Writing list of files")
                # Receive a list of files.
                while True:
                    # First receive: file path (string)
                    print("Receiving file path...")
                    path_data = rdma_src.recv()
                    
                    if len(path_data) == 0:
                        # No more files to send.
                        break
                    
                    # Decode the path if it's bytes, or handle as string
                    if isinstance(path_data, bytes):
                        image_path = path_data.decode('utf-8')
                    elif isinstance(path_data, np.ndarray):
                        image_path = path_data.tobytes().decode('utf-8')
                    else:
                        image_path = str(path_data)
                    
                    print(f"Received path: {image_path}")
                    
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
            elif command[0] == 1:
                print("Received command: Fetching directory")
                # Receive the session directory.
                session_directory = rdma_src.recv()
                
                # Decode the path if it's bytes, or handle as string
                if isinstance(session_directory, bytes):
                    session_directory = session_directory.decode('utf-8')
                elif isinstance(session_directory, np.ndarray):
                    session_directory = session_directory.tobytes().decode('utf-8')
                else:
                    session_directory = str(session_directory)
                    
                send_session_dir_via_rdma(session_directory)
                
                # Send all the files
                
            else:
                raise ValueError(f"Unknown command: {command[0]}")
            
    except KeyboardInterrupt:
        print("\nReceiver interrupted by user")
    except Exception as e:
        print(f"Error in receive loop: {e}")
        raise

if __name__ == '__main__':
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Initializing RDMA receiver...")
    
    # Find RDMA device
    dev, rdma_port, gid_idx = rdma.find_device(IP_RDMA_BACK)
    print(f"Found RDMA device: {dev}, port: {rdma_port}, gid_idx: {gid_idx}")
    
    # Configure RDMA arguments for receiver (client mode)
    args = rdma.RdmaArgs()
    args.dev = dev                          # RDMA device name
    args.ip = IP_RDMA_BACK                  # Connect to sender's IP
    args.port = 5555                        # TCP port for connection setup (same as sender)
    args.gid_idx = gid_idx                  # RDMA GID index
    args.is_client = False                  # Client mode (receiver connects to sender)
    args.max_msg_bytes = 10 * 1024 * 1024  # 10 MiB max message size
    
    # Create RDMA source (receiver)
    print("Creating RdmaSrc...")
    rdma_src = rdma.RdmaSrc(args)
    print("RDMA receiver initialized successfully!")
    rdma_sink = rdma.RdmaSink(args)
    print("RDMA sink initialized successfully!")
    
    # Start receiving loop
    receive_and_write_file()
