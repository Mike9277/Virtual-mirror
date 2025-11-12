# install openpose
# apt update && apt install -y protobuf-compiler libgoogle-glog-dev libboost-all-dev libhdf5-serial-dev
# cd ~
# git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose
# cd openpose
# git submodule update --init --recursive --remote
# mkdir build
# cd build && cmake .. && make -j$(nproc)

# install 2d-human-parsing
apt install -y python3-pip python-is-python3
pip install torch torchvision networkx scipy opencv-python
cd ~
rm -rf 2D-Human-Parsing
git clone https://github.com/fyviezhao/2D-Human-Parsing
cd 2D-Human-Parsing
# cp /gvirtus/examples/2d-human-parsing/deeplabv3plus-xception-vocNov14_20-51-38_epoch-89.pth ~/2D-Human-Parsing/pretrained/
cp /home/cldemo/guaitolini/GVirtuS/examples/2d-human-parsing/deeplabv3plus-xception-vocNov14_20-51-38_epoch-89.pth ~/2D-Human-Parsing/pretrained/

cat > demo_imgs/img_list.txt <<EOF
$HOME/2D-Human-Parsing/demo_imgs/suit.jpg
$HOME/2D-Human-Parsing/demo_imgs/skirt.jpg
$HOME/2D-Human-Parsing/demo_imgs/coat.jpg
$HOME/2D-Human-Parsing/demo_imgs/multiperson.jpg
EOF

# IMPORTANT:
# Before running the ./run.sh script, you have to download the model from
# https://drive.google.com/drive/folders/1ZvXgp8EdcoHFu9uici7jDtin6hi_VO3h?usp=sharing
# and save it at
# ~/2D-Human-Parsing/pretrained/deeplabv3plus-xception-vocNov14_20-51-38_epoch-89.pth