#!/bin/bash

processingUnit=$1

if ! [[ "$processingUnit" =~ ^(GPU|CPU)$ ]]; then echo "Wrong processing unit !!"; exit 1; fi


echo 
echo "#-----------------------------------------------------------------------#"
echo "|  Installing smart anonymization platform using virtual enviroment"
echo "|  Processing unit:  $processingUnit"
echo "#-----------------------------------------------------------------------#"
echo 

echo "#------------------------------#"
echo "|  \"sudo apt-get update\""
echo "#------------------------------#"

sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update

echo "#------------------------------#"
echo "|  \"sudo apt-get update\" - DONE"
echo "#------------------------------#"


function runInstallScript(){
	
	scriptName=$1
	useVirtualEnv=$2
	dedicatedFolder=$3
	
	./subscripts/_installWrapper.sh  $processingUnit  $scriptName $useVirtualEnv $dedicatedFolder || exit $?
}



#                  Script name      venv    new folder   

runInstallScript   VirtualPython    false   false
runInstallScript   SystemPackages   false   false
runInstallScript   PythonLibs1      true    false
runInstallScript   DownloadFiles    true    false
runInstallScript   NVIDIA           true    false
runInstallScript   Dlib             true    true
runInstallScript   OpenCV           true    true
runInstallScript   PyTorch          true    false
runInstallScript   PythonLibs2      true    false
runInstallScript   Tensorflow       true    false
runInstallScript   DeepPrivacy      true    true



echo 
echo "#-----------------------------------------------------------------------#"
echo "|  Installation to $processingUnit is DONE !!"
echo "#-----------------------------------------------------------------------#"
echo 













