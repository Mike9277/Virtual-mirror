#!/bin/bash
# ---------------------------------------------------------------------------- #
# Parallel preprocess script for VITON application
# Optimized version: runs 2D-Human-Parsing and OpenPose in parallel
# Handles GPU virtualization with GVirtuS for OpenPose
#
# 10 2025, Michelangelo Guaitolini
# ---------------------------------------------------------------------------- #

# --- FOLDER SETTINGS ---
SESSION_DIR="$1"
if [ -z "$SESSION_DIR" ]; then
  echo "Error: No session directory provided"
  exit 1
fi

current_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_CONFIG_PATH="$current_dir/env_config.json"

# Load MAIN_DIR from config
MAIN_DIR=$(jq -r '.MAIN_DIR' "$ENV_CONFIG_PATH")
PASSWORD=$(jq -r '.PASSWORD' "$ENV_CONFIG_PATH")

IMAGE_DIR="$SESSION_DIR"
OUTPUT_JSON_DIR="$SESSION_DIR/openpose_json"
OUTPUT_IMG_DIR="$SESSION_DIR/openpose_img"
IMG_LIST_PATH="$SESSION_DIR/img_list.txt"

mkdir -p "$OUTPUT_JSON_DIR" "$OUTPUT_IMG_DIR"

# --- FIND IMAGE ---
INPUT_FILE=$(find "$IMAGE_DIR" -maxdepth 1 -type f -name "*.jpg" | head -n 1)
if [ -z "$INPUT_FILE" ]; then
    echo "Error: No image found in $IMAGE_DIR"
    exit 1
fi
FILE_NAME=$(basename "$INPUT_FILE")

# ---------------------------------------------------------------------------- #
# TIMER
# ---------------------------------------------------------------------------- #
execute_with_timer() {
   local start_time=$(date +%s)
   local command=$1
   
   # Start the command in the background
   bash -c "$command" > /dev/null 2>&1 &
   local pid=$!

   # Display elapsed time in real-time
   while kill -0 $pid 2> /dev/null; do
       local current_time=$(date +%s.%N)
       local elapsed_time=$(echo "$current_time - $start_time" | bc)
       echo -ne "Running time: $(printf "%.2f" $elapsed_time)s\033[0K\r"
       sleep 0.1
   done
   
   wait $pid
   local status=$?
   
   local end_time=$(date +%s)
   local total_time=$((end_time - start_time))
   
   if [ $status -ne 0 ]; then
       echo -e "\nError during execution of ${command}"
           exit 1    
       else
           echo -e "\nExecution successfully finished. Total time: ${elapsed_time}s."
       fi
}

# Export the function so it's available in the subshells
export -f execute_with_timer

# ---------------------------------------------------------------------------- #
# OPENPOSE (Standard)
# ---------------------------------------------------------------------------- #
# No GVirtus.
# cd $MAIN_DIR/openpose
#   ./build/examples/openpose/openpose.bin \
#   --model_pose COCO \
#   --net_resolution "320x176" \
#   --image_dir $IMAGE_DIR --hand --disable_blending --display 0 \
#   --write_json $OUTPUT_JSON_DIR --write_images $OUTPUT_IMG_DIR \
#   --num_gpu -1 --num_gpu_start 0 & \
# cd ..  


# ---------------------------------------------------------------------------- #
# 2D HUMAN PARSING
# ---------------------------------------------------------------------------- #
HUMAN_PARSING_PATH="$MAIN_DIR/2D-Human-Parsing"
MODEL_PATH="/pretrained/deeplabv3plus-xception-vocNov14_20-51-38_epoch-89.pth"
OUTPUT_PARSE="$SESSION_DIR/img_parse"
mkdir -p "$OUTPUT_PARSE"

HUMAN_LOG="$SESSION_DIR/human_parsing.log"
HUMAN_TIME_LOG="$SESSION_DIR/human_parsing_time.log"

echo "Starting 2D-Human-Parsing..."
(
  PARSE_COMMAND="cd $MAIN_DIR/2D-Human-Parsing/inference && \
  echo $INPUT_FILE > $IMG_LIST_PATH && \
  python3 inference_acc.py \
    --loadmodel $HUMAN_PARSING_PATH$MODEL_PATH \
    --img_list $IMG_LIST_PATH \
    --output_dir $OUTPUT_PARSE \
    > $SESSION_DIR/human_parsing.log 2>&1"
  
  # Run wih timer and capture elapsed time
  execute_with_timer "$PARSE_COMMAND" | tee "$HUMAN_TIME_LOG" &
) &
PID_PARSING=$!

# ---------------------------------------------------------------------------- #
# OPENPOSE (GVirtus)
# ---------------------------------------------------------------------------- #
echo "Starting OpenPose..."
(
   OPENPOSE_LOG="$SESSION_DIR/openpose.log"
   OPENPOSE_TIME_LOG="$SESSION_DIR/openpose_time.log"

  # Execute GVirtus-powered Openpose and get the log.
  cp "$INPUT_FILE" "$MAIN_DIR/GVirtuS/examples/openpose/media/$FILE_NAME"
  
  cd "$MAIN_DIR/GVirtuS" || exit 1
  make run-openpose-test INPUT_FILE="/opt/openpose/examples/media/$FILE_NAME" \
      > "$OPENPOSE_LOG" 2>&1
  
  # Extract last line, with "total time"
  OPENPOSE_TIME_LINE=$(grep 'Total time:' "$OPENPOSE_LOG" | tail -n1 || true)

  if [ -n "$OPENPOSE_TIME_LINE" ]; then
    # Take the portion after "Total time:"
    OPENPOSE_TIME_AFTER=$(echo "$OPENPOSE_TIME_LINE" | awk -F'Total time:' '{print $2}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    # Write the string in the same format of the Openpose log.
    echo "Total time: $OPENPOSE_TIME_AFTER" > "$OPENPOSE_TIME_LOG"
  else
    # Fallback: take just the number.
    OPENPOSE_TIME_NUM=$(grep -Eo 'Total time: [0-9]+(\.[0-9]+)?' "$OPENPOSE_LOG" | awk '{print $3}' | tail -n1)
    if [ -n "$OPENPOSE_TIME_NUM" ]; then
      echo "$OPENPOSE_TIME_NUM" > "$OPENPOSE_TIME_LOG"
    else
      echo "OpenPose time not found in log" > "$OPENPOSE_TIME_LOG"
    fi
  fi

  # Move outputs and clean
  mv "$MAIN_DIR/GVirtuS/examples/openpose/media/${FILE_NAME%.*}_keypoints.json" "$OUTPUT_JSON_DIR/${FILE_NAME%.*}_keypoints.json"
  mv "$MAIN_DIR/GVirtuS/examples/openpose/media/${FILE_NAME%.*}_pose.png" "$OUTPUT_IMG_DIR/${FILE_NAME%.*}_rendered.png"

  rm "$MAIN_DIR/GVirtuS/examples/openpose/media/$FILE_NAME"
) &
PID_OPENPOSE=$!

# ---------------------------------------------------------------------------- #
# WAIT FOR BOTH
# ---------------------------------------------------------------------------- #
wait $PID_PARSING
wait $PID_OPENPOSE

echo "Preprocessing complete."
echo "Human Parsing log: $SESSION_DIR/human_parsing.log"
echo "OpenPose log: $SESSION_DIR/openpose.log"
