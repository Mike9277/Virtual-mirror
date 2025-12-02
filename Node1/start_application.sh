#!/bin/bash
# ------------------------------------------------------------------------------- 
# Read configuration file
CONFIG_FILE="./env_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "File di configurazione $CONFIG_FILE non trovato!"
    exit 1
fi

MAIN_DIR=$(jq -r '.MAIN_DIR' "$CONFIG_FILE")
USER_MAIN=$(jq -r '.USER_MAIN' "$CONFIG_FILE")
WEB_PORT=$(jq -r '.webPort' "$CONFIG_FILE")
API_PORT=$(jq -r '.apiPort' "$CONFIG_FILE")
CAMERA_PORT=$(jq -r '.cameraPort' "$CONFIG_FILE")

# -------------------------------------------------------------------------------
# Start the web application through the docker container.
docker run --rm -it --name virtual_mirror_container \
  --network host \
  --privileged \
  --shm-size=1g \
  -v /home/cldemo/.ssh:/root/.ssh:ro \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $MAIN_DIR/shared-data/:/app/shared-data \
  -v $MAIN_DIR/shared-data-tmp/:/app/shared-data-tmp \
  -v $MAIN_DIR/GVirtuS/:/app/GVirtuS \
  -p 3000:3000 -p 5000:5000 -p 8000:8000 \
  virtual_mirror_node_1:latest ./run_web_app.sh