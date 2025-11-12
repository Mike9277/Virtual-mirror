#!/bin/bash
set -euo pipefail

# --- Configurable variables ---
IMAGE_NAME="openpose_img"
CONTAINER_NAME="openpose_test_container"

# Host paths
PROJECT_ROOT="/home/darshan/openpose_test"
MEDIA_SRC_HOST="${PROJECT_ROOT}/openpose-gvirtus/media"

# In‑container paths
GVIRTUS_TARGET_DIR="/opt/GVirtuS/etc"
OPENPOSE_EXAMPLES_DIR="/opt/openpose/examples/gvirtus"
MEDIA_MOUNT_TARGET="/opt/openpose/examples/media"   # <-- bind mount target

# Local files to copy in
LOCAL_PROPERTIES="${PROJECT_ROOT}/openpose-gvirtus/properties.json"
LOCAL_SCRIPT="${PROJECT_ROOT}/openpose-gvirtus/00_test.cpp"
OPENPOSE_SCRIPT_DIR="${PROJECT_ROOT}/openpose-gvirtus/openpose_scripts"  # optional

# 🐳 Start container in detached mode with media folder mounted
docker run -dit --rm \
  --name "${CONTAINER_NAME}" \
  --gpus all \
  --network host \
  -v "${MEDIA_SRC_HOST}:${MEDIA_MOUNT_TARGET}:rw" \
  "${IMAGE_NAME}" \
  bash

echo "✅ Container started: ${CONTAINER_NAME}"
echo "🔗 Media bind mount: ${MEDIA_SRC_HOST} -> ${MEDIA_MOUNT_TARGET}"

# 📁 Copy properties.json into container
docker cp "${LOCAL_PROPERTIES}" "${CONTAINER_NAME}:${GVIRTUS_TARGET_DIR}/properties.json"
echo "📁 Copied properties.json"

# 📁 Ensure examples dir exists
docker exec "${CONTAINER_NAME}" mkdir -p "${OPENPOSE_EXAMPLES_DIR}"

# 📁 Copy 00_test.cpp into examples
docker cp "${LOCAL_SCRIPT}" "${CONTAINER_NAME}:${OPENPOSE_EXAMPLES_DIR}/00_test.cpp"
echo "📁 Copied 00_test.cpp into OpenPose examples"

# 📁 Copy any additional scripts
if [ -d "${OPENPOSE_SCRIPT_DIR}" ]; then
  docker cp "${OPENPOSE_SCRIPT_DIR}/." "${CONTAINER_NAME}:${OPENPOSE_EXAMPLES_DIR}/"
  echo "📁 Additional scripts copied to OpenPose examples"
fi

# 🛠️ Compile in examples/gvirtus, then run from openpose root
docker exec "${CONTAINER_NAME}" bash -lc "
  set -euo pipefail
  export OPENPOSE_ROOT=/opt/openpose
  export GVIRTUS_HOME=/opt/GVirtuS
  export LD_LIBRARY_PATH=\$OPENPOSE_ROOT/build/src/openpose:\$GVIRTUS_HOME/lib:\$GVIRTUS_HOME/lib/frontend:\$LD_LIBRARY_PATH

  echo '🛠️ Compiling...'
  cd '${OPENPOSE_EXAMPLES_DIR}'
  OPENCV_PKG=\$(pkg-config --exists opencv4 && echo opencv4 || echo opencv)

  nvcc 00_test.cpp -g -o 00_test \
    -std=c++17 \
    -I\"\$OPENPOSE_ROOT/include\" \
    -I\"\$OPENPOSE_ROOT/3rdparty/caffe/include\" \
    -L\"\$OPENPOSE_ROOT/build/src/openpose\" \
    -L\"\$OPENPOSE_ROOT/build/caffe/lib\" \
    -lopenpose -lcaffe -lgflags \$(pkg-config --cflags --libs \"\$OPENCV_PKG\") || \
  nvcc 00_test.cpp -g -o 00_test \
    -std=c++17 \
    -I\"\$OPENPOSE_ROOT/include\" \
    -I\"\$OPENPOSE_ROOT/3rdparty/caffe/include\" \
    -L\"\$OPENPOSE_ROOT/build/src/openpose\" \
    -L\"\$OPENPOSE_ROOT/build/caffe/lib\" \
    -lopenpose -lcaffe -lgflags -lstdc++fs \$(pkg-config --cflags --libs \"\$OPENCV_PKG\")

  echo '🚀 Running from \$OPENPOSE_ROOT...'
  cd \"\$OPENPOSE_ROOT\"
  # Use an image inside the mounted media; adjust file name as needed
  ./examples/gvirtus/00_test \
    --image_path '${MEDIA_MOUNT_TARGET}/img-20250729-wa0007.jpg' \
    --output_dir '${MEDIA_MOUNT_TARGET}'
"

echo "🟢 Done. Outputs will appear on the host in: ${MEDIA_SRC_HOST}"
