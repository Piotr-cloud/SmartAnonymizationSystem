#!/bin/bash



if ! [[ -f Anaconda3-2022.05-Linux-x86_64.sh ]]
then
	#wget https://repo.anaconda.com/archive/Anaconda3-2022.05-Linux-x86_64.sh
	chmod +x Anaconda3-2022.05-Linux-x86_64.sh
fi

./Anaconda3-2022.05-Linux-x86_64.sh -b -p ./conda

conda init
