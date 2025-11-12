# IMPORTANT:
# Before running the ./run.sh script, you have to download the model from
# https://drive.google.com/drive/folders/1ZvXgp8EdcoHFu9uici7jDtin6hi_VO3h?usp=sharing
# and save it at
# ~/2D-Human-Parsing/pretrained/deeplabv3plus-xception-vocNov14_20-51-38_epoch-89.pth

# See more details at:
# https://github.com/fyviezhao/2D-Human-Parsing


#export CUDNN_FRONTEND_LOG_INFO=1
#export PYTORCH_CUDNN_V8_API_DISABLED=1
#export CUDNN_LOGINFO_DBG=1
#export CUDNN_LOGDEST_DBG=stdout
cd ~/2D-Human-Parsing/inference
LD_PRELOAD="${GVIRTUS_HOME}/lib/frontend/libcudart.so:${GVIRTUS_HOME}/lib/frontend/libcuda.so:${GVIRTUS_HOME}/lib/frontend/libcublas.so:${GVIRTUS_HOME}/lib/frontend/libcublasLt.so:${GVIRTUS_HOME}/lib/frontend/libcudnn.so:${GVIRTUS_HOME}/lib/frontend/libcufft.so:${GVIRTUS_HOME}/lib/frontend/libcurand.so:${GVIRTUS_HOME}/lib/frontend/libcusparse.so:${GVIRTUS_HOME}/lib/frontend/libcusolver.so:${GVIRTUS_HOME}/lib/frontend/libnvrtc.so" \
PYTORCH_NVML_BASED_CUDA_CHECK=1 \
TORCHINDUCTOR_FORCE_DISABLE_CACHES=1 \
CUDA_LAUNCH_BLOCKING=1 \
TORCH_USE_CUDA_DSA=1 \
TORCH_SHOW_CPP_STACKTRACES=1  \
TORCH_SHOW_MEMORY_USAGE=1 \
PYTORCH_CUDA_FUSER_DISABLE=1 \
TORCH_CUDA_DEBUG=1 \
TOKENIZERS_PARALLELISM=false \
TORCH_DISABLE_ADDR2LINE=1 \
CUDNN_LOGINFO_DBG=1 \
CUDNN_LOGWARN_DBG=1 \
CUDNN_LOGERR_DBG=1 \
CUDNN_LOGDEST_DBG=stdout \
python inference_acc.py \
--loadmodel '/home/cldemo/guaitolini/GVirtuS/examples/2d-human-parsing/deeplabv3plus-xception-vocNov14_20-51-38_epoch-89.pth' \
--img_list ../demo_imgs/img_list.txt \
--output_dir ../parsing_result
