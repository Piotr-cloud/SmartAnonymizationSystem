#!/bin/bash

sudo apt install ffmpeg -y

git clone https://github.com/hukkelas/DeepPrivacy

cd DeepPrivacy

git checkout 5ee3f1b0608f03ac54d5694b6421f6132cb63f0e

python setup.py install

