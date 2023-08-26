#!/bin/bash



git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

python -m pip install opencv-python==4.8.0.76

CUDA_VERSION=6.1 #cat "$(dpkg -L nvidia-cuda-toolkit | grep 'version.txt')"

cd opencv

git checkout 588ddf1b181aa7243144b27d65fc7690fb89e344

if ! [[ -d build ]]
then
	mkdir build
fi

cd build

if [ "$processingUnit" = "CPU" ] | [ 1 = 1 ] # GPU support is disabled due to build issues on Ubuntu 20.4, since OpenCV requires MSVC compiler libraries
then

	cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_C_EXAMPLES=OFF \
	-D INSTALL_PYTHON_EXAMPLES=OFF \
	-D OPENCV_GENERATE_PKGCONFIG=ON \
	-D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
	-D BUILD_EXAMPLES=OFF ..

else
	cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_PYTHON_EXAMPLES=OFF \
	-D INSTALL_C_EXAMPLES=OFF \
	-D OPENCV_ENABLE_NONFREE=ON \
	-D BUILD_NEW_PYTHON_SUPPORT=ON \
	-D PYTHON3_PACKAGES_PATH=/usr/local/lib/python3.10/dist-packages \
	-D BUILD_opencv_python3=ON \
	-D OPENCV_GENERATE_PKGCONFIG=ON \
	-D OPENCV_PC_FILE_NAME=opencv4.pc \
	-D WITH_TBB=ON \
	-D ENABLE_FAST_MATH=1 \
	-D CUDA_FAST_MATH=1 \
	-D WITH_CUBLAS=1 \
	-D WITH_CUDA=ON \
	-D BUILD_opencv_cudacodec=OFF \
	-D WITH_CUDNN=ON \
	-D WITH_V4L=ON \
	-D OPENCV_DNN_CUDA=ON \
	-D CUDA_ARCH_BIN=$CUDA_VERSION \
	-D WITH_QT=OFF \
	-D WITH_OPENGL=ON \
	-D WITH_QT=OFF \
	-D WITH_GSTREAMER=ON \
	-D WITH_FFMPEG=ON \
	-D WITH_OPENCL=ON \
	-D OPENCV_ENABLE_NONFREE=ON \
	-D ENABLE_PRECOMPILED_HEADERS=YES \
	-D EIGEN_INCLUDE_PATH=/usr/include/eigen3 \
	-D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
	-D HAVE_opencv_python3=ON \
	-D PYTHON_EXECUTABLE=../../../../env/bin/python \
	-D BUILD_EXAMPLES=ON ..
	
	
fi

make -j $(nproc)


cd ..






