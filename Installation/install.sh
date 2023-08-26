#!/bin/bash

# Implements option of GPU support and manages pwd as a directory reference for all the subsripts
# It is strongly recommended to install GPU support manually because GPU instalation is HW related and it's hard to automatize this process


# PWD context setting
THIS_SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $THIS_SCRIPT_DIR 



# GPU support command parsing
processingUnit=$1

if [ -z $processingUnit ]
then
	processingUnit="CPU"
else
	if ! [[ "$processingUnit" =~ ^(GPU|CPU)$ ]]; then echo "Wrong processing unit choice !! Choose one of CPU or GPU"; exit 1; fi
fi



./subscripts/_installSchedule.sh $processingUnit




