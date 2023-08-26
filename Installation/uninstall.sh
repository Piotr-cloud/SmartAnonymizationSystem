
#the following script removes virtual enviroments

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $SCRIPT_DIR # To make sure PWD is in right place

{
	deactivate       # deactivate with echo off
	sudo rm -r CPU   # remove CPU with echo off
	sudo rm -r GPU   # remove GPU with echo off
} &> /dev/null 

echo "Uninstalled!"

