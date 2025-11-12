#!/bin/bash
set -e

export OPENPOSE_ROOT=/opt/openpose
export GVIRTUS_HOME=/opt/GVirtuS
export LD_LIBRARY_PATH=$OPENPOSE_ROOT/build/src/openpose:$GVIRTUS_HOME/lib:$GVIRTUS_HOME/lib/frontend:$LD_LIBRARY_PATH

echo "🛠️ Compiling OpenPose test..."
cd /opt/openpose/examples/gvirtus

JSON_HEADER_DIR=/opt/openpose/examples/gvirtus
if [ ! -f "$JSON_HEADER_DIR/json.hpp" ]; then
    echo "Downloading nlohmann/json.hpp..."
    curl -L -o "$JSON_HEADER_DIR/json.hpp" https://github.com/nlohmann/json/releases/download/v3.11.2/json.hpp
fi

nvcc 01_test.cpp -g -o 01_test \
  -I$OPENPOSE_ROOT/include \
  -I$OPENPOSE_ROOT/3rdparty/caffe/include \
  -I$JSON_HEADER_DIR \
  -L$OPENPOSE_ROOT/build/src/openpose \
  -L$OPENPOSE_ROOT/build/caffe/lib \
  -lopenpose -lcaffe -lgflags $(pkg-config --cflags --libs opencv4)

echo "🚀 Running OpenPose test..."
cd $OPENPOSE_ROOT
./examples/gvirtus/01_test "$@"
