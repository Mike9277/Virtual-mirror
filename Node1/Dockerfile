FROM node:20-bullseye

WORKDIR /app

# ========================
# Copy components
# ========================
COPY web_app/ ./web_app/
COPY env_config.json ./env_config.json
COPY shared-data/ ./shared-data/
COPY run_web_app_build.sh ./run_web_app_build.sh

COPY parallel_process.sh ./parallel_process.sh
COPY shared-data-tmp ./shared-data-tmp/
COPY GVirtuS ./GVirtuS/
COPY opencv ./opencv/
COPY openpose ./openpose/
COPY 2D-Human-Parsing ./2D-Human-Parsing/

# RDMA Functions
COPY rdma_service.sh ./rdma_service.sh
COPY RDMA_functions/ ./RDMA_functions/

# ========================
# Node.js dependencies
# ========================
WORKDIR /app/web_app/viton
RUN npm install

# ========================
# Install dependencies + Docker CLI
# ========================
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    ffmpeg \
    ssh \
    sshpass \
    openssh-client \
    jq \
    libgl1 \
    libglib2.0-0 \
    bc \
    cmake build-essential git libopencv-dev \
    libgflags-dev libgoogle-glog-dev libprotobuf-dev protobuf-compiler \
    libboost-all-dev libhdf5-serial-dev \
    libatlas-base-dev \
    docker.io \
    && python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir \
        flask requests flask-cors pillow opencv-python \
        numpy scipy matplotlib scikit-image \
    && python3 -m pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# ========================
# SSH Key for remote servers
# ========================
RUN ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N "" -q

ARG SERVER_USER
ARG SERVER1_IP
ARG SERVER2_IP
ARG PASSWORD

RUN sshpass -p "$PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no $SERVER_USER@$SERVER1_IP || true
RUN sshpass -p "$PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no $SERVER_USER@$SERVER2_IP || true

# ========================
# Enable scripts
# ========================
WORKDIR /app
RUN chmod +x run_web_app_build.sh
RUN chmod +x parallel_process.sh

# ========================
# Update env_config.json for Docker environment
# ========================
RUN jq '.MAIN_DIR="/app"' env_config.json > env_config_tmp.json && mv env_config_tmp.json env_config.json

# ========================
# Ensure public exists
# ========================
RUN mkdir -p /app/web_app/viton/public

# ========================
# Build OpenPose CPU-only
# ========================
WORKDIR /app/openpose
RUN rm -rf build && mkdir build
WORKDIR /app/openpose/build
RUN cmake .. -DGPU_MODE=CPU_ONLY
RUN make -j$(nproc)

# ========================
# Add OpenPose libraries to LD_LIBRARY_PATH
# ========================
ENV LD_LIBRARY_PATH=/app/openpose/build/src/openpose:$LD_LIBRARY_PATH

# ========================
# Expose ports
# ========================
EXPOSE 3000 5000 8000

# ========================
# Run the script
# ========================
WORKDIR /app
CMD ["./run_web_app_build.sh"]
