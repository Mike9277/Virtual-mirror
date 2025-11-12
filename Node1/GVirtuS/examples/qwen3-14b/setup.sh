#!/bin/bash
apt update && apt install -y python3 python3-pip
pip3 install transformers==4.54.1 accelerate==1.9.0