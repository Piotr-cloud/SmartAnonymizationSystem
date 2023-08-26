#!/bin/bash

# Alternative way to install python from source
#PYTHON_version=3.10.9
#
#wget https://www.python.org/ftp/python/$PYTHON_version/Python-$PYTHON_version.tgz
#tar -xf Python-$PYTHON_version.tgz
#
#cd  Python-$PYTHON_version/
#./configure --enable-optimizations
#
#make -j $(nproc)
#


sudo apt install python3.10 -y

sudo apt-get install python3.10-distutils -y
sudo apt install python3.10-venv -y

/usr/bin/python3.10 -m venv "$basePWD/$processingUnit/env"

sudo apt install libpython3.10-dev -y
sudo apt install python3.10-tk -y



