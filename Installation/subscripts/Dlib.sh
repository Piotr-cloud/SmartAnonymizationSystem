#!/bin/bash

git clone https://github.com/davisking/dlib
cd dlib
git checkout c6c865ba71fb41ff71f653358f4077c12ca5fe28

python -m pip install dlib==19.22.0

if ! [[ -d build ]]
then
	mkdir build
fi

if [ $processingUnit = "CPU" ]
then
	cmake ..
	cmake --build .
	python setup.py install

else
	
	cmake .. -DDLIB_USE_CUDA=1 -DUSE_AVX_INSTRUCTIONS=1
	cmake --build .
	python setup.py install USE_AVX_INSTRUCTIONS=1 DLIB_USE_CUDA=1

fi

cd ..


