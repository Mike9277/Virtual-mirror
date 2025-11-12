#!/bin/bash
# ---------------------------------------------------------------------------- #
# This script is designed to run the web application related to the Smart 
# Shopping Use Case, developed for the project CLEVER. The script was initially
# developed by Emilie le Rouzic.
#
# 07 2025, Michelangelo Guaitolini
# ---------------------------------------------------------------------------- #
current_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_CONFIG_PATH=$current_dir/env_config.json

MAIN_DIR=$(jq -r '.MAIN_DIR' $ENV_CONFIG_PATH)
BACK_DIR=$(jq -r '.BACK_DIR' $ENV_CONFIG_PATH)

IP_BACK=$(jq -r '.IP_BACK' $ENV_CONFIG_PATH)
USER_BACK=$(jq -r '.USER_BACK' $ENV_CONFIG_PATH)

PASSWORD=$(jq -r '.PASSWORD' $ENV_CONFIG_PATH)

DOCKER=$(jq -r '.DOCKER' $ENV_CONFIG_PATH)

# ---------------------------------------------------------------------------- #
# Configuration data for the web application are in a shared-data folder, here
# the paths to the configuration file and shared-data folder are reported:

SHARED_DATA="$MAIN_DIR/shared-data/web_src"

# ---------------------------------------------------------------------------- #

# Colors are used to highlight messages to the user on the Terminal.
RED='\033[1;31m'
NC='\033[0m'
GREEN='\033[42m'

# ---------------------------------------------------------------------------- #
# Run web application:

cd web_app/viton/
cp $ENV_CONFIG_PATH $MAIN_DIR/web_app/viton/public/config.json && \
  npm run dev &

# Wait for a moment
sleep 1

# ---------------------------------------------------------------------------- #
# Read values from the config.json file. Necessary information are:
#
# - ipAddress: the IP Address where the web application is created. It may
#              require to be modified if run under a new Network.
# - webPort: sets the web port.
# - apiPort: sets the API port.
# - cameraPort: sets the camera port.
#
# Tipically the ports values do not need to be changed.

ipAddress=$(jq -r '.IP_MAIN' $ENV_CONFIG_PATH)
webPort=$(jq -r '.webPort' $ENV_CONFIG_PATH)
apiPort=$(jq -r '.apiPort' $ENV_CONFIG_PATH)
cameraPort=$(jq -r '.cameraPort' $ENV_CONFIG_PATH)

cd "$MAIN_DIR/web_app/"
if [ $? -ne 0 ]; then
    echo "Error: Failed to change directory."
    exit 1
fi

# ---------------------------------------------------------------------------- #
# Run GVirtus Docker on backend server
# This portions is needed to execute the backend portion of GVirtus service, 
# which is necessary to use the virtual GPU.

ssh $USER_BACK@$IP_BACK 'export BACK_DIR=$HOME/guaitolini/virtual_mirror_GVirtus
                        pkill -f "$BACK_DIR/bin/gvirtus-backend"; \
                        export GVIRTUS_HOME=$BACK_DIR/GVirtuS; \
                        export LD_LIBRARY_PATH="$GVIRTUS_HOME/lib:$LD_LIBRARY_PATH"; \
                        nohup $GVIRTUS_HOME/bin/gvirtus-backend $GVIRTUS_HOME/etc/properties.json > $GVIRTUS_HOME/gvirtus.log 2>&1 &'


                        
# ---------------------------------------------------------------------------- #
# A series of messages is printed on the Terminal, notifying the status of the
# web application.

echo "Everything is successfully launched."
echo -e "Web is accessible at ${GREEN}https://${ipAddress}:${webPort}${NC},"
echo "API at https://${ipAddress}:${apiPort},"
echo "and camera at https://${ipAddress}:${cameraPort}/video_feed if enabled."

# This command is launches the applications itself. After running docker, this
# will be available under /web_app_container.
python3 app.py

if [ $? -ne 0 ];then 
    echo -e "${RED}The application has been stopped${NC}"
    echo -e "${RED}container web_app was Stop${NC}"
    exit 1
fi
echo -e "${RED}The application has been stopped${NC}"
echo -e "${RED}container${NC} web_app ${RED}was Stop${NC}"
# ---------------------------------------------------------------------------- #


