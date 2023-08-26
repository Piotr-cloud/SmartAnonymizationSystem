#!/bin/bash

processingUnit=$1

cwd=$PWD


THIS_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $THIS_SCRIPT_DIR 


if ! [[ "$processingUnit" =~ ^(GPU|CPU)$ ]]
then 
	if [ -d ./CPU/env ]
	then 
		processingUnit="CPU" # prefer CPU
	else
		processingUnit="GPU"
	fi
fi

echo "Activating python virtual enviroment; $processingUnit"

if [[ -f ./$processingUnit/env/bin/activate ]]
then
	source ./$processingUnit/env/bin/activate
else
	echo "Error! -> No python instance found"
fi

cd $cwd



