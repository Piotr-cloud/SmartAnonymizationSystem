#!/bin/bash



if [ $processingUnit = "GPU" ]
then
	sudo apt install nvidia-driver-515 nvidia-dkms-515 -y  # Nvidia GPU drivers installation
	sudo apt install nvidia-cuda-toolkit -y
	#./../Anaconda/conda/bin/conda install -c cudatoolkit=11.2 cudnn=8.1.0
fi




