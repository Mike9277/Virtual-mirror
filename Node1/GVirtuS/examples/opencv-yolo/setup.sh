#!/bin/bash

apt-get update && apt-get install -y \
    build-essential cmake git pkg-config \
    libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev libxvidcore-dev libx264-dev \
    libjpeg-dev libpng-dev libtiff-dev gfortran openexr \
    libatlas-base-dev

cd ~
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd opencv && mkdir build && cd build

cmake -D CMAKE_BUILD_TYPE=Release \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D WITH_CUDA=ON \
    -D CUDA_ARCH_BIN="8.9" \
    -D WITH_CUDNN=ON \
    -D ENABLE_FAST_MATH=1 \
    -D CUDA_FAST_MATH=1 \
    -D BUILD_opencv_cudaarithm=OFF \
    -D OPENCV_GENERATE_PKGCONFIG=ON \
    -D WITH_CUBLAS=ON \
    -D OPENCV_DNN_CUDA=ON \
    -D CUDA_ARCH_PTX="" \
    -D BUILD_opencv_dnn=ON \
    -D OPENCV_DNN_SKIP_RNN=ON \
    -D BUILD_opencv_cudaimgproc=OFF \
    -D BUILD_opencv_cudaphoto=OFF \
    -D BUILD_opencv_photo=OFF \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_opencv_cudev=ON \
    -D BUILD_opencv_cudalegacy=OFF \
    -D CUDA_USE_STATIC_CUDA_RUNTIME=OFF \
    -D BUILD_EXAMPLES=OFF ..

make -j$(nproc)
make install
ldconfig