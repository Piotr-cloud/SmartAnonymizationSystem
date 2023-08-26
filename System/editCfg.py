'''
Created on Mar 19, 2022

@author: piotr
'''

import argparse



argsParser = argparse.ArgumentParser("The interface to edit processing configuration with no option to run processing")



argsParser.add_argument(
    "-cfg",
    type=str,
    default=None,
    help="Processing configuration file path to edit. When not provided default configuration is loaded"
    )



args = argsParser.parse_args()




if __name__ == "__main__":
    
    from MainExecutor.UserRequestProcessor import UserRequestProcessor_Config_Cls
     
    urp = UserRequestProcessor_Config_Cls()
    
    urp.run(cfgFilePath = args.cfg)
    
