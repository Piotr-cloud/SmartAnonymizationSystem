#!/bin/bash

installWorksp=installWorksp



processingUnit=$1
scriptName=$2
useVirtualEnv=$3
dedicatedFolder=$4


# Parse input arguments
if ! [[ "$processingUnit" =~ ^(GPU|CPU)$ ]];            then echo "Wrong processing unit !!"; exit 1; fi
if ! [[ -f ./subscripts/$scriptName.sh ]] ;             then echo "Install script $scriptName.sh does not exist !!"; exit 3; fi
if ! [[ "$useVirtualEnv" =~ ^(false|true)$ ]];          then echo "Wrong virtual env decision !!"; exit 4; fi
if ! [[ "$dedicatedFolder" =~ ^(false|true)$ ]];        then echo "Wrong dedicated dir decision !!"; exit 4; fi
	

if [ $useVirtualEnv = true ]
then
	# Activation of a virtual enviroment
	source ./activate.sh $processingUnit        # from now on the python and it's installed libraries becomes virtual
fi

echo 
echo "#----------------------------------------#"
echo "|  Installing $scriptName"
echo "|  Processing unit:  $processingUnit"
echo "#----------------------------------------#"
echo 


basePWD=$PWD
if [ $dedicatedFolder = true ]
then
	workspace_dir=./$processingUnit/$installWorksp/$scriptName
else
	workspace_dir=./$processingUnit/$installWorksp/__other
fi

error_exit()
{
	echo 
	echo "#----------------------------------------#"
	echo "|  -> $scriptName installation failed !!!"
	echo "#----------------------------------------#"
	echo 
	
	exit 1
}

function pipinstall()
{
	echo "#----------------------------------------#"
	echo "|  installing python package: $1 "
	echo "#----------------------------------------#"
	python -m pip install ${*}
	echo "#----------------------------------------#"
	echo "|  $1 package installed"
	echo "#----------------------------------------#"
}


mkdir -p $workspace_dir

cd $workspace_dir

source ./../../../subscripts/$scriptName.sh || error_exit $scriptName

cd $basePWD


	
echo 
echo "#----------------------------------------#"
echo "|  $scriptName installed !"
echo "#----------------------------------------#"
echo 


