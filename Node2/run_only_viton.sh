#!/bin/bash
# ---------------------------------------------------------------------------- #
# This script is specifically intended to run solely VITON, either through the
# web application or on its own.
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Get full absolute path to this script
current_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_CONFIG_PATH=$current_dir/env_config.json

# Define necessary VITON-HD directories and files:
MAIN_DIR=$(jq -r '.MAIN_DIR' $ENV_CONFIG_PATH)

person="${1%.jpg}"
cloth="$2"
session_id="$3"

echo $person
echo $cloth
echo "Session ID: $session_id"

# Clean any previous file in the results directory.
RESULT_DIR=$MAIN_DIR/shared-data/results
SESSION_DIR=$MAIN_DIR/shared-data-tmp/$session_id
rm -f $RESULT_DIR/*

cp $SESSION_DIR/openpose_img/${person}_rendered.png $MAIN_DIR/VITON-HD/datasets/test/openpose-img
cp $SESSION_DIR/openpose_json/${person}_keypoints.json $MAIN_DIR/VITON-HD/datasets/test/openpose-json 
cp $SESSION_DIR/img_parse/${person}_label.png $MAIN_DIR/VITON-HD/datasets/test/image-parse/${person}.png

# ---------------------------------------------------------------------------- #
# STEP 3: VITON-HD
cd $MAIN_DIR/VITON-HD
python3 test.py \
  --person $SESSION_DIR/${person}.jpg \
  --cloth $MAIN_DIR/VITON-HD/datasets/test/cloth/${cloth} \
  --save_dir $SESSION_DIR/results \
  --name viton
cd ..

echo "Viton DONE!"