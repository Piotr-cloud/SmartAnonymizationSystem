#!/bin/bash

sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y

sudo apt install cmake pkg-config unzip yasm git checkinstall -y
sudo apt install libjpeg-dev libpng-dev libtiff-dev -y

sudo apt install libavcodec-dev libavformat-dev libswscale-dev libavresample-dev -y
sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev -y
sudo apt install libxvidcore-dev x264 libx264-dev libfaac-dev libmp3lame-dev libtheora-dev -y 
sudo apt install libfaac-dev libmp3lame-dev libvorbis-dev -y

sudo apt-get install libv4l-dev -y



