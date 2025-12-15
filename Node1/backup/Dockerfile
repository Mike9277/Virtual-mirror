FROM nvcr.io/nvidia/doca/doca:3.1.0-devel-host

ENV TZ=US \
    DEBIAN_FRONTEND=noninteractive

# ========================
# Install system deps + Node.js + Python
# ========================
RUN apt-get update && apt-get install -y \
    curl wget gnupg2 \
    python3 python3-dev python3-pip python3-numpy \
    ninja-build build-essential cmake git \
    ffmpeg ssh sshpass openssh-client jq \
    libgl1 libglib2.0-0 \
    bc libopencv-dev \
    libgflags-dev libgoogle-glog-dev libprotobuf-dev protobuf-compiler \
    libboost-all-dev libhdf5-serial-dev \
    libatlas-base-dev \
    apt-transport-https ca-certificates \
    lsb-release gnupg \
    && rm -rf /var/lib/apt/lists/*

# -------------------------
# Install Node.js 20
# -------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# -------------------------
# Install Docker CLI only (for Docker-out-of-Docker)
# -------------------------
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
       | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update && apt-get install -y docker-ce-cli

# -------------------------
# Python pip deps
# -------------------------
RUN python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir \
        flask requests flask-cors pillow opencv-python \
        numpy scipy matplotlib scikit-image \
    && python3 -m pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# ========================
# CREATE WORKDIR
# ========================
WORKDIR /app

# ========================
# Copy all project files
# ========================
COPY . .
COPY rdma-container/ /app/rdma-container/

# ==============================================
# Build Meson C++ application (from container 1)
# ========================
WORKDIR /app/rdma-container
RUN apt-get remove -y meson || true \
    && python3 -m pip install meson pybind11 \
    && meson setup builddir-release -Dbuildtype=release \
    && meson compile -C builddir-release

ENV PYTHONPATH=/app/rdma-container/builddir-release

# ========================
# Node.js dependencies for web app
# ========================
WORKDIR /app/web_app/viton
RUN npm install

# ========================
# SSH KEY + remote access (from container 2)
# ========================
WORKDIR /app
RUN ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N "" -q

ARG SERVER_USER
ARG SERVER1_IP
ARG SERVER2_IP
ARG PASSWORD

RUN sshpass -p "$PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no $SERVER_USER@$SERVER1_IP || true
RUN sshpass -p "$PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no $SERVER_USER@$SERVER2_IP || true

# ========================
# Update env_config.json for Docker path
# ========================
RUN jq '.MAIN_DIR="/app"' env_config.json > env_config_tmp.json \
    && mv env_config_tmp.json env_config.json

# ========================
# Build OpenPose CPU-only
# ========================
WORKDIR /app/openpose
RUN rm -rf build && mkdir build
WORKDIR /app/openpose/build
RUN cmake .. -DGPU_MODE=CPU_ONLY && make -j$(nproc)

ENV LD_LIBRARY_PATH=/app/openpose/build/src/openpose:$LD_LIBRARY_PATH

# ========================
# Expose ports
# ========================
EXPOSE 3000 5000 8000

# ========================
# Start Web Application
# ========================
WORKDIR /app
# CMD ["./run_web_app_build.sh"]
